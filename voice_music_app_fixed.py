"""
voice_music_app_fixed.py — pure music playback module.

Provides: get_youtube_audio_url, play_music, stop_music
Module-level `player` handle tracks the active subprocess.

No CLI, no TTS, no speech recognition — intent is handled by the LangGraph agent.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# MPV path — set MPV_PATH in .env or fall back to hardcoded location
MPV_PATH = os.getenv(
    "MPV_PATH",
    r"C:\Users\ATUL\Downloads\mpv-x86_64-20260810-git-513d3407d4\mpv.exe"
)

# Module-level player handle — None means nothing is playing
player = None


def get_youtube_audio_url(query: str) -> str | None:
    """
    Uses yt-dlp to resolve a YouTube search query into a direct audio stream URL.
    Returns the URL string, or None on failure.
    """
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "--no-playlist",
                "--quiet",
                "--no-warnings",
                "-f", "bestaudio/best",
                "--get-url",
                f"ytsearch1:{query}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"[yt-dlp error] {result.stderr}")
            return None

        urls = [x.strip() for x in result.stdout.splitlines() if x.strip()]
        return urls[-1] if urls else None

    except Exception as e:
        print(f"[yt-dlp] {e}")
        return None


def stop_music() -> str:
    """
    Stops the currently playing MPV process if one exists.
    Returns a status string for logging.
    """
    global player

    if player is not None:
        try:
            if player.poll() is None:
                player.terminate()
                player.wait(timeout=2)
        except Exception:
            try:
                player.kill()
            except Exception:
                pass
        player = None
        return "Music stopped."
    return "Nothing was playing."


def play_music(query: str) -> str:
    """
    Stops any current playback, resolves `query` via yt-dlp, then streams
    the audio through MPV in the background.
    Returns a status string.
    """
    global player

    stop_music()
    print(f"[music] Searching YouTube for: {query}")

    audio_url = get_youtube_audio_url(query)

    if not audio_url:
        return f"Could not find audio for: {query}"

    try:
        player = subprocess.Popen(
            [
                MPV_PATH,
                "--no-video",
                "--really-quiet",
                audio_url,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"Playing: {query}"
    except FileNotFoundError:
        return "MPV not found. Set MPV_PATH in .env"
    except Exception as e:
        return f"Could not start playback: {e}"
