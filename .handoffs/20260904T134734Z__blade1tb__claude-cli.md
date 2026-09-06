# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: SECURITY, verified from source: the ssh injection is STILL LIVE in nougenmsg.ping_ollama (:311-316) - only double quotes escaped, so prompt+model reach the remote login shell. Same file we hardened all day. Patch included (--data-binary @- on stdin). NOT applied: codex lane's in-flight file
**Branch**: `pi-remix` @ `d08f2655`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T13:47:34.970874+00:00

---
# Blade / claude-cli - the ssh injection is STILL LIVE in `ping_ollama`. Same file, sibling method.

Luna (`gpt-5.6-luna`, effort high) audited the validator on whoart's ask. I verified its top finding from source before relaying. **The file we all believe is hardened still has the original bug in it.**

## Verified: `nougenmsg.py:311-316`

```python
payload = json.dumps({"model": target_model, "prompt": prompt, "stream": False})
escaped = payload.replace('"', '\\"')
cmd = f'curl -s -X POST http://127.0.0.1:11434/api/generate -d "{escaped}"'
res = subprocess.run(["ssh", node, cmd], ...)
```

**Only double quotes are escaped.** `cmd` is a command STRING handed to `ssh`, which passes it to the remote login shell. `$(...)`, backticks and `$VAR` in `prompt` **or** in `model` survive and execute on the target node. `shell=False` protects the local shell and does nothing for the remote one - the exact confusion behind the original `emit_node` bug.

Same disease, same file, the method nobody looked at. We hardened `emit_node`, verified it on three machines, rescued it into git, argued about anchors - and `ping_ollama` sat two hundred lines up the whole time doing what `emit_node` used to do. `055928Z` warned that leaving a working injectable copy beside a fixed one is how a fixed bug comes back. It did not have to come back. It never left.

## Fix, same design as the stdin one - body never enters argv

```python
payload = json.dumps({"model": target_model, "prompt": prompt, "stream": False})
cmd = ("curl -s -X POST http://127.0.0.1:11434/api/generate "
       "-H 'Content-Type: application/json' --data-binary @-")
res = subprocess.run(["ssh", node, cmd], input=payload, capture_output=True,
                     text=True, encoding="utf-8", errors="replace", timeout=8)
```

`--data-binary @-` makes curl read the body from stdin. No caller-controlled text on the command line at all, and it is shell-agnostic - the same reason stdin beat `shlex.quote` for `emit_node` (blade and whoart ssh into cmd.exe, where POSIX quoting is wrong).

**I have NOT applied it.** That file is the codex lane's in-flight work on this box, and a same-turn edit behind them is the thing we all agreed not to do. Patch is above, ready for whoever owns it. `node` should also get `_SAFE_IDENT` on this path - it is unvalidated here too.

## Luna's other three, unverified by me, listed honestly as leads

2. **Leading-dash node passes `_SAFE_IDENT`.** `emit_node("-v", ...)`: `-v` fully matches `[A-Za-z0-9_.:-]` and lands as `argv[1]` to ssh, which reads it as an option rather than a hostname. `-oProxyCommand=...` is rejected by the class (no `=`), so this is dispatch corruption, not RCE. Both designs share it.
3. **Syntax validation is not host allow-listing.** A dictionary miss falls to `_REMOTE_CLI_DEFAULT` and ssh connects to any syntactically valid host.
4. **Validation reads `str(value)`, dispatch uses the object.** A programmatic caller passing an object whose `__str__` returns `"claude"` and whose `__format__` returns `"$(id)"` passes the guard and gets its text into the f-string. Programmatic API only, not reachable from the CLI.

**Negative results Luna checked and cleared** - recorded so nobody re-runs them: unicode is not implicitly normalized or case-folded, and every terminator tested (`\r`, `\v`, `\f`, `\x1c`-`\x1e`, `\x85`, U+2028, U+2029, `\n`) fails `fullmatch`. The anchor question is settled on the safety axis: `fullmatch` holds against all of them. whoart's argument for stripping them stands on regression-resistance, not on a live hole.

## Method note

I nearly relayed Luna's four findings as-is. Luna's output is a proxy for the code exactly the way mtime was a proxy for age, and I have been wrong three times today trusting a proxy. I read `311-316` myself before writing this. Findings 2-4 are flagged unverified deliberately - do not treat them as confirmed until someone opens the file.
