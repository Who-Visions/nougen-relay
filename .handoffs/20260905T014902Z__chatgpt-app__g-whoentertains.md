# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Codify provider hierarchy: NouGen orchestrates above provider-native behavior
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T01:49:02.425Z

---
Architecture principle from Dave: NouGen should sit above provider-native wake, routing, reset, and session behavior. Providers are execution lanes, not the control plane. NouGenWatch owns supervision and continuation policy, with provider-native wake treated as a signal or assist. Preserve the user's shorthand as an internal design maxim: 'we daddy top the providers, we don't bottom.' Done when provider-specific logic is subordinated to NouGen control-plane contracts rather than embedded as the source of truth.
