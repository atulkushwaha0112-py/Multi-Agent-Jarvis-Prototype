"""tools/music_tools.py — YouTube music playback tools for LangGraph."""

from langchain_core.tools import tool
from voice_music_app_fixed import play_music, stop_music


@tool
def play_music_tool(query: str) -> str:
    """
    Search YouTube and play audio for the given song or artist query.
    Automatically stops any currently playing music before starting the new one.
    Use this when the user says 'play', 'put on', or names a song/artist.
    query: song name, artist, or description (e.g. 'Believer by Imagine Dragons').
    """
    try:
        return play_music(query)
    except Exception as e:
        return f"Could not play music: {e}"


@tool
def stop_music_tool() -> str:
    """
    Stop the currently playing music immediately.
    Use this when the user says 'stop', 'pause', 'stop the music', or 'quiet'.
    No arguments needed.
    """
    try:
        return stop_music()
    except Exception as e:
        return f"Could not stop music: {e}"
