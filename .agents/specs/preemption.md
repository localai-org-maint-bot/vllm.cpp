# ENG-PREEMPT-RECOMPUTE spike: scheduler recompute preemption

Date: 2026-08-01
Pin: vLLM `5559679229bc961848b121ccdeaa8fa5d79bec98`
Row: `ENG-PREEMPT-RECOMPUTE`
Claim: `CLAIM-ENG-PREEMPT-RECOMPUTE-SPIKE`

## Scope

This spike inventories the running-request recompute-preemption path. The
bounded baseline is FCFS tail eviction when KV allocation fails: release the
victim's KV blocks, mark it `PREEMPTED`, reset computed-token progress, prepend
it to the waiting queue, report its id, and later resend it as a new request.

In scope for row closure are FCFS and priority victim selection, undoing work
already scheduled in the current step, speculative-token cleanup, encoder
cache/in-flight-prefill cleanup, output/event bookkeeping, recomputation with
prefix caching on and off, and resume through the MRV2 runner contract.
Disaggregated preemption, swap preemption, pipeline-parallel stale outputs, and
forced administrative reset are separate mechanisms and are out of scope.

The current PR changes records only. It does not advance a support claim.

## Upstream chain

Pinned vLLM owns this behavior entirely in the host scheduler:

- `vllm/v1/core/sched/scheduler.py:427-443,471-520` derives per-request work
  from `num_tokens_with_spec - num_computed_tokens` and schedules running
  requests first.
- `vllm/v1/core/sched/scheduler.py:563-613` retries KV allocation, selects the
  FCFS tail or lowest-priority victim, restores same-step token/encoder budgets,
  and stops only after the current request evicts itself.
- `vllm/v1/core/sched/scheduler.py:1203-1225` frees KV and encoder state,
  removes the request from in-flight prefills, clears speculative tokens,
  resets computed progress, increments metrics, prepends the victim, and emits
  the reset id.
- `vllm/v1/core/sched/scheduler.py:1227-1245` advances computed progress only
  after a schedule is formed, which is why resetting to zero means recompute.
- `vllm/v1/core/request_queue.py:131-199` defines FCFS prepend/pop ordering.

No runtime-selected dependency kernel participates. A later performance gate
must still trace both engines because recomputation changes the subsequent GPU
workload, but there is no kernel dispatch decision to resolve in this spike.

## Our baseline

The bounded FCFS path is already present:

- `src/vllm/v1/core/sched/scheduler.cpp:129-148` frees KV, changes status,
  resets progress, increments/logs preemption, prepends the request, and records
  the reset id.
- `src/vllm/v1/core/sched/scheduler.cpp:328-383` retries allocation and selects
  FCFS or priority victims, including same-step token-budget rollback.
- `src/vllm/v1/core/sched/scheduler.cpp:419-520` resumes waiting/preempted
  requests, and `:562-586` folds resumed requests into MRV2 new-request output.
- `src/vllm/v1/core/sched/request_queue.cpp:30-49` implements FCFS prepend and
  removal.

Existing CPU evidence covers KV exhaustion, FCFS-front retry, event/count
bookkeeping, and resumed-as-new behavior. Four upstream obligations remain
open, so the row cannot be `DONE`:

1. `preempt_request` does not clear `request->spec_token_ids`.
2. Encoder-cache and `_inflight_prefills` cleanup have no equivalent state in
   this bounded scheduler path.
3. The local same-step rollback does not restore encoder compute allocations;
   the encoder scheduling surface is not yet ported here.
4. No focused test proves prefix-cache-enabled recomputation or preservation of
   an already-sampled output token across preemption, both exercised upstream.

The first gap is locally implementable and must be RED-tested. Gaps 2 and 3
depend on the encoder/cross-attention scheduler rows. Gap 4 is CPU-testable.

## Port map

| Upstream | Local target | Disposition |
|---|---|---|
| `scheduler.py:563-613` | `src/vllm/v1/core/sched/scheduler.cpp:328-383` | Present for FCFS/priority and token-budget rollback; encoder rollback deferred |
| `scheduler.py:1203-1225` | `src/vllm/v1/core/sched/scheduler.cpp:129-148` | KV/status/progress/metrics/queue present; spec-token and encoder cleanup incomplete |
| `scheduler.py:1227-1245` | `src/vllm/v1/core/sched/scheduler.cpp:562-586` | Present through the MRV2 resumed-as-new fold |
| `request_queue.py:131-199` | `src/vllm/v1/core/sched/request_queue.cpp:30-49` | Present |

The only deliberate structural deviation is C++ ownership: `Scheduler` owns
requests in a map and queues hold borrowed pointers. Behavior and ordering
remain vLLM-defined.

