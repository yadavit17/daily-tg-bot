import json
import os
import random
import requests

TOKEN = os.environ["BOT_TOKEN"]
CHAT_IDS = [int(os.environ["CHAT_ID_1"]), int(os.environ["CHAT_ID_2"])]

MESSAGES_FILE = "messages.json"
STATE_FILE = "state.json"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    messages = load_json(MESSAGES_FILE)
    if not messages:
        raise SystemExit("messages.json пуст — добавь хотя бы одно сообщение")

    state = load_json(STATE_FILE)
    remaining = state.get("remaining", [])

    # Если пул закончился (или это первый запуск) — перемешиваем заново
    if not remaining:
        remaining = list(range(len(messages)))
        random.shuffle(remaining)

    idx = remaining.pop()
    text = messages[idx]

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        resp = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=15)
        if not resp.ok:
            print(f"Ошибка отправки для chat_id={chat_id}: {resp.status_code} {resp.text}")
            resp.raise_for_status()

    state["remaining"] = remaining
    save_json(STATE_FILE, state)

    print(f"Отправлено сообщение #{idx}: {text}")
    print(f"Осталось в пуле до следующего перемешивания: {len(remaining)}")


if __name__ == "__main__":
    main()
