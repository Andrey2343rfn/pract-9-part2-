from datetime import datetime, timezone

SENSORS = ("vibration", "bearing_temp", "motor_current", "rpm", "noise_db", "pressure")


def statistics(events):
    result = {}
    for sensor in SENSORS:
        values = [e["values"][sensor] for e in events if sensor in e.get("values", {})]
        result[sensor] = {
            "average": round(sum(values) / len(values), 2) if values else None,
            "minimum": round(min(values), 2) if values else None,
            "maximum": round(max(values), 2) if values else None,
        }
    return result


def aggregate(events, period="minute"):
    fmt = {"minute": "%Y-%m-%dT%H:%M", "hour": "%Y-%m-%dT%H", "day": "%Y-%m-%d"}.get(period)
    if fmt is None:
        raise ValueError("period must be minute, hour or day")
    groups = {}
    for event in events:
        timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        bucket = timestamp.astimezone(timezone.utc).strftime(fmt)
        groups.setdefault(bucket, []).append(event)
    return [{"time": key, "count": len(items), "sensors": statistics(items)} for key, items in sorted(groups.items())]
