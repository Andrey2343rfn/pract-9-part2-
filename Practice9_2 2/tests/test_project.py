import json
import random
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sensors"))
sys.path.insert(0, str(ROOT / "edge"))
sys.path.insert(0, str(ROOT / "cloud"))

from patterns import generate_values
from rules import evaluate, load_thresholds
from analytics import aggregate, statistics


class SensorTests(unittest.TestCase):
    def test_six_sensors_generated(self):
        values, fault = generate_values(datetime(2026, 11, 9, tzinfo=timezone.utc), 0, random.Random(42))
        self.assertEqual(len(values), 6)
        self.assertIsNone(fault)
        self.assertGreater(values["rpm"], 1000)

    def test_fault_injection(self):
        rng = random.Random(2)
        observed = set()
        thresholds = load_thresholds()
        for _ in range(120):
            values, fault = generate_values(fault_rate=1.0, rng=rng)
            observed.add(fault)
            self.assertTrue(evaluate(values, thresholds))
        self.assertEqual(len(observed), 6)


class EdgeTests(unittest.TestCase):
    def test_normal_data_has_no_alerts(self):
        normal = {"vibration": 1.7, "bearing_temp": 55, "motor_current": 12, "rpm": 1500, "noise_db": 69, "pressure": 5}
        self.assertEqual(evaluate(normal, load_thresholds()), [])

    def test_high_temperature_turns_cooling_on(self):
        alerts = evaluate({"bearing_temp": 94.5}, load_thresholds())
        self.assertEqual(alerts[0]["action"], "cooling_on")

    def test_low_pressure_alert(self):
        alerts = evaluate({"pressure": 1.8}, load_thresholds())
        self.assertEqual(alerts[0]["level"], "critical")


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            {"timestamp": "2026-11-09T12:00:01+00:00", "values": {"vibration": 1, "bearing_temp": 50}},
            {"timestamp": "2026-11-09T12:00:30+00:00", "values": {"vibration": 3, "bearing_temp": 70}},
            {"timestamp": "2026-11-09T12:01:01+00:00", "values": {"vibration": 2, "bearing_temp": 60}},
        ]

    def test_stats(self):
        self.assertEqual(statistics(self.events)["bearing_temp"]["average"], 60)

    def test_minute_aggregation(self):
        groups = aggregate(self.events, "minute")
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0]["count"], 2)

    def test_bad_bucket(self):
        with self.assertRaises(ValueError):
            aggregate(self.events, "second")


if __name__ == "__main__":
    unittest.main()
