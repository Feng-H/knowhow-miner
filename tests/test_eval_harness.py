"""
Test Suite for Industrial Knowledge Miner Evaluation Harness
"""

import os
import pytest
from miner.eval_runner import HarnessEvaluator

def test_eval_benchmark_harness():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    noise_path = os.path.join(base_dir, "benchmarks", "noise_fixtures.json")
    gold_path = os.path.join(base_dir, "benchmarks", "gold_standard_v1.json")

    assert os.path.exists(noise_path), f"Noise fixtures not found: {noise_path}"
    assert os.path.exists(gold_path), f"Gold standard not found: {gold_path}"

    evaluator = HarnessEvaluator(noise_path, gold_path)
    report = evaluator.run_all()

    # Assertions on quantitative performance gates
    assert report["overall_harness_score"] >= 85.0, f"Harness overall score fell below 85: {report['overall_harness_score']}"
    
    m = report["metrics"]
    # Level 1: Cleaning must preserve technical parameters 100% (zero false positives)
    assert m["level1_cleaning"]["critical_tech_preservation_rate"] == 100.0
    assert m["level1_cleaning"]["disclaimer_strip_rate"] >= 95.0

    # Level 3: PR vs Physics Decoupling
    assert m["level3_causal"]["pr_vs_physics_decoupling_rate"] >= 90.0

    # Level 4: DFM syntax validity
    assert m["level4_physics_dfm"]["formula_syntax_validity"] == 100.0
