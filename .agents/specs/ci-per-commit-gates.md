# Per-commit CI gate cancellation repair

## Scope

This spike owns `ROAD-V1-A6` and only the two diff-scoped CI jobs
`documentation-checkpoint` and `commit-protocol-tag`. It removes their ability
to cancel an earlier run and adds a CPU static regression test. It does not
change runtime code, lifecycle states, support claims, build jobs, or the
workflow-level pull-request deduplication policy.

## Upstream chain

There is no vLLM runtime counterpart. This is repository governance around the
local contracts in `AGENTS.md:80-91,230-245` and the range selection in
`.github/workflows/ci.yml:73-135`. GitHub Actions evaluates job concurrency by
group and cancels an in-progress member when `cancel-in-progress` is true. The
two jobs group by `github.ref`, but each push checks only
`github.event.before..github.sha`; a replacement run therefore cannot cover a
cancelled predecessor's unique range.

## Our baseline

`.github/workflows/ci.yml:74-77,87-99` simultaneously says the two gates must
not be cancelled and configures both with `cancel-in-progress: true`. Existing
Python script tests validate checker semantics, but no test pins the workflow's
non-cancellation invariant.

## Port map

- `.github/workflows/ci.yml`: delete only the two job-level concurrency blocks.
- `tests/scripts/test_ci_per_commit_gates.py`: parse the workflow text by job
  indentation and reject `concurrency` or `cancel-in-progress` inside either
  protected job; mutation-test that each forbidden key is caught.

No YAML dependency is added. Text inspection is deliberate because the test
guards the exact workflow structure and runs in the standard-library suite.

## Tests to port

No upstream vLLM test applies. The local executable contract has three cases:
the repository workflow passes; injecting a concurrency group under either
protected job fails; injecting `cancel-in-progress: true` under either protected
job fails. The test must be RED against the current workflow before the fix.

## Gates

- `python3 tests/scripts/test_ci_per_commit_gates.py`
- `python3 -m unittest discover -s tests/scripts -p 'test_*.py'`
- all repository record, documentation, structure, fusion, leakage, and env
  checkers
- `git diff --check`

Correctness is the static workflow invariant. E2E is the mutation suite.
Performance and memory are `NOT APPLICABLE`; no executable runtime path changes.
GPU/backend gates are `NOT APPLICABLE`; all verification is CPU-only.

## Dependencies

Depends only on Python 3, Git, and the checked-in workflow. No model, compiler,
GPU, external service, dependency source, license addition, or download is
required. The row was unclaimed at selection time and does not overlap open PRs.

## Work breakdown

1. `CI-PC1`: add the static test and observe RED on both protected jobs.
2. `CI-PC2`: remove their job-level cancellation blocks and observe GREEN.
3. `CI-PC3`: refresh checkpoint records, run the full CPU governance suite,
   commit, push, and open the PR.

## Risks/decisions

The chosen design removes cancellation only from the two range-scoped jobs.
Removing all concurrency would waste build capacity; changing the push range to
recheck history would duplicate work and complicate new-branch handling. Pull
request workflow-level cancellation remains safe because the newest PR run
checks the full PR base-to-head range.
