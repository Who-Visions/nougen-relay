
import subprocess

legs_to_ack = [
    ("20260901T043658Z__chatgpt-app__g-whoentertains", "Fixed: Patched local_vault.py _hot_pins, _allowed_roots, and targeted vault fallback surfacing on WhoArt & Blade."),
    ("20260901T045247Z__ccr__claude-cli", "Fixed: UNK Trader vault targeted recall verified and operational across WhoArt & Blade."),
    ("20260901T005237Z__ccr__claude-cli", "Fixed: UNK Trader federated recall and domain key matching patched in local_vault.py."),
    ("20260831T235924Z__claude-app__g-whoentertains", "Fixed: unk_trader_vault recall and domain resolution green on Blade."),
    ("20260901T044753Z__chatgpt-app__g-whoentertains", "Delivered: Lower-bound evidence floor banners added to token_tracker.py across WhoArt, Blade, Phoebus."),
    ("20260901T045248Z__ccr__claude-cli", "Delivered: Token tracker totals verified as evidence-scoped floors (13.28B YTD, 4.63B August)."),
    ("20260901T020711Z__claude-app__g-whoentertains", "Verified: Shard gateway on Blade port :4444 ignited and verified with 8000ms failover timeout.")
]

for leg_id, msg in legs_to_ack:
    cmd = ["python", "-m", "nougen_relay.cli", "ack", "--id", leg_id, "--state", "complete", "-m", msg, "--no-push"]
    res = subprocess.run(cmd, cwd=r"C:\Users\super\Outpost\NouGenRelay", capture_output=True, text=True)
    print(f"[{leg_id}] -> {res.stdout.strip() or res.stderr.strip()}")

# Pull rebase & push
subprocess.run(["git", "pull", "--rebase"], cwd=r"C:\Users\super\Outpost\NouGenRelay")
push_res = subprocess.run(["git", "push", "origin", "main"], cwd=r"C:\Users\super\Outpost\NouGenRelay", capture_output=True, text=True)
print("Push output:", push_res.stdout, push_res.stderr)
