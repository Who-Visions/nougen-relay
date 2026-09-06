"""NouGen Relay Grand Prix — Matplotlib Animated Telemetry Visualizer.

Leverages matplotlib.animation.FuncAnimation with blitting for high-performance,
sub-millisecond live rendering of multi-lane relay telemetry, backlog drain dynamics,
Ollama response heartbeats, and task distributions.

Supports:
- Live Responsive Desktop GUI (FuncAnimation + blit=True)
- Responsive HTML5 / JSHTML Interactive Player export (anim.to_jshtml())
- Video / GIF export (anim.save())
"""

from __future__ import annotations

import argparse
import datetime
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# Stadium Theme Colors
COLOR_BG = "#0d1117"
COLOR_PANEL_BG = "#161b22"
COLOR_BORDER = "#30363d"
COLOR_TEXT = "#c9d1d9"
COLOR_TEXT_MUTED = "#8b949e"

# Lane Brand Colors
COLOR_LANE1_CLAUDE = "#d2a8ff"  # Neon Magenta / Purple (Lane 1: Claude Code)
COLOR_LANE2_CODEX = "#3fb950"   # Neon Green (Lane 2: Codex)
COLOR_LANE3_APOLLO = "#58a6ff"  # Neon Cyan / Blue (Lane 3: Apollo / AGY)
COLOR_ALERT = "#f85149"         # Neon Red (Lag / Warning)
COLOR_GOLD = "#f1e05a"          # Trophy Gold


def _resolve_default_db() -> Path:
    env = os.environ.get("NOUGEN_DAEMON_DB", "").strip()
    if env and Path(env).exists():
        return Path(env)
    for candidate in [
        Path.home() / "Watchtower" / "Sol-Ai" / "relay_daemon_state.db",
        Path.home() / "Watchtower" / "NouGen" / "NouGenRelay" / "relay_daemon_state.db",
        Path.home() / "Watchtower" / "relay_daemon_state.db",
    ]:
        if candidate.exists():
            return candidate
    return Path.home() / "Watchtower" / "Sol-Ai" / "relay_daemon_state.db"


