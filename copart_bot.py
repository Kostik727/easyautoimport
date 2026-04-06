import os
import json
import time
import logging
import requests
from datetime import datetime

BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID   = os.environ.get("CHANNEL_ID", "@easyautoimport")
SEEN_FILE    = "seen_lots.json"
MAX_POSTS    = 10
MIN_YEAR     = 2018

# Приоритетные марки (в порядке приоритета)
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


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


def get_hd_photo_url(tims):
    """Получить ссылку на HD фото из поля tims."""
    if not tims:
        return ""
    # tims может быть полным URL или путём
    if tims.startswith("http"):
        base = tims
    else:
        base = f"https://cs.copart.com/v1/AUTH_svc.pdoc00001/{tims}"
    # Убираем "tn_" из имени файла для получения HD версии
    import re
    hd_url = re.sub(r'/tn_', '/', base)
    return hd_url


def make_priority_key(make):
    """Возвращает индекс приоритета марки (меньше = выше)."""
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
                "page": 0,
                "size": 100,
                "start": 0
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
            lot_num  = str(item.get("ln", ""))
            year     = int(item.get("y", 0) or 0)
            make     = str(item.get("mk", "") or "").upper()
            model    = str(item.get("md", "") or "")
            title    = f"{year} {make} {model}".strip()
            damage   = item.get("dd", "")
            odometer = item.get("orr", "")
            price    = (item.get("dynamicLotDetails") or {}).get("currentBid")
            url_lot  = f"https://www.copart.com/lot/{lot_num}"
            photo    = get_hd_photo_url(item.get("tims", ""))

            # Фильтр по году
            if year < MIN_YEAR:
                continue

            if lot_num:
                lots.append({
                    "id": lot_num,
                    "title": title,
                    "year": year,
                    "make": make,
                    "damage": damage,
                    "odometer": odometer,
                    "price": price,
                    "url": url_lot,
                    "photo": photo,
                    "priority": make_priority_key(make)
                })

        # Сортируем: сначала приоритетные марки, потом по году
        lots.sort(key=lambda x: (x["priority"], -x["year"]))
        log.info(f"After filters: {len(lots)} lots (run&drive, year>={MIN_YEAR})")

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
    lines.append("\U0001f4e2 @easyautoimport")
    return "\n".join(lines)


def send_post(lot):
    caption = build_caption(lot)
    # Пробуем HD фото
    if lot.get("photo"):
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                json={"chat_id": CHANNEL_ID, "photo": lot["photo"],
                      "caption": caption, "parse_mode": "HTML"},
                timeout=15
            )
            if resp.status_code == 200:
                return True
            log.warning(f"Photo failed ({resp.status_code}), trying text...")
        except Exception as e:
            log.warning(f"Photo error: {e}")
    # Fallback: текстовое сообщение
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": caption, "parse_mode": "HTML",
                  "disable_web_page_preview": False},
            timeout=15
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        log.error(f"Send error: {e}")
        return False


def main():
    log.info(f"=== Bot started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    log.info(f"Filters: Run&Drive, year>={MIN_YEAR}, brands={PRIORITY_MAKES}")

    seen     = load_seen()
    lots     = fetch_lots()
    new_lots = [l for l in lots if l["id"] not in seen]

    if not new_lots:
        log.info("No new lots found.")
        return

    log.info(f"New lots to post: {len(new_lots)}")
    posted = 0
    for lot in new_lots[:MAX_POSTS]:
        if send_post(lot):
            seen.add(lot["id"])
            posted += 1
            log.info(f"Posted: {lot['title']} | Lot #{lot['id']}")
            time.sleep(1.5)
        else:
            log.error(f"Failed: {lot['title']}")

    save_seen(seen)
    log.info(f"=== Done. Posted: {posted}/{len(new_lots[:MAX_POSTS])} ===")


if __name__ == "__main__":
    main()
