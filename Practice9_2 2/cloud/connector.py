import json
import os
import signal
import sqlite3
import threading
from datetime import datetime, timezone
from uuid import uuid4

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient, Point, WritePrecision
from analytics import SENSORS, aggregate, statistics


class Cloud:
    def __init__(self):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(os.getenv("CLOUD_DB", "/app/data/cloud.db"), check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, timestamp TEXT, payload TEXT NOT NULL, committed INTEGER NOT NULL DEFAULT 0)")
        self.db.execute("CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, payload TEXT NOT NULL)")
        self.db.commit()
        self.influx = InfluxDBClient(url=os.getenv("INFLUX_URL", "http://influxdb:8086"), token=os.getenv("INFLUX_TOKEN", ""), org=os.getenv("INFLUX_ORG", "college-lab"), timeout=3000)
        self.bucket = os.getenv("INFLUX_BUCKET", "smart_factory")
        self.org = os.getenv("INFLUX_ORG", "college-lab")
        self.mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="practice92-cloud")
        self.mqtt.reconnect_delay_set(min_delay=1, max_delay=15)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message
        self.mqtt.connect_async(os.getenv("MQTT_HOST", "mqtt-broker"), 1883)
        self.mqtt.loop_start()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe([("cloud/upload", 1), ("edge/actions", 1)])
            print("CLOUD connected to MQTT", flush=True)

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            if message.topic == "cloud/upload":
                self.store(payload)
            elif message.topic == "edge/actions":
                with self.lock:
                    self.db.execute("INSERT INTO actions(timestamp, payload) VALUES (?,?)", (payload.get("timestamp", ""), json.dumps(payload)))
                    self.db.commit()
                print(f"CLOUD action received {payload.get('command')}", flush=True)
        except Exception as exc:
            print(f"CLOUD message error: {exc}", flush=True)

    def store(self, event):
        event_id = str(event["event_id"])
        values = event["values"]
        if not all(sensor in values and isinstance(values[sensor], (int, float)) for sensor in SENSORS):
            raise ValueError("invalid measurements")
        with self.lock:
            self.db.execute("INSERT OR IGNORE INTO events(event_id, timestamp, payload) VALUES (?,?,?)", (event_id, event["timestamp"], json.dumps(event)))
            self.db.commit()
            existing = self.db.execute("SELECT committed FROM events WHERE event_id=?", (event_id,)).fetchone()
        if existing[0] == 0:
            record = Point("cloud_measurements").tag("device", str(event["device_id"])).tag("event_id", event_id)
            for sensor, value in values.items():
                record = record.field(sensor, float(value))
            record = record.field("alert_count", len(event.get("alerts", [])))
            record = record.field("edge_latency_ms", float(event.get("edge_latency_ms", 0)))
            record = record.time(event["timestamp"], WritePrecision.NS)
            with self.influx.write_api() as writer:
                writer.write(bucket=self.bucket, org=self.org, record=record)
            with self.lock:
                self.db.execute("UPDATE events SET committed=1 WHERE event_id=?", (event_id,))
                self.db.commit()
            if event.get("alerts"):
                print(f"CLOUD stored {event_id[:8]} with {len(event['alerts'])} alerts", flush=True)
        self.mqtt.publish("cloud/ack", json.dumps({"event_id": event_id}), qos=1)

    def events(self, limit=120, committed_only=True):
        with self.lock:
            clause = "WHERE committed=1" if committed_only else ""
            rows = self.db.execute(f"SELECT payload FROM events {clause} ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row[0]) for row in reversed(rows)]

    def counts(self):
        with self.lock:
            stored = self.db.execute("SELECT COUNT(*) FROM events WHERE committed=1").fetchone()[0]
            pending = self.db.execute("SELECT COUNT(*) FROM events WHERE committed=0").fetchone()[0]
        return stored, pending

    def actions(self, limit=30):
        with self.lock:
            rows = self.db.execute("SELECT payload FROM actions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row[0]) for row in rows]


cloud = Cloud()
app = Flask(__name__)


@app.get("/api/health")
def health():
    stored, pending = cloud.counts()
    return jsonify({"status": "ok", "stored_events": stored, "awaiting_influx": pending})


@app.get("/api/summary")
def summary():
    events = cloud.events(500)
    stored, pending = cloud.counts()
    latest = events[-1] if events else None
    return jsonify({"events": stored, "pending_cloud": pending, "latest": latest, "stats": statistics(events), "alerts_recent": sum(len(e.get("alerts", [])) for e in events), "edge_latency_ms": round(sum(e.get("edge_latency_ms", 0) for e in events) / len(events), 3) if events else None, "last_update": latest["timestamp"] if latest else None})


@app.get("/api/history")
def history():
    limit = max(1, min(2000, request.args.get("limit", 120, type=int)))
    return jsonify(cloud.events(limit))


@app.get("/api/aggregate")
def aggregated():
    period = request.args.get("period", "minute")
    if period not in {"minute", "hour", "day"}:
        return jsonify({"error": "unsupported period"}), 400
    return jsonify(aggregate(cloud.events(2000), period))


@app.get("/api/alerts")
def alerts():
    events = cloud.events(500)
    items = []
    for e in reversed(events):
        for alert in e.get("alerts", []):
            items.append({"timestamp": e["timestamp"], "device_id": e["device_id"], **alert})
    return jsonify(items[:60])


@app.get("/api/actions")
def actions():
    return jsonify(cloud.actions())


@app.post("/api/commands")
def command():
    data = request.get_json(silent=True) or {}
    name = data.get("command")
    if name not in {"stop_line", "start_line", "cooling_on", "cooling_off"}:
        return jsonify({"error": "unsupported command"}), 400
    message = {"command_id": str(uuid4()), "command": name, "timestamp": datetime.now(timezone.utc).isoformat()}
    result = cloud.mqtt.publish("cloud/commands", json.dumps(message), qos=1)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        return jsonify({"error": "broker unavailable"}), 503
    return jsonify({"status": "sent", **message}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
