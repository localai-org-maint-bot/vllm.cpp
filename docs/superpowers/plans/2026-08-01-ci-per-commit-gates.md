# Per-commit CI Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure the documentation and commit-protocol range gates can never be cancelled before validating their unique push range.

**Architecture:** Keep the existing range computation unchanged and remove job-level cancellation from only the two protected jobs. Add a standard-library Python test that extracts those job blocks and mutation-proves both forbidden concurrency keys are rejected.

**Tech Stack:** GitHub Actions YAML, Python 3 `unittest`, repository record checkers.

## Global Constraints

- CPU-only, with no GPU, model, compiler, service, or download.
- Do not change workflow-level PR deduplication or any tree-scoped job.
- Do not change runtime code, lifecycle state, support claims, or benchmarks.

---

### Task 1: Pin the non-cancellation invariant

**Files:**
- Create: `tests/scripts/test_ci_per_commit_gates.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: the `jobs:` mapping and the two job names in `.github/workflows/ci.yml`.
- Produces: `job_block(text: str, name: str) -> str` and `gate_errors(text: str) -> list[str]` in the test module.

- [ ] **Step 1: Write the failing test**

  Add tests asserting the checked-in workflow has no `concurrency:` or
  `cancel-in-progress:` key inside either protected job, plus mutations that
  inject each forbidden key and assert an error names the job and key.

- [ ] **Step 2: Run test to verify it fails**

  Run: `python3 tests/scripts/test_ci_per_commit_gates.py`

  Expected: FAIL for both repository job blocks because each currently contains
  `concurrency` and `cancel-in-progress`.

- [ ] **Step 3: Write minimal implementation**

  Delete only the four-line job-level concurrency blocks beneath
  `documentation-checkpoint` and `commit-protocol-tag`. Retain their comments,
  range selection, and workflow-level concurrency unchanged.

- [ ] **Step 4: Run test to verify it passes**

  Run: `python3 tests/scripts/test_ci_per_commit_gates.py`

  Expected: PASS, including both mutation families.

- [ ] **Step 5: Run full verification and commit**

  Run the script unittest discovery, all repository governance checkers, and
  `git diff --check`; update the owned checkpoint records; commit with
  `FOLLOWING_AGENTS_PROTOCOL` and `Assisted-by: Codex:GPT-5 [Codex]`.
