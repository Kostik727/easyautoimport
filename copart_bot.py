"""
Telegram Bot: ÐÐ¾Ð½Ð¸ÑÐ¾ÑÐ¸Ð½Ð³ Ð½Ð¾Ð²ÑÑ Ð»Ð¾ÑÐ¾Ð² Ð½Ð° copart.com
ÐÑÐ±Ð»Ð¸ÐºÑÐµÑ Ð¿Ð¾ÑÑÑ Ñ HD ÑÐ¾ÑÐ¾ Ð² ÐºÐ°Ð½Ð°Ð» @easyautoimport
"""

import os
import re
import json
import time
import logging
import requests
from datetime import datetime

# ââââââââââââââââââââââââââââââââââââââââââââââ
BOT_TOKEN  = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
CHANNEL_ID = "@easyautoimport"
SEEN_FILE  = "seen_lots.json"
MAX_POSTS  = 10
MIN_YEAR   = 2018

PRIORITY_MAKES = [
    "BMW", "Toyota", "Lexus", "Subaru",
    "Mercedes-Benz", "Ford", "Dodge"
]
# ââââââââââââââââââââââââââââââââââââââââââââââ

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


# ââ Seen lots ââââââââââââââââââââââââââââââââ

def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


# ââ Photo helpers ââââââââââââââââââââââââââââ

def build_photo_urls(tims: str) -> list:
    """Return [hd_url, thumb_url] to try in order."""
    if not tims:
        return []
    base = tims if tims.startswith("http") else \
           f"https://cs.copart.com/v1/AUTH_svc.pdoc00001/{tims}"
    hd = re.sub(r'/tn_', '/', base)
    if hd != base:
        return [hd, base]   # try HD first, then thumbnail
    return [base]


def download_photo(urls: list) -> bytes | None:
    """Try each URL with a 3-second delay; return first bytes >10 KB, else None."""
    for url in urls:
        try:
            time.sleep(3)   # wait for Copart CDN to be ready
            resp = requests.get(url, headers=HEADERS, timeout=25)
            size = len(resp.content)
            log.info(f"  photo {url[-60:]}: {resp.status_code} {size//1024}KB")
            if resp.status_code == 200 and size > 10_000:
                return resp.content
        except Exception as e:
            log.warning(f"  photo error: {e}")
    return None


# ââ Copart API âââââââââââââââââââââââââââââââ

def fetch_lots() -> list:
    """
    ÐÐ»Ñ ÐºÐ°Ð¶Ð´Ð¾Ð¹ Ð¿ÑÐ¸Ð¾ÑÐ¸ÑÐµÑÐ½Ð¾Ð¹ Ð¼Ð°ÑÐºÐ¸ Ð´ÐµÐ»Ð°ÐµÐ¼ Ð¿Ð¾Ð¸ÑÐº Â«{Make} run and driveÂ»
    ÑÐµÑÐµÐ· /public/lots/search-results â ÑÐµÐ°Ð»ÑÐ½ÑÐ¹ endpoint Ð±ÑÐ°ÑÐ·ÐµÑÐ½Ð¾Ð³Ð¾ UI.
    Ð¤Ð¸Ð»ÑÑÑÑÐµÐ¼ Ð¿Ð¾ Ð³Ð¾Ð´Ñ Ð½Ð° ÐºÐ»Ð¸ÐµÐ½ÑÐµ.
    """
    lots = []
    seen_ids: set = set()

    for make in PRIORITY_MAKES:
        query_str = f"{make} run and drive"
        log.info(f"ÐÑÐµÐ¼: {query_str}")

        for page in range(0, 5):  # 5 ÑÑÑÐ°Ð½Ð¸Ñ Ã 20 = Ð´Ð¾ 100 Ð»Ð¾ÑÐ¾Ð² Ð½Ð° Ð¼Ð°ÑÐºÑ
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
                log.info(f"  {make} ÑÑÑ.{page}: HTTP {resp.status_code}")
                resp.raise_for_status()
                data  = resp.json()
                items = data.get("data", {}).get("results", {}).get("content", [])
                log.info(f"  {make} ÑÑÑ.{page}: Ð»Ð¾ÑÐ¾Ð² = {len(items)}")

                if not items:
                    break

                # DEBUG: Ð¿Ð¾ÐºÐ°Ð·ÑÐ²Ð°ÐµÐ¼ Ð¿ÐµÑÐ²ÑÐ¹ Ð»Ð¾Ñ Ð¿ÐµÑÐ²Ð¾Ð¹ ÑÑÑÐ°Ð½Ð¸ÑÑ
                if page == 0:
                    first = items[0]
                    log.info(
                        f"  DEBUG lot0: ln={first.get('ln')} "
                        f"lcy={first.get('lcy')} mkn={first.get('mkn')} "
                        f"dd={first.get('dd')!r}"
                    )

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

                    make_name = (item.get("mkn") or item.get("mk") or "").strip()
                    model     = (item.get("lm")  or item.get("md") or "").strip()
                    damage    = (item.get("dd")  or "").strip()
                    tims      = item.get("tims", "")
                    odo       = item.get("orr", "")
                    price     = (item.get("dynamicLotDetails") or {}).get("currentBid")

                    lots.append({
                        "id":       lot_num,
                        "title":    f"{year} {make_name} {model}".strip(),
                        "damage":   damage,
                        "odometer": odo,
                        "price":    price,
                        "url":      f"https://www.copart.com/lot/{lot_num}",
                        "photos":   build_photo_urls(tims),
                    })
                    log.info(f"  â {year} {make_name} {model} | {damage}")

            except Exception as e:
                log.error(f"  ÐÑÐ¸Ð±ÐºÐ° {make} ÑÑÑ.{page}: {e}", exc_info=True)
                break

            if len(lots) >= MAX_POSTS:
                break

        if len(lots) >= MAX_POSTS:
            break

    log.info(f"ÐÑÐ¾Ð³Ð¾ Ð¿Ð¾Ð´ÑÐ¾Ð´ÑÑÐ¸Ñ Ð»Ð¾ÑÐ¾Ð²: {len(lots)}")
    return lots


