from argparse import Namespace
from pathlib import Path

import pytest

from deepswe_runner.cli import (
    RunnerError,
    _decode_credential_blob,
    _copilot_credential_host,
    build_pier_command,
    normalize_model,
    pier_result_succeeded,
    redact_command,
    selected_count,
    _run_command,
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
        "benchmark_dir": Path(".cache/deep-swe"),
        "update_benchmark": False,
        "job_name": "test",
        "copilot_version": "1.0.75",
        "max_ai_credits": 30,
        "reasoning_effort": None,
        "keep_containers": False,
        "debug": False,
        "pier_arg": [],
        "dry_run": False,
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


@pytest.mark.parametrize("agent", ["copilot-cli", "mini-swe-agent"])
def test_command_omits_credit_limit_by_default(monkeypatch, tmp_path, agent):
    monkeypatch.setattr("deepswe_runner.cli.shutil.which", lambda name: f"/bin/{name}")
    command = build_pier_command(
        args(agent=agent, max_ai_credits=None),
        benchmark_dir=tmp_path,
        credential_file=tmp_path / "credential",
    )
    joined = " ".join(command)
    assert "max_ai_credits=" not in joined
    assert "cost_limit=" not in joined


def test_command_output_redacts_credential_path():
    credential_file = Path("/tmp/deepswe-copilot-secret")
    rendered = redact_command(
        ["pier", "--agent-kwarg", f"credential_file={credential_file}"],
        credential_file,
    )
    assert str(credential_file) not in rendered
    assert "credential_file=<temporary-credential>" in rendered


def test_windows_credential_blob_decodes_utf8():
    assert _decode_credential_blob(b"token-secret") == "token-secret"


def test_windows_credential_blob_decodes_utf16():
    assert _decode_credential_blob("token-secret".encode("utf-16-le")) == "token-secret"


@pytest.mark.parametrize(
    ("target", "host"),
    [
        ("https://github.com:james.copilot-cli", "github.com"),
        ("https://servername.ghe.com:james.copilot-cli", "servername.ghe.com"),
        ("https://acme.ghe.com:person@example.com.copilot-cli", "acme.ghe.com"),
        ("unrelated-credential", None),
    ],
)
def test_copilot_credential_host_accepts_enterprise_targets(target, host):
    assert _copilot_credential_host(target) == host


def test_enterprise_host_is_passed_to_agent(monkeypatch, tmp_path):
    monkeypatch.setattr("deepswe_runner.cli.shutil.which", lambda name: f"/bin/{name}")
    command = build_pier_command(
        args(github_host="servername.ghe.com"),
        benchmark_dir=tmp_path,
        credential_file=tmp_path / "credential",
    )
    assert "github_host=servername.ghe.com" in command


def test_pier_result_detects_trial_errors(tmp_path):
    result_path = tmp_path / "result.json"
    result_path.write_text(
        '{"finished_at":"now","n_total_trials":1,"stats":'
        '{"n_completed_trials":1,"n_errored_trials":1,"n_cancelled_trials":0}}',
        encoding="utf-8",
    )
    assert not pier_result_succeeded(result_path)


def test_pier_result_accepts_clean_completion(tmp_path):
    result_path = tmp_path / "result.json"
    result_path.write_text(
        '{"finished_at":"now","n_total_trials":1,"stats":'
        '{"n_completed_trials":1,"n_errored_trials":0,"n_cancelled_trials":0}}',
        encoding="utf-8",
    )
    assert pier_result_succeeded(result_path)


def test_direct_cli_rejects_credit_cap_below_upstream_minimum(monkeypatch, tmp_path):
    run_args = args(max_ai_credits=29, benchmark_dir=tmp_path, dry_run=True)
    monkeypatch.setattr("deepswe_runner.cli.ensure_benchmark", lambda *a, **k: tmp_path)
    monkeypatch.setattr("deepswe_runner.cli.task_names", lambda path: ["task-a"])
    with pytest.raises(RunnerError, match="at least 30"):
        _run_command(run_args)
