# Qualify the historical Kolibri-1 TT capture study

## Scope

Documentation correction for `BACKEND-TENSTORRENT`, tracked by
`ISSUE-LOCAL-01M4YR6QSEEZEAAW2FJNANM67V`. Base: `50d425bec`.
Preserve the capture study and all original measurements. Identify which
observations predate the deterministic-decode and golden-index fixes.
No implementation, lifecycle, default, or benchmark disposition changes.

## Source and design

| Surface | Source | Change |
|---|---|---|
| Prototype timings | `docs/gap-kolibri1-tt-captured-decode.md` | Label historical results and qualify their interpretation |
| Cache lifetime fixes | `src/vllm/model_executor/models/kolibri1_tt_forward.cpp`, `src/vt/tenstorrent/tenstorrent_residency.cpp`, commit `ad8d9b45b` | Explain recorded repeatability after fixes |
| Correctness comparison | `tests/vllm/models/test_kolibri1_tt_b2ii.cpp`, commit `50d425bec` | Explain corrected decode indexing and remaining failures |
| Retained evidence | `.agents/issues/BACKEND-TENSTORRENT/ISSUE-LOCAL-01M4P21TZ1Q9CA7P66XBH0BQTX.md` | Link the recorded results without claiming a fresh run |

Add a short current-status note near the start so readers see the limitation
before the analysis. Mark the prototype section as historical. Qualify its
nondeterminism attribution and its conclusion about bias caching. Preserve
original timings and structural capture limitations. Avoid a new speed ratio.

## Tests and gates

This is prose-only work. No upstream tests need porting and no runtime oracle
or accelerator is required. Verify every new assertion against the sources
above. Check that all three timing rows remain byte-identical. Check changed
links locally, run `git diff --check`, `scripts/check-site.py`, and
`scripts/check-agent-record.py`. Run the full preflight and report unavailable
tooling separately from the focused documentation gate. A fresh reviewer
checks the immutable implementation commit and the source evidence.

## Risks and stop conditions

Repeatable output does not prove oracle correctness. The recorded token gate
still fails. Historical timings cannot establish current performance. Stop if
a proposed claim requires new accelerator measurements. Do not edit README
news: this corrects an old study, and existing PRs own the new CPU features.

## Work breakdown

1. Commit this scope and local issue before editing public prose.
2. A fresh implementer edits only the study and records source checks.
3. A fresh reviewer checks the committed diff. The operator reruns the focused
   gate before pushing to the maintenance fork and opening an upstream PR.
