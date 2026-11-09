import json
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")


def evaluate(values, thresholds):
    alerts = []
    for sensor, rule in thresholds.items():
        value = values.get(sensor)
        if not isinstance(value, (int, float)):
            continue
        if "high" in rule and value > rule["high"]:
            alerts.append({"sensor": sensor, "value": value, "limit": rule["high"], "level": rule["level"], "action": rule["action"]})
        if "low" in rule and value < rule["low"]:
            alerts.append({"sensor": sensor, "value": value, "limit": rule["low"], "level": rule["level"], "action": rule["action"]})
    return alerts


def load_thresholds(path=CONFIG_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))["thresholds"]
