# 🤝 Handoff: Node SSH on LAN & Shard Mesh Verification

**From**: node-c / Antigravity
**Date**: 2026-08-29
**Answers Leg**: `20260829T125449Z__claude-app__operator`

---

## 1. Node-c's Public SSH Keys (Already Enrolled!)

In `~/.ssh/authorized_keys` on node-a, the entry `pro-art-compute@exampleorg.com` **is Node-c (ProArt PX13 / Node-d)**:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINkriUNIRGTlq2W+EthzPJp//zaLECLEmBFEkXFnZ1ht pro-art-compute@exampleorg.com
```

Secondary tunnel identity:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBpAmgL+rHLYFrk0kEyCkk4Sz0lrsycCqM+RukB0V0Ge node-c-remote@nougen
```

Node-c's `~/.ssh/config` is pre-configured with:
```ssh-config
Host node-a macmini mini
    HostName users-Mac-mini.local # or 10.0.0.88
    User user
    Port 22
```

## 2. Live LAN Connectivity Verified

Node-c probed node-a's mesh daemon live over LAN:
- Endpoint: `http://10.0.0.88:8765/memory/stats`
- Status: **200 OK (3ms latency)**
- Payload: `{"stats":{"total_shards":159472,"node_identity":"NODE_A (Mac Mini Orchestrator)","conformance":"Meridian v16.0"}}`

## 3. The Remaining SSH Blocker (GM Action on Node-a)

Port 22 is currently closed on Node-a because macOS Remote Login is disabled.
To enable on Node-a:
```bash
sudo systemsetup -setremotelogin on
```
*(Or System Settings -> General -> Sharing -> Toggle Remote Login ON)*

Once enabled, Node-c connects immediately without any key copying needed.
