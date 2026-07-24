# Server and real-model end-to-end nightly (`SERVE-E2E-NIGHTLY`)

Status: **SPIKE**, 2026-07-24. Owner:
`CLAIM-SERVE-E2E-NIGHTLY-SPIKE-1`.

Pins: vLLM `e24d1b24`; vllm.cpp base `9721e848`.

## Scope

This spike defines the scheduled regression surface that continuously proves
the already-implemented server and real-model release gates. It does not add a
workflow, run a checkpoint, or claim support. The implementation is split so
that ordinary pull-request CI remains CPU-only while scheduled jobs consume
provisioned checkpoints on an explicitly selected runner.

In scope:

- inventory vLLM's API-server and V1 e2e CI topology;
- inventory every existing local server-conformance and real-model executable;
- define deterministic manifests, runner preflight, isolation, timeouts,
  artifacts, and failure classification;
- define the CPU presubmit and scheduled accelerator leaves;
- make skipped checkpoint tests a hard nightly failure rather than a green run.

Out of scope:

- new endpoint semantics or model support;
- performance acceptance, which remains owned by `SERVE-GATE-ONLINE` and the
  backend gate rows;
- downloading models during the timed job;
- multi-node/multi-GPU coverage until the corresponding scale-out rows are
  implemented;
- implementing or executing the nightly in this spike.

## Upstream chain

At vLLM `e24d1b24`, CI is a set of explicit hardware jobs rather than one
undifferentiated "nightly":

| Upstream surface | Contract to mirror |
|---|---|
| `.buildkite/test_areas/entrypoints.yaml:37-50` | real API-server integration is isolated in its own process/job |
| `.buildkite/test_areas/entrypoints.yaml:57-92` | OpenAI tests are split into bounded shards rather than one timeout-prone suite |
| `.buildkite/test_areas/entrypoints.yaml:116-124` | Responses API is a distinct surface, not inferred from completions |
| `.buildkite/test_areas/engine.yaml:52-76` | async scheduling and core V1 e2e are separate one-GPU jobs |
| `.buildkite/test_areas/engine.yaml:88-160` | topology-specific 2/4-GPU cases are explicit optional jobs |
| `tests/entrypoints/openai/{completion,chat_completion,responses}/` | endpoint behavior, streaming, errors, tools, and protocol compatibility |
| `tests/entrypoints/serve/{tokenize,instrumentator,lora}/` | non-generation serving endpoints and observability |
| `tests/v1/e2e/general/` | scheduling, context limits, sliding window, cascade attention, prefix caching, and streaming input |
| `tests/v1/e2e/spec_decode/` | speculative-decoding e2e behavior, separately shardable |
| `.buildkite/performance-benchmarks/tests/nightly-tests.json:1-220` | benchmark nightlies use an explicit workload manifest; this row borrows the manifest discipline, not its performance numbers |

Deviation: GitHub Actions is the repository's available scheduler, and
vllm.cpp has one GB10 rather than vLLM's heterogeneous fleet. The logical split
is mirrored; unavailable hardware cases remain linked to their owning backend
or scale-out rows and must not appear as passing nightly coverage.

## Our baseline

Existing local coverage is stronger than the matrix's old "current
unit/conformance tests only" wording but is not scheduled as one release gate:

| Surface | Existing anchor | Current limitation |
|---|---|---|
| HTTP contract | `tests/vllm/entrypoints/openai/test_conformance.cpp:1` and `tests/vllm/entrypoints/openai/test_api_server.cpp:1` | synthetic model only; runs in ordinary CTest |
| 27B/35B release models | `tests/parity/test_qwen27_paged_engine.cpp:110`, `tests/parity/test_qwen36_paged_engine.cpp:78` | checkpoint-gated; a missing checkpoint becomes SKIP |
| breadth models | paged-engine targets registered in `tests/CMakeLists.txt:585-717` | individually run by feature claims, not from a versioned nightly manifest |
| online serving | `scripts/dgx-online-serving.sh:1` | binding benchmark harness, intentionally too expensive and evidence-sensitive to become a generic correctness nightly |
| focused model gate pattern | `scripts/opt-dgx-gate.sh:1` | one model plus regressions; not a complete release manifest |
| CPU thread safety | `tests/vt/test_cpu_threadpool.cpp:173` | full multi-context server case is explicitly tracked but skipped |
| CI | `.github/workflows/ci.yml:1` | presubmit CPU build/checkers only; no scheduled self-hosted job |

The key correctness gap is not a missing model test. It is orchestration:
today a scheduled command can exit zero after every checkpoint test skipped,
there is no single pinned inventory proving which release gates ran, and logs
are not normalized into a durable summary.

## Port map

| Upstream | Local implementation leaf | Notes |
|---|---|---|
| entrypoint shards in `test_areas/entrypoints.yaml` | `scripts/nightly/manifest.json`, `scripts/nightly/run.py` | declarative target list plus a fail-closed runner |
| V1 e2e shards in `test_areas/engine.yaml` | same manifest/runner | local targets are CTest executables, not pytest directories |
| hardware selection fields (`device`, `num_devices`, timeout) | `.github/workflows/nightly.yml` | self-hosted label, concurrency group, scheduled/manual triggers, per-shard timeout |
| Buildkite artifacts/logs | `scripts/nightly/summarize.py` and uploaded `nightly-summary.json` plus raw logs | no benchmark promotion; correctness disposition only |
| vLLM job isolation | one subprocess per target, process-group timeout/cleanup | prevents one server or model allocation contaminating the next target |

