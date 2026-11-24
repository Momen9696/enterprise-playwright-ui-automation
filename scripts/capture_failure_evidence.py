#!/usr/bin/env python3
"""Run one intentional UI failure and confirm screenshot, trace, and video files."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    shots = ROOT / "artifacts" / "screenshots"
    traces = ROOT / "artifacts" / "traces"
    videos = ROOT / "artifacts" / "videos"
    for folder in (shots, traces, videos):
        if folder.exists():
            shutil.rmtree(folder)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests/meta/test_failure_artifacts.py",
        "-m",
        "evidence",
        "-o",
        "addopts=-ra --tb=line",
        "--browser",
        "chromium",
        "--record-video",
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    pngs = list(shots.glob("*.png")) if shots.exists() else []
    zips = list(traces.glob("*.zip")) if traces.exists() else []
    movies = list(videos.rglob("*.webm")) + list(videos.rglob("*.mp4")) if videos.exists() else []
    print(f"pytest exit code: {completed.returncode}")
    print(f"screenshots: {len(pngs)}")
    print(f"traces: {len(zips)}")
    print(f"videos: {len(movies)}")
    if completed.returncode == 0 or not pngs or not zips or not movies:
        print("Failure artifacts were not captured.")
        return 1
    for path in pngs + zips + movies:
        print(f"captured {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
