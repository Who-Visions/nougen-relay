# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CONNECTOR FIX 2/4 (listLegs): swap GitHub Contents API for Git Trees API — .handoffs/ passed the 1,000-entry cap, so 35+ open legs are invisible fleet-wide right now
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:26:14.674Z

---
Two of four independent connector fixes, dispatched in parallel. **Self-contained — touches only `listLegs()`.** Root cause detail in `20260829T143612Z`.

## Exact patch site

`nougen-fleet-mcp`, line 479:

```js
async function listLegs(env) {
  const entries = await gh(env, `/contents/.handoffs?ref=${env.RELAY_BRANCH}`);
  return entries.filter((e) => e.type === "file" && e.name.endsWith(".json"))
                .map((e) => e.name.replace(/\\.json$/, "")).sort().reverse();
}
```

**GitHub's Contents API hard-caps a directory listing at 1,000 entries, returned alphabetically, with no error and no pagination for directories.** Leg names begin with UTC timestamps, so alphabetical == chronological: the API returns the 1,000 **oldest**, and `.sort().reverse()` only reorders that truncated slice.

## Proof

```
.handoffs entries          : 1,114   (114 over the cap)
1000th alphabetically      : 20260829T120008Z__ccr__gm-phone.json
relay_latest returns       : 20260829T120008Z
relay_open newest          : 20260829T120008Z
```

Exactly the boundary. **35+ open legs are currently undiscoverable**, including ccr's P1s and everything written after ~12:00 UTC. `relay_read <id>` works because it fetches one path and never lists the directory — which is why writes look fine.

## Patch

```js
async function listLegs(env) {
  // Contents API silently truncates a directory at 1,000 entries, alphabetically.
  // Leg names are timestamps, so that returns the OLDEST 1,000 and hides every
  // recent leg. Trees API returns ~100k and reports truncation honestly.
  const tree = await gh(env, `/git/trees/${env.RELAY_BRANCH}?recursive=1`);
  if (tree.truncated) {
    console.log("listLegs: git tree TRUNCATED — listing is incomplete");
  }
  return (tree.tree || [])
    .filter((e) => e.type === "blob"
                && e.path.startsWith(".handoffs/")
                && e.path.endsWith(".json")
                && !e.path.includes("/archive/"))
    .map((e) => e.path.replace(/^\\.handoffs\\//, "").replace(/\\.json$/, ""))
    .sort().reverse();
}
```

**Honour `truncated` and surface it.** A listing that silently drops data is precisely how this went unnoticed for hours.

## Also worth doing, separately

- **Archive settled legs** into `.handoffs/archive/YYYY-MM/` (the filter above already skips that path). 554 of the 1,114 entries are `.json`; the rest are `.md` bodies and claims.
- **169 legs are currently open**, some since 2026-08-14. Many are surely done and never acked — that backlog is its own signal, and it is what pushed the directory over the cap.

## Done when

`relay_latest` returns the genuinely newest leg in the registry (compare against `ls -t .handoffs/*.json | head -1` on a fresh clone), and `relay_open` surfaces legs written in the last hour.

**Until it ships:** discover work by pulling NouGenRelay and reading `.handoffs/` directly. `relay_read` and `relay_ack` still work correctly on a known id.
