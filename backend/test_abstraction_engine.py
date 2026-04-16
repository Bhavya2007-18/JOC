import unittest
from intelligence.patterns.abstraction_engine import AbstractionEngine

class TestAbstractionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AbstractionEngine()
        self.base_baseline = {"window_fill": 1.0, "cpu_z_score": 0.0, "ram_z_score": 0.0}
        self.base_pred = {
            "predicted_cpu": {"trend": "stable"},
            "predicted_ram": {"trend": "stable"}
        }

    def test_t1_cpu_spike(self):
        baseline = {**self.base_baseline, "cpu_z_score": 3.2, "ram_z_score": 0.1}
        pred = {"predicted_cpu": {"trend": "rising_fast"}, "predicted_ram": {"trend": "stable"}}
        result = self.engine.classify(95, 50, baseline, pred)
        self.assertEqual(result["pattern_type"], "spike")
        self.assertEqual(result["resource"], "cpu")

    def test_t2_ram_spike(self):
        baseline = {**self.base_baseline, "cpu_z_score": 0.5, "ram_z_score": 2.5}
        pred = {"predicted_cpu": {"trend": "stable"}, "predicted_ram": {"trend": "rising_fast"}}
        result = self.engine.classify(30, 95, baseline, pred)
        self.assertEqual(result["pattern_type"], "spike")
        self.assertEqual(result["resource"], "memory")

    def test_t3_combined_spike(self):
        baseline = {**self.base_baseline, "cpu_z_score": 2.5, "ram_z_score": 2.2}
        pred = {"predicted_cpu": {"trend": "rising_fast"}, "predicted_ram": {"trend": "rising_fast"}}
        result = self.engine.classify(90, 90, baseline, pred)
        self.assertEqual(result["pattern_type"], "spike")
        self.assertEqual(result["resource"], "combined")

    def test_t4_ram_leak(self):
        baseline = {**self.base_baseline, "cpu_z_score": 0.1, "ram_z_score": 1.8}
        pred = {"predicted_cpu": {"trend": "stable"}, "predicted_ram": {"trend": "rising"}}
        result = self.engine.classify(40, 75, baseline, pred)
        self.assertEqual(result["pattern_type"], "leak")
        self.assertEqual(result["resource"], "memory")

    def test_t5_oscillation(self):
        # We need 3 sign changes. E.g. +, -, +, -
        z_scores = [1.5, -1.2, 1.3, -1.5]
        for z in z_scores:
            baseline = {**self.base_baseline, "cpu_z_score": z}
            result = self.engine.classify(50, 50, baseline, self.base_pred)
            
        self.assertEqual(result["pattern_type"], "oscillation")
        self.assertEqual(result["resource"], "combined")

    def test_t6_burst(self):
        # Tick 1: low
        baseline_low = {**self.base_baseline, "cpu_z_score": 0.2}
        self.engine.classify(50, 50, baseline_low, self.base_pred)
        
        # Tick 2: high
        baseline_high = {**self.base_baseline, "cpu_z_score": 2.8}
        result = self.engine.classify(90, 50, baseline_high, self.base_pred)
        self.assertEqual(result["pattern_type"], "burst")

    def test_t7_stable(self):
        baseline = {**self.base_baseline, "cpu_z_score": 1.2, "ram_z_score": 0.8}
        result = self.engine.classify(60, 60, baseline, self.base_pred)
        self.assertEqual(result["pattern_type"], "stable")

    def test_t8_not_enough_data(self):
        baseline = {**self.base_baseline, "cpu_z_score": 3.0, "window_fill": 0.05}
        result = self.engine.classify(90, 50, baseline, self.base_pred)
        self.assertEqual(result["pattern_type"], "stable")

if __name__ == '__main__':
    unittest.main()
