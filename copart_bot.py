"""
Telegram Bot: Мониторинг новых лотов на copart.com
Публикует посты с HD фото в канал @easyautoimport
"""

import os
import re
import json
import time
import logging
import requests
from datetime import datetime

# ──────────────────────────────────────────────
BOT_TOKEN  = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
CHANNEL_ID = "@easyautoimport"
SEEN_FILE  = "seen_lots.json"
MAX_POSTS  = 10
MIN_YEAR   = 2018

PRIORITY_MAKES = {
    "BMW", "TOYOTA", "LEXUS", "SUBARU",
    "MERCEDES-BENZ", "FORD", "DODGE"
}
# ──────────────────────────────────────────────

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


# ── Seen lots ────────────────────────────────

def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


# ── Photo helpers ────────────────────────────

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


# ── Copart API ───────────────────────────────

def fetch_lots() -> list:
    """
    Пагинируем по страницам Copart, фильтруем на клиенте.
    DEBUG MODE: логируем поля первого лота и счётчики на каждом шаге.
    """
    lots = []
    seen_ids: set = set()
    try:
        for page in range(0, 3):  # 3 страницы × 100 = 300 лотов
            payload = {
                "query": {
                    "query": "*",
                    "filter": {},
                    "sort": ["auction_date_type desc", "cd desc"],
                    "watchListOnly": False,
                    "freeFormSearch": True,
                    "hideFilters": False,
                    "defaultSort": False,
                    "specificRowProviderFlag": True,
                    "page": page,
                    "size": 100,
                    "start": page * 100
                },
                "isBuyNowSearch": False,
                "isCleanTitle": False
            }

            resp = requests.post(
                "https://www.copart.com/public/lots/search",
                json=payload, headers=HEADERS, timeout=25
            )
            log.info(f"Страница {page}: HTTP {resp.status_code}")
            resp.raise_for_status()
            data  = resp.json()
            items = data.get("data", {}).get("results", {}).get("content", [])
            log.info(f"Страница {page}: получено лотов = {len(items)}")

            if not items:
                break

            # DEBUG: показываем ключи и важные поля первого лота
            if page == 0:
                first = items[0]
                log.info(f"DEBUG keys: {list(first.keys())}")
                log.info(
                    f"DEBUG lot0: ln={first.get('ln')} "
                    f"lcy={first.get('lcy')} mkn={first.get('mkn')} "
                    f"mk={first.get('mk')} dd={first.get('dd')!r} "
                    f"ldu={first.get('ldu')!r} hd={first.get('hd')!r}"
                )

            cnt_yr = cnt_mk = cnt_rd = 0
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

                make   = (item.get("mkn") or item.get("mk") or "").upper().strip()
                model  = (item.get("lm")  or item.get("md") or "").strip()
                damage = (item.get("dd")  or "").strip()

                if year < MIN_YEAR:
                    continue
                cnt_yr += 1

                if make not in PRIORITY_MAKES:
                    continue
                cnt_mk += 1

                # Run & Drive check — логируем поле damage для первых совпадений
                if cnt_mk <= 3:
                    log.info(f"  MATCH make {make} {year} — dd={damage!r}")

                if "RUN AND DRIVE" not in damage.upper():
                    continue
                cnt_rd += 1

                tims  = item.get("tims", "")
                odo   = item.get("orr", "")
                price = (item.get("dynamicLotDetails") or {}).get("currentBid")

                lots.append({
                    "id":       lot_num,
                    "title":    f"{year} {make.title()} {model}".strip(),
                    "damage":   damage,
                    "odometer": odo,
                    "price":    price,
                    "url":      f"https://www.copart.com/lot/{lot_num}",
                    "photos":   build_photo_urls(tims),
                })

            log.info(f"Стр.{page}: год≥{MIN_YEAR}={cnt_yr}, марка={cnt_mk}, R&D={cnt_rd}")

            if lots:
                break

        log.info(f"Итого подходящих лотов: {len(lots)}")

    except Exception as e:
        log.error(f"Ошибка при получении лотов: {e}", exc_info=True)

    return lots


# ── Telegram ─────────────────────────────────

def build_caption(lot: dict) -> str:
    lines = [f"🚗 <b>{lot['title']}</b>"]
    if lot.get("damage"):
        lines.append(f"💥 Повреждения: {lot['damage']}")
    if lot.get("odometer"):
        lines.append(f"📏 Пробег: {lot['odometer']}")
    if lot.get("price"):
        lines.append(f"💰 Ставка: ${lot['price']}")
    lines.append(f"\n🔗 <a href=\"{lot['url']}\">Открыть лот #{lot['id']}</a>")
    lines.append("📢 @easyautoimport")
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
        log.warning("Фото не прошло, отправляю текст")

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


# ── Main ──────────────────────────────────────

def main():
    log.info("=" * 50)
    log.info(f"Бот запущен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 50)

    lots = fetch_lots()

    if not lots:
        log.info("Подходящих лотов не найдено.")
        return

    # ── TEST MODE: один лот ──
    lot = lots[0]
    log.info(f"TEST: обрабатываем лот {lot['id']} — {lot['title']}")
    success = send_post(lot)
    log.info("✅ Опубликовано" if success else "❌ Не удалось опубликовать")


if __name__ == "__main__":
    main()
