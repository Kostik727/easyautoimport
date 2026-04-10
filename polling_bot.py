"""
Polling bot for @easyautoimport
Handles: /start, /saved, /help, /subscribe, /admin, callback queries
Also runs Copart scraper, reminders, and digest in background threads.
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

import users

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
API = "https://api.telegram.org/bot" + BOT_TOKEN
SCRAPE_INTERVAL = 10 * 60  # every 10 minutes

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Kaspi payment link (phone number for transfer)
KASPI_PHONE = "+77476899519"
KASPI_URL = "https://kaspi.kz/pay/" + KASPI_PHONE.replace("+", "")

CHANNEL_MAP = {
    "jp": {"label": "🇯🇵 Японские", "channel_id": "@easyautoimport"},
    "us": {"label": "🇺🇸 Американские", "channel_id": "@easyautoimportusa"},
    "eu": {"label": "🇩🇪 Немецкие", "channel_id": "@easyautoimporteu"},
    "kr": {"label": "🇰🇷 Корейские", "channel_id": "@easyautoimportkr"},
}

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


# ---- Telegram helpers ----

def send(method, **kwargs):
    try:
        r = requests.post(API + "/" + method, json=kwargs, timeout=15)
        return r.json()
    except Exception as e:
        log.error("send %s error: %s", method, e)
        return {}


def send_form(method, data=None, files=None):
    try:
        r = requests.post(API + "/" + method, data=data, files=files, timeout=15)
        return r.json()
    except Exception as e:
        log.error("send_form %s error: %s", method, e)
        return {}


def answer_callback(cb_id, text):
    send("answerCallbackQuery", callback_query_id=cb_id, text=text, show_alert=False)


# ---- channel selection keyboard ----

def build_channel_keyboard(user_id):
    user = users.get_user(user_id)
    selected = user.get("channels", []) if user else []
    rows = []
    for key, info in CHANNEL_MAP.items():
        check = "✅" if key in selected else "⬜"
        rows.append([{"text": "%s %s" % (check, info["label"]), "callback_data": "ch_%s" % key}])
    rows.append([{"text": "✔️ Готово", "callback_data": "ch_done"}])
    rows.append([{"text": "🟡 Kaspi.kz — Оплатить подписку", "url": KASPI_URL}])
    return {"inline_keyboard": rows}


# ---- handlers ----

def handle_start(chat_id, user):
    user_id = user.get("id", 0)
    username = user.get("username", "")
    first_name = user.get("first_name", "")
    users.get_or_create_user(user_id, username, first_name)

    text = (
        "Привет, %s! 👋\n\n"
        "Я бот <b>Easy Auto Import</b> — нахожу лучшие авто с аукциона Copart (США) и доставляю в Казахстан.\n\n"
        "📌 <b>Как это работает:</b>\n"
        "1. Выберите категории авто ниже\n"
        "2. Получайте лоты каждые 10 минут в канал\n"
        "3. Нажимайте ❤️ на понравившемся лоте\n"
        "4. Получайте напоминания перед аукционом\n"
        "5. Напишите менеджеру для покупки\n\n"
        "🎁 <b>Первые 2 дня — бесплатно!</b>\n"
        "Вам доступны все функции: сохранение лотов, напоминания об аукционах и ежедневный дайджест лучших предложений.\n\n"
        "💳 После пробного периода — <b>5 000 ₸/мес</b>\n"
        "Оплата через Kaspi. Подробнее: /subscribe\n\n"
        "👇 <b>Выберите интересующие категории:</b>"
    ) % (first_name or "друг")

    kb = build_channel_keyboard(user_id)
    send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)


def handle_saved(chat_id, user_id):
    sub = users.check_subscription(user_id)
    lots = users.get_saved_lots(user_id)

    if not lots:
        send("sendMessage", chat_id=chat_id, text="У вас пока нет сохраненных лотов.\nНажмите ❤️ на постах канала.")
        return

    if sub == "expired":
        # Show limited + upsell
        lines = ["💾 <b>Ваши сохраненные лоты:</b>\n"]
        for lot_id in lots[-3:]:
            lines.append('<a href="https://www.copart.com/lot/%s">Lot #%s</a>' % (lot_id, lot_id))
        lines.append("\n🔒 Подписка истекла. Показаны 3 из %d." % len(lots))
        lines.append("Используйте /subscribe для продления.")
        send("sendMessage", chat_id=chat_id, text="\n".join(lines), parse_mode="HTML",
             disable_web_page_preview=True)
        return

    lines = ["💾 <b>Ваши сохраненные лоты:</b>\n"]
    for lot_id in lots[-20:]:
        lines.append('<a href="https://www.copart.com/lot/%s">Lot #%s</a>' % (lot_id, lot_id))
    if len(lots) > 20:
        lines.append("\n... и ещё %d" % (len(lots) - 20))
    send("sendMessage", chat_id=chat_id, text="\n".join(lines), parse_mode="HTML",
         disable_web_page_preview=True)


def handle_help(chat_id):
    text = (
        "🔧 <b>Помощь</b>\n\n"
        "/start - выбрать категории авто\n"
        "❤️ Сохранить - сохранить лот из канала\n"
        "/saved - посмотреть сохраненные\n"
        "/subscribe - подписка\n"
        "/help - эта справка\n\n"
        "Каналы:\n"
        "🇯🇵 @easyautoimport\n"
        "🇺🇸 @easyautoimportusa\n"
        "🇩🇪 @easyautoimporteu\n"
        "🇰🇷 @easyautoimportkr"
    )
    send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


def handle_subscribe(chat_id, user_id):
    info = users.get_subscription_info(user_id)
    status = info["status"]
    sub_type = info["type"]
    expires = info.get("expires_at", "")

    if status == "active":
        exp_display = ""
        try:
            dt = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%S")
            exp_display = dt.strftime("%d.%m.%Y %H:%M")
        except (ValueError, TypeError):
            exp_display = expires
        label = "Пробный период" if sub_type == "trial" else "Подписка"
        text = "✅ %s активен до <b>%s</b>" % (label, exp_display)
        send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")
        return

    text = (
        "🔒 <b>Подписка истекла</b>\n\n"
        "С подпиской вы получаете:\n"
        "• Сохранение лотов ❤️\n"
        "• Напоминания об аукционах ⏰\n"
        "• Ежедневный дайджест лучших лотов 📊\n\n"
        "Стоимость: <b>5 000 ₸/мес</b>\n\n"
        "Оплатите через Kaspi и отправьте скриншот."
    )
    kb = {"inline_keyboard": [
        [{"text": "🟡 Kaspi.kz — Оплатить 5 000 ₸", "url": KASPI_URL}],
        [{"text": "📸 Отправить скриншот оплаты", "callback_data": "payment_screenshot"}],
    ]}
    send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)


# ---- admin ----

def handle_admin(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        return

    parts = args.strip().split()
    cmd = parts[0] if parts else "help"

    if cmd == "saves":
        save_log = users.get_save_log()
        if not save_log:
            send("sendMessage", chat_id=chat_id, text="Нет сохранений.")
            return
        lines = ["<b>Последние сохранения:</b>\n"]
        for entry in save_log[-20:]:
            lines.append("@%s → Lot #%s (%s)" % (
                entry.get("username", "?"),
                entry.get("lot_id", "?"),
                entry.get("at", "")[:16],
            ))
        send("sendMessage", chat_id=chat_id, text="\n".join(lines), parse_mode="HTML")

    elif cmd == "users":
        stats = users.get_all_users_stats()
        text = (
            "<b>Пользователи:</b>\n"
            "Всего: %d\n"
            "Trial: %d\n"
            "Paid: %d\n"
            "Expired: %d"
        ) % (stats["total"], stats["trial"], stats["paid"], stats["expired"])
        send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")

    elif cmd == "user" and len(parts) >= 2:
        uid = parts[1]
        u = users.get_user(uid)
        if not u:
            send("sendMessage", chat_id=chat_id, text="Пользователь не найден.")
            return
        sub_status = users.check_subscription(int(uid))
        text = (
            "<b>User #%s</b>\n"
            "Username: @%s\n"
            "Имя: %s\n"
            "Каналы: %s\n"
            "Подписка: %s (%s)\n"
            "Сохранено лотов: %d\n"
            "Регистрация: %s"
        ) % (
            uid,
            u.get("username", "-"),
            u.get("first_name", "-"),
            ", ".join(u.get("channels", [])) or "-",
            u.get("subscription", {}).get("status", "-"),
            sub_status,
            len(u.get("saved_lots", [])),
            u.get("registered_at", "-")[:16],
        )
        send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")

    elif cmd == "activate" and len(parts) >= 2:
        uid = parts[1]
        days = int(parts[2]) if len(parts) >= 3 else 30
        ok = users.activate_subscription(int(uid), days, admin_id=user_id)
        if ok:
            send("sendMessage", chat_id=chat_id,
                 text="✅ Подписка активирована для %s на %d дней." % (uid, days))
            # Notify user
            send("sendMessage", chat_id=int(uid),
                 text="🎉 Ваша подписка активирована на %d дней! Спасибо за оплату." % days)
        else:
            send("sendMessage", chat_id=chat_id, text="Пользователь не найден.")

    else:
        text = (
            "<b>Admin команды:</b>\n"
            "/admin saves - последние сохранения\n"
            "/admin users - статистика\n"
            "/admin user ID - инфо о пользователе\n"
            "/admin activate ID [DAYS] - активировать подписку"
        )
        send("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


# ---- callback handlers ----

def handle_callback(cb):
    cb_id = cb["id"]
    data = cb.get("data", "")
    user = cb.get("from", {})
    user_id = user.get("id", 0)
    msg = cb.get("message", {})

    # Channel toggle
    if data.startswith("ch_"):
        key = data[3:]
        if key == "done":
            u = users.get_user(user_id)
            channels = u.get("channels", []) if u else []
            if not channels:
                answer_callback(cb_id, "Выберите хотя бы один канал!")
                return
            labels = [CHANNEL_MAP[c]["label"] for c in channels if c in CHANNEL_MAP]
            answer_callback(cb_id, "Готово!")
            text = "✅ Вы подписаны на:\n" + "\n".join(labels)
            text += "\n\nЛоты публикуются каждые 10 минут. Нажмите ❤️ на понравившемся!"
            send("sendMessage", chat_id=msg.get("chat", {}).get("id", user_id), text=text)
            return

        if key in CHANNEL_MAP:
            users.toggle_channel(user_id, key)
            kb = build_channel_keyboard(user_id)
            send("editMessageReplyMarkup",
                 chat_id=msg.get("chat", {}).get("id", user_id),
                 message_id=msg.get("message_id"),
                 reply_markup=kb)
            answer_callback(cb_id, CHANNEL_MAP[key]["label"])
            return

    # Save lot
    if data.startswith("save_"):
        lot_id = data[5:]
        sub = users.check_subscription(user_id)
        if sub == "expired":
            answer_callback(cb_id, "🔒 Подписка истекла. /subscribe")
            return
        # Ensure user exists
        username = user.get("username", "")
        first_name = user.get("first_name", "")
        users.get_or_create_user(user_id, username, first_name)
        added = users.add_saved_lot(user_id, lot_id)
        if added:
            answer_callback(cb_id, "❤️ Сохранено! /saved")
            log.info("User %s saved lot %s", user_id, lot_id)
        else:
            answer_callback(cb_id, "Уже сохранено!")
        return

    # Payment screenshot
    if data == "payment_screenshot":
        users.set_awaiting_payment(user_id, True)
        answer_callback(cb_id, "Отправьте скриншот оплаты в этот чат")
        send("sendMessage", chat_id=msg.get("chat", {}).get("id", user_id),
             text="📸 Отправьте скриншот оплаты через Kaspi в этот чат.")
        return


def handle_photo(msg):
    """Handle photo messages — check if it's a payment screenshot."""
    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]

    if not users.is_awaiting_payment(user_id):
        return

    users.set_awaiting_payment(user_id, False)

    # Forward to admin
    if ADMIN_ID:
        send("forwardMessage", chat_id=ADMIN_ID, from_chat_id=chat_id,
             message_id=msg["message_id"])
        u = users.get_user(user_id)
        username = u.get("username", "") if u else ""
        send("sendMessage", chat_id=ADMIN_ID,
             text="💳 Скриншот оплаты от @%s (ID: %s)\n/admin activate %s 30" % (
                 username, user_id, user_id),
             parse_mode="HTML")

    send("sendMessage", chat_id=chat_id,
         text="✅ Скриншот получен! Ожидайте подтверждения оплаты.")