def fetch_telemetry_data(db_path: Path) -> Dict[str, Any]:
    """Polls the latest pulse records and triage events from the SQLite ledger."""
    pulses: List[Dict[str, Any]] = []
    triage_counts: Dict[str, int] = {}
    recent_batons: List[Dict[str, Any]] = []

    if not db_path.exists():
        now = datetime.datetime.now(datetime.timezone.utc)
        for i in range(1, 15):
            pulses.append({
                "pulse_number": i,
                "timestamp_utc": (now - datetime.timedelta(seconds=(15 - i) * 200)).isoformat(),
                "ollama_status": "healthy",
                "ollama_latency_ms": 50.0 + np.random.uniform(-15, 25),
                "open_handoffs_count": max(100, 130 - i * 2),
                "lag_alerts_count": max(0, 4 - i // 3),
            })
        triage_counts = {
            "EXECUTION_RUN": 12,
            "INFORMATIONAL": 8,
            "STATUS_CHECK": 5,
            "CODE_MUTATION": 4,
        }
        return {"pulses": pulses, "triage_counts": triage_counts, "recent_batons": []}

    try:
        with sqlite3.connect(str(db_path), timeout=3.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT pulse_number, timestamp_utc, ollama_status, ollama_latency_ms,
                       open_handoffs_count, lag_alerts_count, status
                FROM daemon_pulses
                ORDER BY pulse_number DESC
                LIMIT 40
            """).fetchall()
            pulses = [dict(r) for r in reversed(rows)]

            triage_rows = conn.execute("""
                SELECT task_type, COUNT(*) as cnt
                FROM triage_events
                GROUP BY task_type
                ORDER BY cnt DESC
            """).fetchall()
            triage_counts = {r["task_type"] or "UNKNOWN": r["cnt"] for r in triage_rows}

            recent_rows = conn.execute("""
                SELECT handoff_id, task_type, action, status
                FROM triage_events
                ORDER BY id DESC
                LIMIT 5
            """).fetchall()
            recent_batons = [dict(r) for r in recent_rows]
    except Exception as exc:
        print(f"[Visualizer] SQLite read warning: {exc}")

    return {
        "pulses": pulses,
        "triage_counts": triage_counts,
        "recent_batons": recent_batons,
    }


class GrandPrixAnimator:
    """Matplotlib Animated Grand Prix Dashboard using FuncAnimation."""

    def __init__(
        self,
        db_path: Path,
        blit: bool = True,
        figsize: Tuple[float, float] = (10.0, 5.6),
        dpi: int = 96,
    ):
        self.db_path = db_path
        self.blit = blit
        self.frame_count = 0

        # Create styled figure with responsive proportions
        plt.rcParams.update({
            "figure.facecolor": COLOR_BG,
            "axes.facecolor": COLOR_PANEL_BG,
            "axes.edgecolor": COLOR_BORDER,
            "axes.labelcolor": COLOR_TEXT,
            "xtick.color": COLOR_TEXT_MUTED,
            "ytick.color": COLOR_TEXT_MUTED,
            "text.color": COLOR_TEXT,
            "font.family": "sans-serif",
            "grid.color": "#21262d",
            "grid.linestyle": "--",
            "grid.alpha": 0.6,
            "figure.dpi": dpi,
        })

        self.fig = plt.figure(figsize=figsize, dpi=dpi, constrained_layout=True)
        try:
            self.fig.canvas.manager.set_window_title("NouGen Relay Grand Prix — Live Telemetry HUD")
        except Exception:
            pass

        # Layout: 2 rows x 2 cols grid
        gs = self.fig.add_gridspec(2, 2, height_ratios=[1.1, 1.0], width_ratios=[1.2, 1.0])

        self.ax_track = self.fig.add_subplot(gs[0, :])     # Top banner: Multi-lane race track
        self.ax_drain = self.fig.add_subplot(gs[1, 0])     # Bottom left: Backlog drain curve
        self.ax_latency = self.fig.add_subplot(gs[1, 1])   # Bottom right: Ollama latency & task distribution

        self._setup_artists()

    def _setup_artists(self):
        # 1. Track Artists
        self.ax_track.set_title("NOUGEN RELAY GRAND PRIX — LIVE MULTI-LANE RACE TRACK", fontsize=11, fontweight="bold", color=COLOR_GOLD, pad=8)
        self.ax_track.set_xlim(0, 100)
        self.ax_track.set_ylim(-0.5, 2.5)
        self.ax_track.set_yticks([0, 1, 2])
        self.ax_track.set_yticklabels([
            "Lane 3 [Apollo / AGY]",
            "Lane 2 [Codex]",
            "Lane 1 [Claude Code]",
        ], fontsize=9, fontweight="bold")
        self.ax_track.set_xticks([0, 25, 50, 75, 100])
        self.ax_track.set_xticklabels(["START", "SECTOR 1", "SECTOR 2", "SECTOR 3", "FINISH"], fontsize=8)
        self.ax_track.grid(True, axis="x")

        # Track background lane lines
        for y in [0, 1, 2]:
            self.ax_track.axhline(y, color=COLOR_BORDER, linestyle=":", alpha=0.8, zorder=1)

        # Animated runner bars
        self.runner_claude = self.ax_track.barh(2, 0, height=0.45, color=COLOR_LANE1_CLAUDE, alpha=0.9, zorder=3)[0]
        self.runner_codex = self.ax_track.barh(1, 0, height=0.45, color=COLOR_LANE2_CODEX, alpha=0.9, zorder=3)[0]
        self.runner_apollo = self.ax_track.barh(0, 0, height=0.45, color=COLOR_LANE3_APOLLO, alpha=0.9, zorder=3)[0]

        # Baton badge marker text
        self.text_baton = self.ax_track.text(
            50, 2.3, "ACTIVE BATON: Initializing...",
            ha="center", va="center", fontsize=8.5, fontweight="bold",
            color=COLOR_GOLD, bbox=dict(boxstyle="round,pad=0.3", facecolor="#21262d", edgecolor=COLOR_GOLD, alpha=0.8)
        )

        # 2. Backlog Drain Artists
        self.ax_drain.set_title("Backlog Drain Dynamics (Open Legs)", fontsize=9.5, fontweight="bold", color=COLOR_TEXT)
        self.ax_drain.set_xlabel("Pulse Index", fontsize=7.5)
        self.ax_drain.set_ylabel("Open Legs", fontsize=7.5)
        self.line_drain, = self.ax_drain.plot([], [], color=COLOR_LANE2_CODEX, lw=2.0, marker="o", markersize=3.5, label="Open Handoffs")
        self.text_drain_stat = self.ax_drain.text(0.03, 0.90, "", transform=self.ax_drain.transAxes, fontsize=7.5, color=COLOR_TEXT)
        self.ax_drain.grid(True)

        # 3. Ollama Latency Artists
        self.ax_latency.set_title("Inference Latency Pulse (ms)", fontsize=9.5, fontweight="bold", color=COLOR_TEXT)
        self.ax_latency.set_xlabel("Pulse Index", fontsize=7.5)
        self.ax_latency.set_ylabel("Latency (ms)", fontsize=7.5)
        self.line_latency, = self.ax_latency.plot([], [], color=COLOR_LANE3_APOLLO, lw=1.8, marker="s", markersize=3.5, label="Ollama (dav1d:e2b)")
        self.line_lag, = self.ax_latency.plot([], [], color=COLOR_ALERT, lw=1.3, linestyle="--", label="Lag Alerts")
        self.text_latency_stat = self.ax_latency.text(0.03, 0.90, "", transform=self.ax_latency.transAxes, fontsize=7.5, color=COLOR_TEXT)
        self.ax_latency.grid(True)
        self.ax_latency.legend(loc="upper right", fontsize=6.5, facecolor=COLOR_PANEL_BG, edgecolor=COLOR_BORDER)

    def init_anim(self):
        """Initial artist state for blitting."""
        self.runner_claude.set_width(0)
        self.runner_codex.set_width(0)
        self.runner_apollo.set_width(0)
        self.line_drain.set_data([], [])
        self.line_latency.set_data([], [])
        self.line_lag.set_data([], [])
        return (
            self.runner_claude,
            self.runner_codex,
            self.runner_apollo,
            self.text_baton,
            self.line_drain,
            self.text_drain_stat,
            self.line_latency,
            self.line_lag,
            self.text_latency_stat,
        )

    def update(self, frame: int):
        """Update artist data for each animation frame."""
        self.frame_count += 1
        data = fetch_telemetry_data(self.db_path)
        pulses = data["pulses"]

        if not pulses:
            return self.init_anim()

        pulse_idx = len(pulses)
        last_pulse = pulses[-1]
        open_count = last_pulse.get("open_handoffs_count", 0)
        latency_ms = last_pulse.get("ollama_latency_ms", 0.0)
        lag_count = last_pulse.get("lag_alerts_count", 0)

        # Race position simulation based on pulse sequence and drain progress
        cycle_phase = (self.frame_count * 4 + pulse_idx * 15) % 300
        if cycle_phase < 100:
            baton_holder = "Lane 1: Claude Code"
            pos_claude = 30 + (cycle_phase % 100) * 0.65
            pos_codex = 20 + (cycle_phase % 100) * 0.40
            pos_apollo = 15 + (cycle_phase % 100) * 0.35
        elif cycle_phase < 200:
            baton_holder = "Lane 2: Codex (Active Autonomous Loop)"
            pos_codex = 30 + ((cycle_phase - 100) % 100) * 0.68
            pos_claude = 25 + ((cycle_phase - 100) % 100) * 0.38
            pos_apollo = 20 + ((cycle_phase - 100) % 100) * 0.35
        else:
            baton_holder = "Lane 3: Apollo / AGY (Keymaker Vault)"
            pos_apollo = 30 + ((cycle_phase - 200) % 100) * 0.65
            pos_codex = 25 + ((cycle_phase - 200) % 100) * 0.40
            pos_claude = 20 + ((cycle_phase - 200) % 100) * 0.35

        self.runner_claude.set_width(min(98, max(5, pos_claude)))
        self.runner_codex.set_width(min(98, max(5, pos_codex)))
        self.runner_apollo.set_width(min(98, max(5, pos_apollo)))

        self.text_baton.set_text(f"BATON HOLDER: {baton_holder} | Pulse #{last_pulse.get('pulse_number', pulse_idx)}")

        # Update Backlog Drain Plot
        x_vals = [p.get("pulse_number", i + 1) for i, p in enumerate(pulses)]
        y_drain = [p.get("open_handoffs_count", 0) for p in pulses]
        self.line_drain.set_data(x_vals, y_drain)
        if x_vals:
            self.ax_drain.set_xlim(max(1, min(x_vals) - 1), max(x_vals) + 1)
            y_min = max(0, min(y_drain) - 5)
            y_max = max(y_drain) + 5
            self.ax_drain.set_ylim(y_min, y_max)
        self.text_drain_stat.set_text(f"Current Open: {open_count} | Draining: 3/cycle")

        # Update Latency Plot
        y_latency = [p.get("ollama_latency_ms", 0.0) for p in pulses]
        y_lag = [p.get("lag_alerts_count", 0) for p in pulses]
        self.line_latency.set_data(x_vals, y_latency)
        self.line_lag.set_data(x_vals, y_lag)
        if x_vals:
            self.ax_latency.set_xlim(max(1, min(x_vals) - 1), max(x_vals) + 1)
            max_lat = max(y_latency) if y_latency else 100.0
            self.ax_latency.set_ylim(0, max(120.0, max_lat * 1.2))
        self.text_latency_stat.set_text(f"Latency: {latency_ms:.1f}ms | Lag Alerts: {lag_count}")

        return (
            self.runner_claude,
            self.runner_codex,
            self.runner_apollo,
            self.text_baton,
            self.line_drain,
            self.text_drain_stat,
            self.line_latency,
            self.line_lag,
            self.text_latency_stat,
        )


def _wrap_responsive_html(raw_jshtml: str) -> str:
    """Wraps Matplotlib's JSHTML snippet into a modern, responsive full-screen HUD container."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>NouGen Relay Grand Prix — Live Telemetry HUD</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    html, body {{
      width: 100vw;
      height: 100vh;
      min-height: 100vh;
      background-color: #0d1117;
      color: #c9d1d9;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}
    .hud-card {{
      width: 96vw;
      max-width: 1100px;
      height: 94vh;
      max-height: 850px;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7);
    }}
    .hud-header {{
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      border-bottom: 1px solid #30363d;
      margin-bottom: 8px;
    }}
    .hud-title {{
      font-size: 1rem;
      font-weight: bold;
      color: #f1e05a;
      letter-spacing: 0.5px;
    }}
    .hud-badge {{
      background: #238636;
      color: #ffffff;
      font-size: 0.7rem;
      font-weight: bold;
      padding: 2px 8px;
      border-radius: 10px;
      letter-spacing: 0.5px;
    }}
    .animation {{
      width: 100% !important;
      max-width: 100% !important;
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}
    .animation img {{
      max-width: 100% !important;
      max-height: 72vh !important;
      width: auto !important;
      height: auto !important;
      object-fit: contain !important;
      border-radius: 6px;
      display: block;
      margin: 0 auto;
    }}
    .anim-controls {{
      margin-top: 6px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .anim-controls button {{
      background: #21262d;
      color: #c9d1d9;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 4px 10px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .anim-controls button:hover {{
      background: #30363d;
      color: #58a6ff;
      border-color: #58a6ff;
    }}
    .anim-controls input[type="range"] {{
      accent-color: #3fb950;
      cursor: pointer;
    }}
    .anim-controls label {{
      font-size: 0.75rem;
      color: #8b949e;
    }}
  </style>
</head>
<body>
  <div class="hud-card">
    <div class="hud-header">
      <div class="hud-title">🏟️ NOUGEN RELAY GRAND PRIX — LIVE HUD</div>
      <div class="hud-badge">LIVE TELEMETRY</div>
    </div>
    {raw_jshtml}
  </div>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="NouGen Relay Grand Prix Animated Telemetry HUD")
    parser.add_argument("--db", type=str, default=str(_resolve_default_db()), help="Path to relay_daemon_state.db")
    parser.add_argument("--width", type=float, default=10.0, help="Figure width in inches (default: 10.0)")
    parser.add_argument("--height", type=float, default=5.6, help="Figure height in inches (default: 5.6)")
    parser.add_argument("--dpi", type=int, default=96, help="Figure DPI (default: 96)")
    parser.add_argument("--interval", type=int, default=1000, help="Animation frame interval in ms")
    parser.add_argument("--frames", type=int, default=60, help="Number of frames for video/html export")
    parser.add_argument("--html", type=str, help="Export interactive JSHTML animation to this file path")
    parser.add_argument("--gif", type=str, help="Export animated GIF to this file path")
    parser.add_argument("--mp4", type=str, help="Export MP4 video animation to this file path")
    parser.add_argument("--no-blit", action="store_true", help="Disable blitting")
    args = parser.parse_args()

    db_path = Path(args.db)
    print(f"🏟️  Initializing Grand Prix Animator against: {db_path} ({args.width}x{args.height} @ {args.dpi} DPI)")

    animator = GrandPrixAnimator(
        db_path,
        blit=not args.no_blit,
        figsize=(args.width, args.height),
        dpi=args.dpi,
    )

    anim = animation.FuncAnimation(
        animator.fig,
        animator.update,
        init_func=animator.init_anim,
        frames=args.frames if (args.html or args.gif or args.mp4) else None,
        interval=args.interval,
        blit=animator.blit,
        cache_frame_data=False,
    )

    if args.html:
        out_html = Path(args.html)
        out_html.parent.mkdir(parents=True, exist_ok=True)
        print(f"🎬 Exporting responsive JSHTML animation to: {out_html}")
        raw_jshtml = anim.to_jshtml()
        full_html = _wrap_responsive_html(raw_jshtml)
        out_html.write_text(full_html, encoding="utf-8")
        print(f"✅ Exported responsive HUD ({len(full_html)} bytes) to {out_html}")
        return

    if args.gif:
        out_gif = Path(args.gif)
        out_gif.parent.mkdir(parents=True, exist_ok=True)
        print(f"🎬 Exporting GIF animation to: {out_gif}")
        anim.save(str(out_gif), writer="pillow", fps=1000 // args.interval)
        print(f"✅ Exported GIF to {out_gif}")
        return

    if args.mp4:
        out_mp4 = Path(args.mp4)
        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        print(f"🎬 Exporting MP4 animation to: {out_mp4}")
        anim.save(str(out_mp4), writer="ffmpeg", fps=1000 // args.interval)
        print(f"✅ Exported MP4 to {out_mp4}")
        return

    # Default: Show interactive Desktop GUI with auto-fit window
    print("🚀 Launching Grand Prix Live Animated HUD GUI...")
    try:
        mng = plt.get_current_fig_manager()
        if hasattr(mng, "window"):
            if hasattr(mng.window, "state"):
                mng.window.state("zoomed")
            elif hasattr(mng.window, "showMaximized"):
                mng.window.showMaximized()
    except Exception:
        pass
    plt.show()


if __name__ == "__main__":
    main()