## Tests to port

| Upstream test | Local tier | Current disposition |
|---|---|---|
| `tests/v1/core/test_scheduler.py:1016-1072::test_preempt_during_execution` | CPU doctest | Partial: `tests/vllm/v1/test_scheduler.cpp:370-408` covers eviction/reset, but not the upstream sampled-output preservation tail |
| `tests/v1/core/test_scheduler.py` priority preemption/resumption cases | CPU doctest | Present at `tests/vllm/v1/test_scheduler.cpp:895-959,1091-1155`; keep as cross-policy coverage |
| FCFS prepend behavior used by `_preempt_request` | CPU doctest | Present at `tests/vllm/v1/test_request_queue.cpp:113-129` |
| Spec-token clearing on preemption | CPU doctest | Missing; add a RED-first case before the implementation change |
| Prefix-cache-enabled recomputation | CPU doctest | Missing; port with caching on/off parametrization and exact recomputed-token/block assertions |
| Encoder-cache/in-flight-prefill cleanup | CPU doctest | SKIPPED until encoder scheduling state exists; tracked by the dependent encoder rows |

## Gates

W1 and W2 are fully CPU-verifiable:

```sh
cmake -S . -B build-cpu -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DVLLM_CPP_CUDA=OFF -DVLLM_CPP_SERVER=OFF
cmake --build build-cpu --target test_scheduler test_request_queue -j2
ctest --test-dir build-cpu --output-on-failure \
  -R '^(test_scheduler|test_request_queue)$'
```

Run the record gates at every checkpoint:

```sh
python3 scripts/check-agent-record.py
python3 tests/scripts/test_agent_record.py
python3 scripts/check-doc-checkpoint.py --staged
python3 tests/scripts/test_doc_checkpoint.py
python3 scripts/check-readme-structure.py
python3 scripts/check-model-checklist.py
python3 scripts/check-fusion-consistency.py
python3 scripts/check-device-leakage.py
python3 scripts/check-env-doc.py
```

Correctness closure additionally requires an identical seeded request stream
against pinned vLLM with caching on and off, comparing schedule outputs,
statuses, recomputed-token counts, reset ids, and final token ids. The eventual
performance/memory closure uses both gate models at the standard large-
concurrency workload, preemption forced by an identical KV budget, with nsys on
both engines and every-axis comparison under the benchmark protocol. Those GPU
gates keep the row below `DONE`; they are not required for this records-only
spike.

## Dependencies

- W1/W2 depend only on `ENG-SCHED-CORE` and `KV-MANAGER-ALLOC`, whose bounded
  implementations already exist; no model, GPU, network data, or new license is
  required.
- W3 depends on the encoder/cross-attention scheduler surface (`KV-CROSS-ENCODER-SPECS`
  and `ATTN-ENCODER-CROSS`) and cannot be silently folded into this row early.
- W4 requires the pinned vLLM oracle, both gate models, and an uncontended GPU
  host selected by developer preferences.

## Work breakdown

| Leaf | Scope | Files | Gate |
|---|---|---|---|
| W1 | Complete the upstream basic case: preserve sampled output, clear stale spec tokens, assert reset id/event/count | scheduler implementation plus `test_scheduler.cpp` | CPU focused tests |
| W2 | Add prefix-cache on/off recomputation and resume-totality cases | `test_scheduler.cpp`, optionally KV-manager test helpers | CPU focused tests + pinned scheduler differential |
| W3 | Add encoder-cache/in-flight-prefill cleanup and same-step encoder-budget restoration after its dependencies land | scheduler/encoder manager and ported upstream tests | CPU oracle fixtures, then multimodal e2e |
| W4 | Close token, memory, latency, and throughput parity under forced preemption | parity/e2e harness and benchmark records only | both gate models, vLLM, nsys, every-axis grid |

W1 and W2 are sequential because they share the scheduler test file. W3 is
dependency-blocked. W4 follows semantic closure.

## Risks and decisions

- Recompute means resetting computed progress, not deleting sampled output.
  Tests must keep these two token domains distinct.
- Prefix caching may reduce the amount physically recomputed after reset; this
  is expected upstream behavior, not a reason to demand a full-prompt miss.
- A preempted request can have been scheduled earlier in the same step. Budget
  restoration is part of correctness, not an optimization.
- We considered closing only the already-tested FCFS subset, splitting every
  policy into separate rows, or keeping one upstream-semantic row. The selected
  design keeps one row and uses W leaves because FCFS and priority share the
  same `_preempt_request` state transition; separate lifecycle claims would
  hide cross-policy cleanup gaps.
