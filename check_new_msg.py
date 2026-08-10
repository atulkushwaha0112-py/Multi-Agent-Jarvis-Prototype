
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