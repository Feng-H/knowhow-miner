"""
Test Suite for Industrial Knowledge Miner Evaluation Harness
"""

import os
import unittest
from miner.eval_runner import HarnessEvaluator

class TestEvalHarness(unittest.TestCase):
    def test_eval_benchmark_harness(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        noise_path = os.path.join(base_dir, "benchmarks", "noise_fixtures.json")
        gold_path = os.path.join(base_dir, "benchmarks", "gold_standard_v1.json")

        self.assertTrue(os.path.exists(noise_path), f"Noise fixtures not found: {noise_path}")
        self.assertTrue(os.path.exists(gold_path), f"Gold standard not found: {gold_path}")

        evaluator = HarnessEvaluator(noise_path, gold_path)
        report = evaluator.run_all()

        # Assertions on quantitative performance gates
        self.assertGreaterEqual(report["overall_harness_score"], 85.0)
        
        m = report["metrics"]
        # Level 1: Cleaning must preserve technical parameters 100% (zero false positives)
        self.assertEqual(m["level1_cleaning"]["critical_tech_preservation_rate"], 100.0)
        self.assertGreaterEqual(m["level1_cleaning"]["disclaimer_strip_rate"], 95.0)

        # Level 3: PR vs Physics Decoupling
        self.assertGreaterEqual(m["level3_causal"]["pr_vs_physics_decoupling_rate"], 90.0)

        # Level 4: DFM syntax validity
        self.assertEqual(m["level4_physics_dfm"]["formula_syntax_validity"], 100.0)

        # Level 5: Evidence hierarchy & citation traceability
        self.assertEqual(m["level5_evidence"]["citation_anchoring_rate"], 100.0)
        self.assertEqual(m["level5_evidence"]["evidence_grade_validity"], 100.0)

if __name__ == "__main__":
    unittest.main()
