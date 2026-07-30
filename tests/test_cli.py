from argparse import Namespace
from decimal import Decimal
from pathlib import Path
import tempfile

import pytest

from deepswe_runner.cli import (
    RunnerError,
    _decode_credential_blob,
    _copilot_credential_host,
    build_pier_command,
    ai_credits_consumed,
    job_credential_path,
    normalize_model,
    normalize_opencode_model,
    pier_result_succeeded,
    redact_command,
    report_ai_credits,
    resolve_ordered_selection,
    selected_count,
    _run_command,
    validate_selection,
    write_job_credential,
)


def args(**overrides):
    values = {
        "agent": "copilot-cli",
        "model": ["gpt-5-mini"],
        "task": ["task-a"],
        "n_tasks": None,
        "n_ordered_tasks_start": None,
        "n_ordered_tasks_end": None,
        "sample_seed": 0,
        "all_tasks": False,
        "concurrency": 1,
        "docker_build_retries": 2,
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


def test_ordered_task_range_is_zero_based_and_inclusive():
    run_args = args(
        task=[],
        n_ordered_tasks_start=1,
        n_ordered_tasks_end=3,
    )
    available = ["a", "b", "c", "d", "e"]

    validate_selection(run_args, available)
    resolve_ordered_selection(run_args, available)

    assert run_args.task == ["b", "c", "d"]
    assert run_args.sample_seed is None
    assert selected_count(run_args, available) == 3


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        (0, None, "must be used together"),
        (None, 1, "must be used together"),
        (-1, 1, "cannot be negative"),
        (2, 1, "greater than or equal"),
        (0, 5, "last task index is 4"),
    ],
)
def test_invalid_ordered_task_bounds_are_rejected(start, end, message):
    with pytest.raises(RunnerError, match=message):
        validate_selection(
            args(
                task=[],
                n_ordered_tasks_start=start,
                n_ordered_tasks_end=end,
            ),
            ["a", "b", "c", "d", "e"],
        )


def test_ordered_task_range_cannot_be_combined_with_other_selectors():
    with pytest.raises(RunnerError, match="cannot be combined"):
        validate_selection(
            args(
                task=["a"],
                n_ordered_tasks_start=0,
                n_ordered_tasks_end=1,
            ),
            ["a", "b"],
        )


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
    assert (
        "--environment-import-path "
        "deepswe_runner.environments:RetryingDockerEnvironment"
    ) in joined
    assert "--environment-kwarg build_retries=2" in joined


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


def test_opencode_command_uses_native_agent_without_copilot_options(monkeypatch, tmp_path):
    monkeypatch.setattr("deepswe_runner.cli.shutil.which", lambda name: f"/bin/{name}")
    command = build_pier_command(
        args(
            agent="opencode",
            model=["qwen3-coder", "ollama/deepseek-r1"],
            reasoning_effort="high",
        ),
        benchmark_dir=tmp_path,
        credential_file=None,
    )
    joined = " ".join(command)
    assert "--agent opencode" in joined
    assert "--model openai/qwen3-coder" in joined
    assert "--model ollama/deepseek-r1" in joined
    assert "credential_file=" not in joined
    assert "max_ai_credits=" not in joined
    assert "cost_limit=" not in joined
    assert "reasoning_effort=" not in joined


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


def test_opencode_model_uses_provider_model_scheme():
    assert normalize_opencode_model("qwen3-coder") == "openai/qwen3-coder"
    assert normalize_opencode_model("ollama/qwen3-coder") == "ollama/qwen3-coder"


def test_command_output_redacts_credential_path():
    credential_file = Path("/tmp/deepswe-copilot-secret")
    rendered = redact_command(
        ["pier", "--agent-kwarg", f"credential_file={credential_file}"],
        credential_file,
    )
    assert str(credential_file) not in rendered
    assert "credential_file=<temporary-credential>" in rendered


def test_job_credential_path_is_stable_and_job_specific(tmp_path):
    first = job_credential_path(tmp_path / "jobs", "full-bench")
    resumed = job_credential_path(tmp_path / "jobs", "full-bench")
    other_job = job_credential_path(tmp_path / "jobs", "other-bench")

    assert first == resumed
    assert first != other_job
    assert first.parent == Path(tempfile.gettempdir())


def test_job_credential_is_rewritten_at_the_same_path(tmp_path):
    path = write_job_credential("first-token", tmp_path / "jobs", "full-bench")
    try:
        resumed_path = write_job_credential(
            "replacement-token",
            tmp_path / "jobs",
            "full-bench",
        )
        assert resumed_path == path
        assert path.read_text(encoding="utf-8") == "replacement-token"
    finally:
        path.unlink(missing_ok=True)


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


def test_ai_credits_are_aggregated_across_trials(tmp_path):
    for name, credits in (("trial-a", "13.4"), ("trial-b", "2.75")):
        agent_dir = tmp_path / name / "agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "copilot-cli.txt").write_text(
            f"Changes  +1 -1\nAI Credits {credits} (1m 2s)\n",
            encoding="utf-8",
        )
    total, reports, trials = ai_credits_consumed(tmp_path)
    assert total == Decimal("16.15")
    assert reports == 2
    assert trials == 2


def test_credit_report_marks_partial_totals(tmp_path, capsys):
    (tmp_path / "trial-a" / "agent").mkdir(parents=True)
    (tmp_path / "trial-a" / "agent" / "copilot-cli.txt").write_text(
        "AI Credits 4.5 (30s)\n",
        encoding="utf-8",
    )
    (tmp_path / "trial-b").mkdir()
    report_ai_credits(tmp_path)
    assert capsys.readouterr().out.strip() == (
        "AI credits consumed: 4.5 "
        "(reported by 1 of 2 trials; total may be incomplete)"
    )


def test_credit_report_is_explicit_when_unavailable(tmp_path, capsys):
    (tmp_path / "mini-trial").mkdir()
    report_ai_credits(tmp_path)
    assert capsys.readouterr().out.strip() == (
        "AI credits consumed: unavailable (the agent did not report credit usage)"
    )
