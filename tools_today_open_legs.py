import glob
import json

files = sorted(glob.glob(".handoffs/*.json"), reverse=True)
today_legs = []

for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            if data.get("status") == "open" and "20260829" in data.get("id", ""):
                today_legs.append(data)
    except Exception:
        pass

print("======================================================================")
print(f"ACTIVE OPEN RELAY LEGS FROM TODAY (2026-08-29): {len(today_legs)} total")
print("======================================================================\n")

for leg in today_legs:
    lid = leg.get("id", "unknown")
    machine = leg.get("machine", "unknown")
    agent = leg.get("agent", "unknown")
    goal = leg.get("goal", "no goal")
    created = leg.get("created_utc", "unknown")
    print(f"* [{lid}] | {machine}/{agent}")
    print(f"  Goal: {goal}")
    print(f"  When: {created}")
    print()
