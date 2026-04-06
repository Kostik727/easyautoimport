import os
import json
import time
import logging
import requests
from datetime import datetime

BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID   = os.environ.get("CHANNEL_ID", "@easyautoimport")
SEARCH_QUERY = os.environ.get("SEARCH_QUERY", "car")
SEEN_FILE    = "seen_lots.json"
MAX_POSTS    = 10

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


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


def get_photo_url(tims):
    if not tims:
        return ""
    if tims.startswith("http"):
        return tims
    return f"https://cs.copart.com/v1/AUTH_svc.pdoc00001/{tims}"


def fetch_lots():
    lots = []
    try:
        url = "https://www.copart.com/public/lots/search"
        payload = {
            "query": {
                "query": SEARCH_QUERY,
                "filter": {},
                "sort": ["auction_date_type desc", "cd desc"],
                "watchListOnly": False,
                "freeFormSearch": True,
                "hideFilters": False,
                "defaultSort": False,
                "specificRowProviderFlag": True,
                "page": 0,
                "size": 50,
                "start": 0
            },
            "isBuyNowSearch": False,
            "isCleanTitle": False
        }
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", {}).get("results", {}).get("content", [])
        for item in items:
            lot_num  = str(item.get("ln", ""))
            title    = f"{item.get('y','')} {item.get('mk','')} {item.get('md','')}".strip()
            damage   = item.get("dd", "")
            odometer = item.get("orr", "")
            price    = (item.get("dynamicLotDetails") or {}).get("currentBid")
            url_lot  = f"https://www.copart.com/lot/{lot_num}"
            photo    = get_photo_url(item.get("tims", ""))
            if lot_num:
                lots.append({"id": lot_num, "title": title, "damage": damage,
                             "odometer": odometer, "price": price, "url": url_lot, "photo": photo})
        log.info(f"Lots found: {len(lots)}")
    except Exception as e:
        log.error(f"Error fetching lots: {e}")
    return lots


def build_caption(lot):
    lines = [f"\U0001f697 <b>{lot['title']}</b>"]
    if lot.get("damage"):
        lines.append(f"\U0001f4a5 Damage: {lot['damage']}")
    if lot.get("odometer"):
        lines.append(f"\U0001f4cf Odometer: {lot['odometer']}")
    if lot.get("price"):
        lines.append(f"\U0001f4b0 Bid: ${lot['price']}")
    lines.append(f"\n\U0001f517 <a href=\"{lot['url']}\">Lot #{lot['id']}</a>")
    lines.append(f"\U0001f4e2 @easyautoimport")
    return "\n".join(lines)


def send_post(lot):
    caption = build_caption(lot)
    if lot.get("photo"):
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                json={"chat_id": CHANNEL_ID, "photo": lot["photo"], "caption": caption, "parse_mode": "HTML"},
                timeout=15
            )
            if resp.status_code == 200:
                return True
        except Exception:
            pass
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": caption, "parse_mode": "HTML"},
            timeout=15
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        log.error(f"Send error: {e}")
        return False


def main():
    log.info(f"Bot started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    seen     = load_seen()
    lots     = fetch_lots()
    new_lots = [l for l in lots if l["id"] not in seen]
    if not new_lots:
        log.info("No new lots.")
        return
    log.info(f"New lots: {len(new_lots)}")
    posted = 0
    for lot in new_lots[:MAX_POSTS]:
        if send_post(lot):
            seen.add(lot["id"])
            posted += 1
            log.info(f"Posted: {lot['title']} #{lot['id']}")
            time.sleep(1.5)
    save_seen(seen)
    log.info(f"Done. Posted: {posted}")


if __name__ == "__main__":
    main()
