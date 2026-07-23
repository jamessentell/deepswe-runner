from argparse import Namespace
from pathlib import Path

import pytest

from deepswe_runner.cli import (
    RunnerError,
    build_pier_command,
    normalize_model,
    redact_command,
    selected_count,
    validate_selection,
)


def args(**overrides):
    values = {
        "agent": "copilot-cli",
        "model": ["gpt-5-mini"],
        "task": ["task-a"],
        "n_tasks": None,
        "sample_seed": 0,
        "all_tasks": False,
        "concurrency": 1,
        "jobs_dir": Path("jobs"),
        "job_name": "test",
        "copilot_version": "1.0.73",
        "max_ai_credits": 30,
        "reasoning_effort": None,
        "keep_containers": False,
        "debug": False,
        "pier_arg": [],
    }
    values.update(overrides)
    return Namespace(**values)


def test_model_prefix_is_normalized():
    assert normalize_model("gpt-5-mini") == "github_copilot/gpt-5-mini"
    assert (
        normalize_model("github_copilot/claude-sonnet-4.6")
        == "github_copilot/claude-sonnet-4.6"
    )


def test_implicit_full_run_is_rejected():
    with pytest.raises(RunnerError, match="Refusing to run all"):
        validate_selection(args(task=[], n_tasks=None), ["task-a", "task-b"])


def test_unknown_explicit_task_is_rejected():
    with pytest.raises(RunnerError, match="Unknown task"):
        validate_selection(args(task=["missing"]), ["task-a", "task-b"])


def test_subset_count_accounts_for_models_later():
    assert selected_count(args(task=[], n_tasks=3), [str(i) for i in range(10)]) == 3
    assert selected_count(args(task=["a", "b"], n_tasks=1), ["a", "b"]) == 1


def test_direct_command_has_models_subset_and_credit_limit(monkeypatch, tmp_path):
    monkeypatch.setattr("deepswe_runner.cli.shutil.which", lambda name: f"/bin/{name}")
    command = build_pier_command(
        args(model=["gpt-5-mini", "claude-haiku-4.5"]),
        benchmark_dir=tmp_path,
        credential_file=tmp_path / "credential",
    )
    joined = " ".join(command)
    assert "--agent-import-path deepswe_runner.agents:CopilotCliAgent" in joined
    assert "--model github_copilot/gpt-5-mini" in joined
    assert "--model github_copilot/claude-haiku-4.5" in joined
    assert "--include-task-name task-a" in joined
    assert "--agent-kwarg max_ai_credits=30" in joined
    assert "--n-concurrent 1" in joined


def test_mini_command_uses_dollar_limit(monkeypatch, tmp_path):
    monkeypatch.setattr("deepswe_runner.cli.shutil.which", lambda name: f"/bin/{name}")
    command = build_pier_command(
        args(agent="mini-swe-agent"),
        benchmark_dir=tmp_path,
        credential_file=tmp_path / "credential",
    )
    joined = " ".join(command)
    assert "--agent-import-path deepswe_runner.agents:CopilotMiniSweAgent" in joined
    assert "--agent-kwarg cost_limit=0.3" in joined


def test_command_output_redacts_credential_path():
    credential_file = Path("/tmp/deepswe-copilot-secret")
    rendered = redact_command(
        ["pier", "--agent-kwarg", f"credential_file={credential_file}"],
        credential_file,
    )
    assert str(credential_file) not in rendered
    assert "credential_file=<temporary-credential>" in rendered
