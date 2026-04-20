"""
User management module for Easy Auto Import bot.
Handles user data, subscriptions, saved lots, and Telegram backup.
"""

import os
import json
import logging
import threading
import requests
from typing import Optional
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

USERS_FILE = "users.json"
SAVED_FILE = "saved_lots.json"
TRIAL_DAYS = 30

_lock = threading.Lock()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8435399634:AAHSjsvlP3LSGo-6TKg9v777dfC-iFct6bk")
BACKUP_CHAT_ID = os.environ.get("BACKUP_CHAT_ID", BOT_TOKEN.split(":")[0])


# ---- persistence ----

def load_users() -> dict:
    with _lock:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def save_users(data: dict):
    with _lock:
        tmp = USERS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, USERS_FILE)


def backup_users():
    """Upload users.json to bot's own chat as pinned document."""
    try:
        users = load_users()
        if not users:
            return
        data = json.dumps(users, ensure_ascii=False, indent=2).encode("utf-8")
        resp = requests.post(
            "https://api.telegram.org/bot%s/sendDocument" % BOT_TOKEN,
            data={"chat_id": BACKUP_CHAT_ID, "caption": "users_backup"},
            files={"document": ("users.json", data, "application/json")},
            timeout=15,
        )
        if resp.status_code == 200:
            log.info("Backed up users.json (%d users)", len(users))
    except Exception as e:
        log.warning("Users backup failed: %s", e)


def restore_users():
    """Try to restore users.json from Telegram backup if file missing."""
    if os.path.exists(USERS_FILE):
        return
    log.info("Restoring users.json from Telegram backup...")
    try:
        resp = requests.post(
            "https://api.telegram.org/bot%s/getChat" % BOT_TOKEN,
            json={"chat_id": BACKUP_CHAT_ID}, timeout=10
        )
        pinned = resp.json().get("result", {}).get("pinned_message", {})
        doc = pinned.get("document")
        if not doc:
            return
        file_resp = requests.get(
            "https://api.telegram.org/bot%s/getFile" % BOT_TOKEN,
            params={"file_id": doc["file_id"]}, timeout=10
        )
        file_path = file_resp.json().get("result", {}).get("file_path", "")
        if not file_path:
            return
        dl = requests.get(
            "https://api.telegram.org/file/bot%s/%s" % (BOT_TOKEN, file_path),
            timeout=10
        )
        data = dl.json()
        if isinstance(data, dict) and data:
            save_users(data)
            log.info("Restored %d users from backup", len(data))
    except Exception as e:
        log.warning("Could not restore users: %s", e)


# ---- user CRUD ----

def get_or_create_user(user_id, username="", first_name="") -> dict:
    uid = str(user_id)
    users = load_users()
    if uid in users:
        user = users[uid]
        if username:
            user["username"] = username
        if first_name:
            user["first_name"] = first_name
        save_users(users)
        return user

    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    expires = (datetime.utcnow() + timedelta(days=TRIAL_DAYS)).strftime("%Y-%m-%dT%H:%M:%S")
    user = {
        "user_id": int(user_id),
        "username": username or "",
        "first_name": first_name or "",
        "channels": [],
        "registered_at": now,
        "subscription": {
            "status": "trial",
            "expires_at": expires,
        },
        "saved_lots": [],
        "reminder_sent": {},
        "last_digest_at": None,
        "awaiting_payment_proof": False,
    }
    users[uid] = user
    save_users(users)
    log.info("New user: %s @%s", user_id, username)
    return user


def get_user(user_id) -> Optional[dict]:
    users = load_users()
    return users.get(str(user_id))


# ---- channels ----

def update_channels(user_id, channels: list):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return
    users[uid]["channels"] = channels
    save_users(users)


def toggle_channel(user_id, channel_key: str) -> list:
    """Toggle a channel and return updated channel list."""
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return []
    channels = users[uid].get("channels", [])
    if channel_key in channels:
        channels.remove(channel_key)
    else:
        channels.append(channel_key)
    users[uid]["channels"] = channels
    save_users(users)
    return channels


# ---- saved lots ----

def add_saved_lot(user_id, lot_id) -> bool:
    """Add lot to saved. Returns False if already saved."""
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return False
    lots = users[uid].get("saved_lots", [])
    if lot_id in lots:
        return False
    lots.append(lot_id)
    users[uid]["saved_lots"] = lots

    # Save log for admin
    save_log = users.get("_save_log", [])
    save_log.append({
        "user_id": int(user_id),
        "username": users[uid].get("username", ""),
        "lot_id": lot_id,
        "at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
    })
    if len(save_log) > 100:
        save_log = save_log[-100:]
    users["_save_log"] = save_log

    save_users(users)
    return True


