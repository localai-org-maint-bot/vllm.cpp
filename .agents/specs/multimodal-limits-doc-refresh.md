# Refresh multimodal limit instructions

## Scope

Documentation correction under `ENG-MM-INPUT-PIPELINE`, tracked by
[ISSUE-LOCAL-01M42DVD1H44AV0JTT2F6K3JDB](../issues/ENG-MM-INPUT-PIPELINE/ISSUE-LOCAL-01M42DVD1H44AV0JTT2F6K3JDB.md).
Base: `33fb82b09`. Update the multimodal input guide, its server flag reference,
and one README news entry. No model lifecycle or benchmark disposition changes.

## Baseline and source anchors

| Surface | Source | Documentation gap |
|---|---|---|
| Dense tower skip | `src/vllm/model_executor/models/qwen3_5_dense_weights.cpp:1193`, `src/vllm/model_executor/models/qwen3_5_dense.cpp:55` and `:133` | The guide and flag reference omit the dense loader. |
| Shared zero-limit predicate | `src/vllm/model_executor/models/interfaces.cpp:9` | Explain that every modality served by a tower must be zero. |
| Projector loading | `src/vllm/entrypoints/llm.cpp`, `SkipTowerForModalities` and `LoadQwen3VLVisionFromClipMmproj` call sites | Preserve the distinction between metadata validation and skipped tensor validation. |
| Serving limits | `src/vllm/entrypoints/openai/chat_mm.cpp` and `chat_utils.cpp` | Preserve architecture ceilings and configured-limit refusal behavior. |
| Dense loader test | `tests/vllm/models/test_qwen3_5_dense_vision.cpp`, `qwen3_5_dense_loader_leaves_the_tower_unread_at_zero_limits` | Source evidence only. No new execution claim. |

The existing implementation spec is
[qwen35-dense-tower-modality-limits.md](qwen35-dense-tower-modality-limits.md).
This task documents local behavior. It ports no upstream behavior or tests and
makes no new oracle, token, memory, or speed claim. No GPU is available.

## Design and work breakdown

1. Add a short README news entry for the dense loader's text-only loading change.
   Link to the input guide. Do not imply new multimodal HTTP architecture support.
2. Rewrite the guide's per-prompt limits section as user instructions. Include
   the dense loader, keep the dots3-note exception, and explain both zero-limit
   spellings. Keep C API request limitations and projector validation caveats.
3. Replace the long server flag cell with its behavior and a guide link.
4. Link benchmark history to `docs/benchmarks/memory.md`, which already retains
   the historical measurements. Do not duplicate or change those measurements.

Keep unrelated guide content intact unless an adjacent sentence contradicts the
corrected zero-limit behavior. Any additional loader named in a coverage list
needs its production call site verified. Use short sentences and avoid internal
wave names, superseded attempt narratives, and speculative support claims.

## Tests and gates

No new test is needed for this documentation-only correction. Verify each changed
statement against the production source and existing tests. Check Markdown links
and executable flag spellings. Run:

```sh
python3 scripts/check-readme-structure.py
python3 scripts/check-agent-record.py
git diff --check 33fb82b09
bash scripts/agent-preflight.sh --quiet
```

Record exact results. Pre-existing full-preflight failures must reproduce at the
pinned base. Do not alter a checker to make this documentation change pass.
A fresh reviewer checks the committed diff in a separate worktree. Because no
behavior or test changes, production-call deletion is not an applicable gate.
The reviewer uses a scratch documentation mutation to demonstrate any applicable
structural guard and separately checks semantic claims against source.

## Dependencies, risks, and stop conditions

Local CPU, Python, Git, and the repository sources are sufficient. No checkpoint,
GPU, new benchmark, remote compute, or upstream checkout is required. An existing
PR covers ABI documentation, and another covers Qwen3.8 quantized arms. Do not
duplicate those changes. Stop on an unresolved source contradiction that changes
the intended scope. The user authorized a fork PR, not a merge to upstream.

## Now

The source audit identifies a documentation gap. The implementation and review
must complete before the fork pull request is ready. Model lifecycle states and
benchmark dispositions remain unchanged.
