"""
Telegram Bot: monitor copart.com and post to multiple channels
🇺🇸 @easyautoimport — American brands
🇯🇵 @easyautoimportjp — Japanese brands
🇩🇪 @easyautoimporteu — German brands
🇰🇷 @easyautoimportkr — Korean brands
"""

import os
import re
import json
import time
import logging
import requests
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
SEEN_FILE  = "seen_lots.json"
MAX_POSTS  = 5   # post up to 5 lots per channel per run
MIN_YEAR   = 2020

COOLDOWN_HOURS = 6  # don't repost same lot within this period

# ---- Channel configurations ----

CHANNELS = [
    {
        "id": "@easyautoimport",
        "name": "Japanese",
        "makes": {"TOYOTA", "LEXUS", "HONDA", "ACURA", "NISSAN", "INFINITI",
                  "MAZDA", "SUBARU", "MITSUBISHI"},
        "brand_priority": ["LEXUS", "TOYOTA", "HONDA", "NISSAN"],
        "queries": [
            "Lexus RX run and drive",
            "Lexus NX run and drive",
            "Lexus ES run and drive",
            "Lexus GX run and drive",
            "Lexus LX run and drive",
            "Toyota Camry run and drive",
            "Toyota Corolla run and drive",
            "Toyota RAV4 run and drive",
            "Toyota Highlander run and drive",
            "Toyota 4Runner run and drive",
            "Toyota Tacoma run and drive",
            "Toyota Tundra run and drive",
            "Toyota Sienna run and drive",
            "Toyota Prius run and drive",
            "Toyota Sequoia run and drive",
            "Toyota Land Cruiser run and drive",
            "Honda CR-V run and drive",
            "Honda Civic run and drive",
            "Honda Accord run and drive",
            "Honda Pilot run and drive",
            "Acura MDX run and drive",
            "Nissan Rogue run and drive",
            "Nissan Pathfinder run and drive",
            "Infiniti QX80 run and drive",
            "Mazda CX-5 run and drive",
            "Subaru Outback run and drive",
            "Subaru Forester run and drive",
        ],
    },
    {
        "id": "@easyautoimporteu",
        "name": "German",
        "makes": {"BMW", "MERCEDES-BENZ", "AUDI", "VOLKSWAGEN", "PORSCHE"},
        "brand_priority": ["BMW", "MERCEDES-BENZ", "AUDI", "PORSCHE"],
        "queries": [
            "BMW X5 run and drive",
            "BMW X3 run and drive",
            "BMW 3 Series run and drive",
            "BMW 5 Series run and drive",
            "BMW X7 run and drive",
            "Mercedes-Benz GLE run and drive",
            "Mercedes-Benz GLC run and drive",
            "Mercedes-Benz E-Class run and drive",
            "Audi Q5 run and drive",
            "Audi Q7 run and drive",
            "Volkswagen Tiguan run and drive",
            "Porsche Cayenne run and drive",
        ],
    },
    {
        "id": "@easyautoimportusa",
        "name": "American",
        "makes": {"FORD", "CHEVROLET", "DODGE", "GMC", "JEEP", "RAM",
                  "CADILLAC", "LINCOLN", "TESLA"},
        "brand_priority": ["FORD", "TESLA", "CHEVROLET", "JEEP"],
        "queries": [
            "Ford F-150 run and drive",
            "Ford Explorer run and drive",
            "Ford Mustang run and drive",
            "Ford Bronco run and drive",
            "Ford Expedition run and drive",
            "Chevrolet Tahoe run and drive",
            "Chevrolet Silverado run and drive",
            "GMC Yukon run and drive",
            "Jeep Grand Cherokee run and drive",
            "Jeep Wrangler run and drive",
            "Dodge Durango run and drive",
            "RAM 1500 run and drive",
            "Cadillac Escalade run and drive",
            "Lincoln Navigator run and drive",
            "Tesla Model Y run and drive",
            "Tesla Model 3 run and drive",
        ],
    },
    {
        "id": "@easyautoimportkr",
        "name": "Korean",
        "makes": {"HYUNDAI", "KIA", "GENESIS"},
        "brand_priority": ["HYUNDAI", "KIA", "GENESIS"],
        "queries": [
            "Hyundai Tucson run and drive",
            "Hyundai Santa Fe run and drive",
            "Hyundai Sonata run and drive",
            "Hyundai Palisade run and drive",
            "Kia Sportage run and drive",
            "Kia Sorento run and drive",
            "Kia Telluride run and drive",
            "Genesis GV80 run and drive",
        ],
    },
]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

