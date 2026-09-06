import subprocess
import glob
import os

legs_to_ack = [
    ("20260829T204154Z", "Adopted by Antigravity / WhoArt: 'parallelogram your work' codified as concurrent orchestration grammar."),
    ("20260829T204503Z", "Verified by Antigravity / WhoArt: https://aiwithdav3.com and www.aiwithdav3.com both answer HTTP 200 (Next.js body verified)."),
]

for pattern, note in legs_to_ack:
    matches = glob.glob(f".handoffs/{pattern}*.json")
    for m in matches:
        bname = os.path.basename(m).replace(".json", "")
        print(f"--> Acking: {bname} ...")
        cmd = ["python", "-m", "nougen_relay.cli", "ack", "--id", bname, "--state", "complete", "-m", note]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print("Result:", res.returncode)

subprocess.run(["git", "push", "origin", "main"])
print("Pushed to main.")
