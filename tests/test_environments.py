from unittest.mock import AsyncMock, MagicMock

import pytest

from deepswe_runner.environments import RetryingDockerEnvironment
from pier.environments.base import ExecResult


@pytest.mark.asyncio
async def test_docker_build_failures_are_retried_without_rerunning_other_commands(
    monkeypatch,
):
    environment = object.__new__(RetryingDockerEnvironment)
    environment._build_retries = 2
    environment.logger = MagicMock()
    run = AsyncMock(
        side_effect=[
            RuntimeError("temporary network failure"),
            ExecResult(stdout="built", stderr=None, return_code=0),
        ]
    )
    monkeypatch.setattr(
        "pier.environments.docker.docker.DockerEnvironment."
        "_run_docker_compose_command",
        run,
    )
    sleep = AsyncMock()
    monkeypatch.setattr("deepswe_runner.environments.asyncio.sleep", sleep)

    result = await environment._run_docker_compose_command(["build"])

    assert result.return_code == 0
    assert run.await_count == 2
    sleep.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_non_build_commands_are_not_retried(monkeypatch):
    environment = object.__new__(RetryingDockerEnvironment)
    environment._build_retries = 2
    run = AsyncMock(side_effect=RuntimeError("start failed"))
    monkeypatch.setattr(
        "pier.environments.docker.docker.DockerEnvironment."
        "_run_docker_compose_command",
        run,
    )

    with pytest.raises(RuntimeError, match="start failed"):
        await environment._run_docker_compose_command(["up", "-d"])

    assert run.await_count == 1
