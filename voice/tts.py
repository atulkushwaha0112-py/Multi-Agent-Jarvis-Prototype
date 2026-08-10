"""
voice/tts.py — Synchronous TTS wrapper around rime.py's async speak() coroutine.

Usage:
    from voice.tts import speak
    speak("Hello, this is JARVIS.")
"""

import asyncio
import sys

# Import the async speak from rime.py at project root
# (rime.py raises ValueError at import if RIME_API_KEY is missing — let it bubble up)
import rime


def speak(text: str, speaker: str = "astra", model_id: str = "coda") -> None:
    """
    Speak `text` aloud using the Rime TTS API.

    Synchronous wrapper: blocks until all audio has finished playing.
    Internally calls `asyncio.run(rime.speak(...))`.

    Parameters
    ----------
    text     : str  — text to synthesise and play.
    speaker  : str  — Rime voice ID (default 'astra').
    model_id : str  — Rime model (default 'coda').
    """
    if not text or not text.strip():
        return

    # Truncate extremely long responses to avoid very long TTS waits
    max_chars = 600
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"

    try:
        # asyncio.run creates a fresh event loop — safe to call from any sync context
        asyncio.run(rime.speak(text, speaker=speaker, model_id=model_id))
    except Exception as e:
        # TTS failure should never crash the voice loop
        print(f"[TTS] Error: {e}", file=sys.stderr)
