# Public documentation for ABI 30 audio interfaces

## Now

Documentation audit of `SERVE-C-ABI` at base `1de097c46`.
Issue: ISSUE-LOCAL-01M3JZF0TM67WEV1V63ZTJ00VQ.
The underlying capability lifecycle and benchmark dispositions do not change.

## Scope and source inventory

| Surface | Source | Documentation action |
|---|---|---|
| Current ABI | `include/vllm.h:389` | Replace obsolete current-version statements with 30 |
| Diarization and speaker-attributed ASR | `include/vllm.h:1116`; `src/capi/vllm_c.cpp:1527` | Explain separate handles, PCM format, result cleanup, and disabled-build errors |
| Build dependency | `CMakeLists.txt:1587` | Document default ON, fetch from parakeet.cpp main, OFF option, and local-source caveat |
| HTTP attachment | `include/vllm/entrypoints/openai/api_server.h:286`; `src/vllm/entrypoints/openai/api_server.cpp:1829` | Distinguish conditional callbacks from bundled-server availability |
| ASR handle | `src/capi/vllm_c.cpp:864` | Inspect the actual loader before suggesting a combined-ASR recipe |

The source change is `2833d6300`. This task documents existing local APIs.
It ports no upstream behavior or tests and needs no GPU or model downloads.

## Design and owned files

Update README news and its current ABI statement, docs/BUILD.md,
docs/USAGE.md, docs/reference/c-api.md, docs/reference/server.md, and the
relevant public C API row in docs/FEATURES.md. Keep prose brief and practical.
Document unsupported or unwired paths explicitly. Do not imply runtime parity,
working model artifacts, or benchmark results from header declarations.
Use a short C example only if every call and ownership rule is source-grounded.

## Tests and gates

Read every changed claim against the header, C implementation, build files,
and server wiring. Run the existing README structure and public-document
checks applicable to these pages, plus their mutation suites. Check local link
targets and `git diff --check`. An independent reviewer checks the immutable
implementation commit. The operator repeats focused verification.

Full preflight has pre-existing failures at the base. Preserve its log and
report these separately. Do not change checkers, product code, lifecycle
matrices, or benchmark numbers to make this documentation repair pass.

## Risks and stop conditions

A declaration is not proof of runtime availability. In particular, check
whether the bundled server ever installs diarization callbacks and whether
SAS has a runnable ASR loading recipe. Explain limits rather than inventing
flags or verified artifacts. Do not repair implementation defects in this row.

## Git integration

One fork pull request containing the spec commit before the documentation
commit. User authorizes pushing the task branch and opening an upstream PR.
No merge authority, external compute, or GPU execution is granted.
