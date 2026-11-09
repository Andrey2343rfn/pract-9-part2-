from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import random
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sensors"))
sys.path.insert(0, str(ROOT / "edge"))
from patterns import generate_values
from rules import evaluate, load_thresholds

rng = random.Random(92)
start = datetime(2026, 9, 1, tzinfo=timezone.utc)
thresholds = load_thresholds()
rows = []
latencies = []
for i in range(2016):
    ts = start + timedelta(minutes=5 * i)
    values, fault = generate_values(ts, fault_rate=0.10, rng=rng)
    t = time.perf_counter()
    alerts = evaluate(values, thresholds)
    latency_ms = 1000 * (time.perf_counter() - t)
    latencies.append(latency_ms)
    rows.append({"timestamp": ts.isoformat(), "values": values, "fault": fault, "alerts": alerts})
positives = sum(bool(r["fault"]) for r in rows)
tp = sum(bool(r["fault"]) and bool(r["alerts"]) for r in rows)
fp = sum(not r["fault"] and bool(r["alerts"]) for r in rows)
fn = positives - tp
precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0
metrics = {
    "verification_scope": "Pure functions only, no Docker/MQTT/Cloud runtime in this environment",
    "synthetic_samples": len(rows),
    "synthetic_faults": positives,
    "rule_true_positives": tp,
    "rule_false_positives": fp,
    "rule_false_negatives": fn,
    "rule_precision": precision,
    "rule_recall": recall,
    "rule_latency_mean_ms": statistics.mean(latencies),
    "rule_latency_p95_ms": sorted(latencies)[int(0.95 * len(latencies))],
}
(ROOT / "artifacts" / "local_validation.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

plt.rcParams.update({"font.size": 9})
fig, ax = plt.subplots(figsize=(10.2, 3.5))
xs = list(range(420))
temps = [r["values"]["bearing_temp"] for r in rows[:420]]
ax.plot(xs, temps, linewidth=1.25, color="#2a78a5", label="Температура підшипника")
red_x=[i for i in xs if rows[i]["fault"]=="overheat"]
ax.scatter(red_x, [temps[i] for i in red_x], color="#d24e55", s=18, label="Перегрів",zorder=3)
ax.axhline(82, linestyle="--", linewidth=1.2, color="#d98c32", label="Поріг 82°C")
ax.set(xlabel="Номер вимірювання (кожні 5 хв)",ylabel="°C",title="Штучні дані датчиків: температура та аномалії")
ax.grid(alpha=0.2)
ax.legend(ncol=3,fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(ROOT / "docs" / "chart_temperature.png", dpi=170)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9,3.6))
counts = [sum(bool(row["fault"]==f) for row in rows) for f in ["overheat","vibration","motor","pressure","overload","noise"]]
labels=["Перегрів","Вібрація","Двигун","Тиск","Струм","Шум"]
bars=ax.bar(labels,counts,color=["#3b6b99","#5387a9","#6b9ab9","#83b7a6","#d1a26c","#b87981"])
for bar, count in zip(bars,counts):
    ax.text(bar.get_x()+bar.get_width()/2,count+.5,str(count),ha="center",va="bottom",fontsize=9)
ax.set(ylabel="Кількість",title="Структура змодельованих несправностей")
ax.grid(axis="y",alpha=0.15)
fig.tight_layout()
fig.savefig(ROOT / "docs" / "chart_faults.png",dpi=170)
plt.close(fig)
print(json.dumps(metrics, indent=2))
