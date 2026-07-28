"""Pier custom agents backed by a GitHub Copilot subscription."""

from __future__ import annotations

import shlex
from pathlib import Path

from pier.agents.installed.base import BaseInstalledAgent
from pier.agents.installed.mini_swe_agent import MiniSweAgent
from pier.environments.base import BaseEnvironment
from pier.models.agent.context import AgentContext
from pier.models.agent.install import AgentInstallSpec, InstallStep
from pier.models.agent.network import NetworkAllowlist

_REMOTE_TOKEN_PATH = "/tmp/deepswe-copilot-token"
_LITELLM_TOKEN_DIR = "/tmp/deepswe-copilot-auth/litellm"
_COPILOT_DOMAINS = ["github.com", "api.github.com", ".githubcopilot.com"]


class _CredentialMixin:
    """Upload a host credential without placing its value in Pier's config or logs."""

    _credential_file: Path
    _github_host: str | None

    def _set_credential_file(self, credential_file: str | Path) -> None:
        path = Path(credential_file).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"GitHub credential file does not exist: {path}")
        self._credential_file = path

    def _set_github_host(self, github_host: str | None) -> None:
        self._github_host = github_host.strip().lower() if github_host else None

    def _copilot_domains(self) -> list[str]:
        domains = list(_COPILOT_DOMAINS)
        if self._github_host:
            domains.extend([self._github_host, f"api.{self._github_host}"])
        return list(dict.fromkeys(domains))

    async def _upload_credential(self, environment: BaseEnvironment) -> None:
        # Pier's Docker upload uses `docker compose cp`. On Docker Desktop for
        # Windows, copying to a newly-created nested directory can race with
        # Pier's container lifecycle. /tmp is guaranteed to exist.
        await environment.upload_file(self._credential_file, _REMOTE_TOKEN_PATH)
        await environment.exec(
            command=f"chmod 600 {shlex.quote(_REMOTE_TOKEN_PATH)}",
            user="root",
        )


class CopilotCliAgent(_CredentialMixin, BaseInstalledAgent):
    """Run the official GitHub Copilot CLI as a Pier installed agent."""

    SUPPORTS_ATIF = False

    def __init__(
        self,
        *args,
        credential_file: str | Path,
        github_host: str | None = None,
        max_ai_credits: int | None = None,
        reasoning_effort: str | None = None,
        **kwargs,
    ) -> None:
        self._set_credential_file(credential_file)
        self._set_github_host(github_host)
        if max_ai_credits is not None and max_ai_credits <= 0:
            raise ValueError("max_ai_credits must be greater than zero")
        self._max_ai_credits = max_ai_credits
        self._reasoning_effort = reasoning_effort
        super().__init__(*args, **kwargs)

    @staticmethod
    def name() -> str:
        return "copilot-cli"

    def get_version_command(self) -> str:
        return (
            'if [ -s "$HOME/.nvm/nvm.sh" ]; then . "$HOME/.nvm/nvm.sh"; fi; '
            "copilot --version"
        )

    def parse_version(self, stdout: str) -> str:
        for line in stdout.splitlines():
            if "GitHub Copilot CLI" in line:
                return line.rsplit(" ", 1)[-1].rstrip(".")
        return stdout.strip()

    def install_spec(self) -> AgentInstallSpec:
        package_version = f"@{self._version}" if self._version else "@latest"
        root_run = (
            "set -euo pipefail; "
            "if command -v apk >/dev/null 2>&1; then "
            "apk add --no-cache bash curl git npm nodejs; "
            "elif command -v apt-get >/dev/null 2>&1; then "
            "for source in /etc/apt/sources.list.d/*; do "
            "[ -f \"$source\" ] || continue; "
            "if grep -qF deb.nodesource.com \"$source\"; then "
            "mv \"$source\" \"$source.disabled\"; "
            "fi; "
            "done; "
            "apt-get update && DEBIAN_FRONTEND=noninteractive "
            "apt-get install -y --no-install-recommends bash ca-certificates curl git; "
            "elif command -v yum >/dev/null 2>&1; then "
            "yum install -y bash ca-certificates curl git; "
            "elif command -v dnf >/dev/null 2>&1; then "
            "dnf install -y bash ca-certificates curl git; "
            "fi"
        )
        agent_run = (
            "set -euo pipefail; "
            "node_major=0; "
            "if command -v node >/dev/null 2>&1; then "
            "node_major=\"$(node -p 'process.versions.node.split(\".\")[0]')\"; "
            "fi; "
            'if command -v npm >/dev/null 2>&1 && [ "$node_major" -ge 22 ]; then '
            f"npm install -g @github/copilot{package_version}; "
            "else "
            "export NVM_DIR=\"$HOME/.nvm\"; "
            "curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh "
            "| bash; "
            '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"; '
            "nvm install 22; nvm alias default 22; "
            f"npm install -g @github/copilot{package_version}; "
            "fi; copilot --version"
        )
        symlink_run = (
            "set -euo pipefail; "
            'if [ -s "$HOME/.nvm/nvm.sh" ]; then . "$HOME/.nvm/nvm.sh"; fi; '
            "for binary in node copilot; do "
            'path="$(command -v "$binary")"; '
            'ln -sf "$path" "/usr/local/bin/$binary"; '
            "done"
        )
        return AgentInstallSpec(
            agent_name=self.name(),
            version=self._version,
            steps=[
                InstallStep(user="root", run=root_run),
                InstallStep(user="agent", run=agent_run),
                InstallStep(user="root", run=symlink_run),
            ],
            verification_command=self.get_version_command(),
        )

    def network_allowlist(self) -> NetworkAllowlist:
        return NetworkAllowlist(domains=self._copilot_domains())

    def populate_context_post_run(self, context: AgentContext) -> None:
        # Copilot's text transcript is retained in /logs/agent. Pier still records
        # task result and verifier metrics even though no ATIF converter is available.
        return None

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        del context
        if not self.model_name:
            raise ValueError("A Copilot model is required")
        await self._upload_credential(environment)

        model = self.model_name.removeprefix("github_copilot/")
        flags = [
            "--allow-all-tools",
            "--allow-all-paths",
            "--no-ask-user",
            "--disable-builtin-mcps",
            "--no-auto-update",
            "--no-color",
            "--no-remote-export",
            "--secret-env-vars=COPILOT_GITHUB_TOKEN",
            f"--model={shlex.quote(model)}",
            "--share=/logs/agent/copilot-transcript.md",
            f"--prompt={shlex.quote(instruction)}",
        ]
        if self._max_ai_credits is not None:
            flags.insert(-3, f"--max-ai-credits={self._max_ai_credits}")
        if self._reasoning_effort:
            flags.insert(-2, f"--reasoning-effort={shlex.quote(self._reasoning_effort)}")

        command = (
            "set -euo pipefail; "
            f'trap "rm -f {shlex.quote(_REMOTE_TOKEN_PATH)}" EXIT; '
            f'export COPILOT_GITHUB_TOKEN="$(cat {shlex.quote(_REMOTE_TOKEN_PATH)})"; '
            + (
                f"export COPILOT_GH_HOST={shlex.quote(self._github_host)}; "
                if self._github_host
                else ""
            )
            +
            f"copilot {' '.join(flags)} 2>&1 | tee /logs/agent/copilot-cli.txt"
        )
        await self.exec_as_agent(environment, command=command)


