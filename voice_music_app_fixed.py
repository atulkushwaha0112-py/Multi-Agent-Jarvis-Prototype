import subprocess
import sys
import argparse

MPV_PATH = r"C:\Users\Shivam Pandey\Downloads\mpv-x86_64-20260810-git-513d3407d4\mpv.exe"
player = None


def speak(text, tts=None):
    print(f"ECHO: {text}")
    if tts:
        try:
            tts.say(text)
            tts.runAndWait()
        except Exception:
            pass


def stop_music(tts=None, announce=True):
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

        if announce:
            speak("Music stopped.", tts)
    elif announce:
        speak("Nothing is playing.", tts)


def get_youtube_audio_url(query):
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
            print(result.stderr)
            return None

        urls = [x.strip() for x in result.stdout.splitlines() if x.strip()]
        return urls[-1] if urls else None

    except Exception as e:
        print(f"[yt-dlp] {e}")
        return None


def play_music(query, tts=None):
    global player

    stop_music(tts, announce=False)
    speak(f"Searching YouTube for {query}.", tts)

    audio_url = get_youtube_audio_url(query)

    if not audio_url:
        speak("I couldn't find that song.", tts)
        return

    speak(f"Playing {query}.", tts)

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
    except FileNotFoundError:
        speak("MPV was not found.", tts)
    except Exception as e:
        print(f"[MPV] {e}")
        speak("I couldn't start the music.", tts)


def extract_song_name(command):
    text = command.lower().strip()

    for prefix in [
        "please play the song ",
        "please play ",
        "play the song ",
        "play song ",
        "play ",
    ]:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break

    for suffix in [
        " on youtube music",
        " in youtube music",
        " on youtube",
        " in youtube",
    ]:
        if text.endswith(suffix):
            text = text[:-len(suffix)].strip()

    return text.strip()


def handle_command(command, tts=None):
    command = command.lower().strip()

    if command in ["stop", "stop music", "stop the music", "stop playing"]:
        stop_music(tts)
        return True

    if command in ["exit", "quit", "bye", "shutdown", "close jarvis"]:
        stop_music(tts, announce=False)
        speak("Goodbye! Enjoy the music.", tts)
        return False

    if command.startswith("play "):
        query = extract_song_name(command)
        if query:
            play_music(query, tts)
        else:
            speak("Tell me the song name.", tts)
        return True

    if command in ["help", "what can you do"]:
        speak("Say play followed by a song name, stop, or exit.", tts)
        return True

    speak("I didn't understand. Say play followed by a song name.", tts)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()

    tts = None
    try:
        import pyttsx3
        tts = pyttsx3.init()
    except Exception as e:
        print(f"[TTS] unavailable: {e}")

    recognizer = None
    microphone = None

    if not args.text:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
        except Exception as e:
            print(f"[Microphone] unavailable: {e}")
            print("Use --text for now.")
            args.text = True

    speak("JARVIS music assistant is ready.", tts)

    try:
        while True:
            if args.text:
                command = input("Command: ").strip()
            else:
                import speech_recognition as sr

                try:
                    with microphone as source:
                        print("[Listening...]")
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio = recognizer.listen(
                            source, timeout=8, phrase_time_limit=10
                        )

                    try:
                        command = recognizer.recognize_google(audio)
                        print(f"You: {command}")
                    except sr.UnknownValueError:
                        speak("I didn't understand that.", tts)
                        continue
                    except sr.RequestError as e:
                        print(f"[Speech recognition] {e}")
                        continue

                except sr.WaitTimeoutError:
                    continue

            if not handle_command(command, tts):
                break

    except KeyboardInterrupt:
        print("\nJARVIS: Goodbye!")

    finally:
        stop_music(tts, announce=False)


if __name__ == "__main__":
    main()
