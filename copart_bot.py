import os
import re
import json
import time
import logging
import requests
from datetime import datetime

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@easyautoimport")
MIN_YEAR   = 2018

PRIORITY_MAKES = {
    "BMW", "TOYOTA", "LEXUS", "SUBARU",
    "MERCEDES-BENZ", "FORD", "DODGE"
I}

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


def build_photo_urls(tims):
    """Return [hd_url, thumb_url] to try in order."""
    if not tims:
        return []
    if tims.startswith("http"):
        base = tims
    else:
        base = f"https://cs.copart.com/v1/AUTH_svc.pdoc00001/{tims}"
    hd = re.sub(r'/tn_', '/', base)
    if hd != base:
        return [hd, base]   # try HD first, then thumbnail
    return [base]


def download_photo(urls):
    """Try each URL with a 3-sec wait; return first bytes >10 KB, else None."""
    for url in urls:
        try:
            time.sleep(3)   # wait for Copart CDN
            resp = requests.get(url, headers=HEADERS, timeout=25)
            size = len(resp.content)
            log.info(f"  photo {url[-50:]}: {resp.status_code} {size//1024}KB")
            if resp.status_code == 200 and size > 10_000:
                return resp.content
        except Exception as e:
            log.warning(f"  photo error: {e}")
    return None


def make_priority_key(make):
    m = (make or "").upper().strip()
    for i, pm in enumerate(PRIORITY_MAKES):
        if pm in m or m in pm:
            return i
    return len(PRIORITY_MAKES)


def fetch_lots():
    lots = []
    try:
        payload = {
            "query": {
                "query": "*",
                "filter": {
                    "SPECIAL_FILTER": ["RUN_AND_DRIVE_FILTER"]
                },
                "sort": ["auction_date_type desc", "cd desc"],
                "watchListOnly": False,
                "freeFormSearch": True,
                "hideFilters": False,
                "defaultSort": False,
                "specificRowProviderFlag": True,
                "page": 0,
                "size": 100,
                "start": 0
            },
            "isBuyNowSearch": False,
            "isCleanTitle": False
        }

        resp = requests.post(
            "https://www.copart.com/public/lots/search",
            json=payload, headers=HEADERS, timeout=25
        )
        resp.raise_for_status()
        items = resp.json().get("data", {}).get("results", {}).get("content", [])
        log.info(f"API returned {len(items)} items")

        for item in items:
            lot_num = str(item.get("ln", "")).strip()
            year_raw = item.get("lcy") or item.get("y")
            try:
                year = int(year_raw)
            except (TypeError, ValueError):
                year = 0
            make  = (item.get("mkn") or item.get("mk") or "").upper().strip()
            model = (item.get("lm")  or item.get("md") or "").strip()

            if not lot_num or year < MIN_YEAR:
                continue
            if make not in PRIORITY_MAKES:
                continue

            tims   = item.get("tims", "")
            damage = item.get("dd", "")
            odo    = item.get("orr", "")
            price  = (item.get("dynamicLotDetails") or {}).get("currentBid")

            lots.append({
                "id":       lot_num,
                "title":    f"{year} {make.title()} {model}".strip(),
                "damage":   damage,
                "odometer": odo,
                "price":    price,
                "url":      f"https://www.copart.com/lot/{lot_num}",
                "photos":   build_photo_urls(tims),
                "priority": make_priority_key(make),
            })

        lots.sort(key=lambda x: (x["priority"], -x["year"]) if "year" in x else x.get("priority", 99))
        log.info(f"After filters (year>={MIN_YEAR}, priority makes): {len(lots)} lots")

    except Exception as e:
        log.error(f"Error fetching lots: {e}")

    return lots


def build_caption(lot):
    lines = [f"\u1f697 <b>{lot['title']}</b>"]
    if lot.get("damage"):
        lines.append(f"\u1f4a5 Damage: {lot['damage']}")
    if lot.get("odometer"):
        lines.append(f"\u1f4cf Odometer: {lot['odometer']}")
    if lot.get("price"):
        lines.append(f"\u1f4b0 Bid: ${lot['price']}")
    lines.append(f"\n\u1f517 <a href=\"{lot['url']}\">Lot #{lot['id']}</a>")
    lines.append("\u1f4e2 @easyautoimport")
    return "\n".join(lines)


def send_post(lot):
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
        log.warning("Photo upload failed, sending text only")

    # fallback: text only
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHANNEL_ID,
            "text":       caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=15
    )
    log.info(f"sendMessage: {resp.status_code}")
    return resp.status_code == 200


def main():
    log.info("=" * 50)
    log.info(f"Bot started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 50)

    lots = fetch_lots()

    if not lots:
        log.info("No qualifying lots found.")
        return

    # TEST MODE: send first lot only
    lot = lots[0]
    log.info(f"TEST: {lot['title']} | Lot #{lot['id']}")
    success = send_post(lot)
    log.info("SUCCESS - check @easyautoimport" if success else "FAILED")


if __name__ == "__main__":
    main()
