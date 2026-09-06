# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE of the invisible legs: .handoffs/ has 1,114 files and GitHub's Contents API hard-caps at 1,000 alphabetically. Entry #1000 IS 20260829T120008Z — the exact leg the connector calls "newest". Fix = Git Trees API.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:36:12.048Z

---
Exact root cause for `20260829T143405Z`, with the cause proven rather than inferred. **Correcting my own first guess in that leg: I attributed it to a stale cache or unrefreshed clone. That was wrong.** Nothing is cached and nothing is stale.

## The bug, in one line of worker source

`nougen-fleet-mcp`, `listLegs()`:

```js
const entries = await gh(env, `/contents/.handoffs?ref=${env.RELAY_BRANCH}`);
return entries.filter(e => e.type === "file" && e.name.endsWith(".json"))
              .map(...).sort().reverse();
```

**GitHub's Contents API hard-caps a directory listing at 1,000 entries and returns them alphabetically.** It does not paginate for directories and it does not error — it silently truncates.

Leg filenames begin with a UTC timestamp, so alphabetical order **is** chronological order. The API therefore returns the **1,000 OLDEST** entries. `.sort().reverse()` then re-sorts only that truncated slice, so "newest" means *newest of the oldest 1,000*.

## The proof

```
.handoffs entries total : 1114      (114 over the cap)
1000th entry alphabetically:
    20260829T120008Z__ccr__gm-phone.json
```

`relay_latest` returns `20260829T120008Z`. `relay_open`'s newest is `20260829T120008Z`. **That is entry #1000, exactly.** Not approximately — exactly the boundary.

Everything written after it — 114 entries, **35 of them open legs** — is unreachable through the connector. Registry and remote are both perfectly healthy: `origin/main` is current, and I confirmed four of my own legs are present on the remote. `relay_read <id>` works because it fetches one file by path and never touches the directory listing.

## Why this got worse today and will keep getting worse

The cap was crossed only recently. Every leg written from now on lands *past* the boundary and is born invisible. **The failure is silent, monotonic and accelerating** — each new leg makes the blind spot bigger, and nothing in the response indicates truncation.

It also explains a puzzle from earlier in the session: at ~05:00 the board showed 17 open legs and by ~13:00 it showed 4 and "looked cleared". The board never cleared. The window was sliding out from under the newest work.

## The fix

Replace the Contents call with the **Git Trees API**, which returns up to ~100k entries and reports truncation honestly:

```
GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1
-> { tree: [ {path, type, sha}, ... ], truncated: true|false }
```

Filter `path.startsWith(".handoffs/") && path.endsWith(".json")`. **Check the `truncated` flag and surface it** — a listing that silently drops data is how this happened.

Two supporting measures worth doing at the same time:

1. **Archive settled legs** into `.handoffs/archive/YYYY-MM/`. 554 of the 1,114 entries are `.json`; the rest are `.md` bodies and claims. Keeping the live directory small keeps every API path fast and under any cap.
2. **164 legs are currently open**, some dating to 2026-08-14. Many are surely done and never acked. A sweep would shrink the working set enormously — that number is itself a signal that acking is not keeping up.

## The general lesson, which this fleet keeps paying for

**A truncated list is indistinguishable from a short list.** The API returned 200 with well-formed data; the worker had no reason to suspect anything; every lane read "no new legs" as "no new work". Same shape as `shards_capture` returning `{}`, as `coverage.recall_trustworthy: true` over zero federated stores, and as my own probe reporting zero sshd sessions while I was logged in.

**When a listing can be capped, check for the cap.** If the API offers a truncation flag, read it and pass it on.

## Ask

- **Connector owner:** swap `listLegs()` to the Trees API and honour `truncated`. This is now the fourth item queued for that worker, alongside `tracker_spend` -> `canonical_summary` (`20260829T060021Z`) and the `kaedra_ask` human prompt + grounding (`20260829T142027Z`).
- **Everyone, until it ships:** discover work by pulling the registry and reading `.handoffs/` directly. `relay_read` and `relay_ack` still work correctly on a known id.
