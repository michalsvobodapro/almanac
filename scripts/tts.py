"""Best-effort text-to-speech for the weekly synthesis (English only).

Tries, in order:
  1. Piper (set PIPER_VOICE to a .onnx voice; PIPER_BIN or `piper` on PATH) — CI.
  2. macOS `say` — local dev.
Both pipe through ffmpeg to MP3. Returns the public-relative audio path, or
None if no engine is available (the caller then ships a text-only weekly).

The weekly essay is English (site chrome language), so a single English voice
is enough — sidestepping the bilingual-TTS quality problem entirely.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = REPO_ROOT / "public" / "audio"


def _build_text(result: dict[str, Any]) -> str:
    parts: list[str] = [result.get("title", ""), result.get("dek", ""), result.get("intro", "")]
    for s in result.get("sections", []):
        if s.get("heading"):
            parts.append(s["heading"].rstrip(".") + ".")
        if s.get("body"):
            parts.append(s["body"])
    return "\n\n".join(p for p in parts if p and p.strip())


def _to_mp3(src: Path, dest: Path) -> bool:
    if not shutil.which("ffmpeg"):
        return False
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
             "-codec:a", "libmp3lame", "-qscale:a", "5", str(dest)],
            check=True,
        )
        return dest.exists() and dest.stat().st_size > 0
    except subprocess.SubprocessError:
        return False


def _piper(text: str, dest: Path) -> bool:
    voice = os.environ.get("PIPER_VOICE")
    binary = os.environ.get("PIPER_BIN") or shutil.which("piper")
    if not voice or not binary or not Path(voice).exists():
        return False
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "weekly.wav"
        try:
            subprocess.run(
                [binary, "-m", voice, "-f", str(wav)],
                input=text.encode("utf-8"), check=True,
            )
        except subprocess.SubprocessError:
            return False
        if not wav.exists():
            return False
        return _to_mp3(wav, dest)


def _macos_say(text: str, dest: Path) -> bool:
    if sys.platform != "darwin" or not shutil.which("say"):
        return False
    with tempfile.TemporaryDirectory() as td:
        txt = Path(td) / "weekly.txt"
        txt.write_text(text, encoding="utf-8")
        aiff = Path(td) / "weekly.aiff"
        try:
            subprocess.run(["say", "-f", str(txt), "-o", str(aiff)], check=True)
        except subprocess.SubprocessError:
            return False
        if not aiff.exists():
            return False
        return _to_mp3(aiff, dest)


def synthesize_weekly_audio(end: date, result: dict[str, Any]) -> str | None:
    """Render the weekly essay to public/audio/weekly-<isoweek>.mp3.
    Returns the public-relative path, or None if no TTS engine is available."""
    text = _build_text(result)
    if not text.strip():
        return None
    iso = end.isocalendar()
    week_id = f"{iso[0]}-W{iso[1]:02d}"
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    dest = AUDIO_DIR / f"weekly-{week_id}.mp3"
    if _piper(text, dest) or _macos_say(text, dest):
        return f"/audio/weekly-{week_id}.mp3"
    return None
