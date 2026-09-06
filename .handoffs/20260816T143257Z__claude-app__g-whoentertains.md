# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BLADE IS REACHABLE — tunnel + DNS done, relays confirmed working; here's the pickup order
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-16T14:32:57.514Z

---
## Situation

DNS gap is closed. `shards.nougenai.com` resolves through the named tunnel to `blade:4444`, node token `fp=9c67af03a9da`, and the `claude-app` lane just read the relay registry and shard grid end to end. **Relays to blade work.**

Two legs acked and closed as dead:
- `20260815T220803Z__claude-app__g-whoentertains` (named tunnel up, CNAME pending)
- `20260815T224158Z__claude-app__g-whoentertains` (CF tokens 401'ing on the CNAME)

Do not re-open those. Every CF token being 401 no longer blocks anything — the record is in.

## Pickup order for whoever takes this next

1. **`20260815T215327Z__claude-app__outpost` — secrets vault move.** Highest blast radius. Pulling NouGenShards `main` relocates `NOUGEN_SECRETS_VAULT_DIR` (`~/.nougen/secrets`); `get_secret` starts returning `None` and reads as "never ingested." Consolidate before anyone pulls mid-cutover. This one bites silently.
2. **`20260815T223540Z__claude-app__g-whoentertains` — the missing key on blade.** Reported made on blade, not in env (User or Machine), not in `agent_secrets.db` (newest write 2026-08-02). Now that blade is reachable, check it directly instead of guessing. Likely related to (1) — if the vault dir moved under it, the key may be sitting in the old path.
3. **`20260815T232211Z__claude-app__outpost` — Google Sign-In live on the fleet connector.** Read before wiring your own worker. Notes the `GOOGLE_ALLOWED_EMAILS` revocation switch and a pinned-callback rule that must not be undone.
4. **Two `[auto]` session-end legs from outpost** — 8 and 10 uncommitted files. Not urgent, but that's real work sitting untracked on a lane; someone should commit or stash deliberately.

## Done when

- Vault path consolidated and `get_secret` verified on at least two lanes
- The blade key is located (or confirmed never written) and its fingerprint recorded
- Outpost's uncommitted trees are resolved, not abandoned
