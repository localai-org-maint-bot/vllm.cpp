# Tenstorrent public overview

## Scope

Update README news and hardware guidance, docs/BUILD.md, and docs/FEATURES.md
for the quantized Qwen completion already present on main at 31509d91f.
This is an editorial audit, not a model or backend lifecycle transition.
Do not edit code, tests, measurements, matrices, or other open documentation PRs.

## Source and evidence

- src/vt/tenstorrent/tenstorrent_ops.cpp:2828 and :2845 select the opt-in
  VT_TT_KEEPQUANT_INT8DOT path. Read the complete dispatch before describing it.
- examples/bench/main.cpp:49 declares the benchmark command arguments.
- docs/benchmarks/tt-keepquant-27b-decode.md records two completed prompts on
  Qwen3.8-27B Q4_K_M and Qwen3.5-0.8B Q4_K_M on the P150. This run supplies
  neither token correctness nor comparative speed evidence.
- .agents/specs/tenstorrent-keepquant.md retains the separate correctness
  record and open work. Do not infer correctness from benchmark exit status.
- docs/benchmarks/tt-capture-default-decode.md owns the earlier capture A/B.

## Design

Add one compact September news entry with the model, backend, opt-in condition,
smoke scope, and benchmark link. Update the hardware row and build section to
make that same capability discoverable. In FEATURES, add a concise keep-quant
entry next to the existing Tenstorrent rows. Preserve their existing evidence.
Explain that keep-quant computes from compressed weights. Do not quote new
ratios or imply default-on operation or production readiness.

## Tests and gates

Documentation only. Upstream test ports, inference comparisons, and performance
reruns are not applicable because executable behavior and measurements do not
change. All validation runs locally on the CPU.

Run scripts/check-readme-structure.py, scripts/check-benchmark-index.py,
scripts/check-agent-record.py, and their applicable existing mutation suites.
Run git diff --check. Review each changed assertion against source and the
published evidence. No new tests that merely match prose.
Run scripts/agent-preflight.sh and distinguish baseline or environment failures
from regressions. The current environment requires a user-local Python runtime.

## Work breakdown

1. Commit this scope and its local issue before editing public prose.
2. A fresh implementer edits only the three public documents.
3. A fresh reviewer checks the immutable commit against source and evidence.
4. The coordinator reruns the applicable CPU gates and opens one fork PR.

## Risks and stop conditions

No accelerator execution, remote compute, model downloads, service changes,
or backend state promotion. Missing evidence leaves a claim out of the prose.
Conflicting source and measurement claims need a narrow caveat, not a new
measurement. The user authorizes a fork PR, not merging upstream.

## Now

Scope recorded before implementation. Benchmark disposition: NOT APPLICABLE
for editorial changes. Existing measurements remain owned by their detail pages.

## Owed

