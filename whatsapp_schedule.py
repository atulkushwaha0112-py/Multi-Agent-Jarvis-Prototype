import pyautogui
import time
import datetime

# ==============================
# CONFIG
# ==============================

CONTACT_NAME = "Mummy"   # exact name in WhatsApp
MESSAGE = "Hello! This is a scheduled message 🚀"
SEND_TIME = "23:10"  # 24-hour format HH:MM


# ==============================
# FUNCTIONS
# ==============================

def wait_until_time(target_time):
    print(f"[INFO] Waiting until {target_time}...")
    
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now == target_time:
            print("[✔] Time reached!")
            break
        time.sleep(10)


def open_whatsapp():
    print("[INFO] Opening WhatsApp...")
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write('WhatsApp')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)


def search_contact(name):
    print(f"[INFO] Searching contact: {name}")
    
    # CTRL + F (search)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.write(name)
    time.sleep(2)
    
    pyautogui.press('enter')
    time.sleep(2)


def send_message(msg):
    print("[INFO] Sending message...")
    
    pyautogui.write(msg)
    time.sleep(1)
    
    pyautogui.press('enter')
    print("[✔] Message Sent!")


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    
    wait_until_time(SEND_TIME)
    
    open_whatsapp()

    
    
    search_contact(CONTACT_NAME)
    
    send_message(MESSAGE)