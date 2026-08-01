# Chunked prefill spike

Row: `ENG-CHUNKED-PREFILL`. Claim: `CLAIM-ENG-CHUNKED-PREFILL-SPIKE`.
Upstream pin: vLLM `5559679229bc961848b121ccdeaa8fa5d79bec98` (`0.26.0.dev0`).

## Scope

This spike backfills the contract for basic token-budget chunked prefill that already exists in vllm.cpp. The row-sized supported slice is: split a prompt across scheduler steps when it exceeds the remaining token budget; admit multiple partial prefills into one step; cap each request with `long_prefill_token_threshold`; keep partial prefills in the running set; emit no sampled token until prefill completes; and refuse an over-budget waiting request when chunking is disabled.

This spike does not claim newer adjacent modes as part of the basic row: multimodal encoder-input chunk boundaries, Mamba-aligned/fine-grained-prefix stops, DP prefill throttling, pooling-specific policy, or configurable multi-partial-prefill admission limits. Those need their own rows or an explicit split before implementation. No runtime source changes in this PR.

## Upstream chain

- `vllm/config/scheduler.py:58-91,126-136,261-310`: budgets, `enable_chunked_prefill`, `long_prefill_token_threshold`, partial-prefill limits, and validation/default derivation.
- `vllm/v1/core/sched/scheduler.py:427-561`: running-first remaining-token calculation, threshold cap, token-budget cap, and zero-work skip.
- `vllm/v1/core/sched/scheduler.py:640-930`: waiting admission, prefix-hit accounting, chunking-disabled stop, budget clipping, encoder-input and Mamba clipping, and slot allocation.
- `vllm/v1/core/sched/scheduler.py:1845-1900`: output folding and the `is_prefill_chunk`/discard contract that prevents sampling from incomplete prefills.

No dependency kernel selects the chunk size. This is host scheduler policy; scheduled token counts shape normal model-runner batches. Dynamic execution tracing is therefore a follow-on performance gate, not a missing semantic dependency.

## Our baseline

- Configuration exists at `include/vllm/config/scheduler.h:91-158` and is validated at `src/vllm/config/scheduler.cpp:49-92`.
- The running loop caps remaining work by the threshold, token budget, and model length at `src/vllm/v1/core/sched/scheduler.cpp:280-404`.
- The waiting loop handles cached and uncached work, the chunking enable gate, budget clipping, allocation, and admission at `src/vllm/v1/core/sched/scheduler.cpp:431-534`.
- Invariants are checked at `src/vllm/v1/core/sched/scheduler.cpp:543-550`; partial-prefill state is refreshed at `src/vllm/v1/core/sched/scheduler.cpp:945-982`.
- Existing CPU coverage lives at `tests/vllm/v1/test_scheduler.cpp:205-227,315-336,713-735,1329-1369`.

The basic slice is implemented and CPU-testable. The local suite does not directly pin `enable_chunked_prefill=false` ordering, the three-request `long_prefill_token_threshold=400` distribution, or that distribution with prefix caching toggled. The row remains `SPIKE`, not `DONE`, until those pinned cases are ported and the existing implementation is re-gated.

## Port map

| Upstream | Local | Disposition |
|---|---|---|
| `config/scheduler.py:58-91,126-136,261-310` | `include/vllm/config/scheduler.h`; `src/vllm/config/scheduler.cpp` | Basic fields and validation exist; multi-partial-prefill configuration is adjacent deferred scope. |
| `scheduler.py:427-561` running loop | `src/vllm/v1/core/sched/scheduler.cpp:280-404` | Basic token/threshold/model-length clipping exists. |
| `scheduler.py:640-930` waiting loop | `src/vllm/v1/core/sched/scheduler.cpp:431-534` | Basic cached-prefix accounting, disable gate, clipping, allocation, and admission exist. |
| `scheduler.py:1845-1900` output/discard | `src/vllm/v1/core/sched/scheduler.cpp:945-982`; runner discard tracked by `ENG-ASYNC-SCHED` | Basic state/output behavior exists; async runner ownership stays separate. |

