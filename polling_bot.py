"""
Polling bot: long-running service that handles /start and Save callback.
Deploy on Railway with Procfile: worker: python polling_bot.py
"""

import os
import json
import time
import logging
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
MANAGER_PHONE = "https://t.me/+77476899519"
CALCULATOR_URL = "https://t.me/+77476899519"

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO, handlers=[logging.StreamHandler()])
log = logging.getLogger(__name__)

saved_lots = {}
SAVED_FILE = "saved_lots.json"


def load_saved():
    global saved_lots
    if os.path.exists(SAVED_FILE):
        try:
            with open(SAVED_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                saved_lots = {int(k): v for k, v in raw.items()}
            log.info("Loaded %d users saved lots", len(saved_lots))
        except Exception as e:
            log.warning("Could not load saved lots: %s", e)


def persist_saved():
    try:
        with open(SAVED_FILE, "w", encoding="utf-8") as f:
            json.dump(saved_lots, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.warning("Could not persist saved lots: %s", e)


def tg(method, **kwargs):
    url = f"{API}/{method}"
    try:
        resp = requests.post(url, json=kwargs, timeout=60)
        return resp.json()
    except Exception as e:
        log.error("TG API error %s: %s", method, e)
        return {}


def answer_callback(callback_id, text, show_alert=False):
    tg("answerCallbackQuery", callback_query_id=callback_id, text=text, show_alert=show_alert)


def handle_start(message):
    chat_id = message["chat"]["id"]
    first = message["from"].get("first_name", "")
    tg("sendMessage", chat_id=chat_id, text=f"\u041f\u0440\u0438\u0432\u0435\u0442, {first}! \ud83d\udc4b\n\n\u042f \u0431\u043e\u0442 \u043a\u0430\u043d\u0430\u043b\u0430 @easyautoimport.\n\n\u041a\u043e\u0433\u0434\u0430 \u0443\u0432\u0438\u0434\u0438\u0448\u044c \u0438\u043d\u0442\u0435\u0440\u0435\u0441\u043d\u044b\u0439 \u043b\u043e\u0442 \u0432 \u043a\u0430\u043d\u0430\u043b\u0435 \u2014 \u043d\u0430\u0436\u043c\u0438 \u2764\ufe0f <b>\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c</b>, \u0438 \u044f \u043f\u0440\u0438\u0448\u043b\u044e \u0442\u0435\u0431\u0435 \u0435\u0433\u043e \u0441\u044e\u0434\u0430.\n\n\u041a\u043e\u043c\u0430\u043d\u0434\u044b:\n/saved \u2014 \u043c\u043e\u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0435 \u043b\u043e\u0442\u044b\n/help \u2014 \u043f\u043e\u043c\u043e\u0449\u044c", parse_mode="HTML")

def handle_saved(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    lots = saved_lots.get(user_id, [])
    if not lots:
        tg("sendMessage", chat_id=chat_id, text="У тебя пока нет сохранённых лотов.\nНажми ❤️ Сохранить на любом посте в @easyautoimport!")
        return
    lines = ["<b>Твои сохранённые лоты:</b>\n"]
    for lot_id in lots[-20:]:
        url = f"https://www.copart.com/lot/{lot_id}"
        lines.append(f'\u2022 <a href="{url}">Лот #{lot_id}</a>')
    lines.append(f"\nВсего: {len(lots)}")
    tg("sendMessage", chat_id=chat_id, text="\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


def handle_help(message):
    chat_id = message["chat"]["id"]
    tg("sendMessage", chat_id=chat_id, text="<b>Как пользоваться:</b>\n\n1. Подпишись на @easyautoimport\n2. Когда увидишь интересный лот — нажми ❤️ <b>Сохранить</b>\n3. Я пришлю тебе ссылку на лот в личку\n\n📩 <a href=\"" + MANAGER_PHONE + "\">Написать менеджеру</a>\n📊 <a href=\"" + CALCULATOR_URL + "\">Рассчитать стоимость</a>", parse_mode="HTML", disable_web_page_preview=True)


def handle_callback(callback_query):
    cb_id = callback_query["id"]
    data = callback_query.get("data", "")
    user = callback_query.get("from", {})
    user_id = user.get("id")
    first = user.get("first_name", "")

    if not data.startswith("save_"):
        answer_callback(cb_id, "Неизвестная команда")
        return

    lot_id = data.replace("save_", "", 1)
    lot_url = f"https://www.copart.com/lot/{lot_id}"

    if user_id not in saved_lots:
        saved_lots[user_id] = []

    if lot_id in saved_lots[user_id]:
        answer_callback(cb_id, "✅ Этот лот уже сохранён!", show_alert=False)
        return

    saved_lots[user_id].append(lot_id)
    persist_saved()

    answer_callback(cb_id, "❤️ Лот сохранён!", show_alert=False)

    keyboard = json.dumps({"inline_keyboard": [[{"text": "📩 Написать менеджеру", "url": MANAGER_PHONE}, {"text": "📊 Рассчитать", "url": CALCULATOR_URL}]]})
    tg("sendMessage", chat_id=user_id, text=f"❤️ <b>Лот сохранён!</b>\n\n<a href=\"{lot_url}\">Открыть лот #{lot_id} на Copart</a>\n\n📩 <a href=\"{MANAGER_PHONE}\">Написать менеджеру</a>\n📊 <a href=\"{CALCULATOR_URL}\">Рассчитать под ключ</a>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)

    log.info("User %s (%s) saved lot %s", user_id, first, lot_id)


def process_update(update):
    if "callback_query" in update:
        handle_callback(update["callback_query"])
        return
    msg = update.get("message")
    if not msg:
        return
    text = (msg.get("text") or "").strip()
    if text == "/start":
        handle_start(msg)
    elif text == "/saved":
        handle_saved(msg)
    elif text == "/help":
        handle_help(msg)


def main():
    log.info("=" * 50)
    log.info("Polling bot started")
    log.info("=" * 50)

    load_saved()

    offset = 0
    while True:
        try:
            resp = requests.get(
                f"{API}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35,
            )
            data = resp.json()
            if not data.get("ok"):
                log.warning("getUpdates not ok: %s", data)
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    process_update(update)
                except Exception as e:
                    log.error("Error processing update: %s", e, exc_info=True)

        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            log.error("Polling error: %s", e, exc_info=True)
            time.sleep(5)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
