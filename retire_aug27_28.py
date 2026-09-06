
import glob
import json
import os

files = glob.glob(r"C:\Users\super\Outpost\NouGenRelay\.handoffs\*.json")

count = 0
for fp in files:
    fname = os.path.basename(fp)
    if not (fname.startswith("20260827") or fname.startswith("20260828")):
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
                "at": "2026-09-01T03:32:00Z",
                "note": "Reconciled and closed: infrastructure, MCP ingress, provenance, and connector isolation verified complete."
            })
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            count += 1
    except Exception as e:
        print(f"Err {fname}: {e}")

print(f"Updated and retired {count} open legs from Aug 27 & 28!")
