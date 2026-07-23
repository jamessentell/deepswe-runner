# DeepSWE Copilot runner

Run [DeepSWE Bench](https://deepswe.datacurve.ai/run) against models included
with a GitHub Copilot account. The runner uses
[Pier](https://github.com/datacurve-ai/pier) for the benchmark sandbox and
verifier, and offers two agent harnesses:

- `copilot-cli`: the official GitHub Copilot CLI runs as the coding agent.
- `mini-swe-agent`: mini-swe-agent runs the agent loop and calls the selected
  Copilot model through LiteLLM's `github_copilot` provider.

The DeepSWE checkout is cloned automatically into `.cache/deep-swe`; benchmark
jobs are written to `jobs/`. Neither is committed to this repository.

## Requirements

- Linux, Python 3.12+, `uv`, Git, and a running Docker daemon.
- GitHub CLI (`gh`) authenticated to an account with Copilot access, or a
  supported token in `COPILOT_GITHUB_TOKEN`.
- Enough disk for the benchmark images. DeepSWE tasks request up to 20 GB of
  container storage.

The runner reads a credential from `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`,
`GITHUB_TOKEN`, or `gh auth token` (in that order). It writes the credential to
a mode-`0600` temporary file, uploads it into each isolated task container, and
deletes both copies after the run. The token value is not placed in Pier's
configuration or command line.

## Quick start

List task IDs (this also performs the initial benchmark clone):

```bash
./run-deepswe list-tasks
```

Preview a one-task Copilot CLI run without authenticating or spending credits:

```bash
./run-deepswe run \
  --agent copilot-cli \
  --model gpt-5-mini \
  --task abs-stepped-slices \
  --max-ai-credits 30 \
  --dry-run
```

Remove `--dry-run` to execute it. The direct CLI's credit limit is a soft
per-trial limit enforced by Copilot CLI. GitHub notes that in-flight responses
can make actual use slightly exceed the limit.

Run the same model through mini-swe-agent:

```bash
./run-deepswe run \
  --agent mini-swe-agent \
  --model gpt-5-mini \
  --task abs-stepped-slices \
  --max-ai-credits 30
```

For mini-swe-agent, the credit limit is converted to its dollar cost limit
(`30` credits = `$0.30`). That limit is best-effort because it depends on
LiteLLM receiving and pricing Copilot's usage metadata.

## Models and subsets

Pass `--model` more than once to compare models:

```bash
./run-deepswe run \
  --agent copilot-cli \
  --model gpt-5-mini \
  --model claude-haiku-4.5 \
  --task abs-stepped-slices
```

Pass `--task` more than once for an explicit subset:

```bash
./run-deepswe run \
  --agent mini-swe-agent \
  --model gpt-5-mini \
  --task abs-stepped-slices \
  --task httpx-streaming-json-iteration
```

Or select a deterministic random subset, matching DeepSWE's documented Pier
workflow:

```bash
./run-deepswe run \
  --agent mini-swe-agent \
  --model gpt-5-mini \
  --n-tasks 10 \
  --sample-seed 0
```

Every model/task pair is one trial. For example, two models and three selected
tasks create six trials.

The runner refuses to launch the entire benchmark unless you explicitly pass
`--all`. This makes an accidental invocation fail before authentication or
model use:

```bash
./run-deepswe run --agent copilot-cli --model gpt-5-mini --all
```

Use a model string accepted by the Copilot client, such as `gpt-5-mini`,
`gpt-5.3-codex`, or `claude-sonnet-4.6`. The optional
`github_copilot/` prefix is accepted but not required.

## Useful options

```text
--agent {copilot-cli,mini-swe-agent}
--model MODEL                 repeatable
--task TASK_ID                repeatable
--n-tasks N
--sample-seed N
--all                         explicit full-corpus opt-in
--max-ai-credits N            per trial; default 50
--reasoning-effort LEVEL
--concurrency N               default 1
--job-name NAME
--jobs-dir PATH
--benchmark-dir PATH
--update-benchmark
--keep-containers
--dry-run
--pier-arg ARG                repeatable advanced Pier argument
```

Run `./run-deepswe run --help` for the complete CLI help. Concurrency defaults
to one to keep both resource and credit usage predictable.

## Results

Pier writes each job beneath `jobs/<job-name>/`. Its `result.json`,
per-trial verifier output, captured patch, and agent logs are the authoritative
results. Direct Copilot CLI trials also retain:

```text
agent/
  copilot-cli.txt
  copilot-transcript.md
```

mini-swe-agent trials retain its native trajectory and Pier's converted ATIF
trajectory. Inspect a completed job with Pier's viewer:

```bash
uv run pier view jobs/<job-name>
```

## Development checks

```bash
uv sync --all-groups
uv run ruff check .
uv run pytest
```
