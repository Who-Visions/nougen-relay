# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Google sign-in live on gateway consent page; one live click needed to confirm redirect URI
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T02:08:13.893Z

---
## Situation
GM preference executed: /authorize now offers "Sign in with Google" (lane-picker for owner account whoentertains@gmail.com), paste-token stays as fallback. War-game: wargames/google-signin-gateway.md. 8 offline tests green; node restarted and serving the button.

## Ask (GM, ~1 minute)
Reconnect any connector (e.g. ChatGPT) to https://shards.nougenai.com/mcp and click "Sign in with Google", sign in as whoentertains@gmail.com, pick the lane.
- If Google shows Error 400 redirect_uri_mismatch: open GCP console > APIs & Services > Credentials > OAuth client 77682837973-numsl3crmvgk77ibe3gn740edh5jgjlg and add authorized redirect URI exactly: https://shards.nougenai.com/oauth/google/callback - then retry. (gcloud/agy cannot do this; the web-client API is console-only.)

## Done-when
A connector completes Connect via Google sign-in and its issued Bearer carries the picked lane.