MANAGER_PHONE = "https://t.me/+77476899519"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.copart.com/",
    "Origin": "https://www.copart.com",
}


BACKUP_CHAT_ID = os.environ.get("BACKUP_CHAT_ID", BOT_TOKEN.split(":")[0])


def load_seen() -> dict:
    # Try local file first
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {lot_id: "2000-01-01T00:00:00" for lot_id in data}
            for k, v in data.items():
                if isinstance(v, int):
                    data[k] = "2000-01-01T00:00:00"
            if data:
                return data

    # File missing or empty — restore from Telegram backup
    log.info("Restoring seen_lots from Telegram backup...")
    try:
        resp = requests.post(
            "https://api.telegram.org/bot%s/getChat" % BOT_TOKEN,
            json={"chat_id": BACKUP_CHAT_ID}, timeout=10
        )
        pinned = resp.json().get("result", {}).get("pinned_message", {})
        doc = pinned.get("document")
        if doc:
            file_resp = requests.get(
                "https://api.telegram.org/bot%s/getFile" % BOT_TOKEN,
                params={"file_id": doc["file_id"]}, timeout=10
            )
            file_path = file_resp.json().get("result", {}).get("file_path", "")
            if file_path:
                dl = requests.get(
                    "https://api.telegram.org/file/bot%s/%s" % (BOT_TOKEN, file_path),
                    timeout=10
                )
                data = dl.json()
                log.info("Restored %d lots from backup", len(data))
                save_seen(data)
                return data
    except Exception as e:
        log.warning("Could not restore from backup: %s", e)

    return {}


def save_seen(seen: dict):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def backup_seen(seen: dict):
    """Upload seen_lots.json to bot's own chat as pinned document."""
    try:
        data = json.dumps(seen, ensure_ascii=False, indent=2).encode("utf-8")
        resp = requests.post(
            "https://api.telegram.org/bot%s/sendDocument" % BOT_TOKEN,
            data={"chat_id": BACKUP_CHAT_ID},
            files={"document": ("seen_lots.json", data, "application/json")},
            timeout=15,
        )
        if resp.status_code == 200:
            msg_id = resp.json().get("result", {}).get("message_id")
            if msg_id:
                requests.post(
                    "https://api.telegram.org/bot%s/pinChatMessage" % BOT_TOKEN,
                    json={"chat_id": BACKUP_CHAT_ID, "message_id": msg_id,
                          "disable_notification": True},
                    timeout=10,
                )
            log.info("Backed up seen_lots (%d lots)", len(seen))
    except Exception as e:
        log.warning("Backup failed: %s", e)


def _hours_ago(timestamp_str, now):
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        return (now - dt).total_seconds() / 3600
    except (ValueError, TypeError):
        return 999


def build_photo_urls(tims: str) -> list:
    if not tims:
        return []
    base = tims if tims.startswith("http") else \
           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/" + tims
    hd1 = re.sub(r'/tn_', '/', base)
    hd2 = re.sub(r'_thb\.', '_ful.', base)
    hd3 = re.sub(r'_thb\.', '.', base)
    results = []
    if hd1 != base:
        results.append(hd1)
    if hd2 != base and hd2 not in results:
        results.append(hd2)
    if hd3 != base and hd3 not in results:
        results.append(hd3)
    results.append(base)
    return results


