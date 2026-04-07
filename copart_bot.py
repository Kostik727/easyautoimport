"""
Telegram Bot: monitor copart.com and post to @easyautoimport
"""

import os
import re
import json
import time
import logging
import requests
from datetime import datetime

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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
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
    hd = re.sub(r'/tn_', '/', base)
    if hd != base:
        return [hd, base]
    return [base]


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
    seen_ids: set = set()

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

                if page == 0 and items:
                    first = items[0]
                    log.info("  DEBUG lot0: ln=%s lcy=%s mkn=%s dd=%r",
                             first.get("ln"), first.get("lcy"),
                             first.get("mkn"), first.get("dd"))

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
                        log.info("  skip make=%s", make)
                        continue

                    damage = (item.get("dd") or "").strip()
                    tims   = item.get("tims", "")
                    odo    = item.get("orr", "")
                    price  = (item.get("dynamicLotDetails") or {}).get("currentBid")

                    lots.append({
                        "id":       lot_num,
                        "title":    "%d %s %s" % (year, make.title(), model),
                        "damage":   damage,
                        "odometer": odo,
                        "price":    price,
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


def build_caption(lot: dict) -> str:
    lines = ["<b>%s</b>" % lot["title"]]
    if lot.get("damage"):
        lines.append("Damage: %s" % lot["damage"])
    if lot.get("odometer"):
        lines.append("Odometer: %s mi" % lot["odometer"])
    if lot.get("price"):
        lines.append("Current bid: $%s" % lot["price"])
    lines.append("")
    lines.append('<a href="%s">Open lot #%s</a>' % (lot["url"], lot["id"]))
    lines.append("@easyautoimport")
    return "\n".join(lines)


def send_post(lot: dict) -> bool:
    caption     = build_caption(lot)
    photo_bytes = download_photo(lot.get("photos", []))

    if photo_bytes:
        resp = requests.post(
            "https://api.telegram.org/bot%s/sendPhoto" % BOT_TOKEN,
            data={"chat_id": CHANNEL_ID, "caption": caption, "parse_mode": "HTML"},
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
            "chat_id":    CHANNEL_ID,
            "text":       caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=15
    )
    log.info("sendMessage: %s", resp.status_code)
    return resp.status_code == 200


def main():
    log.info("=" * 50)
    log.info("Bot started: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("=" * 50)

    lots = fetch_lots()

    if not lots:
        log.info("No matching lots found.")
        return

    lot = lots[0]
    log.info("TEST: posting lot %s - %s", lot["id"], lot["title"])
    success = send_post(lot)
    log.info("Published OK" if success else "Failed to publish")


if __name__ == "__main__":
    main()
