# The relay watcher (`tools/relay_daemon.py`)

The relay itself has no daemon. That is not a caveat in the README, it is the
design: legs travel through git, and a clone that never runs a background
process still sees every baton. Nothing here changes that.

This is a **watcher**, and it is optional. It runs on one machine, reads the
legs that machine can already see, and answers a question the protocol
deliberately does not: *is anyone actually picking these up?* A leg can sit open
for a day because every lane that could take it was asleep. Git will not tell
you that. This will.

## What it does each cycle

1. Pulses local Ollama for health and latency (zero cloud cost).
2. Reads `.handoffs/*.json` straight off disk — no `nougen_shards` import, so it
   runs in a bare clone.
3. Flags legs whose age exceeds the lag threshold.
4. Triages the lagging ones with a local model, and optionally dispatches a
   vetted status action to the AGY CLI.
5. Writes pulses, lag alerts, and triage events to a SQLite ledger.

## Running it

```bash
python tools/relay_daemon.py --once --dry-run   # one cycle, nothing dispatched
python tools/relay_daemon.py --status           # ledger + live Ollama check
python tools/relay_daemon.py --daemon           # continuous
```

**One daemon per state DB.** They share a SQLite ledger, so two live watchers
double every lag alert and each triages legs the other already handled. The
daemon takes an exclusive lock beside its DB (`<db>.lock`, created with
`O_CREAT|O_EXCL`) and a second start exits `3` rather than joining in. A lock
whose PID is dead — the shape a hard kill leaves behind — is reclaimed on the
next start, so a crash never wedges the watcher. `--force` overrides, and is
almost never what you want.

Because a second start is refused cheaply and a crashed one is reclaimed
automatically, a scheduled task that simply runs `--daemon` every few minutes is
a working watchdog: it restarts a dead watcher and no-ops against a live one.

## Configuration

Every path, port, and model resolves at runtime — env first, then discovery,
with a constant only as a logged fallback. Nothing machine-specific is baked in.

| Variable | Default |
|---|---|
| `NOUGEN_RELAY_DIR` | this repo, or `<watchtower>/NouGen/NouGenRelay` |
| `NOUGEN_WATCHTOWER_ROOT` | walked up from the script's own path |
| `NOUGEN_DAEMON_DB` | `<watchtower>/Sol-Ai/relay_daemon_state.db` |
| `NOUGEN_DAEMON_MODEL` | `dav1d:e2b` |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` (`0.0.0.0` is rewritten to loopback — it is a bind address, not a destination) |
| `NOUGEN_AGY_BIN` | `agy`, resolved on `PATH` |
| `NOUGEN_AGY_TIMEOUT_SEC` | `60` |
| `NOUGEN_MACHINE` | `COMPUTERNAME` / hostname |

## Dispatch safety

Triage output is model-written text, so it never reaches a shell. The dispatcher
resolves the AGY binary on `PATH`, builds an argv list from a fixed set of
read-only subcommands (`--version`, `status`, `mcp list`), and runs it without
`shell=True`. A missing binary returns exit `127` instead of raising, and
`--dry-run` never spawns a process at all.

## Tests

`tests/test_relay_daemon.py` covers the lock (concurrent starts, stale reclaim,
corrupt lock file, foreign-holder release), dynamic path resolution, lag
measurement, and the dispatch guards.
