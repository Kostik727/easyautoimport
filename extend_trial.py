"""One-time script: extend all existing users to 30 days from today."""
import users
from datetime import datetime, timedelta

all_u = users.load_users()
now = datetime.utcnow()
expires = (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
count = 0

for uid, u in all_u.items():
    if uid.startswith("_"):
        continue
    u["subscription"]["expires_at"] = expires
    if u["subscription"]["status"] == "expired":
        u["subscription"]["status"] = "trial"
    count += 1
    print("Extended: %s @%s → %s" % (uid, u.get("username", ""), expires))

users.save_users(all_u)
users.backup_users()
print("Done! Extended %d users to %s" % (count, expires))
