#!/usr/bin/env python3
"""Unit and mutation checks for scripts/check-env-doc.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/check-env-doc.py"
SPEC = importlib.util.spec_from_file_location("check_env_doc", CHECKER)
assert SPEC is not None and SPEC.loader is not None
check_env_doc = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_env_doc
SPEC.loader.exec_module(check_env_doc)

undocumented = check_env_doc.undocumented_env_vars


class UndocumentedEnvVarTests(unittest.TestCase):
    def scan_source(self, source: str) -> set[str]:
        with tempfile.TemporaryDirectory(prefix="env-doc-scan-") as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "fixture.cpp").write_text(source, encoding="utf-8")
            return check_env_doc.scan_env_names(root)

    def test_documented_var_passes(self) -> None:
        self.assertEqual(
            undocumented({"VT_FOO"}, {"VT_FOO"}, set()), []
        )

    def test_allowlisted_var_passes(self) -> None:
        self.assertEqual(
            undocumented({"VT_FOO"}, set(), {"VT_FOO"}), []
        )

    def test_undocumented_var_fails(self) -> None:
        # A scanned var covered by neither surface is reported.
        self.assertEqual(
            undocumented({"VT_NEW_KNOB"}, set(), set()), ["VT_NEW_KNOB"]
        )

    def test_mixed_reports_only_the_uncovered(self) -> None:
        result = undocumented(
            {"VT_A", "VT_B", "VLLM_C"},
            documented={"VT_A"},
            allowlisted={"VT_B"},
        )
        self.assertEqual(result, ["VLLM_C"])

    def test_helpers_harvest_names(self) -> None:
        doc = "The `VT_CPU_REF` knob and `VLLM_CPP_CPU_THREADS`."
        self.assertEqual(
            check_env_doc.documented_names(doc),
            {"VT_CPU_REF", "VLLM_CPP_CPU_THREADS"},
        )
        allow = "# comment\nVT_GDN_TMA\nVT_MOE_DECODE   # trailing\n\n"
        self.assertEqual(
            check_env_doc.allowlisted_names(allow), {"VT_GDN_TMA", "VT_MOE_DECODE"}
        )

    def test_scanner_finds_getenv_reads(self) -> None:
        self.assertEqual(
            self.scan_source(
                'const char* a = std::getenv("VT_ALPHA");\n'
                'const char* b = getenv(\n  "VLLM_BETA"\n);\n'
            ),
            {"VT_ALPHA", "VLLM_BETA"},
        )

    def test_scanner_finds_repository_env_reader_wrappers(self) -> None:
        self.assertEqual(
            self.scan_source(
                'EnvOn("VT_CPU_REF");\n'
                'EnvOnOr("VT_GGUF_KEEP_QUANT", true);\n'
                'EnvironmentBool("VT_FP4_PERSISTENT_CACHE", true);\n'
                'EnvironmentValue("VT_FP4_AUTOTUNE_CACHE_PATH");\n'
                'EnvironmentEnabled("VT_FP4_PRE_SERVE_WARMUP");\n'
                'GdnTritonEnvOn("VT_GDN_WU_TRITON");\n'
                'GetEnvNonEmpty("VLLM_PREFIX_CACHING_HASH_SEED");\n'
            ),
            {
                "VT_CPU_REF",
                "VT_GGUF_KEEP_QUANT",
                "VT_FP4_PERSISTENT_CACHE",
                "VT_FP4_AUTOTUNE_CACHE_PATH",
                "VT_FP4_PRE_SERVE_WARMUP",
                "VT_GDN_WU_TRITON",
                "VLLM_PREFIX_CACHING_HASH_SEED",
            },
        )

    def test_scanner_ignores_comments_and_unread_string_literals(self) -> None:
        self.assertEqual(
            self.scan_source(
                '// std::getenv("VT_COMMENT_ONLY")\n'
                '/* getenv("VLLM_BLOCK_COMMENT") */\n'
                'const char* diagnostic = "VT_NOT_AN_ENV_READ";\n'
            ),
            set(),
        )

    def test_shipped_tree_is_fully_covered(self) -> None:
        # The real repo must pass: every scanned name is documented or allowlisted.
        scanned = check_env_doc.scan_env_names(ROOT)
        documented = check_env_doc.documented_names(
            (ROOT / "docs/ENVIRONMENT.md").read_text(encoding="utf-8")
        )
        allowlisted = check_env_doc.allowlisted_names(
            (ROOT / "scripts/env-doc-allowlist.txt").read_text(encoding="utf-8")
        )
        self.assertEqual(undocumented(scanned, documented, allowlisted), [])
        self.assertGreater(len(scanned), 100)  # the sweep actually found names

    def test_a_fabricated_new_var_would_fail(self) -> None:
        # Mutation: pretend the code grew a new undocumented var; it must trip.
        scanned = check_env_doc.scan_env_names(ROOT)
        documented = check_env_doc.documented_names(
            (ROOT / "docs/ENVIRONMENT.md").read_text(encoding="utf-8")
        )
        allowlisted = check_env_doc.allowlisted_names(
            (ROOT / "scripts/env-doc-allowlist.txt").read_text(encoding="utf-8")
        )
        mutated = set(scanned) | {"VT_A_BRAND_NEW_UNDOCUMENTED_KNOB"}
        result = undocumented(mutated, documented, allowlisted)
        self.assertIn("VT_A_BRAND_NEW_UNDOCUMENTED_KNOB", result)


if __name__ == "__main__":
    unittest.main()
