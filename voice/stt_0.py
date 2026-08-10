"""
voice/stt.py — Speech-to-text using OpenAI Whisper (local, CUDA GPU).

Replaces Google STT with a local Whisper model for much better accuracy,
especially with accented/Indian English and noisy environments.
Model is loaded once and cached — fast from the second call onward.

Usage:
    from voice.stt import listen_and_transcribe
    text = listen_and_transcribe()
"""
import sys
sys.dont_write_bytecode = True

import os
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()

# ── Helpers defined FIRST so they can be used below ─────────────────────

def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# ── Config ───────────────────────────────────────────────────────────────

SAMPLE_RATE  = 16000                             # Whisper requires 16 kHz
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base.en")  # base.en = fast English
DEVICE       = "cuda" if _cuda_available() else "cpu"

_raw_index   = os.getenv("MIC_DEVICE_INDEX", "").strip()
MIC_DEVICE_INDEX: int | None = int(_raw_index) if _raw_index else None


# ── Whisper model — loaded once, cached globally ─────────────────────────

_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print(f"[STT] Loading Whisper '{WHISPER_MODEL}' on {DEVICE}...")
        _whisper_model = whisper.load_model(WHISPER_MODEL, device=DEVICE)
        print("[STT] Whisper ready ✅")
    return _whisper_model


# ── Recording ────────────────────────────────────────────────────────────

def _record_until_silence(
    samplerate: int = SAMPLE_RATE,
    device: int | None = MIC_DEVICE_INDEX,
    silence_threshold: float = 0.015,  # RMS amplitude; tune lower in quiet rooms
    silence_duration: float = 1.2,     # seconds of quiet before stopping
    max_duration: float = 12.0,        # hard cap — never record longer than this
    min_duration: float = 0.4,         # discard recordings shorter than this
) -> np.ndarray | None:
    """
    Record from the microphone until silence is detected.
    Returns a float32 mono numpy array at SAMPLE_RATE, or None if silent.
    """
    chunk_size         = int(samplerate * 0.1)    # 100 ms windows
    max_chunks         = int(max_duration  * samplerate / chunk_size)
    silence_needed     = int(silence_duration * samplerate / chunk_size)

    frames        = []
    silent_chunks = 0
    speaking      = False

    sd_kwargs = {"device": device} if device is not None else {}

    print("[STT] Listening...")
    with sd.InputStream(samplerate=samplerate, channels=1, dtype="float32", **sd_kwargs) as stream:
        for _ in range(max_chunks):
            chunk, _ = stream.read(chunk_size)
            rms = float(np.sqrt(np.mean(chunk ** 2)))

            if rms > silence_threshold:
                speaking = True
                silent_chunks = 0
                frames.append(chunk)
            elif speaking:
                frames.append(chunk)
                silent_chunks += 1
                if silent_chunks >= silence_needed:
                    break  # enough silence after speech → done

    if not speaking:
        return None

    audio = np.concatenate(frames, axis=0).flatten()
    if len(audio) / samplerate < min_duration:
        return None   # too short — probably noise

    return audio


# ── Public API ───────────────────────────────────────────────────────────

def listen_and_transcribe(
    device_index: int | None = MIC_DEVICE_INDEX,
    language: str = "en",
) -> str | None:
    """
    Listen from the microphone and return transcribed text via local Whisper.

    Parameters
    ----------
    device_index : int | None  — mic device index, None = system default
    language     : str         — Whisper language code (default 'en')

    Returns
    -------
    str   — transcribed text (stripped) on success
    None  — if nothing heard or transcription failed
    """
    try:
        audio = _record_until_silence(device=device_index)
        if audio is None:
            print("[STT] No speech detected.")
            return None

        model  = _get_model()
        result = model.transcribe(audio, language=language, fp16=(DEVICE == "cuda"))
        text   = result.get("text", "").strip()

        if not text:
            print("[STT] Empty transcript.")
            return None

        print(f"[STT] Heard: {text}")
        return text

    except Exception as e:
        print(f"[STT] Error: {e}")
        return None


if __name__ == "__main__":
    print("Speak now...")
    t = listen_and_transcribe()
    print("Transcript:", t)
