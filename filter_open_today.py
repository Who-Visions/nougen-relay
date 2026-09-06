import glob
import json
import os

legs = sorted(glob.glob('.handoffs/20260830*.json'))
open_count = 0
acked_count = 0
complete_count = 0

for f in legs:
    d = json.load(open(f))
    s = d.get('status', 'open')
    bname = os.path.basename(f).replace('.json', '')
    goal = d.get('goal', '')[:150]
    
    if s == 'open':
        open_count += 1
        print(f"[OPEN] {bname}")
        print(f"  {goal}")
        print()
    elif s == 'acked':
        acked_count += 1
    elif s == 'complete':
        complete_count += 1

print(f"\n--- SUMMARY: {len(legs)} total today | {open_count} OPEN | {acked_count} ACKED | {complete_count} COMPLETE ---")
