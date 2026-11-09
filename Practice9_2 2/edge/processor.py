import json
import os
import signal
import sqlite3
import threading
import time
from collections import deque
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from rules import evaluate, load_thresholds


class EdgeProcessor:
    def __init__(self):
        self.lock = threading.RLock()
        self.running = True
        self.thresholds = load_thresholds()
        self.history = deque(maxlen=120)
        self.db = sqlite3.connect(os.getenv("EDGE_DB", "/app/data/edge.db"), check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS pending (event_id TEXT PRIMARY KEY, payload TEXT NOT NULL, created REAL NOT NULL)")
        self.db.commit()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="practice92-edge")
        self.client.reconnect_delay_set(min_delay=1, max_delay=15)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.influx = InfluxDBClient(url=os.getenv("INFLUX_URL", "http://influxdb:8086"), token=os.getenv("INFLUX_TOKEN", ""), org=os.getenv("INFLUX_ORG", "college-lab"), timeout=1500)
        self.bucket = os.getenv("INFLUX_BUCKET", "smart_factory")
        self.org = os.getenv("INFLUX_ORG", "college-lab")
        self.paused = False
        self.last_sent = 0.0
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def stop(self, *_):
        self.running = False

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe([("sensors/factory/telemetry", 1), ("cloud/ack", 1), ("cloud/commands", 1)])
            print("EDGE connected to MQTT", flush=True)

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            if message.topic == "sensors/factory/telemetry":
                self.process(payload)
            elif message.topic == "cloud/ack":
                event_id = str(payload.get("event_id", ""))
                with self.lock:
                    self.db.execute("DELETE FROM pending WHERE event_id=?", (event_id,))
                    self.db.commit()
            elif message.topic == "cloud/commands":
                self.command(payload)
        except (ValueError, KeyError, TypeError, sqlite3.Error) as exc:
            print(f"EDGE input error: {exc}", flush=True)

    def command(self, payload):
        name = payload.get("command")
        if name not in {"stop_line", "start_line", "cooling_on", "cooling_off"}:
            return
        with self.lock:
            if name == "stop_line":
                self.paused = True
            elif name == "start_line":
                self.paused = False
        result = {"command_id": payload.get("command_id"), "command": name, "timestamp": datetime.now(timezone.utc).isoformat(), "status": "executed", "line_paused": self.paused}
        self.client.publish("edge/actions", json.dumps(result), qos=1)
        print(f"EDGE CLOUD COMMAND {name}: executed", flush=True)

    def process(self, data):
        started = time.perf_counter()
        event_id = str(data["event_id"])
        values = data["values"]
        if not isinstance(values, dict) or not all(isinstance(v, (float, int)) for v in values.values()):
            raise ValueError("invalid sensor values")
        alerts = evaluate(values, self.thresholds)
        if len(self.history) >= 5:
            avg = sum(item["bearing_temp"] for item in self.history if "bearing_temp" in item) / len(self.history)
            if values.get("bearing_temp", 0) > avg + 30 and not any(a["sensor"] == "bearing_temp" for a in alerts):
                alerts.append({"sensor": "bearing_temp", "value": values["bearing_temp"], "limit": round(avg + 30, 2), "level": "warning", "action": "inspect_temperature_trend"})
        self.history.append(values)
        out = dict(data)
        out["alerts"] = alerts
        out["edge_processed_at"] = datetime.now(timezone.utc).isoformat()
        out["edge_latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
        with self.lock:
            self.db.execute("INSERT OR IGNORE INTO pending VALUES (?, ?, ?)", (event_id, json.dumps(out), time.time()))
            self.db.commit()
            count = self.db.execute("SELECT COUNT(*) FROM pending").fetchone()[0]
        for alert in alerts:
            self.client.publish("actuators/factory", json.dumps({"device_id": data["device_id"], "action": alert["action"], "sensor": alert["sensor"], "timestamp": out["edge_processed_at"]}), qos=1)
            print(f"EDGE ALERT {alert['sensor']}={alert['value']} action={alert['action']}", flush=True)
            if alert["action"] == "stop_line":
                self.paused = True
        if alerts or count % 10 == 0:
            print(f"EDGE processed={event_id[:8]} latency={out['edge_latency_ms']}ms pending={count} alerts={len(alerts)}", flush=True)
        try:
            record = Point("edge_measurements").tag("device", data["device_id"])
            for name, value in values.items():
                record = record.field(name, float(value))
            record = record.time(data["timestamp"], WritePrecision.NS)
            with self.influx.write_api() as writer:
                writer.write(bucket=self.bucket, org=self.org, record=record)
        except Exception as exc:
            print(f"EDGE Influx unavailable: {exc}", flush=True)

    def resend_pending(self):
        now = time.time()
        if now - self.last_sent < 3:
            return
        self.last_sent = now
        with self.lock:
            batch = self.db.execute("SELECT payload FROM pending ORDER BY created LIMIT 120").fetchall()
        for (payload,) in batch:
            self.client.publish("cloud/upload", payload, qos=1)
        if batch:
            print(f"EDGE sync attempted={len(batch)}", flush=True)

    def run(self):
        self.client.connect_async(os.getenv("MQTT_HOST", "mqtt-broker"), 1883)
        self.client.loop_start()
        try:
            while self.running:
                self.resend_pending()
                time.sleep(0.5)
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            self.influx.close()
            self.db.close()


if __name__ == "__main__":
    EdgeProcessor().run()
