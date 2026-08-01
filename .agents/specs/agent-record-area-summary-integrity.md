# Per-area lifecycle-summary integrity spike

## Scope

This spike covers `ROAD-V1-A6` and `CLAIM-RECORD-AREA-SUMMARY`. It makes the
engine matrix lifecycle scoreboard fail closed when any named area row drifts
from the claimable rows below it. It does not change a feature lifecycle,
runtime behavior, the matrix inventory, or any support claim.

## Upstream chain

There is no vLLM runtime analogue. The binding sources are the local row
contract in `AGENTS.md:119-150`, the lifecycle summary in
`.agents/engine-matrix.md:31-43`, and `check_engine_summary` in
`scripts/check-agent-record.py:510-541`. Runtime tracing is not applicable
because this is a repository-governance checker.

## Our baseline

`check_engine_summary` parses the summary header but selects only the
`**Total**` row. It compares that row with all claimable engine rows, so the
grand total is protected while the nine named area rows are unchecked. A
mutation can move one lifecycle count from `INVENTORIED` to `ACTIVE` in a named
area without changing the total and the checker still exits successfully.

## Port map

| Contract | Local implementation |
|---|---|
| Parse each named engine summary row and its declared row count/state counts | `scripts/check-agent-record.py::check_engine_summary` |
| Map claimable rows to their enclosing `##` area section | `scripts/check-agent-record.py`, using row line numbers and section headings |
| Reject missing, duplicate, unknown, non-numeric, or drifting area rows | `scripts/check-agent-record.py::check_engine_summary` |
| Prove a named-area drift is rejected while the baseline remains green | `tests/scripts/test_agent_record.py` |

The implementation remains dependency-free Python and preserves the existing
grand-total checks.

## Tests to port

No upstream vLLM test exists for this project-local record. The local mutation
suite gains a case that changes one named-area lifecycle count without changing
the grand total and requires an area-specific error. Existing malformed-row,
spec, owner, evidence, and commit mutations remain the regression suite.

## Gates

- Correctness: `python3 tests/scripts/test_agent_record.py` must show the new
  mutation RED before the checker change and all tests green afterward.
- Integration: `python3 scripts/check-agent-record.py` must report the exact
  engine/model/quant/kernel/backend inventory with no errors.
- Documents: run `check-doc-checkpoint.py`, `check-readme-structure.py`,
  `check-model-checklist.py`, `check-fusion-consistency.py`, and
  `check-device-leakage.py` plus their available Python mutation suites.
- Formatting: `git diff --check`.
- Performance and memory: `NOT APPLICABLE`; no executable runtime path changes.
- Architectures/backends: all, because the checker is host-only and does not
  compile or dispatch backend code.

## Dependencies

Python 3 and the repository contents are sufficient. No compiler, model,
network asset, external service, GPU, or hardware lock is required. The work
does not depend on another roadmap row and does not overlap an open PR.

## Work breakdown

| Work | Files | Gate |
|---|---|---|
| W0 accepted spike and claim | this file, `.agents/coordination.md` | record checker |
| W1 RED mutation for one named area | `tests/scripts/test_agent_record.py` | focused unittest fails for missing enforcement |
| W2 section-aware area validation | `scripts/check-agent-record.py` | focused unittest and baseline checker pass |
| W3 checkpoint records and full CPU verification | roadmap/status/benchmark/ledger/state surfaces | all listed gates pass |

## Risks and decisions

Three approaches were considered. Checking only the total preserves the bug.
Hard-coding line ranges is brittle as sections grow. The selected approach
derives area membership from the existing second-level Markdown headings and
matches those names to the summary table, keeping the table as the canonical
declaration. Unknown or duplicate area labels fail closed. This is a
project-governance decision, not a vLLM behavior choice.
