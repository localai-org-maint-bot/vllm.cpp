# DOCS-PUBLIC-SURFACE-ALIGN-342

Issue: [#342](https://github.com/mudler/vllm.cpp/issues/342)

## Scope

Repair the public README and usage guide where they have drifted from the
shipped command, C ABI, conditional HTTP routes, registry-backed architecture
inventory, and benchmark scope. This is a documentation-only projection repair.
It changes no code, checker semantics, lifecycle state, or accepted measurement.

Authority is limited to this spec, the issue table in `.agents/roadmap_v1.md`,
one timeless positioning sentence in `.agents/mission.md`, `README.md`, and
`docs/USAGE.md`. `docs/STATUS.md` and `docs/BENCHMARKS.md` remain untouched.

## Source anchors and design

- `examples/CMakeLists.txt:86` sets target `server`'s output name to
  `vllm-server`. Public commands must invoke `build/examples/vllm-server`.
- `include/vllm.h:39-145` is the ABI evolution record and defines
  `VLLM_ABI_VERSION 17`. Public prose will name ABI v17 and describe additions
  through v17 without preserving an aging export count.
- `src/vllm/entrypoints/openai/api_server.cpp:1024-1068` conditionally
  registers `POST /v1/embeddings` when an embedder is attached and
  `POST /v1/audio/transcriptions` when a transcriber is attached. The endpoint
  table will state those conditions rather than implying every server exposes
  the routes.
- `docs/FEATURES.md:82-163`, checked against `REGISTER_VLLM_MODEL` by
  `scripts/check-supported-models.py`, is the keyed public model projection. The
  README will distinguish 35 registered architectures from the 27 that carry a
  passing correctness gate. It will not claim that every registered
  architecture is token-gated.
- `docs/BENCHMARKS.md:18-20,40-42` separates checkpoint-specific speed results.
  The passing six-concurrency table is the Qwen3.6-27B NVFP4 `unsloth`
  checkpoint at revision `890bdef7`. NVIDIA ModelOpt 27B at `0893e160` and the
  35B-A3B grid remain speed-pending. README performance prose will make that
  boundary explicit and will not change any measured value.

The writing pass keeps the existing LocalAI project structure, uses plain
language, and introduces no em dashes.

## Risks and stop conditions

- Counts can drift again if they are copied without their registry/gate meaning.
  Every count in README must say whether it is registered or correctness-gated.
- A broad "Qwen3.6-27B" speed claim can accidentally include a different
  checkpoint layout. Every passing grid claim must name `unsloth` and
  `890bdef7`; current ModelOpt and 35B gaps must remain visible.
- Endpoint wording must preserve conditional registration. Do not describe the
  embedding or transcription route as present on a text-only server.
- Stop if a requested public-doc gate requires checker changes or an edit beyond
  the authority above.

## Tests and evidence

Capture a focused stale-string scan before the implementation and require it to
find the old server path, ABI v10/export-count wording, conflicting architecture
counts, blanket correctness-gate language, and unscoped throughput language.
After the repair, require that scan to return no matches. Then run:

```sh
python3 scripts/check-readme-structure.py
python3 scripts/check-public-doc-tables.py
python3 scripts/check-supported-models.py
python3 scripts/check-surface-coverage.py
python3 scripts/check-doc-checkpoint.py --base 5812b8b6 --head HEAD
cmake -S . -B build-docs-cpu -DVLLM_CPP_CUDA=OFF -DVLLM_CPP_METAL=OFF -DVLLM_CPP_VULKAN=OFF -DVLLM_CPP_ROCM=OFF
cmake --build build-docs-cpu --target server vllm-cli -j2
build-docs-cpu/examples/vllm-server --help
```

Run `scripts/agent-preflight.sh --staged` before each commit. The known baseline
`check-test-registration` configure failure and `audit-live-rows` debt may be
reported only if unchanged; they do not expand this row.

## Outcome

Pending implementation and verification.
