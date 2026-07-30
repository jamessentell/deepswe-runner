# DeepSWE Copilot runner

Run [DeepSWE Bench](https://deepswe.datacurve.ai/run) against models included
with a GitHub Copilot account. The runner uses
[Pier](https://github.com/datacurve-ai/pier) for the benchmark sandbox and
verifier, and offers three agent harnesses:

- `copilot-cli`: the official GitHub Copilot CLI runs as the coding agent.
- `mini-swe-agent`: mini-swe-agent runs the agent loop and calls the selected
  Copilot model through LiteLLM's `github_copilot` provider.
- `opencode`: Pier's native OpenCode harness runs any OpenCode
  `provider/model`, including local OpenAI-compatible inference servers.

The DeepSWE checkout is cloned automatically into `.cache/deep-swe`; benchmark
jobs are written to `jobs/`. Neither is committed to this repository.

## Requirements

- Windows 10/11 or Linux, Python 3.12+, `uv`, Git, and a running Docker daemon.
- On Windows, Docker Desktop configured with its WSL 2 Linux-container engine.
- GitHub CLI (`gh`) authenticated to an account with Copilot access, or a
  supported token in `COPILOT_GITHUB_TOKEN`. On Windows, an authenticated
  official Copilot CLI installation is also detected automatically.
- Enough disk for the benchmark images. DeepSWE tasks request up to 20 GB of
  container storage.

The runner reads a credential from `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or
`GITHUB_TOKEN` (in that order), then the official Copilot CLI's Windows
Credential Manager entry on Windows, and finally `gh auth token`. It writes the
credential to a user-protected temporary file, uploads it into each isolated
task container, and deletes both copies after the run. The token value is not
placed in Pier's configuration or command line.

Windows credential discovery accepts official Copilot CLI logins for any HTTPS
host, including GitHub Enterprise Cloud data-residency hosts such as
`servername.ghe.com`. The selected host is passed into the isolated agent as
`COPILOT_GH_HOST`. If several Copilot CLI accounts are saved, set
`COPILOT_GH_HOST` to select the intended host; otherwise `github.com` is
preferred, followed by the first available Copilot credential.

For mini-swe-agent, the runner queries GitHub's authenticated
`/copilot_internal/user` metadata endpoint inside the task container and
supplies LiteLLM with the returned account-specific Copilot inference endpoint.
This supports the OAuth token created by current official Copilot CLI releases;
the credential and generated LiteLLM cache are deleted after the trial.

Use `./run-deepswe` on Linux. On Windows, the policy-free launcher works from
PowerShell or Command Prompt:

```powershell
.\run-deepswe.cmd list-tasks
```

`run-deepswe.ps1` is also provided for PowerShell environments that permit
local scripts.

The benchmark checkout is created with `core.autocrlf=false` on every platform.
This is required on Windows because its scripts and patch fixtures are consumed
inside Linux containers. If an older clean checkout contains tracked CRLF
files, the runner repairs those text files automatically; it refuses to
overwrite a checkout with real local changes.

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
  --model gpt-4o-mini \
  --task abs-stepped-slices \
  --max-ai-credits 30
```

For mini-swe-agent, the credit limit is converted to its dollar cost limit
(`30` credits = `$0.30`). That limit is best-effort because it depends on
LiteLLM receiving and pricing Copilot's usage metadata. Current Copilot
responses may not include a price, in which case LiteLLM records token usage
but cannot enforce the dollar limit. Use one task and concurrency `1` for an
initial smoke test.

Runs are uncapped by default. `--max-ai-credits` is passed to the selected
harness only when you specify it. Copilot CLI requires any explicit cap to be
at least `30`.

Run OpenCode with an explicit provider/model:

```bash
./run-deepswe run \
  --agent opencode \
  --model anthropic/claude-sonnet-4-6 \
  --task abs-stepped-slices
```

For an OpenAI-compatible local server, an unqualified model defaults to the
`openai` provider. From Windows, use Docker's `host.docker.internal` address
because OpenCode runs inside the Linux task container:

```powershell
$env:OPENAI_BASE_URL = "http://host.docker.internal:11434/v1"
$env:OPENAI_API_KEY = "local"
.\run-deepswe.cmd run --agent opencode --model qwen3-coder `
  --task abs-stepped-slices
```

You can also specify the provider explicitly, for example
`--model ollama/qwen3-coder`. OpenCode reads the standard environment variables
for the selected provider. It does not read or upload Copilot credentials.
`--max-ai-credits` and `--reasoning-effort` are Copilot-harness options and are
not passed to OpenCode.

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

For deterministic manual pagination across machines, select an inclusive,
zero-based range from the alphabetical output of `list-tasks`:

```cmd
run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex ^
  --reasoning-effort xhigh --n-ordered-tasks-start 0 ^
  --n-ordered-tasks-end 5 --concurrency 1 --job-name shard-0-through-5
```

The next machine can use start `6` and end `10`. The bounds are inclusive, so
`0` through `5` selects six tasks. The runner expands the range into explicit
alphabetically ordered task IDs before calling Pier. Ordered bounds cannot be
combined with `--task`, `--n-tasks`, or `--all`. Keep every machine on the same
runner and DeepSWE benchmark commits so the indexed task list is identical.

The runner refuses to launch the entire benchmark unless you explicitly pass
`--all`. This makes an accidental invocation fail before authentication or
model use:

```bash
./run-deepswe run --agent copilot-cli --model gpt-5-mini --all
```

The direct Copilot CLI harness accepts Copilot CLI model names such as
`gpt-5-mini`, `gpt-5.3-codex`, or `claude-sonnet-4.6`. mini-swe-agent uses
Copilot's OpenAI-compatible endpoint through LiteLLM, whose model catalog can
be smaller; `gpt-4o-mini` is a conservative smoke-test choice. An unsupported
model fails before meaningful agent work. The optional `github_copilot/`
prefix is accepted but not required.

## Windows quick start

After installing Python/`uv`, Git, Docker Desktop, and Copilot CLI, open a new
PowerShell or Command Prompt so newly installed commands are on `PATH`.
Authenticate once with `copilot login`, then:

```powershell
docker version
copilot --version
.\run-deepswe.cmd list-tasks
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5-mini `
  --task abs-stepped-slices --max-ai-credits 30 --dry-run
.\run-deepswe.cmd run --agent mini-swe-agent --model gpt-4o-mini `
  --task abs-stepped-slices --max-ai-credits 30 --dry-run
.\run-deepswe.cmd run --agent opencode --model openai/qwen3-coder `
  --task abs-stepped-slices --dry-run
```

Remove `--dry-run` from one command at a time to execute the smoke trial.
Docker Desktop must be running in Linux-container mode.

## Useful options

```text
--agent {copilot-cli,mini-swe-agent,opencode}
--model MODEL                 repeatable
--task TASK_ID                repeatable
--n-tasks N
--n-ordered-tasks-start INDEX  inclusive alphabetical index
--n-ordered-tasks-end INDEX    inclusive alphabetical index
--sample-seed N
--all                         explicit full-corpus opt-in
--max-ai-credits N            optional per trial; unlimited when omitted
--reasoning-effort LEVEL
--concurrency N               default 1
--docker-build-retries N      failed pre-agent builds; default 2
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

Docker image builds are retried twice by default. These retries occur entirely
before the agent starts, so transient registry, Git, or package-index failures
cannot cause duplicate model calls or additional AI-credit use. Set
`--docker-build-retries 0` to disable them or choose a larger value on an
unreliable network.

## Resuming a full benchmark

Give a full run an explicit job name:

```powershell
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex `
  --reasoning-effort xhigh --all --concurrency 1 `
  --job-name full-gpt-5.3-codex-xhigh
```

If the process or computer stops before the benchmark finishes, rerun that
exact command. Pier retains completed trials in the named job, removes an
incomplete scratch trial, and runs only the remaining task/model pairs. The
job's `result.json` combines completed results and aggregate metrics.

The runner uses a stable per-job path for its short-lived Copilot credential so
the credential filename does not invalidate Pier's configuration comparison
during a resume. The credential contents are rewritten with user-only
permissions for each invocation and the file is deleted when that invocation
ends.

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

After every non-dry run, the runner prints the total `AI Credits` reported by
Copilot CLI across the job's trials. If some trials or the selected harness do
not expose credit usage (notably mini-swe-agent through LiteLLM), the terminal
labels the value as unavailable or incomplete rather than treating it as zero.

## Development checks

```bash
uv sync --all-groups
uv run ruff check .
uv run pytest
```
