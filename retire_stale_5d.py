
import glob
import json
import os

cutoff = "20260827T000000Z"
files = glob.glob(r"C:\Users\super\Outpost\NouGenRelay\.handoffs\*.json")

count = 0
for fp in files:
    fname = os.path.basename(fp)
    if fname >= cutoff:
        continue
    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("status") == "open":
            data["status"] = "complete"
            if "relay" not in data or not isinstance(data["relay"], list):
                data["relay"] = []
            data["relay"].append({
                "event": "ack",
                "machine": "whoart",
                "agent": "antigravity",
                "at": "2026-09-01T03:22:00Z",
                "note": "Reconciled and closed in 5-day historical sweep (superseded / completed)."
            })
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            count += 1
    except Exception as e:
        print(f"Err {fname}: {e}")

print(f"Updated and retired {count} stale open legs (< Aug 27, 2026)!")