## Tests to port

- `tests/v1/core/test_scheduler.py:271-333` `test_schedule_partial_requests`: multiple partial requests share one budget and incomplete rows produce no sampled token.
- `tests/v1/core/test_scheduler.py:589-661` `test_schedule_concurrent_partial_requests`, both prefix-cache modes: three 800-token prompts distribute as 400/400/224, then 400/400/224, then 1/1/352.
- `tests/v1/core/test_scheduler.py:988-1020` `test_schedule_order`, both `enable_chunked_prefill` values: enabled chunking fills the budget while disabled mode preserves waiting order and stops at an over-budget head.
- `tests/v1/core/test_scheduler.py:1433-1517` `test_no_spec_tokens_scheduled_for_prefill_chunks`: already ported at `tests/vllm/v1/test_scheduler.cpp:1329-1369`; retain as regression coverage.

Adjacent cases stay deferred under their owning rows: multimodal input chunking (`:538-585`), DP throttling (`:335-537`), and Mamba/fine-grained prefix stops. They must not inflate this row's support claim.

## Gates

```sh
cmake -S . -B build-cpu -DVLLM_CPP_CUDA=OFF -DVLLM_CPP_SERVER=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS=-Werror
cmake --build build-cpu --target test_scheduler test_scheduler_config -j2
ctest --test-dir build-cpu --output-on-failure -R '^(test_scheduler|test_scheduler_config)$'
```

The ported cases must fail if the token-budget clip or threshold cap is removed, or the chunking-disabled break is bypassed. Prefix caching on and off must both pass.

Because this policy changes batch composition, the closure gate on an authorized GPU host must compare an identical long-prompt concurrency sweep against pinned vLLM with chunking on/off, correctness first, then total/output throughput, request rate, TTFT, TPOT, ITL, and peak memory for 2-3 uncontended repetitions. The exact model, prompt/output lengths, concurrency grid, seed, engine/oracle commands, build, and evidence destination are recipe-definition `PENDING` until CP1 fixes and passes the semantic workload. This records-only spike is `NOT APPLICABLE` to benchmarking; the current executable next reproduction command is the CPU gate above.

## Dependencies

- `ENG-SCHED-CORE`: unified running/waiting scheduling and output folding.
- `KV-PREFIX-CACHE`: cached-token lookup before remaining-work calculation.
- `ENG-ASYNC-SCHED`: incomplete-prefill discard behavior in the async runner.
- `ENG-PARTIAL-PREFILL`: future configurable concurrent-partial limits, outside this row.
- `KV-MAMBA-ALIGN` and `KV-PREFIX-MATCH-UNIT`: hybrid/fine-grained stops, outside this row.

The spike and implementation tests need only pinned source plus a CPU toolchain and no model data. The binding performance gate needs an authorized GPU host and the project exclusion protocol.

## Work breakdown

- `CP0` (this PR): accept this spike and reconcile records without changing runtime support claims.
- `CP1` (CPU-only): port the three missing upstream behavioral groups, prove RED mutations, and re-gate existing scheduler/config targets. Own only `tests/vllm/v1/test_scheduler.cpp` unless a defect is reproduced.
- `CP2` (CPU-only if needed): fix only a reproduced basic budget/threshold/disable defect, preserving adjacent row ownership.
- `CP3` (GPU-required): same-workload vLLM correctness and every-axis performance gate; only this leaf may close the speed-sensitive lifecycle.

## Risks and decisions

- Keep this row basic; combining multimodal, Mamba alignment, DP throttling, and configurable partial-prefill concurrency would hide independently gateable gaps.
- Local file headers cite older `e24d1b24`; CP1 ports pin-era `555967922` tests before changing implementation claims.
- Unit tests prove allocation semantics, not runtime latency or memory; CP3 remains mandatory for closure.
- Disabling chunking is ordering-sensitive; assert token counts and waiting/running queue state.
