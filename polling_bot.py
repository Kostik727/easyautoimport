"""
Polling bot for @easyautoimport
Handles: /start, /saved, /help, callback queries (save button)
Also runs Copart scraper periodically in a background thread.
"""

import os
import json
import time
import logging
import threading
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
API = "https://api.telegram.org/bot" + BOT_TOKEN
SAVED_FILE = "saved_lots.json"
SCRAPE_INTERVAL = 3 * 3600  # every 3 hours

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


# ---- saved lots persistence ----

def load_saved():
    if os.path.exists(SAVED_FILE):
        with open(SAVED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_saved(data):
    with open(SAVED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---- Telegram helpers ----

def send(method, **kwargs):
    try:
        r = requests.post(API + "/" + method, json=kwargs, timeout=15)
        return r.json()
    except Exception as e:
        log.error("send %s error: %s", method, e)
        return {}


def answer_callback(cb_id, text):
    send("answerCallbackQuery", callback_query_id=cb_id, text=text, show_alert=False)


# ---- handlers ----

def handle_start(chat_id):
    text = (
        "\u041f\u0440\u0438\u0432\u0435\u0442! \u{1F44B}\n\n"
        "\u042f \u0431\u043e\u0442 \u043a\u0430\u043d\u0430\u043b\u0430 @easyautoimport.\n"
        "\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u2764\ufe0f \u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043d\u0430 \u043f\u043e\u0441\u0442\u0430\u0445 \u043a\u0430\u043d\u0430\u043b\u0430,\n"
        "\u0447\u0442\u043e\u0431\u044b \u0441\u043e\u0445\u0440\u0430\u043d\u044f\u0442\u044c \u043b\u043e\u0442\u044b.\n\n"
        "\u041a\u043e\u043c\u0430\u043d\u0434\u044b:\n"
        "/saved - \u043c\u043e\u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0435\n"
        "/help - \u043f\u043e\u043c\u043e\u0449\u044c"
    )
    send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


def handle_saved(chat_id, user_id):
    data = load_saved()
    user_lots = data.get(str(user_id), [])
    if not user_lots:
        send("sendMessage", chat_id=chat_id, text="\u0423 \u0432\u0430\u0441 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0445 \u043b\u043e\u0442\u043e\u0432.")
        return
    lines = ["\u{1F4BE} <b>\u0412\u0430\u0448\u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0435 \u043b\u043e\u0442\u044b:</b>\n"]
    for lot_id in user_lots[-20:]:
        lines.append('<a href="https://www.copart.com/lot/%s">Lot #%s</a>' % (lot_id, lot_id))
    send("sendMessage", chat_id=chat_id, text="\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


def handle_help(chat_id):
    text = (
        "\u{1F527} <b>\u041f\u043e\u043c\u043e\u0449\u044c</b>\n\n"
        "\u2764\ufe0f \u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c - \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043b\u043e\u0442\n"
        "/saved - \u043f\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0435\n"
        "/help - \u044d\u0442\u0430 \u0441\u043f\u0440\u0430\u0432\u043a\u0430"
    )
    send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


def handle_callback(cb):
    cb_id = cb["id"]
    data = cb.get("data", "")
    user = cb.get("from", {})
    user_id = str(user.get("id", ""))

    if data.startswith("save_"):
        lot_id = data[5:]
        saved = load_saved()
        user_lots = saved.get(user_id, [])
        if lot_id in user_lots:
            answer_callback(cb_id, "\u0423\u0436\u0435 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043e!")
            return
        user_lots.append(lot_id)
        saved[user_id] = user_lots
        save_saved(saved)
        answer_callback(cb_id, "\u2764\ufe0f \u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043e! /saved")
        log.info("User %s saved lot %s", user_id, lot_id)


def process_update(update):
    if "callback_query" in update:
        handle_callback(update["callback_query"])
        return

    msg = update.get("message")
    if not msg:
        return

    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    text = (msg.get("text") or "").strip()

    if text == "/start":
        handle_start(chat_id)
    elif text == "/saved":
        handle_saved(chat_id, user_id)
    elif text == "/help":
        handle_help(chat_id)


# ---- background scraper ----

def scraper_loop():
    """Run copart scraper every SCRAPE_INTERVAL seconds."""
    log.info("Scraper thread started, interval=%ds", SCRAPE_INTERVAL)
    # Wait 30 seconds before first run to let bot stabilize
    time.sleep(30)
    while True:
        try:
            log.info("Running Copart scraper...")
            from copart_bot import run_scraper
            posted = run_scraper()
            log.info("Scraper finished, posted %s lots", posted)
        except Exception as e:
            log.error("Scraper error: %s", e, exc_info=True)
        time.sleep(SCRAPE_INTERVAL)


# ---- main polling loop ----

def main():
    log.info("=" * 50)
    log.info("Polling bot started")
    log.info("=" * 50)

    # Start scraper in background thread
    t = threading.Thread(target=scraper_loop, daemon=True)
    t.start()

    offset = 0
    while True:
        try:
            resp = requests.get(
                API + "/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35
            )
            updates = resp.json().get("result", [])
            for u in updates:
                offset = u["update_id"] + 1
                try:
                    process_update(u)
                except Exception as e:
                    log.error("process error: %s", e, exc_info=True)
        except Exception as e:
            log.error("polling error: %s", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
