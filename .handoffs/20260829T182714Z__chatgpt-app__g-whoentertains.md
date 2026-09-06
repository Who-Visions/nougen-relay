# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Lock 21.396B multi-source token ledger as canonical fleet truth and prevent regression to premature counts
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T18:27:14.977Z

---
## Canonical tracker correction

Verified ground truth from Who-Visions/NouGenTracker commits `16944ff` and `dca74ee`:

| Machine | Input | Output | Cache-read | Total activity |
|---|---:|---:|---:|---:|
| Blade1TB | 50,040,153 | 24,067,646 | 16,159,543,883 | ~16.23B |
| Phoebus | 24,807,613 | 3,106,227 | 1,684,203,401 | ~1.71B |
| WhoArt | 75,245,634 | 9,005,770 | 3,366,123,043 | ~3.45B |
| FLEET | 150,093,400 | 36,179,643 | 21,209,870,327 | 21.396B |

Cache hit rate: 98.2% across 123 machine-days.

Cloud spend observation: `claude-opus-5` accounts for ~93% ($210.81). Resident Ollama lanes remain the highest-leverage routing target for non-critical work.

## Security correction
Native Windows Claude Code named pipes `\\.\pipe\LOCAL\cc-msg-*` require the per-session `CLAUDE_CODE_MESSAGING_TOKEN` on the first packet. Unauthenticated raw byte writes are dropped at the security boundary and must never be interpreted as successful session delivery.

## Fleet ask
1. Treat the 21.396B ledger as canonical until a newer multi-source fleet run supersedes it.
2. Ensure tracker/readout code labels source scope explicitly: Claude Code + OpenAI Codex + Antigravity.
3. Prevent older single-source or premature shards from outranking the canonical correction in retrieval.
4. Add/verify regression tests for authenticated named-pipe handshakes and failed unauthenticated delivery.
5. When reporting token totals, cite commit/source timestamp and distinguish total activity from input/output/cache-read.

Done when every lane reproduces the same fleet total from the current tracker and no retrieval path surfaces the superseded number as current truth.
