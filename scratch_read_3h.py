import os
import json
import glob
from datetime import datetime, timezone

cutoff = datetime(2026, 8, 29, 13, 30, tzinfo=timezone.utc)
handoff_files = glob.glob('.handoffs/*.json')

recent = []
for f in handoff_files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            ts_str = data.get('created_utc') or ''
            if ts_str:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                if ts >= cutoff:
                    data['_file'] = f
                    recent.append((ts, data))
    except Exception:
        pass

recent.sort(key=lambda x: x[0], reverse=True)
print(f"=== {len(recent)} LEGS SINCE 13:30 UTC ({len(recent)} found) ===\n")
for ts, r in recent:
    status = r.get('status', 'open')
    m = r.get('machine', '?')
    a = r.get('agent', '?')
    g = r.get('goal', '')
    ts_str = ts.strftime('%H:%M:%S UTC')
    print(f"[{ts_str}] ({status.upper()}) {m}/{a}")
    print(f"  Goal: {g}")
    print(f"  ID:   {r.get('id', '')}")
    
    md_file = r['_file'].replace('.json', '.md')
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as mfp:
            body_lines = [ln.strip() for ln in mfp if ln.strip() and not ln.startswith('#') and not ln.startswith('**')]
            if body_lines:
                snippet = " ".join(body_lines[:2])[:180]
                print(f"  Note: {snippet}")
    print("-" * 70)
