import subprocess
import glob
import os

resolved_patterns = [
    ("20260829T120007Z", "Verified by Antigravity on Outpost: gateway_probe.py returned Exit 0 with content."),
    ("20260829T185246Z", "Verified by Antigravity: 36% ratio is multi-block deduplication (6453 calls / 14986 lines = 36.05%)."),
    ("20260829T185245Z", "Verified by Claude and Antigravity: 13-route split preserved, Custom Domain flattening rejected."),
    ("20260829T185244Z", "Verified by Claude: 7-day report validated at 1.623B throughput (+35.6M delta)."),
    ("20260829T181552Z", "Verified by Antigravity: WhoArt disk recovered +14.47 GB, 24.04 GB free."),
    ("20260829T134704Z", "Verified by Antigravity: Blade 2.55 GB crash dump purged over SSH (22.07 GB free)."),
    ("20260829T133955Z", "Verified by Antigravity: Gateway probe verified with FLEET_KEY_OUTPOST (Exit 0)."),
]

acked = 0
for pattern, note in resolved_patterns:
    matches = glob.glob(f".handoffs/{pattern}*.json")
    for m in matches:
        bname = os.path.basename(m).replace(".json", "")
        print(f"--> Acking resolved leg: {bname} ...")
        cmd = ["python", "-m", "nougen_relay.cli", "ack", "--id", bname, "--state", "complete", "-m", note]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(res.stdout.strip() if res.stdout else res.stderr.strip())
        acked += 1

print(f"\nTotal legs acked in this sweep: {acked}")
