# Correct the quickstart's Hugging Face download guidance

## Scope

Documentation-only repair for `ENG-HF-MODEL-DOWNLOAD`, tracked by
`ISSUE-LOCAL-01M3X91X8VCVS38PC6WAR8BWSY`. Base: `9d96b162c`.
No engine behavior, lifecycle state, benchmark, or support gate changes.

The quickstart still declares relative redirects an unresolved blocker.
The repair is already in the source at `3bee664bc`.
Open documentation PRs 3343 and 3366 cover ABI and serving reference updates,
not this quickstart correction.

## Source and evidence

| Fact | Anchor |
|---|---|
| Redirect resolution | `src/vllm/transformers_utils/hf_hub.cpp:295` (`HfResolveUrl`) |
| Both download loops use the resolver | `src/vllm/transformers_utils/downloader.cpp:389`, `:541` |
| Relative redirect regression cases | `tests/vllm/transformers_utils/test_downloader.cpp:618`, `:640`, `:705` |
| Existing download guide | `docs/guides/hugging-face-access.md` |
| Prior live-download evidence | `.agents/specs/hf-model-download.md:991` |
| Published recipe grammar | `scripts/check-quickstart-recipes.py` and `release/container-matrix.json` |

## Design

Edit only `docs/QUICKSTART.md`. Remove the obsolete redirect blocker from the
opening caveat, repository-ID recipe, and executed-model explanation. Describe
the repository-ID form as the current download workflow. Preserve the mounted
checkpoint recipe and its exact recorded result. Keep the release archive caveat
and container-tag caveats. Do not infer a new container run from source tests.
Use short, direct sentences instead of repeated explanations of evidence policy.

No new README news is owed: this corrects an August repair, not a new feature.
Recent ABI and server news already have separate open PRs.

## Gates and stop conditions

CPU-only documentation verification:

- `python3 scripts/check-quickstart-recipes.py`
- `python3 -m unittest tests.scripts.test_check_quickstart_recipes`
- `python3 scripts/check-readme-structure.py`
- Check changed local Markdown links and `git diff --check`.
- Fresh review against the named source and unchanged executed-run evidence.

Do not change checker semantics, fetch model weights, run inference, or claim
new runtime verification. No upstream tests need porting because no code is
ported. Runtime correctness and performance comparisons are not applicable.

Full preflight already fails on the base, including unresolved canonical issue
references and unavailable build prerequisites. Record those failures separately;
do not alter unrelated records or weaken gates to make this documentation pass.

## Now

Scope recorded before editing. One PR carries the spec and correction.