The manifest is the canonical executable inventory. Each entry carries stable
ID, target path, tier (`cpu` or `dgx`), timeout, required environment variables,
checkpoint identity, expected assertion/token count where stable, owning matrix
row, and artifact policy.

## Tests to port

| Upstream test intent | Local test |
|---|---|
| API server split and lifecycle isolation from `tests/entrypoints/openai/` | existing `test_openai_api_server` and `test_openai_conformance`; nightly runner invokes each independently |
| async/core V1 split from `tests/v1/e2e/general/` | existing scheduler, prefix-cache, streaming, and paged-engine targets selected by manifest; missing behavior remains owned by its feature row |
| topology-specific selection from `engine.yaml:88-160` | runner unit test rejects a manifest entry whose declared hardware is unavailable instead of silently skipping it |
| explicit nightly workload inventory | new `tests/scripts/test_nightly_manifest.py`: schema, unique IDs, resolvable targets, valid row IDs, CPU/DGX separation |
| fail-closed checkpoint execution | new `tests/scripts/test_nightly_runner.py`: PASS, FAIL, TIMEOUT, CRASH, and SKIP are distinct; only PASS satisfies a required entry |
| process isolation | runner test starts a child process, times it out, and proves the process group is gone |
| artifact determinism | summarizer fixture test proves stable JSON ordering and preserves command, SHA, duration, exit/signal, disposition, and log path |

There is no upstream unit test for vllm.cpp's manifest runner. These are
tooling tests modeled on the repository's existing mutation suites.

## Gates

### Spike gate

This spike is complete when the record and doc checkpoint checkers pass. It
requires no build, checkpoint, GPU, or benchmark.

### Implementation gates

1. `N1` manifest/schema: Python unit tests pass on a GPU-less host; every
   required target resolves in a CPU build or is explicitly a DGX target.
2. `N2` runner: mutation tests prove required SKIP, timeout, signal death,
   missing executable, missing checkpoint, wrong checkpoint identity, and
   duplicate IDs all fail.
3. `N3` CPU presubmit: clean CPU `-Werror` build; `test_openai_api_server`,
   `test_openai_conformance`, runner tests, and manifest validation pass.
4. `N4` scheduled DGX correctness: clean production CUDA build, then every
   required manifest entry runs standalone under the repository GPU lock.
   The job records zero required SKIPs and uploads the summary even on failure.
5. `N5` release totality: both gate models and every model/backend marked
   supported in current matrices are present with their exact oracle/golden
   identity. Unsupported/blocked rows are absent, not xfailed.
6. Nightly correctness produces no speed claim. Any performance target calls
   the existing binding harness and remains subject to the benchmark protocol.

## Dependencies

| Dependency | Disposition |
|---|---|
| `SERVE-GATE-ONLINE` | reuse its build/model/corpus provenance where applicable; do not duplicate benchmark execution |
| `SERVE-STREAM-USAGE` and endpoint rows | nightly includes only implemented behavior; missing semantics stay on their owning rows |
| model/backend matrices | source of truth for which paged-engine targets are required |
| self-hosted DGX runner | required only for `N4`; implementation can land through `N3` first |
| model files and goldens | pre-provisioned, checksum-verified before execution; never downloaded in the timed job |
| GitHub Actions secrets/labels | workflow must not print secrets; runner label and model roots are repository configuration |
| hardware | spike/N1-N3: none; N4-N5: GB10; later multi-GPU shards remain blocked on their owning rows |

## Work breakdown

| ID | Work | Hardware | Exit state |
|---|---|---|---|
| `N1` | manifest schema, initial CPU/DGX inventory, validator, mutation tests | none | manifest is executable and fail-closed |
| `N2` | isolated subprocess runner plus deterministic JSON summarizer and tests | none | all disposition/error cases proven |
| `N3` | CPU presubmit job and local reproduction command | none | CPU shard required on every PR |
| `N4` | scheduled/manual DGX workflow, lock, preflight, production build, artifact upload | GB10 | required entries run with zero SKIPs |
| `N5` | reconcile manifest against matrices and close missing model/endpoint coverage | GB10 as rows require | release-totality report; row can enter `DONE` only here |

`N1` and `N2` may be one CPU-only PR if their files do not overlap another
claim. `N3` is separately revertible workflow policy. `N4` cannot be claimed
on a host unable to execute and verify the scheduled runner.

## Risks and decisions

- **Decision: required SKIP is failure.** Checkpoint-gated doctests are useful
  locally, but a nightly that skipped its release model proved nothing.
- **Decision: correctness and performance stay separate.** This row may invoke
  the binding harness but never republishes a partial/contended number.
- **Decision: manifest, not glob.** A glob silently grows, shrinks, and mixes
  unsupported rows. Stable IDs make additions reviewable and failures owned.
- **Risk: stale required counts.** Counts are optional unless stable; token and
  oracle identity are mandatory for release-model entries.
- **Risk: leaked processes or memory contamination.** Each target gets a new
  process group, hard timeout, cleanup verification, and standalone execution.
- **Risk: branch code on a privileged runner.** Scheduled runs use repository
  default-branch commits; manual runs require an explicit SHA and preserve it
  in the summary.
- **Risk: one GB10 serializes the suite.** Start with correctness-only targets,
  bounded timeouts, and one concurrency group. Performance campaigns remain
  separate and cannot overlap.
