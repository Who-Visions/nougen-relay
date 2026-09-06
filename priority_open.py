import glob
import json
import os

legs = []
for f in sorted(glob.glob('.handoffs/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    if d.get('status', 'open') != 'open':
        continue
    bname = os.path.basename(f).replace('.json', '')
    goal = d.get('goal', '')
    source = bname.split('__')[1] if '__' in bname else '?'
    agent = bname.split('__')[2] if bname.count('__') >= 2 else '?'
    ts = bname.split('__')[0] if '__' in bname else bname
    
    # Priority classification
    g = goal.upper()
    if 'P1' in g or 'CRITICAL' in g or 'ESCALATION' in g:
        pri = 0  # P1
    elif 'TRUE ROOT CAUSE' in g or 'ROOT CAUSE' in g or 'INCIDENT RESOLVED' in g:
        pri = 1  # Root cause / resolution
    elif 'FIXED' in g or 'RESTORED' in g or 'SOLVED' in g or 'CLOSED' in g or 'CORRECTION' in g:
        pri = 2  # Fix applied / correction
    elif goal.startswith('TODO:'):
        pri = 3  # Actionable TODO
    elif 'IN FLIGHT' in g or 'RETRACTION' in g:
        pri = 4  # In-flight work
    elif 'Architecture' in goal or 'directive' in goal.lower():
        pri = 5  # Architecture directive
    else:
        pri = 6  # Research / canon / other
    
    legs.append((pri, ts, bname, goal[:160], source, agent))

legs.sort()
pri_labels = {0: 'P1 / CRITICAL', 1: 'ROOT CAUSE', 2: 'FIX APPLIED', 3: 'TODO', 4: 'IN FLIGHT', 5: 'DIRECTIVE', 6: 'OTHER'}

current_pri = -1
for pri, ts, bname, goal, source, agent in legs:
    if pri != current_pri:
        current_pri = pri
        label = pri_labels.get(pri, '?')
        print(f"\n{'='*80}")
        print(f"  [{label}]")
        print(f"{'='*80}")
    print(f"  {bname}")
    print(f"    {source}/{agent}")
    print(f"    {goal}")
    print()

print(f"\nTotal open: {len(legs)}")
