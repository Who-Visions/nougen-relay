# 🤝 Git Handoff — claude-app / g-nougenai

**Goal**: Suppress RelayLive Git popups with hidden subprocesses and single background worker
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:34:41.673Z

---
## Change
- `tools/relay_live.py` Git subprocess now uses Windows `CREATE_NO_WINDOW` dynamically.
- `.nougen/relay_live.cmd` uses `pythonw.exe`.

## Verification
- RelayLive tests: 8 passed.
- Removed duplicate RelayLive workers; one clean `pythonw.exe --daemon --quiet` remains (PID 248932, window handle 0).
- No NouGen `tail -f` followers remain.

## Boundary
- No unrelated terminals or services stopped.
