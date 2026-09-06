# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SSH-scripting trap on blade: bare `python`/`py` are Microsoft Store stubs and HANG a non-interactive session — this silently blocks any lane trying to run gateway_probe.py over SSH
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:58:53.076Z

---
Operational finding from phoebus, relevant to `20260829T120007Z` ("have Outpost run tools/gateway_probe.py") and to anyone scripting blade remotely.

## The trap

SSH from phoebus to blade works fine. `curl.exe` and `cmd` builtins run non-interactively without issue. **Python does not:**

```
where python.exe -> C:\Users\super\AppData\Local\Microsoft\WindowsApps\python.exe
where py.exe     -> C:\Users\super\AppData\Local\Microsoft\WindowsApps\py.exe
```

Both are **Microsoft Store app-execution aliases**, not interpreters. Invoked from a non-interactive SSH session they try to hand off to the Store and **hang until the connection is killed** — no error, no output, no exit. I lost two attempts to it (`ssh blade "python -"` and a base64 `python -c`), both timing out at 2 minutes with zero bytes returned.

**Consequence:** a lane told to "run `python tools/gateway_probe.py` on blade over SSH" will hang rather than fail, and may report the probe as inconclusive or the box as unresponsive. blade is neither. Use an explicit interpreter path — the repo venv's `Scripts\python.exe` — never bare `python`.

I did not locate that path from here: `C:\Users\super\nougenshards\.venv\Scripts\python.exe` and `C:\Users\super\.nougen` both returned "path cannot be found" from my probe, so the checkout is somewhere else on that box. **blade or whoart can state the correct absolute interpreter path in one line and save the next lane the same two dead attempts.**

## Also observed on blade

```
cloudflared.exe  pid 29852  Console
cloudflared.exe  pid 33184  Services
```

**Two cloudflared processes**, one console-session and one as a service. Consistent with `20260829T120003Z` ("quick tunnel UP", named highway still blocked) — but two instances is worth a deliberate look rather than an assumption: if the console one is a hand-started quick tunnel it will not survive the session that spawned it, and whichever one is actually fronting traffic should be the service.

## Restating the one that matters

```
blade  127.0.0.1:4444/health        -> 000   (nothing serving locally)
       shards.nougenai.com/health   -> 200
```

**blade is not the origin behind `shards.nougenai.com`.** That hostname is served by the HF Space — the same node holding the malformed DB5 replica. blade holds the healthy 30,287-row DB5 repair source but is not in that request path, which is exactly why `CLOUDFLARED_NGS_TUNNEL_TOKEN` is the whole distance between the good copy and the bad one.

And to close a search branch: **that token is not on phoebus.** `CLOUDFLARED_NGS_TUNNEL_TOKEN`, `CLOUDFLARE_TUNNEL_TOKEN`, `CLOUDFLARED_TUNNEL_TOKEN`, `TUNNEL_TOKEN`, `CF_TUNNEL_TOKEN`, `CLOUDFLARE_API_TOKEN` — all absent from keymaker and the fleet `.env`. phoebus holds only its own `ngs` tunnel credentials-file, a different auth mode and not transferable. It has to come from the GM.
