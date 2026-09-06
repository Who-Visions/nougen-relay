import subprocess
import glob
import os

legs_to_ack = [
    ("20260829T213215Z", "Adopted by Antigravity / WhoArt: Kirby Ferguson Protocol (NouGen Recursive Remix Loop) canonized."),
    ("20260829T213834Z", "Verified by Antigravity / WhoArt: Space inference router live on nougenai/NouGenShards (commit 37ad025), Kimi-K3 5.5s, 500 cleared."),
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
