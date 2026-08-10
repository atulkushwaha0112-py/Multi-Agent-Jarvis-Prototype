"""
main.py — Jarvis voice loop entry point.

Flow per turn:
  1. listen_and_transcribe()          → raw text from mic
  2. Fast-path stop-music check       → stop_music() directly (no LLM round-trip)
  3. app.invoke()                     → LangGraph agent processes the request
  4. Extract last AIMessage content   → reply text
  5. speak(reply)                     → Rime TTS plays the response
  6. Repeat until KeyboardInterrupt

Run with the Jarvis venv Python (NOT system python):
    Jarvis\Scripts\python.exe main.py
"""
import sys
sys.dont_write_bytecode = True  # always load source files, never stale .pyc

import sys
from langchain_core.messages import HumanMessage, AIMessage

from graph import app
from state import AgentState
from voice.stt import listen_and_transcribe
from voice.tts import speak
from voice_music_app_fixed import stop_music

# ──────────────────────────────────────────────────────────────
# Phrases that trigger the music-stop fast-path
# (bypasses the LLM entirely for zero-latency response)
# ──────────────────────────────────────────────────────────────

STOP_MUSIC_TRIGGERS = {
    "stop",
    "stop music",
    "stop the music",
    "stop playing",
    "pause",
    "pause music",
    "quiet",
    "silence",
    "mute",
}


def _extract_reply(result: dict) -> str:
    """Pull the last AIMessage content from a graph invocation result."""
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return str(msg.content)
    return "I'm sorry, I didn't get a response."


def voice_loop():
    """
    Main continuous voice loop.
    Initialises conversation state once, then processes turns indefinitely.
    """
    # ── Boot greeting ──────────────────────────────────────────
    boot_msg = "Jarvis is ready. How can I help you?"
    print(f"\n {boot_msg}\n")
    speak(boot_msg)

    # ── Persistent LangGraph state across turns ────────────────
    state: AgentState = {
        "messages": [],
        "music": None,
        "last_contact": None,
        "pending_confirmation": None,
        "turn_count": 0,
    }

    print("Listening… (Ctrl+C to quit)\n")

    while True:
        try:
            # ── 1. Listen ──────────────────────────────────────
            user_text = listen_and_transcribe()

            if not user_text:
                # Timeout or nothing heard — keep looping silently
                continue

            print(f"🎤 You: {user_text}")

            # ── 2. Fast-path: stop-music triggers ─────────────
            if user_text.strip().lower() in STOP_MUSIC_TRIGGERS:
                status = stop_music()
                print(f"🎵 [fast-path] {status}")
                speak("Music stopped.")
                continue

            # ── 3. Invoke LangGraph ────────────────────────────
            state["messages"] = state["messages"] + [HumanMessage(content=user_text)]

            result = app.invoke(state)

            # Merge returned state (LangGraph returns a full state dict)
            state.update(result)

            # ── 4. Extract reply ───────────────────────────────
            reply = _extract_reply(result)
            print(f" Jarvis: {reply}\n")

            # ── 5. Speak ───────────────────────────────────────
            speak(reply)

        except KeyboardInterrupt:
            print("\n\nJarvis: Goodbye!")
            speak("Goodbye!")
            stop_music()
            sys.exit(0)
        except Exception as e:
            err_msg = "Something went wrong. Please try again."
            print(f"[ERROR] {e}")
            speak(err_msg)


if __name__ == "__main__":
    voice_loop()