# ââ Telegram âââââââââââââââââââââââââââââââââ

def build_caption(lot: dict) -> str:
    lines = [f"ð <b>{lot['title']}</b>"]
    if lot.get("damage"):
        lines.append(f"ð¥ ÐÐ¾Ð²ÑÐµÐ¶Ð´ÐµÐ½Ð¸Ñ: {lot['damage']}")
    if lot.get("odometer"):
        lines.append(f"ð ÐÑÐ¾Ð±ÐµÐ³: {lot['odometer']}")
    if lot.get("price"):
        lines.append(f"ð° Ð¡ÑÐ°Ð²ÐºÐ°: ${lot['price']}")
    lines.append(f"\nð <a href=\"{lot['url']}\">ÐÑÐºÑÑÑÑ Ð»Ð¾Ñ #{lot['id']}</a>")
    lines.append("ð¢ @easyautoimport")
    return "\n".join(lines)


def send_post(lot: dict) -> bool:
    caption      = build_caption(lot)
    photo_bytes  = download_photo(lot.get("photos", []))

    if photo_bytes:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={"chat_id": CHANNEL_ID, "caption": caption, "parse_mode": "HTML"},
            files={"photo": ("photo.jpg", photo_bytes, "image/jpeg")},
            timeout=30
        )
        log.info(f"sendPhoto: {resp.status_code} {resp.text[:200]}")
        if resp.status_code == 200:
            return True
        log.warning("Ð¤Ð¾ÑÐ¾ Ð½Ðµ Ð¿ÑÐ¾ÑÐ»Ð¾, Ð¾ÑÐ¿ÑÐ°Ð²Ð»ÑÑ ÑÐµÐºÑÑ")

    # fallback: text only
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id":    CHANNEL_ID,
            "text":       caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=15
    )
    log.info(f"sendMessage: {resp.status_code}")
    return resp.status_code == 200


# ââ Main ââââââââââââââââââââââââââââââââââââââ

def main():
    log.info("=" * 50)
    log.info(f"ÐÐ¾Ñ Ð·Ð°Ð¿ÑÑÐµÐ½: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 50)

    lots = fetch_lots()

    if not lots:
        log.info("ÐÐ¾Ð´ÑÐ¾Ð´ÑÑÐ¸Ñ Ð»Ð¾ÑÐ¾Ð² Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð¾.")
        return

    # ââ TEST MODE: Ð¾Ð´Ð¸Ð½ Ð»Ð¾Ñ ââ
    lot = lots[0]
    log.info(f"TEST: Ð¾Ð±ÑÐ°Ð±Ð°ÑÑÐ²Ð°ÐµÐ¼ Ð»Ð¾Ñ {lot['id']} â {lot['title']}")
    success = send_post(lot)
    log.info("â ÐÐ¿ÑÐ±Ð»Ð¸ÐºÐ¾Ð²Ð°Ð½Ð¾" if success else "â ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ Ð¾Ð¿ÑÐ±Ð»Ð¸ÐºÐ¾Ð²Ð°ÑÑ")


if __name__ == "__main__":
    main()
