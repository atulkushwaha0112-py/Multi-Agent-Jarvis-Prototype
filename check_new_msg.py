import pyautogui
import time
import requests
import base64
import io
import os
from dotenv import load_dotenv

# ==============================
# LOAD ENV
# ==============================

load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

# Load multiple API keys
API_KEYS = [
    os.getenv("API_KEY_OLLAMA"),
]

MODEL = "gemma4:cloud"

SEARCH_BOX = (284, 126)
UNREAD_BUTTON_POS = (172, 170)
ALL_BUTTON_POS = (105, 166)  # same button toggles back to "All" — update if different

CHAT_LIST_REGION = (67, 193, 575, 648)


# ==============================
# FUNCTIONS
# ==============================

def open_whatsapp():
    print("[INFO] Opening WhatsApp...")
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write('WhatsApp')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)


def click_unread_filter():
    print("[INFO] Clicking 'Unread' filter...")
    pyautogui.click(UNREAD_BUTTON_POS)
    time.sleep(2)


def clear_search():
    print("[INFO] Clearing search box...")
    pyautogui.click(SEARCH_BOX)
    time.sleep(1)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.5)
    pyautogui.press("backspace")
    time.sleep(1)


def capture_image_base64():
    print("[INFO] Capturing chat list...")
    img = pyautogui.screenshot(region=CHAT_LIST_REGION)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def click_all_filter():
    print("[INFO] Clicking 'All chats'...")
    pyautogui.click(ALL_BUTTON_POS)
    time.sleep(2)


def close_whatsapp():
    print("[INFO] Closing WhatsApp...")
    pyautogui.hotkey("alt", "f4")


def analyze_with_gemma(base64_image):
    print("[INFO] Sending to Gemma (with key rotation)...")

    prompt = """
    This is a WhatsApp chat list filtered to unread chats.

    Extract ONLY the names of people or groups that have unread messages.

    Return strictly as a Python list.
    """

    for key in API_KEYS:
        if not key:
            continue

        try:
            print(f"[TRY] Using API KEY: {key[:5]}***")

            response = requests.post(
                OLLAMA_API_URL,
                headers={
                    "Authorization": f"Bearer {key}"
                },
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "images": [base64_image],
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                print("[✔] Success with current key")
                return response.json().get("response", "")
            else:
                print(f"[WARN] Failed with key: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] Key failed: {str(e)}")

    return "[ERROR] All API keys failed"


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    open_whatsapp()

    click_unread_filter()   # 1. click unread
    clear_search()          # 2. clear search bar
    img_base64 = capture_image_base64()  # 3. take screenshot

    click_all_filter()      # 4. click all
    close_whatsapp()        # 5. close whatsapp

    result = analyze_with_gemma(img_base64)

    print("\n====== GEMMA OUTPUT ======\n")
    print(result)