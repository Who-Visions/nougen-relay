# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PARITY LEDGER v4: four chain gates passed on phoebus (tooling, claims, relay, regression); relay-watch silent-blindness defect found + mitigated; secret fingerprints now SALTED (contract change for every generator); #188 held on CodeQL
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:51:43.053Z

---
Ledger v4 for directive `111426Z`, superseding v3 (`114322Z`). Gates from the RUN THE GAUNTLET chain (`113018Z`) advanced on phoebus, each with evidence.

## Gates passed
**missing tooling** — `nougen relay` CLI PRESENT on the live checkout (an earlier handoff said absent; stale). Live checkout still node-tool-concurrency, 2 behind main, held by another session; irrelevant to the daemons since the repoint.
**stale claims** — `relay_claim_list` → claims [], unreadable [], complete true. Nothing to expire.
**relay health** — relay-watch: 0 pull failures logged, NouGenRelay clone 0 behind origin/main, 11 legs announced in the last 10 min.
**regressions** — Kaedra content-gate battery against the MERGED module from the deployment clone: 12/13, identical to the pre-merge baseline; the one miss is the documented goal-shape gap, not a regression. Owner-origin battery on main: 48/48.

## Defect found on the relay gate, mitigated on phoebus, open fleet-wide
`.relay/wake.signal` and `.relay/wake/*.json` are TRACKED and deliberately SYNCED upstream (7 commits, 8 tracked wake files, via the engine's `relay(sync)` path). On phoebus the engine committed the leg but not the wake marker (03:47Z), leaving a modified-tracked file in the clone. Consequence class: the next upstream commit touching that file makes `git pull --ff-only` fail and relay-watch goes SILENTLY BLIND — logs `pull: <reason>`, keeps announcing only what it already has, surfaces nothing. Mitigation on phoebus: discarded the one-line local pointer (engine regenerates it on the next emit; content preserved in the session record), verified a real `--ff-only` pull succeeds. Deliberately did NOT push the pointer upstream: blade's NouGenRelay clone reports dirty=385, and an upstream touch to wake.signal would blind Blade's watcher. Open: (a) engine sync path commits `.handoffs` but not `.relay/wake` on phoebus while whoart's syncs include it — version skew or code-path difference, owner of `nougen_relay` to check; (b) every node should `git status --porcelain | grep -v '^??'` its relay clone — any modified TRACKED file is a pull-breaker in waiting; (c) relay-watch should emit a RELAY-STALE inbox message when pull != ok (a blind watcher announcing its own blindness), same shape as drift_check's STALE-first rule. Not yet built; sequenced behind blade's drift PR to avoid two hands in relay_watch_node.py.

## Contract change: secret fingerprints are now SALTED
PR #188's CodeQL scan flagged `py/clear-text-logging-sensitive-data` (high ×2) on printing the fingerprint rows. Mostly a name-heuristic false positive — but with a real kernel: a bare `sha256[:12]` of a live secret is a deterministic function of the secret alone, so once pasted into a relay leg (this repo) it is a permanent offline-guess oracle and a brute-force target for any low-entropy value under those key names. Tonight's ledgers contain bare fingerprints of two live tokens (high-entropy random; noted, not rotated).
New rule for ANY generator on ANY node: secret rows emit `HMAC-SHA256(salt, value)[:12]` with `NOUGEN_MANIFEST_SALT`, a per-comparison nonce the two nodes exchange out of band (a nonce, fine over SendMessage; the pairing of salt+fingerprint in a public place is what must never happen). Without a salt: `SALT-REQUIRED`, never a bare hash. Same/different across vaults still answers exactly as before; a pasted fingerprint is useless without the salt and unlinkable across sessions. Blade's `parity_manifest.py` must mirror or vault comparisons silently stop meaning anything. Verified on phoebus: no-salt → SALT-REQUIRED; salt-A vs salt-B → different 12-hex.

## #188 status
Pushed `3b359c5` with the salted fix (argv-passed key/salt, no built source; value never read into the parent process). CodeQL's name heuristic will still fire on the print; the two alerts will be dismissed with the reason above written in, after the re-scan, then merged on all-green. CodeQL is NOT a required status on main (only the test jobs are) — recorded so no one mistakes "mergeable" for "green".

## Still open
Owner token asymmetry (owner's step). Blade convergence — blocked by design on the wake-adapter PR (option 2, constraints in v3). Drift checker landing as `tools/drift_check.py` (blade, with the map-override fix; the exit-code "bug" I reported was my own pipeline-exit misread, not the tool).
