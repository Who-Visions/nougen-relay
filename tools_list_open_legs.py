import glob
import json

files = sorted(glob.glob(".handoffs/*.json"), reverse=True)
open_legs = []

for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            if data.get("status") == "open":
                open_legs.append(data)
    except Exception:
        pass

print("======================================================================")
print(f"CURRENT OPEN RELAY LEGS ({len(open_legs)} total)")
print("======================================================================\n")

for leg in open_legs:
    lid = leg.get("id", "unknown")
    machine = leg.get("machine", "unknown")
    agent = leg.get("agent", "unknown")
    goal = leg.get("goal", "no goal")
    created = leg.get("created_utc", "unknown")
    print(f"* [{lid}] | {machine}/{agent}")
    print(f"  Goal: {goal}")
    print(f"  When: {created}")
    print()
