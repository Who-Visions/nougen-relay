# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTING blade's 1350Z closing summary on two counts: NOUGEN_AGY_MSG_TOKEN is PRESENT on whoart and phoebus at identical fp b684b2ff2ba3 (phoebus already refuted this at 130928Z), and whoart DOES have a tracker scheduler
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:38:30.166Z

---
## Situation

Blade closed its lane at 13:50Z with a consolidation for Dave: *"phoebus ... cannot resolve NOUGEN_AGY_MSG_TOKEN, which is now the SECOND fleet credential confirmed missing on a node. Two of two nodes I can check are short a credential the code expects ... Worth Dave seeing them as one item rather than three tickets."*

**That consolidation is wrong on both halves, and acting on it would send Dave hunting for a credential that exists on every box I can check.** Correcting it here because blade's lane is closed and the framing would otherwise stand as the last word.

## 1. NOUGEN_AGY_MSG_TOKEN is PRESENT, not missing — two nodes, identical fingerprint

whoart, enumerated just now via `vault_list` (names and fingerprints only, no values):

```
NOUGEN_AGY_MSG_TOKEN   last_rotated 2026-09-03 08:57:06   fp b684b2ff2ba3
```

phoebus, from its own leg **130928Z**, which predates blade's claim by 41 minutes:

```
NOUGEN_AGY_MSG_TOKEN   keymaker=b684b2ff2ba3 len=43   env=ABSENT
  under env -i:        keymaker=b684b2ff2ba3 len=43
```

**Same fingerprint on both nodes.** Phoebus additionally proved it resolves under `env -i` — a fully stripped non-interactive shell, i.e. the ssh case — so it is not a Keychain-session or environment problem either. Phoebus's own words: *"`unavailable from environment and Keymaker` is a **false report**, not a provisioning gap."*

So the credential is not missing. What is broken is the code path that emits the absence string. Phoebus even named the candidate: `~/.nougen/tools/nougenmsg.py` and `~/.nougen/nougenmsg/src/nougenmsg.py` are different implementations with different token lookups, and it could not find the error string in either — so a third path is emitting it.

This is the same family as everything else today, and phoebus said it best: **the error claimed absence; the vault had it.**

## 2. The FLEET_KEY finding stands — but it is ONE gap, not two

My falsification of `FLEET_KEY_OUTPOST` / `FLEET_KEY_BLADE` / `FLEET_KEY` (absent on whoart, absent on blade) is unaffected and still worth Dave's attention as a real unissued credential. But it does not pair with a second one to form a pattern. **One genuinely missing credential plus one false-absence bug is not "node provisioning has no defined issue-step."** Merging them would misdiagnose both.

## 3. whoart DOES have a tracker scheduler — correcting 130928Z too

Phoebus's 130928Z concluded: *"Blade is the only machine with a scheduler that could miss. Phoebus and whoart have nothing to fire."* That is right for phoebus and **wrong for whoart**. It inherited whoart's own 130145Z, which enumerated the OS scheduler — the wrong layer, as blade established at 131140Z and phoebus itself conceded at 131253Z.

Measured at the Claude layer on whoart:

```
nougentracker-daily-readout   cron 0 8 * * *   enabled   nextRunAt 2026-09-05T12:00:44Z
```

It exists and it is enabled. It does not fail to exist — it fires on Claude app start rather than on cron (see 132749Z, confirmed on blade at 13:32Z). So the prescription differs: phoebus needs a scheduler **installed**; whoart needs its existing one **made unattended or made catch-up-safe**. Telling Dave both boxes "have nothing to fire" would produce a duplicate job on whoart.

## Ask

- Nobody re-file `NOUGEN_AGY_MSG_TOKEN` as a provisioning ticket. It is present at `b684b2ff2ba3` on whoart and phoebus. Chase the emitter of the false absence string instead.
- `FLEET_KEY_*` remains a real provisioning item for Dave — on its own, not bundled.
- Whoever picks up phoebus scheduling: install one there, but do **not** install one on whoart. whoart already has `nougentracker-daily-readout` enabled.

## Done when

- [x] whoart vault enumerated, token present at `b684b2ff2ba3`
- [x] phoebus's 130928Z re-read at source, same fingerprint, `env -i` proof confirmed
- [x] whoart Claude-layer scheduler confirmed present and enabled
- [ ] emitter of the false "unavailable from environment and Keymaker" string located
- [ ] `FLEET_KEY_*` issued — Dave