def get_saved_lots(user_id) -> list:
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return []
    return users[uid].get("saved_lots", [])


def get_users_with_saved_lot(lot_id) -> list:
    """Return user_ids who saved this lot."""
    users = load_users()
    result = []
    for uid, u in users.items():
        if uid.startswith("_"):
            continue
        if lot_id in u.get("saved_lots", []):
            result.append(int(uid))
    return result


# ---- subscriptions ----

def check_subscription(user_id) -> str:
    """Returns 'active' or 'expired'."""
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return "expired"
    sub = users[uid].get("subscription", {})
    status = sub.get("status", "trial")
    expires = sub.get("expires_at", "")

    if status == "paid" or status == "trial":
        try:
            exp_dt = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%S")
            if datetime.utcnow() < exp_dt:
                return "active"
        except (ValueError, TypeError):
            pass
        # Expired — update status
        users[uid]["subscription"]["status"] = "expired"
        save_users(users)
    return "expired"


def activate_subscription(user_id, days=30, admin_id=None):
    """Activate paid subscription for N days."""
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return False
    expires = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    users[uid]["subscription"] = {
        "status": "paid",
        "expires_at": expires,
    }
    save_users(users)
    log.info("Subscription activated: user %s for %d days by admin %s", user_id, days, admin_id)
    return True


def get_subscription_info(user_id) -> dict:
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return {"status": "none"}
    sub = users[uid].get("subscription", {})
    return {
        "status": check_subscription(user_id),
        "type": sub.get("status", "trial"),
        "expires_at": sub.get("expires_at", ""),
    }


# ---- payment ----

def set_awaiting_payment(user_id, value=True):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return
    users[uid]["awaiting_payment_proof"] = value
    save_users(users)


def is_awaiting_payment(user_id) -> bool:
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return False
    return users[uid].get("awaiting_payment_proof", False)


# ---- reminders ----

def mark_reminder_sent(user_id, lot_id, reminder_type):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return
    reminders = users[uid].get("reminder_sent", {})
    sent = reminders.get(lot_id, [])
    if reminder_type not in sent:
        sent.append(reminder_type)
    reminders[lot_id] = sent
    users[uid]["reminder_sent"] = reminders
    save_users(users)


def was_reminder_sent(user_id, lot_id, reminder_type) -> bool:
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return True
    reminders = users[uid].get("reminder_sent", {})
    return reminder_type in reminders.get(lot_id, [])


# ---- digest ----

def update_last_digest(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return
    users[uid]["last_digest_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    save_users(users)


def get_last_digest(user_id) -> Optional[str]:
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return None
    return users[uid].get("last_digest_at")


# ---- admin helpers ----

def get_save_log() -> list:
    users = load_users()
    return users.get("_save_log", [])


def get_all_users_stats() -> dict:
    users = load_users()
    total = 0
    trial = 0
    paid = 0
    expired = 0
    for uid, u in users.items():
        if uid.startswith("_"):
            continue
        total += 1
        status = check_subscription(int(uid))
        sub_type = u.get("subscription", {}).get("status", "trial")
        if status == "active" and sub_type == "trial":
            trial += 1
        elif status == "active" and sub_type == "paid":
            paid += 1
        else:
            expired += 1
    return {"total": total, "trial": trial, "paid": paid, "expired": expired}


# ---- migration ----

def migrate_saved_lots():
    """One-time migration from saved_lots.json into users.json."""
    if not os.path.exists(SAVED_FILE):
        return
    log.info("Migrating saved_lots.json → users.json...")
    try:
        with open(SAVED_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        users = load_users()
        migrated = 0
        for uid, lot_ids in saved.items():
            if uid in users:
                existing = set(users[uid].get("saved_lots", []))
                existing.update(lot_ids)
                users[uid]["saved_lots"] = list(existing)
            else:
                now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
                expires = (datetime.utcnow() + timedelta(days=TRIAL_DAYS)).strftime("%Y-%m-%dT%H:%M:%S")
                users[uid] = {
                    "user_id": int(uid),
                    "username": "",
                    "first_name": "",
                    "channels": [],
                    "registered_at": now,
                    "subscription": {"status": "trial", "expires_at": expires},
                    "saved_lots": lot_ids,
                    "reminder_sent": {},
                    "last_digest_at": None,
                    "awaiting_payment_proof": False,
                }
            migrated += 1
        save_users(users)
        os.rename(SAVED_FILE, SAVED_FILE + ".bak")
        log.info("Migrated %d users from saved_lots.json", migrated)
    except Exception as e:
        log.warning("Migration failed: %s", e)
