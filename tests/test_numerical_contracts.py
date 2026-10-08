from __future__ import annotations

import importlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/paper-craft/scripts"
sys.path.insert(0, str(SCRIPTS))
contract = importlib.import_module("numerical_contract_check")


class NumericalContractTests(unittest.TestCase):
    def test_int32_counterexample_when_fragments_clip(self) -> None:
        result = contract.evaluate(1 << 30, -(1 << 30))
        self.assertEqual(result["fragment_sum"], -1)
        self.assertEqual(result["fragment_sum_final_saturation"], -1)
        self.assertEqual(result["joint_saturation"], 0)
        self.assertFalse(result["equivalent"])

    def test_equality_when_no_intermediate_clips(self) -> None:
        result = contract.evaluate(7, -3, 2)
        self.assertEqual(result["joint_saturation"], 16)
        self.assertTrue(result["equivalent"])

    def test_exact_addition_is_distinct_from_final_saturation(self) -> None:
        result = contract.evaluate(127, 127, 0, 8)
        self.assertEqual(result["fragment_sum"], 254)
        self.assertEqual(result["joint_saturation"], 127)
        self.assertTrue(result["equivalent_after_final_saturation"])

    def test_invalid_bounds_are_rejected(self) -> None:
        for values in [(1, 1, -1, 32), (1, 1, 65, 32), (1, 1, 0, 65), (1, 1, 0, 1), (128, 0, 1, 8)]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                contract.evaluate(*values)

    def test_cli_emits_json_counterexample(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPTS / "numerical_contract_check.py")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["fragment_sum"], -1)

    def test_cli_rejects_excessive_shift(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPTS / "numerical_contract_check.py"), "--shift", "1000000"],
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
