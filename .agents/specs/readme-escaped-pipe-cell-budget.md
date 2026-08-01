# ROAD-V1-A6 spike: escaped-pipe README cell-budget repair

## Scope

This spike covers `ROAD-V1-A6` governance only. The checker must measure a
Markdown table cell as one cell when its content contains an escaped pipe
(`\|`). It must continue to split on unescaped delimiter pipes, ignore fenced
code, and enforce the existing `MAX_CELL_CHARS` threshold. Runtime code, README
content, lifecycle states, support claims, and benchmark behavior are out of
scope.

Claim: `CLAIM-README-ESCAPED-PIPE`.

## Upstream chain

There is no vLLM runtime surface to port. The binding project contract is
`AGENTS.md:75-87`, which requires the README table-cell budget and its mutation
test. Markdown defines a backslash-escaped pipe as literal cell content rather
than a delimiter. Dynamic dispatch and runtime tracing are not applicable.

## Our baseline

`scripts/check-readme-structure.py:167-186` scans table rows outside fenced
code. Base `1448e981` used `split("|")` at the corresponding parse site, which
treats `\|` as a delimiter. A single cell whose total length exceeds
`MAX_CELL_CHARS` could therefore pass when escaped pipes divided it into
fragments below the threshold. The repair is anchored at
`scripts/check-readme-structure.py:65-72,175-180`; its regression is
`tests/scripts/test_check_readme_structure.py:126-133`.

## Port map

| Contract | Local implementation | Deviation |
|---|---|---|
| Markdown escaped pipe remains cell content | `scripts/check-readme-structure.py` table-cell splitter | A small negative-lookbehind split is sufficient for the README subset already accepted by the checker; a full Markdown parser is intentionally out of scope. |
| Oversized cell is rejected | `tests/scripts/test_check_readme_structure.py` mutation | None. |

## Tests to port

No upstream vLLM test applies. Add one local mutation case containing one
oversized cell split by escaped pipes into individually sub-threshold fragments.
The production change that makes it fail is reverting the escaped-pipe-aware
splitter to raw `str.split("|")`. Keep the existing ordinary oversized-cell,
long-table, and fenced-code cases as regression coverage.

## Gates

- RED: the focused mutation test fails on base `1448e981` because no
  wall-of-prose error is returned.
- GREEN: `python3 tests/scripts/test_check_readme_structure.py`.
- Regression: `python3 -m unittest discover -s tests/scripts -p 'test_*.py'`.
- Repository governance: every `scripts/check-*.py` checker exits zero.
- Checkpoint: `python3 scripts/check-doc-checkpoint.py --staged`.
- Hygiene: `git diff --cached --check` before commit and `git diff-tree --check
  HEAD` after commit.
- Performance, memory, model, backend, and GPU gates: `NOT APPLICABLE`, because
  only a pure Python documentation checker and its mutation suite change.

## Dependencies

Depends only on Python 3 and the repository files at `upstream/main` `1448e981`.
No compiler, model, hardware accelerator, external host, package download, or
license addition is required. Open PRs #2, #6, #7, and #13-#21 do not own this
escaped-pipe parser behavior or these exact test lines.

## Work breakdown

| Work | Files | Verification |
|---|---|---|
| A6-EP1 | `tests/scripts/test_check_readme_structure.py` | Focused RED proves the bypass. |
| A6-EP2 | `scripts/check-readme-structure.py` | Focused GREEN plus full script suite. |
| A6-EP3 | Coordination, roadmap, status, benchmark, ledger, state records | Record and document checkers. |

## Risks/decisions

Three approaches were considered. Special-casing the length calculation after
raw splitting is fragile because it must reconstruct cells. A full Markdown
parser adds an unnecessary dependency and a much larger parsing surface. The
selected approach splits only on pipes not immediately preceded by a backslash,
matching the repository's existing table parser convention. Multiple-backslash
Markdown edge cases are outside the checker's established subset and do not
justify broadening this governance fix.
