from datetime import datetime, timezone
from math import pi, sin
import random


def generate_values(when=None, fault_rate=0.10, rng=None):
    when = when or datetime.now(timezone.utc)
    rng = rng or random.Random()
    hour = when.hour + when.minute / 60
    daily = sin(2 * pi * (hour - 7) / 24)
    weekday = 1 if when.weekday() < 5 else -1
    load = 0.60 + 0.12 * daily + 0.08 * weekday
    values = {
        "vibration": round(1.1 + 0.65 * load + rng.gauss(0, 0.13), 2),
        "bearing_temp": round(44 + 14 * load + rng.gauss(0, 1.5), 2),
        "motor_current": round(8.0 + 6.5 * load + rng.gauss(0, 0.45), 2),
        "rpm": round(1520 - 45 * load + rng.gauss(0, 22), 2),
        "noise_db": round(61 + 13 * load + rng.gauss(0, 1.5), 2),
        "pressure": round(5.4 - 0.5 * load + rng.gauss(0, 0.15), 2),
    }
    fault = None
    if rng.random() < fault_rate:
        fault = rng.choice(["overheat", "vibration", "motor", "pressure", "overload", "noise"])
        if fault == "overheat":
            values["bearing_temp"] = round(rng.uniform(85, 103), 2)
        elif fault == "vibration":
            values["vibration"] = round(rng.uniform(3.7, 5.2), 2)
        elif fault == "motor":
            values["rpm"] = round(rng.uniform(650, 870), 2)
        elif fault == "pressure":
            values["pressure"] = round(rng.uniform(1.2, 2.1), 2)
        elif fault == "overload":
            values["motor_current"] = round(rng.uniform(20, 24), 2)
        else:
            values["noise_db"] = round(rng.uniform(89, 105), 2)
    return values, fault
