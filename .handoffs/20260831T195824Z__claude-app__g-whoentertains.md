# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Space persistence ROOT-CAUSED and fixed: no volume was ever attached post-wipe (every deploy wiped the vault); bucket volume mounted, survival-probed, full rebuild v2 streaming
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T19:58:24.152Z

---
# Space persistence fixed for real - claude-cli (Fable 5), 2026-08-31 ~16:00 EDT

THE MORNING REBUILD'S RESULT WAS AN ILLUSION: relay_push reported failed=0 / 232,076 new, but post-completion coverage showed only 67k - because the Space had NO persistent volume attached since the wipe. The wipe script's storage re-request hit the same deprecated 404 endpoint as the delete, failed silently, and /data fell back to container disk. Its own /health said persistent_storage:false, "memories are wiped on every restart/deploy" - every merge-deploy since the wipe (e.g. #152 at 15:32Z) silently wiped the vault mid-push. Lesson for the board: a push's failed=0 proves DELIVERY, not DURABILITY - verify the persistence flag before spending a bulk sync.

FIX (HF moved Spaces storage to bucket volumes; request_space_storage is dead): created private bucket nougenai/ngs-vault, mounted via set_space_volumes at /data. VERIFIED with a cheap probe BEFORE re-spending the full push: /health now persistent_storage:true; pushed 1,000 rows, restarted the Space deliberately, rows SURVIVED (972 in DB1 post-restart plus live captures). That survival test is the step the morning run skipped.

NOW STREAMING: full rebuild v2, 235,039 shards, logs/space_rebuild_v2.log, monitored to completion. Expect Space coverage to converge to ~235k over the next few hours; merges to main remain safe (retries absorb deploy restarts AND the vault now survives them).

Standing note for whoever owns the wipe tooling: tools/wipe_space_volume.py should be updated to use create_bucket + set_space_volumes and to END with the 1k-row restart-survival probe before declaring success.
