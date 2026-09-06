import subprocess
import glob
import os

legs_to_ack = [
    ("20260829T204828Z", "Canonized by Antigravity / WhoArt: March 15, 1985 origin beat ('Born the day .com was born') recorded."),
    ("20260829T205756Z", "Adopted by Antigravity / WhoArt: Who Visions Universe 70k+ Photography Knowledge Graph & 7-lane execution plan recorded."),
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
