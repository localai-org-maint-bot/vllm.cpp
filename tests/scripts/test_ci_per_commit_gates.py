#!/usr/bin/env python3
"""Mutation checks for CI jobs that must validate every unique push range."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/ci.yml"
PROTECTED_JOBS = ("documentation-checkpoint", "commit-protocol-tag")


def job_block(text: str, name: str) -> str:
    """Return one top-level job block from a GitHub Actions workflow."""
    lines = text.splitlines()
    marker = f"  {name}:"
    try:
        start = lines.index(marker)
    except ValueError as exc:
        raise AssertionError(f"missing protected CI job: {name}") from exc

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            end = index
            break
    return "\n".join(lines[start:end])


def gate_errors(text: str) -> list[str]:
    """Return cancellation-policy violations for range-scoped jobs."""
    errors: list[str] = []
    for name in PROTECTED_JOBS:
        block = job_block(text, name)
        for key in ("concurrency:", "cancel-in-progress:"):
            if any(line.strip().startswith(key) for line in block.splitlines()[1:]):
                errors.append(f"{name} must not set {key[:-1]}")
    return errors


class PerCommitGateTests(unittest.TestCase):
    def test_range_scoped_jobs_cannot_be_cancelled(self) -> None:
        self.assertEqual(gate_errors(WORKFLOW.read_text()), [])

    def test_mutation_catches_concurrency_group(self) -> None:
        baseline = WORKFLOW.read_text()
        for name in PROTECTED_JOBS:
            with self.subTest(job=name):
                mutated = baseline.replace(
                    f"  {name}:\n", f"  {name}:\n    concurrency:\n      group: mutant\n", 1
                )
                self.assertIn(
                    f"{name} must not set concurrency", gate_errors(mutated)
                )

    def test_mutation_catches_cancel_in_progress(self) -> None:
        baseline = WORKFLOW.read_text()
        for name in PROTECTED_JOBS:
            with self.subTest(job=name):
                mutated = baseline.replace(
                    f"  {name}:\n", f"  {name}:\n    cancel-in-progress: true\n", 1
                )
                self.assertIn(
                    f"{name} must not set cancel-in-progress", gate_errors(mutated)
                )


if __name__ == "__main__":
    unittest.main()
