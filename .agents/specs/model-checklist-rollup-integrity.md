# Model checklist rollup integrity

## Scope

This spike covers the `ROAD-V1-A6` maintenance increment
`CLAIM-MODEL-CHECKLIST-ROLLUP-UNIQUENESS`. It makes the architecture-support
checklist reject duplicate lifecycle-count rows and duplicate `Total` rows.
It does not change model lifecycle states, checklist marks, support claims, or
the model matrix.

## Upstream chain

This is repository-governance tooling with no vLLM runtime equivalent. The
binding local policy is `AGENTS.md` (architecture-support checklist directive),
the rollup parser is `scripts/check-model-checklist.py:132-153`, and CI invokes
the checker from `.github/workflows/ci.yml`. Runtime tracing is not applicable.

## Our baseline

`parse_rollup()` stores rows in a dictionary. A later row with the same key
silently overwrites the earlier row, so two identical `ACTIVE` rows or two
identical `Total` rows pass `checklist_errors()`. The defect reproduces against
the `VALID` fixture in `tests/scripts/test_check_model_checklist.py` by inserting
an identical rollup row and observing an empty error list.

## Port map

There is no upstream port. Add duplicate-key evidence to `parse_rollup()` and
surface it from `checklist_errors()`. Keep the existing pure checker API and
Markdown parser; do not introduce a generic table framework.

## Tests to port

No upstream tests apply. Add two local mutation cases to
`tests/scripts/test_check_model_checklist.py`: one repeats a lifecycle state and
one repeats `Total`. Both must fail before the implementation and pass after it.
The existing shipped-matrix and legitimate-row mutations remain the regression
suite.

## Gates

- Correctness: focused `test_check_model_checklist.py` is RED before and GREEN
  after the fix.
- Regression: `python3 -m unittest discover -s tests/scripts -p 'test_*.py'`.
- Records: run every standalone `scripts/check-*.py` checker and the Triton AOT
  shell mutation test.
- Performance, memory, architectures, and backends: `NOT APPLICABLE`; this is a
  pure Python governance check with no runtime path.

## Dependencies

No model, compiler, GPU, external host, download, or other roadmap row is
required. Python 3, Git, and the repository checkout are sufficient.

## Work breakdown

1. Add RED mutations for duplicate lifecycle and `Total` rows.
2. Preserve duplicate keys while parsing and emit explicit errors.
3. Refresh the mandatory no-lifecycle-change checkpoint records.
4. Run the focused, full Python, and repository-record gates, then open a PR.

## Risks and decisions

Reject duplicates instead of summing them: the rollup is a binding snapshot and
each key must have one authoritative row. Rejecting is deterministic and avoids
hiding malformed data behind arithmetic. A generic Markdown schema layer is out
of scope because this checker already owns the relevant table grammar.
