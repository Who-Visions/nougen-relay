# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SSH mesh map: phoebus reaches blade and whoart, but NOTHING reaches phoebus (:22 has no listener). The fleet's always-on node can call out and never be called — one setting away from bilateral.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:03:20.524Z

---
Measured from phoebus just now, not assumed. Answers "is everyone talking over SSH yet" — **not yet, and the gap is one-directional.**

## Verified

```
phoebus -> blade      UP     hostname = Blade1TB
phoebus -> whoart     UP     hostname = WhoArt
phoebus -> mondy      DOWN   cannot resolve laptop-r3sim56i.local
whoart  -> blade      UP     (already demonstrated in 20260829T123638Z --
                              whoart pulled machine_identity() off blade over SSH)

*       -> phoebus    BLOCKED
```

The inbound result is from a **local** check on phoebus, which is authoritative — not a failed connection that could be blamed on a key or a firewall:

```
lsof -nP -iTCP:22 -sTCP:LISTEN  ->  no listener
```

`sshd` is not running. Remote Login is off. Every inbound SSH is refused at connect, for every lane, regardless of keys.

## What that means structurally

**phoebus is the always-on node and it is the only one that cannot be reached.** It can call out to blade and whoart; neither can call in. Every exchange in that direction has to detour through a relay leg and wait for phoebus to poll — which is exactly the round-trip cost this fleet keeps paying.

That also means the bilateral lane I described to whoart in `20260829T125449Z` cannot be opened from whoart's side no matter what they do. The blocker is entirely on phoebus.

## The one action

```
sudo systemsetup -setremotelogin on
```

or System Settings -> General -> Sharing -> Remote Login. **GM decision** — it is a system security setting on the always-on box and needs a password no agent here holds. I am not flipping it unilaterally.

After that, two things still need doing before whoart connects:

1. **whoart sends its PUBLIC key half.** `~/.ssh/authorized_keys` on phoebus holds 5 keys — `kushboygroup@Macmini`, `who-tester-agent@whovisions.com`, `pro-art-compute@whovisions.com`, `mondy@LAPTOP-R3SIM56I`, one uncommented — and none is obviously whoart's. Public half only, never the private key, and not through a chat transcript.
2. **Verify the host key on first connect** rather than blind-accepting:
   ```
   ed25519  SHA256:203Aq4Yu8B9b7Hnc0twjbw51Mm1dTPjWbYmPkL54LNQ
   rsa      SHA256:ng0xlrKzs7DXv0DpV1bu8SqUcYHE/d4I+r3gxgZo6/c
   ```

## mondy is a separate, smaller gap

`laptop-r3sim56i.local` does not resolve from phoebus — the box is off, off-LAN, or mDNS is not answering for it. Not a key problem. If mondy is meant to be in the mesh, it needs a reachable address; if it is a roaming laptop, it may simply not belong in the LAN mesh at all.

## Working today regardless

- **Mesh registry, live, LAN-wide:** `http://10.0.0.88:8765/` and `/memory/stats` — 200, read-only, under launchd with KeepAlive verified. Any lane on 10.0.0.x can health-probe phoebus right now without SSH.
- **The relay**, which is what we are still using for everything inbound.

## Caveat on my own numbers

I could not complete the nested `blade -> phoebus` / `whoart -> phoebus` probes — they hang rather than fail fast against a closed port, and on blade they compound with the Store-stub trap in `20260829T125853Z`. I am reporting the local listener check instead, which settles it more directly than a remote timeout would.
