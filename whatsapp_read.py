import pyautogui
import time
import pyperclip

# ==============================
# CONFIG (UPDATE IF NEEDED)
# ==============================

SEARCH_BAR = (284, 126)          # your search bar position
BOTTOM_MSG = (1564, 767)         # your captured latest message position
OFFSET_Y = 500                   # how many messages to capture
ALL_BUTTON_POS = (105, 166)  # same button toggles back to "All" — update if different

def click_all_filter():
    print("[INFO] Clicking 'All chats'...")
    pyautogui.click(ALL_BUTTON_POS)
    time.sleep(2)

# ==============================
# CORE FUNCTIONS
# ==============================



def open_whatsapp():
    pyautogui.press('win')
    time.sleep(1)

    pyautogui.write('WhatsApp')
    time.sleep(1)

    pyautogui.press('enter')
    time.sleep(2)


def open_chat(name):
    pyautogui.click(SEARCH_BAR)
    time.sleep(1)

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')

    pyautogui.write(name, interval=0.05)
    time.sleep(1)

    pyautogui.press('enter')
    time.sleep(1)


def select_messages():
    # Scroll a bit to load messages
    pyautogui.scroll(1000)
    time.sleep(1)

    # Click latest message
    pyautogui.click(BOTTOM_MSG)
    time.sleep(1)

    # Select upward using SHIFT
    pyautogui.keyDown('shift')
    pyautogui.click(BOTTOM_MSG[0], BOTTOM_MSG[1] - OFFSET_Y)
    pyautogui.keyUp('shift')

    time.sleep(1)


def copy_messages():
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(2)
    return pyperclip.paste()


def close_whatsapp():
    pyautogui.hotkey('alt', 'f4')


# ==============================
# MAIN FUNCTION
# ==============================

def get_whatsapp_messages(name):
    open_whatsapp()

    click_all_filter()

    open_chat(name)

    select_messages()
    messages = copy_messages()

    close_whatsapp()

    return messages


# For Manula Checkup RUN

if __name__ == "__main__":
    contact_name = "Shivam pandey"   # CHANGE THIS

    msgs = get_whatsapp_messages(contact_name)

    print("\n========== WHATSAPP MESSAGES ==========\n")
    print(msgs)
