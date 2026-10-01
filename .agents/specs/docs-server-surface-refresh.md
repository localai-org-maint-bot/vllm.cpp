# Refresh the public server guide

## Scope

Audit base: `fce36733b`, fetched from upstream `main` on 1 October 2026.
This documentation repair describes shipped behavior. It changes no runtime,
model lifecycle, oracle pin, or benchmark result. No GPU is required.

| Surface | Implementation anchors | Documentation repair |
|---|---|---|
| Decision routes | `src/vllm/entrypoints/openai/api_server.cpp` route registration; `src/capi/vllm_c.cpp` server adapter; `docs/models/tev1.md` | Add the conditional decision routes to the server reference and Tev1 to README news |
| Prompt log probabilities | `serving_completion.cpp` choice builder; `serving_chat.cpp` response builder; `protocol.cpp` validation and serialization, all under `src/vllm/entrypoints/openai/` | Replace the stale HTTP-unavailable claim in the server reference and usage guide |
| EOS fallback | `src/vllm/v1/engine/input_processor.cpp`; `src/vllm/config/model.cpp`; `.agents/specs/tev1-eos-fallback.md` | Explain tokenizer fallback and config precedence in the server reference |

## Design

Keep reference prose short. Describe request conditions, response locations,
and registration conditions with links to existing examples and model recipes.
Give prompt log probabilities one authoritative explanation in the server
reference and link it from the usage guide. Correct the usage introduction
that calls every decision model non-generative. Tev1 samples one answer token
per question through the same engine as chat.

README news describes the newly shipped Tev1 decision path without claiming
GPU correctness, full vLLM parity, or speed. Preserve existing benchmark values.
Avoid unrelated ABI-version edits covered by open pull request 3343.

## Upstream chain and tests to port

No implementation is ported. The checked-in request validators, serializers,
route registration, engine input processing, and their existing tests define
this repair. Existing model specs retain their pinned reference evidence.
No new oracle execution, performance measurement, or runtime test is applicable.

## Gates

- Trace every changed behavior claim to code and existing tests.
- Run `scripts/check-readme-structure.py`, `scripts/check-site.py`, and
  `scripts/check-benchmark-index.py` with Python.
- Check changed local links and heading anchors. Parse any added JSON example.
- Run `git diff --check`, commit-style, and commit-trailer checks against the
  pinned base. No source, test, or build file may change.
- Run the CPU-only preflight. Compare failures with the untouched baseline.
  Do not claim full success if unrelated checks fail or prerequisites are absent.
- A fresh reviewer checks the immutable commit. Scratch mutations of links,
  anchors, and any added JSON must fail the scoped checks. Runtime reachability
  mutations do not apply to a documentation-only change.
- The operator independently reruns the focused gates before the fork push.

## Work breakdown

1. Commit this scope and its canonical local issue.
2. Delegate the public prose to a fresh implementer in a separate worktree.
3. Review the immutable implementation independently and repair any findings.
4. Record results here and open a reviewed pull request from the user's fork.

## Constraints and stop conditions

Only `README.md`, `docs/reference/server.md`, and the relevant server sections
of `docs/USAGE.md` are implementation scope. The spec and its issue carry the
work record. No lifecycle transition requires a shared matrix edit.
Use local CPU tools only. Do not download weights, use an accelerator, change
services, or merge upstream. Stop on an unresolved source contradiction.
Unspecified external environment values remain unavailable. This task needs
none. The user authorizes autonomous fork work and an upstream pull request.

## Owed

- ISSUE-LOCAL-01M3TPN0QZ8856GY1MHN2TKNHX: repair the public server descriptions.
