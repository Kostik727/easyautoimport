"""
Telegram Bot: monitor copart.com and post to @easyautoimport
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
CHANNEL_ID = "@easyautoimport"
SEEN_FILE  = "seen_lots.json"
MAX_POSTS  = 10
MIN_YEAR   = 2018

PRIORITY_MAKES = {
    "BMW", "TOYOTA", "LEXUS", "SUBARU",
    "MERCEDES-BENZ", "FORD", "DODGE"
}

QUERY_TERMS = [
    "BMW run and drive",
    "Toyota run and drive",
    "Lexus run and drive",
    "Subaru run and drive",
    "Mercedes-Benz run and drive",
    "Ford run and drive",
    "Dodge run and drive",
]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

MANAGER_PHONE = "https://t.me/+77476899519"
CALCULATOR_URL = "https://t.me/+77476899519"

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


def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


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

def fetch_lots() -> list:
    lots = []
    seen_ids = set()

    for query_str in QUERY_TERMS:
        log.info("Searching: %s", query_str)

        for page in range(0, 5):
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

                    if make not in PRIORITY_MAKES:
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

    log.info("Total matching lots: %d", len(lots))
    return lots

def build_caption(lot):
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
    lines.append("@easyautoimport")
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


def build_keyboard(lot):
    lot_id = lot["id"]
    rows = [
        [{"text": "📩 Написать менеджеру", "url": MANAGER_PHONE}],
        [{"text": "📊 Рассчитать под ключ", "url": CALCULATOR_URL}],
    ]
    cal_url = build_calendar_url(lot)
    if cal_url:
        rows.append([{"text": "📅 Добавить в календарь", "url": cal_url}])
    rows.append([{"text": "❤️ Сохранить", "callback_data": "save_%s" % lot_id}])
    return {"inline_keyboard": rows}


def send_post(lot):
    caption     = build_caption(lot)
    photo_bytes = download_photo(lot.get("photos", []))
    keyboard    = build_keyboard(lot)
    kb_json     = json.dumps(keyboard, ensure_ascii=False)

    if photo_bytes:
        resp = requests.post(
            "https://api.telegram.org/bot%s/sendPhoto" % BOT_TOKEN,
            data={
                "chat_id":      CHANNEL_ID,
                "caption":      caption,
                "parse_mode":   "HTML",
                "reply_markup": kb_json,
            },
            files={"photo": ("photo.jpg", photo_bytes, "image/jpeg")},
            timeout=30
        )
        log.info("sendPhoto: %s %s", resp.status_code, resp.text[:200])
        if resp.status_code == 200:
            return True
        log.warning("Photo failed, falling back to text")

    resp = requests.post(
        "https://api.telegram.org/bot%s/sendMessage" % BOT_TOKEN,
        json={
            "chat_id":                  CHANNEL_ID,
            "text":                     caption,
            "parse_mode":               "HTML",
            "disable_web_page_preview": False,
            "reply_markup":             keyboard,
        },
        timeout=15
    )
    log.info("sendMessage: %s", resp.status_code)
    return resp.status_code == 200


def run_scraper():
    """Fetch lots from Copart and post new ones to the channel."""
    log.info("=" * 50)
    log.info("Scraper run: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("=" * 50)

    seen = load_seen()
    lots = fetch_lots()

    if not lots:
        log.info("No matching lots found.")
        return 0

    posted = 0
    for lot in lots:
        if lot["id"] in seen:
            log.info("Already posted: %s", lot["id"])
            continue

        log.info("Posting lot %s - %s", lot["id"], lot["title"])
        success = send_post(lot)

        if success:
            seen.add(lot["id"])
            save_seen(seen)
            posted += 1
            log.info("Published OK (%d/%d)", posted, len(lots))
            time.sleep(5)
        else:
            log.warning("Failed to publish lot %s", lot["id"])

    log.info("Scraper done: posted %d new lots", posted)
    return posted


if __name__ == "__main__":
    run_scraper()
