"""
Daily digest and engagement module.
Sends best lots digest and educational tips to users.
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
CHECK_INTERVAL = 30 * 60  # check every 30 minutes

CHANNEL_KEY_MAP = {
    "@easyautoimport": "jp",
    "@easyautoimportusa": "us",
    "@easyautoimporteu": "eu",
    "@easyautoimportkr": "kr",
}

TIPS = [
    "💡 <b>Совет:</b> «Run and Drive» означает, что автомобиль заводится и может передвигаться своим ходом. Это лучший вариант для покупки!",
    "💡 <b>Совет:</b> Обращайте внимание на тип повреждения. «Normal Wear» — минимальные следы эксплуатации, самый безопасный выбор.",
    "💡 <b>Совет:</b> Проверяйте VIN на сайте NICB (nicb.org) бесплатно — узнаете историю аварий и страховых случаев.",
    "💡 <b>Совет:</b> Аукционная цена — это только начало. Добавьте ~15-20% на доставку, таможню и оформление в КЗ.",
    "💡 <b>Совет:</b> Лоты с пометкой «Clean Title» имеют чистую историю без серьёзных ДТП или списаний.",
    "💡 <b>Совет:</b> Следите за одометром. Средний пробег в США — 20 000 км/год. Если сильно больше — автомобиль активно использовался.",
    "💡 <b>Совет:</b> Японские и корейские авто — лучший выбор по надёжности и стоимости запчастей в Казахстане.",
    "💡 <b>Совет:</b> Дизельные авто дороже растаможить в КЗ. Бензин и гибрид — выгоднее.",
    "💡 <b>Совет:</b> Аукцион длится 1-2 минуты на лот. Определите максимальный бюджет заранее и не превышайте его.",
    "💡 <b>Совет:</b> Полный привод (AWD/4WD) востребован в КЗ — такие авто легче перепродать.",
]


def load_cache() -> dict:
    if not os.path.exists(LOT_CACHE_FILE):
        return {}
    try:
        with open(LOT_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_fresh_lots(cache, channel_keys, hours=24):
    """Get lots cached in the last N hours matching given channel keys."""
    now = datetime.utcnow()
    result = []
    for lot_id, lot in cache.items():
        # Check freshness
        cached_at = lot.get("cached_at", "")
        try:
            dt = datetime.strptime(cached_at, "%Y-%m-%dT%H:%M:%S")
            if (now - dt).total_seconds() > hours * 3600:
                continue
        except (ValueError, TypeError):
            continue

        # Check channel match
        ch_id = lot.get("channel_id", "")
        ch_key = CHANNEL_KEY_MAP.get(ch_id)
        if ch_key and ch_key in channel_keys:
            lot["_lot_id"] = lot_id
            result.append(lot)

    # Sort by price (highest first) for "best" lots
    result.sort(key=lambda x: x.get("price") or 0, reverse=True)
    return result[:5]


def send_digest(user_id, lots):
    """Send daily digest to a user."""
    lines = ["🔥 <b>Новые лоты по вашим категориям!</b>\n"]
    for i, lot in enumerate(lots, 1):
        price_str = "$%s" % lot["price"] if lot.get("price") else "нет ставок"
        lines.append('%d. 🚗 <a href="%s">%s</a> — %s' % (
            i,
            lot.get("url", "https://www.copart.com/lot/%s" % lot.get("_lot_id", "")),
            lot.get("title", "?"),
            price_str,
        ))
    lines.append("\nНажмите ❤️ на понравившемся лоте в канале!")

    try:
        requests.post(API + "/sendMessage", json={
            "chat_id": user_id,
            "text": "\n".join(lines),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=10)
        log.info("Digest sent to %s (%d lots)", user_id, len(lots))
    except Exception as e:
        log.warning("Digest send failed to %s: %s", user_id, e)


def send_tip(user_id, tip_index):
    """Send an educational tip."""
    tip = TIPS[tip_index % len(TIPS)]
    try:
        requests.post(API + "/sendMessage", json={
            "chat_id": user_id,
            "text": tip,
            "parse_mode": "HTML",
        }, timeout=10)
    except Exception as e:
        log.warning("Tip send failed to %s: %s", user_id, e)


def run_digest():
    """Send daily digest and weekly tips to eligible users."""
    cache = load_cache()
    if not cache:
        return

    all_users = users.load_users()
    now = datetime.utcnow()
    tip_index = now.timetuple().tm_yday  # rotate tips by day of year

    for uid, u in all_users.items():
        if uid.startswith("_"):
            continue

        # Check subscription
        if users.check_subscription(int(uid)) != "active":
            continue

        channels = u.get("channels", [])
        if not channels:
            continue

        # Daily digest — at most once per 24h
        last_digest = u.get("last_digest_at")
        send_daily = True
        if last_digest:
            try:
                last_dt = datetime.strptime(last_digest, "%Y-%m-%dT%H:%M:%S")
                if (now - last_dt).total_seconds() < 24 * 3600:
                    send_daily = False
            except (ValueError, TypeError):
                pass

        if send_daily:
            lots = get_fresh_lots(cache, channels)
            if lots:
                send_digest(int(uid), lots)
                users.update_last_digest(int(uid))
                time.sleep(0.5)  # rate limit

        # Weekly tip — check if registered_at day aligns (every 7 days)
        reg = u.get("registered_at", "")
        try:
            reg_dt = datetime.strptime(reg, "%Y-%m-%dT%H:%M:%S")
            days_since = (now - reg_dt).days
            if days_since > 0 and days_since % 7 == 0:
                # Only send once per day — use last_digest as proxy
                if send_daily:
                    send_tip(int(uid), tip_index)
                    time.sleep(0.5)
        except (ValueError, TypeError):
            pass


def digest_loop():
    """Background thread: run digest checks every 30 minutes."""
    log.info("Digest thread started, interval=%ds", CHECK_INTERVAL)
    time.sleep(120)  # wait for bot to stabilize
    while True:
        try:
            run_digest()
        except Exception as e:
            log.error("Digest loop error: %s", e, exc_info=True)
        time.sleep(CHECK_INTERVAL)
