"""
Auction reminder background thread.
Checks lot_cache.json for upcoming auctions and notifies users who saved those lots.
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta, timezone

import users

log = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
API = "https://api.telegram.org/bot" + BOT_TOKEN
LOT_CACHE_FILE = "lot_cache.json"
CHECK_INTERVAL = 5 * 60  # check every 5 minutes


def _parse_auction_date(ad):
    """Parse auction_date to UTC datetime."""
    if isinstance(ad, (int, float)):
        return datetime.fromtimestamp(ad / 1000, tz=timezone.utc)
    if isinstance(ad, str) and ad:
        return datetime.strptime(ad, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return None


def _format_astana(dt_utc):
    """Format UTC datetime as Astana (UTC+5) string."""
    dt_kz = dt_utc + timedelta(hours=5)
    return dt_kz.strftime("%d.%m.%Y %H:%M")


def send_reminder(user_id, lot, reminder_type):
    """Send auction reminder to a user."""
    time_label = "1 час" if reminder_type == "1h" else "15 минут"
    ad = lot.get("auction_date")
    try:
        dt_utc = _parse_auction_date(ad)
        time_str = _format_astana(dt_utc) if dt_utc else "?"
    except (ValueError, TypeError):
        time_str = "?"

    text = (
        "⏰ <b>Напоминание!</b> Через %s аукцион:\n\n"
        "🚗 <b>%s</b>\n"
    ) % (time_label, lot.get("title", "?"))

    if lot.get("price"):
        text += "💰 Текущая ставка: $%s\n" % lot["price"]
    text += "📅 Аукцион: %s (Астана)\n\n" % time_str
    text += '<a href="%s">🔗 Лот #%s на Copart</a>' % (
        lot.get("url", ""), lot.get("_lot_id", ""))

    try:
        requests.post(API + "/sendMessage", json={
            "chat_id": user_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=10)
        log.info("Reminder %s sent to %s for lot %s", reminder_type, user_id, lot.get("_lot_id"))
    except Exception as e:
        log.warning("Reminder send failed: %s", e)


def check_reminders():
    """Check lot_cache for upcoming auctions and send reminders."""
    if not os.path.exists(LOT_CACHE_FILE):
        return

    try:
        with open(LOT_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        return

    now = datetime.now(timezone.utc)

    for lot_id, lot in cache.items():
        ad = lot.get("auction_date")
        if not ad:
            continue

        try:
            dt_utc = _parse_auction_date(ad)
            if not dt_utc:
                continue
        except (ValueError, TypeError):
            continue

        minutes_until = (dt_utc - now).total_seconds() / 60

        # Determine which reminders to send
        reminders_to_send = []
        if 55 <= minutes_until <= 65:
            reminders_to_send.append("1h")
        if 10 <= minutes_until <= 20:
            reminders_to_send.append("15m")

        if not reminders_to_send:
            continue

        # Find users who saved this lot
        user_ids = users.get_users_with_saved_lot(lot_id)
        if not user_ids:
            continue

        lot["_lot_id"] = lot_id

        for uid in user_ids:
            # Check subscription
            if users.check_subscription(uid) != "active":
                continue

            for rtype in reminders_to_send:
                if users.was_reminder_sent(uid, lot_id, rtype):
                    continue
                send_reminder(uid, lot, rtype)
                users.mark_reminder_sent(uid, lot_id, rtype)
                time.sleep(0.5)  # rate limit


def reminder_loop():
    """Background thread: check for upcoming auctions every 5 minutes."""
    log.info("Reminder thread started, interval=%ds", CHECK_INTERVAL)
    time.sleep(60)  # wait for bot to stabilize
    while True:
        try:
            check_reminders()
        except Exception as e:
            log.error("Reminder loop error: %s", e, exc_info=True)
        time.sleep(CHECK_INTERVAL)
