# Run the full DeepSWE bench sequentially with combined results

The recommended command runs all 113 tasks sequentially inside one named Pier
job. Completed tasks are saved as they finish, and `result.json` combines the
results and aggregate metrics.

```cmd
cd /d C:\Users\james\deepswe-runner
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --all --concurrency 1 --job-name full-gpt-5.3-codex-xhigh
```

If the process or computer stops, run the exact same command again. The runner
and Pier will keep completed trials and run only the remaining tasks.

No AI-credit cap is specified. To impose a per-task limit, add
`--max-ai-credits 30` (the Copilot CLI minimum) to both the original and resumed
commands. Resume commands must otherwise remain identical.

## Standalone commands for individual tasks
Run these commands from Command Prompt. Each command is a standalone `cmd`
command.
Each command launches exactly one task using the Copilot CLI harness,
`gpt-5.3-codex`, `xhigh` reasoning effort, and concurrency one. No AI-credit
cap is specified, so every trial is uncapped. Run the next command only after
the previous command finishes.

```cmd
cd /d C:\Users\james\deepswe-runner

.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task abs-module-cache-flags --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__abs-module-cache-flags
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task abs-stepped-slices --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__abs-stepped-slices
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task actionlint-action-pinning-lint --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__actionlint-action-pinning-lint
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task adaptix-name-mapping-aliases --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__adaptix-name-mapping-aliases
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task aiomonitor-task-snapshots-diff --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__aiomonitor-task-snapshots-diff
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task anko-default-function-arguments --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__anko-default-function-arguments
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task anko-typed-variable-bindings --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__anko-typed-variable-bindings
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task arcane-drift-detection-baselines --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__arcane-drift-detection-baselines
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task arktype-json-schema-refs-dependencies --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__arktype-json-schema-refs-dependencies
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task awilix-async-container-initialization --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__awilix-async-container-initialization
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task bandit-incremental-cache-control --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__bandit-incremental-cache-control
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task bandit-interprocedural-taint-checks --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__bandit-interprocedural-taint-checks
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task bandit-structured-nosec-directives --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__bandit-structured-nosec-directives
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task boa-hierarchical-evaluation-cancellation --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__boa-hierarchical-evaluation-cancellation
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task cattrs-partial-structuring-recovery --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__cattrs-partial-structuring-recovery
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task clack-async-autocomplete-options --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__clack-async-autocomplete-options
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task claude-code-by-agents-recursive-delegation --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__claude-code-by-agents-recursive-delegation
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task cliffy-config-file-parsing --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__cliffy-config-file-parsing
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task csstree-shorthand-expansion-compression --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__csstree-shorthand-expansion-compression
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task dasel-html-document-format --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__dasel-html-document-format
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task dateutil-rfc5545-timezone-interop --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__dateutil-rfc5545-timezone-interop
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task drizzle-orm-window-function-builders --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__drizzle-orm-window-function-builders
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task dynamodb-toolbox-conditional-attribute-requirements --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__dynamodb-toolbox-conditional-attribute-requirements
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task dynamodb-toolbox-lazy-recursive-schemas --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__dynamodb-toolbox-lazy-recursive-schemas
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task effect-sse-httpapi-streaming --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__effect-sse-httpapi-streaming
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task eicrud-keyset-pagination-cursor --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__eicrud-keyset-pagination-cursor
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task etree-xml-diff-patch --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__etree-xml-diff-patch
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task expr-try-catch-errors --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__expr-try-catch-errors
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task fastapi-deprecation-response-headers --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__fastapi-deprecation-response-headers
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task fastapi-implicit-head-options --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__fastapi-implicit-head-options
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task fd-deterministic-multi-key-sorting --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__fd-deterministic-multi-key-sorting
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task geo-shapeindex-serialization --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__geo-shapeindex-serialization
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task go-critic-doc-link-checker --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__go-critic-doc-link-checker
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task go-genai-streamed-function-args --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__go-genai-streamed-function-args
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task go-git-worktree-merge-conflicts --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__go-git-worktree-merge-conflicts
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task goreleaser-retry-publish-auditing --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__goreleaser-retry-publish-auditing
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task gql-incremental-graphql-delivery --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__gql-incremental-graphql-delivery
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task happy-dom-abort-pending-body-reads --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__happy-dom-abort-pending-body-reads
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task happy-dom-deterministic-intersectionobserver --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__happy-dom-deterministic-intersectionobserver
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task helm-array-merge-strategies --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__helm-array-merge-strategies
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task helm-unified-manifest-stream --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__helm-unified-manifest-stream
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task httpx-deterministic-cookie-store --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__httpx-deterministic-cookie-store
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task httpx-multipart-response-parsing --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__httpx-multipart-response-parsing
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task httpx-streaming-json-iteration --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__httpx-streaming-json-iteration
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task igel-persist-feature-schema --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__igel-persist-feature-schema
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task ink-grid-box-layout --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__ink-grid-box-layout
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task ipython-session-bundle-replay --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__ipython-session-bundle-replay
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task katex-multicolumn-array-spans --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__katex-multicolumn-array-spans
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task kcp-go-multiplexed-kcp-streams --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__kcp-go-multiplexed-kcp-streams
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task kea-atomic-signal-selectors --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__kea-atomic-signal-selectors
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task kgateway-consistent-hash-policy --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__kgateway-consistent-hash-policy
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task kombu-single-active-consumer-priority --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__kombu-single-active-consumer-priority
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task kombu-virtual-queue-dead-lettering --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__kombu-virtual-queue-dead-lettering
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task koota-composite-trait-aspects --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__koota-composite-trait-aspects
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task koota-deferred-mutation-buffer --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__koota-deferred-mutation-buffer
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task koota-entity-snapshot-rollback --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__koota-entity-snapshot-rollback
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task koota-pair-relation-tracking --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__koota-pair-relation-tracking
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task koota-query-predicates --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__koota-query-predicates
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task kysely-window-grouping-helpers --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__kysely-window-grouping-helpers
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task langchain-request-coalescing --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__langchain-request-coalescing
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task mashumaro-flattened-dataclass-fields --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__mashumaro-flattened-dataclass-fields
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task meriyah-explicit-resource-declarations --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__meriyah-explicit-resource-declarations
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task mnamer-daemon-watch-lifecycle --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__mnamer-daemon-watch-lifecycle
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task mobly-grouped-test-barriers --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__mobly-grouped-test-barriers
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task narwhals-rolling-window-suite --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__narwhals-rolling-window-suite
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task numba-stencil-boundary-modes --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__numba-stencil-boundary-modes
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task obsidian-linter-auto-table-of-contents --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__obsidian-linter-auto-table-of-contents
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task obsidian-linter-link-format-conversion --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__obsidian-linter-link-format-conversion
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task obsidian-linter-scoped-ignore-markers --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__obsidian-linter-scoped-ignore-markers
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task ofetch-per-origin-circuit-breaker --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__ofetch-per-origin-circuit-breaker
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task onedump-dump-encryption-pipeline --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__onedump-dump-encryption-pipeline
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task opa-rego-rule-profiling --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__opa-rego-rule-profiling
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task opa-template-string-reconstruction --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__opa-template-string-reconstruction
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task optique-conditional-option-dependencies --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__optique-conditional-option-dependencies
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task oxvg-structural-selector-preservation --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__oxvg-structural-selector-preservation
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task participle-grammar-conflict-analysis --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__participle-grammar-conflict-analysis
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task pebble-durability-wait-apis --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__pebble-durability-wait-apis
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task pest-character-class-coalescing --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__pest-character-class-coalescing
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task prometheus-transactional-reload-status --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__prometheus-transactional-reload-status
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task prometheus-typed-label-sorting --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__prometheus-typed-label-sorting
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task psd-tools-blend-range-api --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__psd-tools-blend-range-api
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task pwntools-tube-multiplexing --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__pwntools-tube-multiplexing
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task python-statemachine-state-data-scoping --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__python-statemachine-state-data-scoping
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task query-persist-restored-query-state --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__query-persist-restored-query-state
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task quill-shared-toolbar-focus --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__quill-shared-toolbar-focus
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task returns-validated-error-accumulation --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__returns-validated-error-accumulation
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task scc-bounded-memory-spilling --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__scc-bounded-memory-spilling
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task scriggo-method-declarations --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__scriggo-method-declarations
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task skrub-duration-encoding --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__skrub-duration-encoding
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task sql-formatter-bigquery-pipe-formatting --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__sql-formatter-bigquery-pipe-formatting
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task sqlfmt-create-table-ddl-formatting --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__sqlfmt-create-table-ddl-formatting
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task sqlite-utils-safe-import-checkpoints --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__sqlite-utils-safe-import-checkpoints
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task superjson-error-stack-serialization --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__superjson-error-stack-serialization
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task task-task-graph-export --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__task-task-graph-export
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task tengo-callable-instance-isolation --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__tengo-callable-instance-isolation
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task tengo-destructuring-bindings --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__tengo-destructuring-bindings
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task termenv-preserve-ansi-resets --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__termenv-preserve-ansi-resets
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task testem-bail-on-test-failure --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__testem-bail-on-test-failure
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task testem-per-launcher-reports --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__testem-per-launcher-reports
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task textual-kitty-key-phases --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__textual-kitty-key-phases
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task textual-richlog-follow-state --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__textual-richlog-follow-state
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task tomlkit-toml-table-converters --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__tomlkit-toml-table-converters
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task true-myth-iterable-collection-combinators --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__true-myth-iterable-collection-combinators
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task ts-pattern-match-each --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__ts-pattern-match-each
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task updo-policy-alerting --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__updo-policy-alerting
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task valibot-recursive-schema-composition --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__valibot-recursive-schema-composition
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task vitest-duration-sharding --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__vitest-duration-sharding
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task vulture-persistent-analysis-cache --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__vulture-persistent-analysis-cache
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task wasmi-trap-coredumps --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__wasmi-trap-coredumps
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task wazero-multi-module-snapshots --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__wazero-multi-module-snapshots
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task yaegi-go-embed-directives --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__yaegi-go-embed-directives
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task yjs-map-conflict-detection --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__yjs-map-conflict-detection
.\run-deepswe.cmd run --agent copilot-cli --model gpt-5.3-codex --reasoning-effort xhigh --task ytt-jsonpath-query-api --concurrency 1 --job-name copilot-cli__gpt-5.3-codex__xhigh__ytt-jsonpath-query-api
```

