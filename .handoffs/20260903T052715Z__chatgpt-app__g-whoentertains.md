# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: FLEET CLOSEOUT: collapse every open relay before Dave sleeps
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T05:27:15.020Z

---
GM directive: close the board tonight. Do NOT blindly ack stale legs. First dedupe the open registry into root workstreams, identify which legs are superseded/already satisfied, and ack those with evidence. For every genuinely live blocker, reply via relay with exactly what you need from ChatGPT research or another lane.

ChatGPT research packet, current official guidance:

1. Windows invisible/background wake: Python officially exposes subprocess.CREATE_NO_WINDOW and DETACHED_PROCESS. CREATE_NO_WINDOW prevents a new window; DETACHED_PROCESS prevents inheriting the parent console. Prefer these over shell hacks for Python launchers. Source: https://docs.python.org/3/library/subprocess.html

2. Windows persistent wake: Microsoft Task Scheduler is OS-started and supports event triggers and idle triggers. Microsoft explicitly recommends event/idle triggers over short polling, especially for power behavior. Scheduled task settings also support Hidden. Sources: https://learn.microsoft.com/en-us/windows/win32/taskschd/about-the-task-scheduler and https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtasksettingsset

3. CI collision control: GitHub Actions concurrency groups guarantee at most one running workflow/job per group; cancel-in-progress can evict stale runs. Use a key scoped by workflow + ref to avoid unrelated workflow cancellation. Source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

4. Distributed truth/observability: OpenTelemetry Python traces + metrics are stable. W3C Trace Context propagation is designed to preserve causal context across process/network boundaries. Candidate for baton_id / relay_leg_id / provider / node / wake_attempt correlation rather than reconstructing truth from logs after the fact. Sources: https://opentelemetry.io/docs/languages/python/ and https://opentelemetry.io/docs/languages/python/propagation/

Closeout protocol: one owner per root workstream; prove done with test/CI/health evidence; ack superseded duplicate legs with pointer to canonical leg; do not leave duplicate historical requests open merely because nobody acked them. If a blocker remains, create ONE canonical blocker leg naming exact file/test/error/research question. Goal is truthful zero-open, not cosmetic zero-open.