class CopilotMiniSweAgent(_CredentialMixin, MiniSweAgent):
    """Run mini-swe-agent with LiteLLM's official GitHub Copilot provider."""

    def __init__(
        self,
        *args,
        credential_file: str | Path,
        github_host: str | None = None,
        **kwargs,
    ) -> None:
        self._set_credential_file(credential_file)
        self._set_github_host(github_host)
        extra_env = dict(kwargs.pop("extra_env", {}) or {})
        # Pier 0.3.0 asks for a generic API-key variable before launching mini,
        # although LiteLLM's github_copilot provider authenticates from its token dir.
        extra_env.setdefault("MSWEA_API_KEY", "managed-by-github-copilot-oauth")
        extra_env["GITHUB_COPILOT_TOKEN_DIR"] = _LITELLM_TOKEN_DIR
        super().__init__(*args, extra_env=extra_env, **kwargs)

    @staticmethod
    def name() -> str:
        return "copilot-mini-swe-agent"

    def network_allowlist(self) -> NetworkAllowlist:
        return NetworkAllowlist(domains=self._copilot_domains())

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        await self._upload_credential(environment)
        await self.exec_as_root(
            environment,
            command=(
                f"mkdir -p {shlex.quote(_LITELLM_TOKEN_DIR)}; "
                f"cp {shlex.quote(_REMOTE_TOKEN_PATH)} "
                f"{shlex.quote(_LITELLM_TOKEN_DIR + '/access-token')}; "
                f"chmod 700 {shlex.quote(_LITELLM_TOKEN_DIR)}; "
                f"chmod 600 {shlex.quote(_LITELLM_TOKEN_DIR + '/access-token')}; "
                "python3 - <<'PY'\n"
                "import json\n"
                "import time\n"
                "import urllib.request\n"
                f"token = open({str(_REMOTE_TOKEN_PATH)!r}, encoding='utf-8').read().strip()\n"
                "request = urllib.request.Request(\n"
                f"    {'https://api.' + (self._github_host or 'github.com') + '/copilot_internal/user'!r},\n"
                "    headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},\n"
                ")\n"
                "with urllib.request.urlopen(request, timeout=20) as response:\n"
                "    user = json.load(response)\n"
                "endpoint = user.get('endpoints', {}).get('api')\n"
                "if not endpoint:\n"
                "    raise RuntimeError('Copilot user response did not include an API endpoint')\n"
                "cache = {'token': token, 'expires_at': time.time() + 3600,\n"
                "         'endpoints': {'api': endpoint}}\n"
                f"with open({str(_LITELLM_TOKEN_DIR + '/api-key.json')!r}, 'w', "
                "encoding='utf-8') as handle:\n"
                "    json.dump(cache, handle)\n"
                "PY\n"
                f"chmod 600 {shlex.quote(_LITELLM_TOKEN_DIR + '/api-key.json')}"
            ),
        )
        try:
            await super().run(instruction, environment, context)
        finally:
            await environment.exec(
                command=(
                    f"rm -f {shlex.quote(_REMOTE_TOKEN_PATH)} "
                    f"{shlex.quote(_LITELLM_TOKEN_DIR + '/access-token')} "
                    f"{shlex.quote(_LITELLM_TOKEN_DIR + '/api-key.json')}"
                ),
                user="root",
            )
