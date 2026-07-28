"""Pier environments with runner-specific reliability behavior."""

from __future__ import annotations

import asyncio

from pier.environments.docker.docker import DockerEnvironment
from pier.environments.base import ExecResult


class RetryingDockerEnvironment(DockerEnvironment):
    """Retry failed Docker image builds before an agent can consume credits."""

    def __init__(self, *args, build_retries: int | str = 2, **kwargs) -> None:
        self._build_retries = int(build_retries)
        if self._build_retries < 0:
            raise ValueError("build_retries cannot be negative")
        super().__init__(*args, **kwargs)

    async def _run_docker_compose_command(
        self,
        command: list[str],
        check: bool = True,
        timeout_sec: int | None = None,
    ) -> ExecResult:
        retries = self._build_retries if command and command[0] == "build" else 0
        for attempt in range(retries + 1):
            try:
                return await super()._run_docker_compose_command(
                    command,
                    check=check,
                    timeout_sec=timeout_sec,
                )
            except RuntimeError:
                if attempt == retries:
                    raise
                delay = min(2**attempt, 10)
                self.logger.warning(
                    "Docker image build failed; retrying in %s second(s) "
                    "(attempt %s of %s)",
                    delay,
                    attempt + 2,
                    retries + 1,
                )
                await asyncio.sleep(delay)

        raise AssertionError("unreachable")