# ---- update router ----

def process_update(update):
    if "callback_query" in update:
        handle_callback(update["callback_query"])
        return

    msg = update.get("message")
    if not msg:
        return

    chat_id = msg["chat"]["id"]
    user_from = msg.get("from", {})
    user_id = user_from.get("id", 0)
    text = (msg.get("text") or "").strip()

    # Photo handling (payment screenshots)
    if msg.get("photo"):
        handle_photo(msg)
        return

    if text == "/start":
        handle_start(chat_id, user_from)
    elif text == "/saved":
        handle_saved(chat_id, user_id)
    elif text == "/help":
        handle_help(chat_id)
    elif text == "/subscribe":
        handle_subscribe(chat_id, user_id)
    elif text.startswith("/admin"):
        args = text[6:].strip()
        handle_admin(chat_id, user_id, args)


# ---- background scraper ----

def scraper_loop():
    """Run copart scraper every SCRAPE_INTERVAL seconds."""
    log.info("Scraper thread started, interval=%ds", SCRAPE_INTERVAL)
    time.sleep(30)
    from copart_bot import run_scraper
    while True:
        try:
            log.info("Running Copart scraper...")
            posted = run_scraper()
            log.info("Scraper finished, posted %s lots", posted)
        except Exception as e:
            log.error("Scraper error: %s", e, exc_info=True)
            try:
                requests.post(API + "/sendMessage", json={
                    "chat_id": "@easyautoimport",
                    "text": "⚠️ Scraper error: %s" % str(e)[:200],
                }, timeout=10)
            except Exception:
                pass
        # Backup users after each scraper run
        try:
            users.backup_users()
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

        lot = {}
        try:
            cache_file = os.path.join(os.path.dirname(__file__) or ".", "lot_cache.json")
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                lot = cache.get(lot_id, {})
        except Exception:
            pass

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

    # Restore users from backup if needed
    users.restore_users()
    # Migrate saved_lots.json → users.json
    users.migrate_saved_lots()

    # Start HTTP server
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start scraper
    scraper_thread = threading.Thread(target=scraper_loop, daemon=True)
    scraper_thread.start()

    # Start reminders
    try:
        from reminders import reminder_loop
        reminder_thread = threading.Thread(target=reminder_loop, daemon=True)
        reminder_thread.start()
    except ImportError:
        log.warning("reminders module not found, skipping")

    # Start digest
    try:
        from digest import digest_loop
        digest_thread = threading.Thread(target=digest_loop, daemon=True)
        digest_thread.start()
    except ImportError:
        log.warning("digest module not found, skipping")

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
