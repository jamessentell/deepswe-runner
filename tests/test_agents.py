from pathlib import Path

import pytest

from deepswe_runner.agents import CopilotCliAgent, CopilotMiniSweAgent


def credential(tmp_path: Path) -> Path:
    path = tmp_path / "credential"
    path.write_text("secret", encoding="utf-8")
    return path


def test_copilot_cli_agent_strips_provider_prefix(tmp_path):
    agent = CopilotCliAgent(
        logs_dir=tmp_path,
        model_name="github_copilot/gpt-5-mini",
        credential_file=credential(tmp_path),
    )
    assert agent.name() == "copilot-cli"
    assert ".githubcopilot.com" in agent.network_allowlist().domains


def test_enterprise_host_is_allowed_and_configured(tmp_path):
    agent = CopilotCliAgent(
        logs_dir=tmp_path,
        model_name="github_copilot/gpt-5-mini",
        credential_file=credential(tmp_path),
        github_host="servername.ghe.com",
    )
    assert "servername.ghe.com" in agent.network_allowlist().domains
    assert "api.servername.ghe.com" in agent.network_allowlist().domains


def test_mini_agent_configures_litellm_auth(tmp_path):
    agent = CopilotMiniSweAgent(
        logs_dir=tmp_path,
        model_name="github_copilot/gpt-5-mini",
        credential_file=credential(tmp_path),
        cost_limit=0.3,
    )
    env = agent.build_process_env()
    assert env["GITHUB_COPILOT_TOKEN_DIR"].endswith("/litellm")
    assert env["MSWEA_API_KEY"] == "managed-by-github-copilot-oauth"
    assert ".githubcopilot.com" in agent.network_allowlist().domains


def test_agents_require_existing_credential(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        CopilotCliAgent(
            logs_dir=tmp_path,
            model_name="github_copilot/gpt-5-mini",
            credential_file=tmp_path / "missing",
        )
