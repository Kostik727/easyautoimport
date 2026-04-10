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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
API = "https://api.telegram.org/bot" + BOT_TOKEN
SAVED_FILE = "saved_lots.json"
SCRAPE_INTERVAL = 10 * 60  # every 10 minutes

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
        "Привет! 👋\n\n"
        "Я бот канала @easyautoimport.\n"
        "Нажмите ❤️ Сохранить на постах канала,\n"
        "чтобы сохранять лоты.\n\n"
        "Команды:\n"
        "/saved - мои сохраненные\n"
        "/help - помощь"
    )
    send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


def handle_saved(chat_id, user_id):
    data = load_saved()
    user_lots = data.get(str(user_id), [])
    if not user_lots:
        send("sendMessage", chat_id=chat_id, text="У вас пока нет сохраненных лотов.")
        return
    lines = ["💾 <b>Ваши сохраненные лоты:</b>\n"]
    for lot_id in user_lots[-20:]:
        lines.append('<a href="https://www.copart.com/lot/%s">Lot #%s</a>' % (lot_id, lot_id))
    send("sendMessage", chat_id=chat_id, text="\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


def handle_help(chat_id):
    text = (
        "🔧 <b>Помощь</b>\n\n"
        "❤️ Сохранить - сохранить лот\n"
        "/saved - посмотреть сохраненные\n"
        "/help - эта справка"
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
            answer_callback(cb_id, "Уже сохранено!")
            return
        user_lots.append(lot_id)
        saved[user_id] = user_lots
        save_saved(saved)
        answer_callback(cb_id, "❤️ Сохранено! /saved")
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
    from copart_bot import run_scraper
    while True:
        try:
            log.info("Running Copart scraper...")
            posted = run_scraper()
            log.info("Scraper finished, posted %s lots", posted)
        except Exception as e:
            log.error("Scraper error: %s", e, exc_info=True)
            # Notify in channel about errors
            try:
                requests.post(API + "/sendMessage", json={
                    "chat_id": "@easyautoimport",
                    "text": "⚠️ Scraper error: %s" % str(e)[:200],
                }, timeout=10)
            except Exception:
                pass
        time.sleep(SCRAPE_INTERVAL)


# ---- calendar HTTP server ----

CAL_PORT = int(os.environ.get("PORT", 8080))

APP_HOST = "https://easyautoimport-production.up.railway.app"

class CalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path in ("/cal", "/cal.ics"):
            self._serve_ics(params)
        elif parsed.path == "/calc":
            self._serve_calc(params)
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_ics(self, params):
        title = params.get("t", ["Аукцион Copart"])[0]
        date = params.get("d", [""])[0]
        lot = params.get("l", [""])[0]
        if not date:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing date param")
            return
        end_date = params.get("de", [date])[0]
        url = "https://www.copart.com/lot/%s" % lot if lot else ""
        ics = (
            "BEGIN:VCALENDAR\r\n"
            "VERSION:2.0\r\n"
            "PRODID:-//EasyAutoImport//Bot//EN\r\n"
            "BEGIN:VEVENT\r\n"
            "DTSTART:%s\r\n"
            "DTEND:%s\r\n"
            "DTSTAMP:%s\r\n"
            "SUMMARY:%s\r\n"
            "DESCRIPTION:Лот #%s\\n%s\r\n"
            "URL:%s\r\n"
            "END:VEVENT\r\n"
            "END:VCALENDAR\r\n"
        ) % (date, end_date, datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
             title, lot, url, url)
        data = ics.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/calendar; charset=utf-8")
        self.send_header("Content-Disposition", "attachment; filename=auction_%s.ics" % lot)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_calc(self, params):
        lot_id = params.get("l", [""])[0]
        if not lot_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing lot param")
            return

        # Load lot from cache
        lot = {}
        try:
            cache_file = os.path.join(os.path.dirname(__file__) or ".", "lot_cache.json")
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                lot = cache.get(lot_id, {})
        except Exception:
            pass

        # Build message text like in channel
        lines = ["Здравствуйте, меня интересует этот автомобиль!", ""]
        lines.append("🚗 %s" % lot.get("title", "Лот #%s" % lot_id))
        lines.append("")
        if lot.get("price"):
            lines.append("💰 Текущая ставка: $%s" % lot["price"])
        if lot.get("damage"):
            lines.append("🔧 Повреждение: %s" % lot["damage"])
        if lot.get("odometer"):
            try:
                odo_km = int(float(lot["odometer"]) * 1.64)
                lines.append("📏 Пробег: %s км" % "{:,}".format(odo_km).replace(",", " "))
            except (ValueError, TypeError):
                lines.append("📏 Пробег: %s км" % lot["odometer"])
        if lot.get("engine"):
            lines.append("⚙️ Двигатель: %s" % lot["engine"])
        if lot.get("drive"):
            lines.append("🔄 Привод: %s" % lot["drive"])
        if lot.get("fuel"):
            lines.append("⛽ Топливо: %s" % lot["fuel"])
        if lot.get("color"):
            lines.append("🎨 Цвет: %s" % lot["color"])
        if lot.get("vin"):
            lines.append("🔑 VIN: %s" % lot["vin"])
        lines.append("")
        copart_url = lot.get("url", "https://www.copart.com/lot/%s" % lot_id)
        lines.append("🔗 Лот #%s на Copart" % lot_id)
        lines.append(copart_url)

        msg_text = "\n".join(lines)
        from urllib.parse import quote as url_quote
        tg_url = "https://t.me/+77476899519?text=%s" % url_quote(msg_text)

        # Serve HTML page that redirects to Telegram
        html = (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="refresh" content="0;url=%s">'
            '<title>Рассчитать под ключ</title>'
            '</head><body style="font-family:sans-serif;text-align:center;padding:40px;">'
            '<p>Открываем чат с менеджером...</p>'
            '<p><a href="%s">Нажмите сюда, если не перенаправило</a></p>'
            '</body></html>'
        ) % (tg_url, tg_url)
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        log.info("HTTP: " + fmt, *args)


def start_http_server():
    server = HTTPServer(("0.0.0.0", CAL_PORT), CalHandler)
    log.info("Calendar HTTP server on port %d", CAL_PORT)
    server.serve_forever()


# ---- main polling loop ----

def main():
    log.info("=" * 50)
    log.info("Polling bot started")
    log.info("=" * 50)

    # Start HTTP server for .ics calendar links
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

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