def download_photo(urls: list):
    for url in urls:
        try:
            time.sleep(2)
            resp = requests.get(url, headers=HEADERS, timeout=25)
            size = len(resp.content)
            log.info("photo %s: %s %dKB", url[-60:], resp.status_code, size // 1024)
            if resp.status_code == 200 and size > 10000:
                return resp.content
        except Exception as e:
            log.warning("photo error: %s", e)
    return None

def fetch_lots(channel) -> list:
    """Fetch lots from Copart for a specific channel config."""
    lots = []
    seen_ids = set()
    makes = channel["makes"]
    queries = channel["queries"]
    brand_priority = channel["brand_priority"]

    for query_str in queries:
        log.info("Searching: %s", query_str)

        for page in range(0, 3):
            payload = {
                "query": [query_str],
                "filter": {},
                "sort": [
                    "salelight_priority asc",
                    "member_damage_group_priority asc",
                    "auction_date_type desc",
                    "auction_date_utc asc"
                ],
                "page": page,
                "size": 20,
                "start": page * 20,
                "watchListOnly": False,
                "freeFormSearch": True,
                "hideImages": False,
                "defaultSort": False,
                "specificRowProvided": False,
                "displayName": "",
                "searchName": "",
                "backUrl": "",
                "includeTagByField": {},
                "rawParams": {}
            }

            try:
                resp = requests.post(
                    "https://www.copart.com/public/lots/search-results",
                    json=payload, headers=HEADERS, timeout=25
                )
                log.info("  %s page%d: HTTP %s", query_str, page, resp.status_code)
                resp.raise_for_status()
                data  = resp.json()
                items = data.get("data", {}).get("results", {}).get("content", [])
                log.info("  %s page%d: got %d lots", query_str, page, len(items))

                if not items:
                    break

                for item in items:
                    lot_num = str(item.get("ln", "")).strip()
                    if not lot_num or lot_num in seen_ids:
                        continue
                    seen_ids.add(lot_num)

                    year_raw = item.get("lcy") or item.get("y")
                    try:
                        year = int(year_raw)
                    except (TypeError, ValueError):
                        year = 0

                    if year < MIN_YEAR:
                        continue

                    make  = (item.get("mkn") or item.get("mk") or "").upper().strip()
                    model = (item.get("lm")  or item.get("md") or "").strip()

                    if make not in makes:
                        continue

                    damage = (item.get("dd") or "").strip()
                    tims   = item.get("tims", "")
                    odo    = item.get("orr", "")
                    price  = (item.get("dynamicLotDetails") or {}).get("currentBid")

                    engine = (item.get("egn") or "").strip()
                    drive  = (item.get("drv") or "").strip()
                    fuel   = (item.get("ft") or "").strip()
                    color  = (item.get("clr") or "").strip()
                    vin    = (item.get("fv") or "").strip()
                    transmission = (item.get("tmtp") or "").strip()
                    auction_date = item.get("ad") or ""

                    lots.append({
                        "id":       lot_num,
                        "title":    "%d %s %s" % (year, make.title(), model),
                        "make":     make.title(),
                        "model":    model,
                        "damage":   damage,
                        "odometer": odo,
                        "price":    price,
                        "engine":   engine,
                        "drive":    drive,
                        "fuel":     fuel,
                        "color":    color,
                        "vin":      vin,
                        "transmission": transmission,
                        "auction_date": auction_date,
                        "url":      "https://www.copart.com/lot/" + lot_num,
                        "photos":   build_photo_urls(tims),
                    })
                    log.info("  OK %d %s %s | %s", year, make, model, damage)

            except Exception as e:
                log.error("  Error %s page%d: %s", query_str, page, e, exc_info=True)
                break

            if len(lots) >= MAX_POSTS:
                break

        if len(lots) >= MAX_POSTS:
            break

    # Sort by brand priority
    def brand_sort_key(lot):
        make = lot.get("make", "").upper()
        try:
            return brand_priority.index(make)
        except ValueError:
            return len(brand_priority)

    lots.sort(key=brand_sort_key)
    log.info("[%s] Total matching lots: %d", channel["name"], len(lots))
    return lots

def build_caption(lot, channel_id):
    lines = ["🚗 <b>%s</b>" % lot["title"]]
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
    if lot.get("auction_date"):
        try:
            ad = lot["auction_date"]
            if isinstance(ad, (int, float)):
                dt_utc = datetime.fromtimestamp(ad / 1000, tz=timezone.utc)
            else:
                dt_utc = datetime.strptime(str(ad), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            dt_kz = dt_utc + timedelta(hours=5)
            lines.append("📅 Аукцион: %s (Астана)" % dt_kz.strftime("%d.%m.%Y %H:%M"))
        except (ValueError, TypeError, OSError):
            lines.append("📅 Аукцион: %s" % lot["auction_date"])
    lines.append("")
    lines.append('<a href="%s">🔗 Лот #%s на Copart</a>' % (lot["url"], lot["id"]))
    tags = []
    if lot.get("make"):
        tags.append("#%s" % lot["make"].replace("-", "").replace(" ", ""))
    if lot.get("model"):
        model_tag = lot["model"].replace("-", "").replace(" ", "")
        if model_tag:
            tags.append("#%s" % model_tag)
    if tags:
        lines.append(" ".join(tags))
    lines.append(channel_id)
    return "\n".join(lines)

def build_calendar_url(lot):
    ad = lot.get("auction_date")
    if not ad:
        return None
    try:
        if isinstance(ad, (int, float)):
            dt = datetime.utcfromtimestamp(ad / 1000)
        else:
            dt = datetime.strptime(str(ad), "%Y-%m-%dT%H:%M:%S.%fZ")
        date_str = dt.strftime("%Y%m%dT%H%M%SZ")
        end_dt = datetime.utcfromtimestamp(dt.timestamp() + 3600)
        end_str = end_dt.strftime("%Y%m%dT%H%M%SZ")
        title = quote("Аукцион Copart: %s" % lot["title"])
        details = quote("Лот #%s\n%s" % (lot["id"], lot["url"]))
        return ("https://calendar.google.com/calendar/render?action=TEMPLATE"
                "&text=%s&dates=%s/%s&details=%s" % (title, date_str, end_str, details))
    except (ValueError, TypeError, OSError):
        return None


def build_calc_url(lot, channel_id):
    caption = build_caption(lot, channel_id)
    # Strip HTML tags for plain text
    text = re.sub(r'<[^>]+>', '', caption)
    text = "Здравствуйте, меня интересует этот автомобиль!\n\n" + text
    return "https://t.me/+77476899519?text=%s" % quote(text)


def build_keyboard(lot, channel_id):
    lot_id = lot["id"]
    rows = [
        [{"text": "📩 Написать менеджеру", "url": MANAGER_PHONE}],
        [{"text": "📊 Рассчитать под ключ", "url": build_calc_url(lot, channel_id)}],
    ]
    cal_url = build_calendar_url(lot)
    if cal_url:
        rows.append([{"text": "📅 Добавить в календарь", "url": cal_url}])
    rows.append([{"text": "❤️ Сохранить", "callback_data": "save_%s" % lot_id}])
    return {"inline_keyboard": rows}


def send_post(lot, channel_id):
    caption     = build_caption(lot, channel_id)
    photo_bytes = download_photo(lot.get("photos", []))
    keyboard    = build_keyboard(lot, channel_id)
    kb_json     = json.dumps(keyboard, ensure_ascii=False)

    if photo_bytes:
        resp = requests.post(
            "https://api.telegram.org/bot%s/sendPhoto" % BOT_TOKEN,
            data={
                "chat_id":      channel_id,
                "caption":      caption,
                "parse_mode":   "HTML",
                "reply_markup": kb_json,
            },
            files={"photo": ("photo.jpg", photo_bytes, "image/jpeg")},
            timeout=30
        )
        log.info("sendPhoto [%s]: %s %s", channel_id, resp.status_code, resp.text[:200])
        if resp.status_code == 200:
            return True
        log.warning("Photo failed, falling back to text")

    resp = requests.post(
        "https://api.telegram.org/bot%s/sendMessage" % BOT_TOKEN,
        json={
            "chat_id":                  channel_id,
            "text":                     caption,
            "parse_mode":               "HTML",
            "disable_web_page_preview": False,
            "reply_markup":             keyboard,
        },
        timeout=15
    )
    log.info("sendMessage [%s]: %s", channel_id, resp.status_code)
    return resp.status_code == 200


def run_scraper():
    """Fetch lots from Copart and post new ones to all channels."""
    log.info("=" * 50)
    log.info("Scraper run: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("=" * 50)

    seen = load_seen()
    now = datetime.utcnow()

    # Clean old entries (>48h) to keep file small
    expired = [k for k, v in seen.items() if _hours_ago(v, now) > 48]
    for k in expired:
        del seen[k]
    if expired:
        save_seen(seen)
        log.info("Cleaned %d expired entries from seen_lots", len(expired))

    total_posted = 0

    for channel in CHANNELS:
        log.info("--- Channel: %s (%s) ---", channel["id"], channel["name"])
        lots = fetch_lots(channel)

        if not lots:
            log.info("[%s] No matching lots found.", channel["name"])
            continue

        posted = 0
        for lot in lots:
            if posted >= MAX_POSTS:
                break

            last_posted = seen.get(lot["id"])
            if last_posted:
                hours = _hours_ago(last_posted, now)
                if hours < COOLDOWN_HOURS:
                    log.info("Posted %.0fh ago, skip: %s", hours, lot["id"])
                    continue

            log.info("Posting lot %s - %s → %s", lot["id"], lot["title"], channel["id"])
            success = send_post(lot, channel["id"])

            if success:
                seen[lot["id"]] = now.strftime("%Y-%m-%dT%H:%M:%S")
                save_seen(seen)
                posted += 1
                log.info("Published OK (%d)", posted)
            else:
                log.warning("Failed to publish lot %s", lot["id"])

        total_posted += posted

    if total_posted > 0:
        backup_seen(seen)
    log.info("Scraper done: posted %d total lots across %d channels", total_posted, len(CHANNELS))
    return total_posted


if __name__ == "__main__":
    run_scraper()
