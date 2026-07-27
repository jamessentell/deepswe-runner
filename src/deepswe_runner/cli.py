"""Command-line entry point for running DeepSWE with Copilot-backed agents."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from ctypes import wintypes
from datetime import datetime
from pathlib import Path
from typing import Sequence

BENCHMARK_URL = "https://github.com/datacurve-ai/deep-swe"
DEFAULT_BENCHMARK_DIR = Path(".cache/deep-swe")
DEFAULT_JOBS_DIR = Path("jobs")
DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_COPILOT_VERSION = "1.0.75"
MIN_COPILOT_CLI_CREDITS = 30

AGENT_IMPORTS = {
    "copilot-cli": "deepswe_runner.agents:CopilotCliAgent",
    "mini-swe-agent": "deepswe_runner.agents:CopilotMiniSweAgent",
}


class RunnerError(RuntimeError):
    """Expected user-facing runner failure."""


def _run_checked(command: Sequence[str], **kwargs) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, text=True, **kwargs)
    except FileNotFoundError as exc:
        raise RunnerError(f"Required command is not installed: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise RunnerError(f"Command failed with exit code {exc.returncode}: {command[0]}") from exc


def ensure_benchmark(path: Path, *, update: bool = False) -> Path:
    path = path.expanduser().resolve()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Cloning DeepSWE Bench into {path}")
        _run_checked(
            [
                "git",
                "-c",
                "core.autocrlf=false",
                "clone",
                "--depth",
                "1",
                BENCHMARK_URL,
                str(path),
            ]
        )
    if not (path / ".git").is_dir() or not (path / "tasks" / "dataset.toml").is_file():
        raise RunnerError(f"Not a DeepSWE checkout: {path}")
    if update:
        print(f"Updating DeepSWE Bench in {path}")
        _run_checked(["git", "-C", str(path), "pull", "--ff-only"])
    if os.name == "nt":
        _ensure_benchmark_lf_checkout(path)
    return path


def _ensure_benchmark_lf_checkout(path: Path) -> None:
    """Keep Linux container scripts byte-for-byte LF on Windows hosts."""
    eol_output = _run_checked(
        ["git", "-C", str(path), "ls-files", "--eol"],
        capture_output=True,
    ).stdout
    crlf_paths = [
        path / line.split("\t", 1)[1]
        for line in eol_output.splitlines()
        if "w/crlf" in line and "\t" in line
    ]
    if not crlf_paths:
        return
    unstaged = subprocess.run(["git", "-C", str(path), "diff", "--quiet"]).returncode
    staged = subprocess.run(
        ["git", "-C", str(path), "diff", "--cached", "--quiet"]
    ).returncode
    untracked = _run_checked(
        ["git", "-C", str(path), "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
    ).stdout.strip()
    if unstaged or staged or untracked:
        raise RunnerError(
            f"DeepSWE checkout contains CRLF scripts and local changes: {path}. "
            "Commit/stash the changes or use a fresh --benchmark-dir."
        )
    print("Repairing DeepSWE checkout line endings for Linux containers")
    _run_checked(["git", "-C", str(path), "config", "core.autocrlf", "false"])
    for tracked_file in crlf_paths:
        contents = tracked_file.read_bytes()
        if b"\r\n" in contents:
            tracked_file.write_bytes(contents.replace(b"\r\n", b"\n"))


def task_names(benchmark_dir: Path) -> list[str]:
    tasks_dir = benchmark_dir / "tasks"
    return sorted(
        child.name
        for child in tasks_dir.iterdir()
        if child.is_dir() and (child / "task.toml").is_file()
    )


def normalize_model(model: str) -> str:
    value = model.strip()
    if not value:
        raise RunnerError("Model names cannot be empty")
    return value if value.startswith("github_copilot/") else f"github_copilot/{value}"


def validate_selection(args: argparse.Namespace, available: Sequence[str]) -> None:
    if args.all_tasks and (args.task or args.n_tasks is not None):
        raise RunnerError("--all cannot be combined with --task or --n-tasks")
    if not args.all_tasks and not args.task and args.n_tasks is None:
        raise RunnerError(
            "Refusing to run all 113 tasks implicitly. Choose --task NAME, "
            "--n-tasks N, or explicitly pass --all."
        )
    if args.n_tasks is not None and args.n_tasks < 1:
        raise RunnerError("--n-tasks must be at least 1")
    missing = sorted(set(args.task) - set(available))
    if missing:
        raise RunnerError(f"Unknown task(s): {', '.join(missing)}")


def selected_count(args: argparse.Namespace, available: Sequence[str]) -> int:
    if args.all_tasks:
        return len(available)
    candidates = list(args.task) if args.task else list(available)
    if args.n_tasks is not None:
        return min(len(candidates), args.n_tasks)
    return len(candidates)


def read_github_token() -> str:
    for variable in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        if value := os.environ.get(variable):
            return value.strip()
    if os.name == "nt":
        if value := _read_windows_copilot_token():
            return value
    if not shutil.which("gh"):
        raise RunnerError(
            "No GitHub credential found. Log in with `copilot login` or "
            "`gh auth login`, or set COPILOT_GITHUB_TOKEN to a supported "
            "fine-grained/OAuth token."
        )
    result = _run_checked(["gh", "auth", "token"], capture_output=True)
    token = result.stdout.strip()
    if not token:
        raise RunnerError("`gh auth token` returned an empty credential")
    return token


def _decode_credential_blob(blob: bytes) -> str:
    """Decode a generic Windows credential without logging its contents."""
    if len(blob) > 1 and blob[1::2].count(0) >= len(blob[1::2]) * 3 // 4:
        return blob.decode("utf-16-le").rstrip("\0").strip()
    return blob.decode("utf-8").rstrip("\0").strip()


def _read_windows_copilot_token() -> str | None:
    """Read the official Copilot CLI OAuth token from Windows Credential Manager."""
    if os.name != "nt":
        return None

    class CREDENTIAL(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    credential_pointer = ctypes.POINTER(CREDENTIAL)
    count = wintypes.DWORD()
    credentials = ctypes.POINTER(credential_pointer)()
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi32.CredEnumerateW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(ctypes.POINTER(credential_pointer)),
    ]
    advapi32.CredEnumerateW.restype = wintypes.BOOL
    advapi32.CredFree.argtypes = [ctypes.c_void_p]

    if not advapi32.CredEnumerateW(None, 0, ctypes.byref(count), ctypes.byref(credentials)):
        error = ctypes.get_last_error()
        if error == 1168:  # ERROR_NOT_FOUND
            return None
        raise RunnerError(f"Unable to read Windows Credential Manager (error {error})")

    try:
        for index in range(count.value):
            credential = credentials[index].contents
            target = credential.TargetName or ""
            if not (
                target.lower().startswith("https://github.com:")
                and target.lower().endswith(".copilot-cli")
            ):
                continue
            blob = ctypes.string_at(
                credential.CredentialBlob, credential.CredentialBlobSize
            )
            try:
                token = _decode_credential_blob(blob)
            except UnicodeDecodeError as exc:
                raise RunnerError(
                    "The Copilot CLI credential in Windows Credential Manager "
                    "has an unsupported format"
                ) from exc
            if token:
                return token
    finally:
        advapi32.CredFree(credentials)
    return None


def write_temporary_credential(token: str) -> Path:
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        prefix="deepswe-copilot-",
        delete=False,
        encoding="utf-8",
    )
    try:
        handle.write(token)
        handle.flush()
    finally:
        handle.close()
    path = Path(handle.name)
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return path


def build_pier_command(
    args: argparse.Namespace,
    *,
    benchmark_dir: Path,
    credential_file: Path,
) -> list[str]:
    pier = shutil.which("pier")
    if not pier:
        raise RunnerError("Pier is unavailable. Run this script through `uv run`.")

    models = [normalize_model(model) for model in args.model]
    command = [
        pier,
        "run",
        "--path",
        str(benchmark_dir / "tasks"),
        "--agent-import-path",
        AGENT_IMPORTS[args.agent],
        "--agent-kwarg",
        f"credential_file={credential_file}",
        "--n-concurrent",
        str(args.concurrency),
        "--jobs-dir",
        str(args.jobs_dir.expanduser().resolve()),
        "--job-name",
        args.job_name,
        "--yes",
    ]
    for model in models:
        command.extend(["--model", model])
    for task in args.task:
        command.extend(["--include-task-name", task])
    if args.n_tasks is not None:
        command.extend(["--n-tasks", str(args.n_tasks)])
    if args.sample_seed is not None:
        command.extend(["--sample-seed", str(args.sample_seed)])

    if args.agent == "copilot-cli":
        command.extend(["--agent-kwarg", f"version={args.copilot_version}"])
        command.extend(["--agent-kwarg", f"max_ai_credits={args.max_ai_credits}"])
        if args.reasoning_effort:
            command.extend(
                ["--agent-kwarg", f"reasoning_effort={args.reasoning_effort}"]
            )
    else:
        # mini-swe-agent tracks dollars; one AI credit is $0.01. This is a
        # best-effort counterpart to Copilot CLI's server-enforced session limit.
        command.extend(
            ["--agent-kwarg", f"cost_limit={args.max_ai_credits / 100:g}"]
        )
        if args.reasoning_effort:
            command.extend(
                ["--agent-kwarg", f"reasoning_effort={args.reasoning_effort}"]
            )
    if args.keep_containers:
        command.append("--no-delete")
    if args.debug:
        command.append("--debug")
    command.extend(args.pier_arg)
    return command


def redact_command(command: Sequence[str], credential_file: Path) -> str:
    credential_path = str(credential_file)
    return shlex.join(
        part.replace(credential_path, "<temporary-credential>")
        for part in command
    )


def pier_result_succeeded(result_path: Path) -> bool:
    if not result_path.is_file():
        return False
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        stats = result["stats"]
        return (
            result.get("finished_at") is not None
            and stats.get("n_completed_trials") == result.get("n_total_trials")
            and stats.get("n_errored_trials") == 0
            and stats.get("n_cancelled_trials") == 0
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return False


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deepswe",
        description="Run DeepSWE Bench with GitHub Copilot models through Pier.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-tasks", help="List DeepSWE task IDs")
    list_parser.add_argument("--benchmark-dir", type=Path, default=DEFAULT_BENCHMARK_DIR)
    list_parser.add_argument("--update-benchmark", action="store_true")

    run_parser = subparsers.add_parser("run", help="Run a benchmark subset")
    run_parser.add_argument(
        "--agent",
        choices=sorted(AGENT_IMPORTS),
        default="copilot-cli",
        help="Agent harness to use (default: copilot-cli)",
    )
    run_parser.add_argument(
        "--model",
        action="append",
        default=[],
        metavar="MODEL",
        help=f"Copilot model; repeat to compare models (default: {DEFAULT_MODEL})",
    )
    selection = run_parser.add_argument_group("task selection")
    selection.add_argument("--task", action="append", default=[], metavar="TASK_ID")
    selection.add_argument("--n-tasks", type=int, metavar="N")
    selection.add_argument("--sample-seed", type=int, default=0)
    selection.add_argument(
        "--all",
        dest="all_tasks",
        action="store_true",
        help="Explicitly opt into the full benchmark",
    )

    run_parser.add_argument("--benchmark-dir", type=Path, default=DEFAULT_BENCHMARK_DIR)
    run_parser.add_argument("--update-benchmark", action="store_true")
    run_parser.add_argument("--jobs-dir", type=Path, default=DEFAULT_JOBS_DIR)
    run_parser.add_argument(
        "--job-name",
        default=None,
        help="Pier job name (default includes agent and timestamp)",
    )
    run_parser.add_argument(
        "--max-ai-credits",
        type=int,
        default=50,
        metavar="N",
        help="Per-trial Copilot credit cap; mini-swe equivalent is best-effort (default: 50)",
    )
    run_parser.add_argument(
        "--reasoning-effort",
        choices=["none", "minimal", "low", "medium", "high", "xhigh", "max"],
    )
    run_parser.add_argument(
        "--copilot-version",
        default=DEFAULT_COPILOT_VERSION,
        help=f"Copilot CLI npm version for direct mode (default: {DEFAULT_COPILOT_VERSION})",
    )
    run_parser.add_argument("--concurrency", type=int, default=1)
    run_parser.add_argument("--keep-containers", action="store_true")
    run_parser.add_argument("--debug", action="store_true")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the resolved Pier command without authentication or execution",
    )
    run_parser.add_argument(
        "--pier-arg",
        action="append",
        default=[],
        metavar="ARG",
        help="Append an advanced argument to `pier run`; repeat for multiple arguments",
    )
    return parser


def _run_command(args: argparse.Namespace) -> int:
    benchmark_dir = ensure_benchmark(args.benchmark_dir, update=args.update_benchmark)
    available = task_names(benchmark_dir)
    validate_selection(args, available)
    if not args.model:
        args.model = [DEFAULT_MODEL]
    if args.max_ai_credits < 1:
        raise RunnerError("--max-ai-credits must be at least 1")
    if args.agent == "copilot-cli" and args.max_ai_credits < MIN_COPILOT_CLI_CREDITS:
        raise RunnerError(
            f"Copilot CLI requires --max-ai-credits to be at least "
            f"{MIN_COPILOT_CLI_CREDITS}"
        )
    if args.concurrency < 1:
        raise RunnerError("--concurrency must be at least 1")
    if args.job_name is None:
        stamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
        args.job_name = f"{args.agent}__{stamp}"

    trials = selected_count(args, available) * len(args.model)
    print(
        f"Plan: {trials} trial(s) = {selected_count(args, available)} task(s) "
        f"× {len(args.model)} model(s), agent={args.agent}, concurrency={args.concurrency}"
    )
    if args.dry_run:
        placeholder = Path(tempfile.gettempdir()) / "deepswe-copilot-credential"
        command = build_pier_command(
            args, benchmark_dir=benchmark_dir, credential_file=placeholder
        )
        print(redact_command(command, placeholder))
        return 0

    token = read_github_token()
    credential_file = write_temporary_credential(token)
    del token
    try:
        command = build_pier_command(
            args,
            benchmark_dir=benchmark_dir,
            credential_file=credential_file,
        )
        print(f"Running: {redact_command(command, credential_file)}")
        return_code = subprocess.run(command, text=True).returncode
        if return_code:
            return return_code
        result_path = args.jobs_dir.expanduser().resolve() / args.job_name / "result.json"
        if not pier_result_succeeded(result_path):
            print(
                f"Pier finished but one or more trials failed; inspect {result_path}",
                file=sys.stderr,
            )
            return 1
        return 0
    finally:
        credential_file.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "list-tasks":
            benchmark_dir = ensure_benchmark(
                args.benchmark_dir, update=args.update_benchmark
            )
            names = task_names(benchmark_dir)
            print("\n".join(names))
            print(f"\n{len(names)} tasks", file=sys.stderr)
            return 0
        return _run_command(args)
    except RunnerError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
