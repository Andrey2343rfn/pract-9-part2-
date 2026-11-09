import json
import os
import random
import signal
import time
from datetime import datetime, timezone
from uuid import uuid4

import paho.mqtt.client as mqtt
from patterns import generate_values


class Simulator:
    def __init__(self):
        self.host = os.getenv("MQTT_HOST", "localhost")
        self.interval = max(0.2, float(os.getenv("SENSOR_INTERVAL", "2")))
        self.fault_rate = min(1.0, max(0.0, float(os.getenv("FAULT_RATE", "0.10"))))
        self.device = os.getenv("DEVICE_ID", "factory-line-01")
        self.running = True
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor-" + self.device)
        self.client.reconnect_delay_set(min_delay=1, max_delay=15)
        self.rng = random.Random()
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def stop(self, *_):
        self.running = False

    def run(self):
        self.client.connect_async(self.host, int(os.getenv("MQTT_PORT", "1883")))
        self.client.loop_start()
        index = 0
        try:
            while self.running:
                now = datetime.now(timezone.utc)
                values, fault = generate_values(now, self.fault_rate, self.rng)
                payload = {
                    "event_id": str(uuid4()),
                    "device_id": self.device,
                    "timestamp": now.isoformat(),
                    "values": values,
                    "fault": fault,
                }
                info = self.client.publish("sensors/factory/telemetry", json.dumps(payload), qos=1)
                index += 1
                if index % 5 == 0 or fault:
                    print(f"SENSOR {index} fault={fault or 'normal'} mqtt={info.rc} temp={values['bearing_temp']} vibration={values['vibration']}", flush=True)
                time.sleep(self.interval)
        finally:
            self.client.loop_stop()
            self.client.disconnect()


if __name__ == "__main__":
    Simulator().run()
