import pyautogui
import time
import pyperclip

# -------- YOUR COORDINATE --------
SEARCH_BOX = (284, 126)
# --------------------------------

def send_whatsapp_desktop(name, message):
    print("🚀 Starting WhatsApp automation...")

    # Step 1: Open Start Menu
    pyautogui.press('win')
    time.sleep(1)

    # Step 2: Search WhatsApp
    pyautogui.write('WhatsApp', interval=0.05)
    time.sleep(1)

    # Step 3: Open WhatsApp
    pyautogui.press('enter')
    time.sleep(2)  # wait for app to open

    # Step 4: Click Search Box
    pyautogui.click(SEARCH_BOX)
    time.sleep(1)

    # Step 5: Clear old search
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')

    # Step 6: Type Name
    pyautogui.write(name, interval=0.05)
    time.sleep(1)

    # Step 7: Open Chat
    pyautogui.press('enter')
    time.sleep(1)

    # Step 8: Paste Message (better than typing)
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)

    # Step 9: Send Message
    pyautogui.press('enter')

    print(f"✅ Message sent to {name}")

    time.sleep(2)

    # Step 10: Close WhatsApp
    pyautogui.hotkey('alt', 'f4')


# -------- TEST --------
if __name__ == "__main__":
    send_whatsapp_desktop("arnav singh", "Hello from MJ ")

