import asyncio
import base64
import json
import os
import queue
import threading
import pyaudio
import websockets
from dotenv import load_dotenv

load_dotenv()

RIME_API_KEY = os.getenv("RIME_API_KEY")
if not RIME_API_KEY:
    raise ValueError("❌ RIME_API_KEY not set in environment variables")

SAMPLE_RATE = 22050
BYTES_PER_SAMPLE = 2  # 16-bit PCM
BYTES_PER_MS = (SAMPLE_RATE * BYTES_PER_SAMPLE) // 1000

PREBUFFER_MS = 300  # tune this: higher = smoother but more startup latency


def audio_player_thread(audio_queue: queue.Queue, stop_event: threading.Event):
    """Runs in its own thread so network jitter never causes underruns."""
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, output=True)

    try:
        while not stop_event.is_set() or not audio_queue.empty():
            try:
                chunk = audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if chunk is None:  # sentinel = done
                break

            stream.write(chunk)

    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


async def speak(text: str, speaker: str = "astra", model_id: str = "coda"):
    url = f"wss://users-ws.rime.ai/ws3?speaker={speaker}&modelId={model_id}&audioFormat=pcm&samplingRate={SAMPLE_RATE}"
    headers = {"Authorization": f"Bearer {RIME_API_KEY}"}

    audio_queue = queue.Queue()
    stop_event = threading.Event()

    # Start playback in a background thread — isolated from network timing
    player = threading.Thread(target=audio_player_thread, args=(audio_queue, stop_event))
    player.start()

    prebuffer = []
    prebuffered_bytes = 0
    started = False
    leftover = b""  # carries over an odd trailing byte between chunks

    prebuffer_target_bytes = PREBUFFER_MS * BYTES_PER_MS

    try:
        async with websockets.connect(url, additional_headers=headers) as ws:
            await ws.send(json.dumps({"text": text}))
            await ws.send(json.dumps({"operation": "eos"}))

            async for message in ws:
                event = json.loads(message)

                if event["type"] == "chunk":
                    audio_bytes = leftover + base64.b64decode(event["data"])

                    # Keep chunks sample-aligned (even byte count for 16-bit PCM)
                    if len(audio_bytes) % 2 != 0:
                        leftover = audio_bytes[-1:]
                        audio_bytes = audio_bytes[:-1]
                    else:
                        leftover = b""

                    if not audio_bytes:
                        continue

                    if not started:
                        prebuffer.append(audio_bytes)
                        prebuffered_bytes += len(audio_bytes)
                        if prebuffered_bytes >= prebuffer_target_bytes:
                            for c in prebuffer:
                                audio_queue.put(c)
                            prebuffer.clear()
                            started = True
                    else:
                        audio_queue.put(audio_bytes)

                elif event["type"] == "done":
                    # flush any leftover prebuffered audio (short utterances)
                    for c in prebuffer:
                        audio_queue.put(c)
                    prebuffer.clear()
                    break

                elif event["type"] == "error":
                    print(f"❌ Rime error: {event}")
                    break

    finally:
        stop_event.set()
        audio_queue.put(None)  # sentinel to unblock the player thread
        player.join()


if __name__ == "__main__":
    asyncio.run(speak("Hello Atul, this should sound smooth now, no glitches."))