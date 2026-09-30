# Make the Qwen3.8 measurement workflow discoverable

## Scope

Documentation follow-up for `BENCH-QWEN38-TENSORFOLD-GAP`, tracked by
`ISSUE-LOCAL-01M3R485ZSPG7VHK1Y8B2207DZ`. The benchmark lifecycle remains
`BLOCKED_MISSING_ARTIFACTS`. This change adds no implementation or measurement.

| Surface | Source | Change | Verification |
|---|---|---|---|
| README news | `tools/bench/qwen38_endpoint_bench.py:466` | Announce the endpoint measurement tool with the blocked comparison caveat | Read parser and public result |
| Public benchmark detail | `benchmarks/manifests/qwen38_tensorfold/README.md:1` | Link the harness instructions and environment templates; explain comparison limits | Resolve links and inspect verdict logic |
| Capture prerequisites | `tools/bench/run_qwen38_tensorfold_gap.py` | Link existing runner instructions where available, without inventing a runnable GPU recipe | Inspect parser and templates |

## Design and sources

Add one short news item to `README.md` and a measurement-tools section to
`docs/benchmarks/qwen38-tensorfold-gap.md`. Reuse the committed manifest guide
instead of duplicating its command. Explain that prompt fingerprints and reply
text evidence are distinct. `PROFILE_COMPARISON` is not token parity and
supplies no cross-engine ratio. Preserve the bounded discovery scope, absent
MTP weights, existing evidence, and benchmark values.

The parser and comparison contract live in
`tools/bench/qwen38_endpoint_bench.py`. The original benchmark spec is
`bench-qwen38-tensorfold-gap.md`. This documentation change does not port vLLM
behavior. Upstream source execution and performance comparisons are not
applicable because no executable code changes.

## Tests and gates

No tests to port. Use existing CPU-only suites:

```sh
python3 tests/scripts/test_qwen38_endpoint_bench.py
python3 tests/scripts/test_run_qwen38_tensorfold_gap.py
python3 tests/scripts/test_validate_qwen38_tensorfold_evidence.py
python3 scripts/check-readme-structure.py
python3 tools/bench/validate_qwen38_tensorfold_evidence.py .agents/evidence/bench-qwen38-tensorfold-gap/latest
```

Check each added relative link and run `git diff --check`. Run repository
preflight and distinguish pre-existing failures from changes introduced here.
A fresh reviewer checks an immutable commit against source. No runtime
behavior or test guarantee changes, so code mutation testing is not applicable.

## Risks and stop conditions

Do not imply a successful endpoint capture, a performance improvement, model
parity, or usable MTP weights. Do not change historical EXL3 measurements or
benchmark-index work already covered by another pull request. Use no GPU,
external compute, model downloads, or service management. Open one fork pull
request; do not merge upstream.

## Now

Documentation scoped. Implementation and independent source review pending.
