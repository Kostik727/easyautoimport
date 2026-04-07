import os
import json
import time
import logging
import requests
import re
from datetime import datetime

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@easyautoimport")
MIN_YEAR   = 2018

PRIORITY_MAKES = [
    "BMW", "TOYOTA", "LEXUS", "SUBARU",
    "MERCEDES-BENZ", "FORD", "DODGE"
]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.copart.com/",
    "Origin": "https://www.copart.com",
}


def get_hd_photo_url(tims):
    """Convert thumbnail URL to HD by removing tn_ prefix."""
    if not tims:
        return ""
    if tims.startswith("http"):
        base = tims
    else:
        base = f"https://cs.copart.com/v1/AUTH_svc.pdoc00001/{tims}"
    return re.sub(r'/tn_', '/', base)


def download_photo(url):
    """Download photo bytes. Returns bytes or None."""
    if not url:
        return None
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200 and len(resp.content) > 5000:
            log.info(f"Photo downloaded: {len(resp.content)//1024} KB")
            return resp.content
        log.warning(f"Photo download failed: status={resp.status_code}, size={len(resp.content)}")
    except Exception as e:
        log.warning(f"Photo download error: {e}")
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
        url = "https://www.copart.com/public/lots/search"
        payload = {
            "query": {
                "query": "*",
                "filter": {
                    "SPECIAL_FILTER": ["RUN_AND_DRIVE_FILTER"],
                    "make": [m.replace("-", " ") for m in PRIORITY_MAKES]
                },
                "sort": ["auction_date_type desc", "cd desc"],
                "watchListOnly": False,
                "freeFormSearch": False,
                "hideFilters": False,
                "defaultSort": False,
                "specificRowProviderFlag": True,
                "page": 0, "size": 100, "start": 0
            },
            "isBuyNowSearch": False,
            "isCleanTitle": False
        }
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", {}).get("results", {}).get("content", [])
        log.info(f"API returned {len(items)} items")

        for item in items:
            lot_num = str(item.get("ln", ""))
            year  = int(item.get("lcy", 0) or 0)
            make  = str(item.get("mkn", "") or "").upper().strip()
            model = str(item.get("lm",  "") or "").strip()
            title = f"{year} {make} {model}".strip()
            damage   = item.get("dd", "")
            odometer = item.get("orr", "")
            price    = (item.get("dynamicLotDetails") or {}).get("currentBid")
            url_lot  = f"https://www.copart.com/lot/{lot_num}"
            photo_url = get_hd_photo_url(item.get("tims", ""))

            log.info(f"  lot {lot_num}: year={year}, make={make}, model={model}, photo={photo_url[:70] if photo_url else 'none'}")

            if year < MIN_YEAR:
                continue
            if not lot_num:
                continue

            lots.append({
                "id":       lot_num,
                "title":    title,
                "year":     year,
                "make":     make,
                "damage":   damage,
                "odometer": odometer,
                "price":    price,
                "url":      url_lot,
                "photo":    photo_url,
                "priority": make_priority_key(make)
            })

        lots.sort(key=lambda x: (x["priority"], -x["year"]))
        log.info(f"After filters: {len(lots)} lots qualify")
    except Exception as e:
        log.error(f"Error fetching lots: {e}")
    return lots


def build_caption(lot):
    lines = [f"\U0001f697 <b>{lot['title']}</b>"]
    if lot.get("damage"):
        lines.append(f"\U0001f4a5 {lot['damage']}")
    if lot.get("odometer"):
        lines.append(f"\U0001f4cf {lot['odometer']}")
    if lot.get("price"):
        lines.append(f"\U0001f4b0 Bid: ${lot['price']}")
    lines.append(f"\n\U0001f517 <a href=\"{lot['url']}\">Lot #{lot['id']}</a>")
    lines.append("\U0001f4e2 @easyautoimport")
    return "\n".join(lines)


def send_post(lot):
    caption = build_caption(lot)

    # Download photo first, then upload as file (reliable HD delivery)
    if lot.get("photo"):
        photo_bytes = download_photo(lot["photo"])
        if photo_bytes:
            try:
                resp = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={"chat_id": CHANNEL_ID, "caption": caption, "parse_mode": "HTML"},
                    files={"photo": ("photo.jpg", photo_bytes, "image/jpeg")},
                    timeout=30
                )
                if resp.status_code == 200:
                    log.info("Photo sent as file upload (HD)")
                    return True
                log.warning(f"Upload failed: {resp.status_code} {resp.text[:200]}")
            except Exception as e:
                log.warning(f"Upload error: {e}")

    # Fallback: text only
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": caption, "parse_mode": "HTML"},
            timeout=15
        )
        resp.raise_for_status()
        log.info("Sent as text message (no photo)")
        return True
    except Exception as e:
        log.error(f"Send error: {e}")
        return False


def main():
    log.info(f"=== Bot started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    lots = fetch_lots()
    if not lots:
        log.info("No lots found.")
        return

    lot = lots[0]
    log.info(f"TEST: Sending -> {lot['title']} | Lot #{lot['id']}")
    if send_post(lot):
        log.info("SUCCESS - check @easyautoimport")
    else:
        log.error("FAILED")


if __name__ == "__main__":
    main()
