import subprocess
import glob
import os

legs_to_ack = [
    ("20260829T220523Z", "Adopted by Antigravity / WhoArt: 'Recurse this into a skill' maturity ladder codified."),
    ("20260829T220707Z", "Adopted by Antigravity / WhoArt: 'Recurse that shit' meta-primitive context routing codified."),
]

for pattern, note in legs_to_ack:
    matches = glob.glob(f".handoffs/{pattern}*.json")
    for m in matches:
        bname = os.path.basename(m).replace(".json", "")
        print(f"--> Acking: {bname} ...")
        cmd = ["python", "-m", "nougen_relay.cli", "ack", "--id", bname, "--state", "complete", "-m", note]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print("Result:", res.returncode)

subprocess.run(["git", "pull", "--rebase", "origin", "main"])
subprocess.run(["git", "push", "origin", "main"])
print("Pushed to main.")
