import telebot
import os
import random
import string
from flask import Flask
from threading import Thread

# သင့် Bot Token
TOKEN = "8535512510:AAFYDZfmxeIP7enJ8pk6iNQg2ef30KPjPlg"
bot = telebot.TeleBot(TOKEN)

# Admin ID
ADMIN_IDS = [1801787123]

ADMIN_IDS = {
    int(x.strip())
    for x in os.environ.get("ADMIN_IDS", "").split(",")
    if x.strip()
}

GITHUB_API = "https://api.github.com/repos/soemoe543/telegram-bot/contents/api.json"
GITHUB_BRANCH = "main"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)


@app.get("/")
def home():
    return "Bot is running!"


def headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_data():
    r = requests.get(
        GITHUB_API,
        headers=headers(),
        params={"ref": GITHUB_BRANCH},
        timeout=20,
    )
    r.raise_for_status()
    result = r.json()
    content = base64.b64decode(result["content"]).decode("utf-8")
    data = json.loads(content)
    data.setdefault("licenses", [])
    return data, result["sha"]


def save_data(data, sha):
    content = json.dumps(data, indent=2, ensure_ascii=False)
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Update licenses from Telegram bot",
        "content": encoded,
        "sha": sha,
        "branch": GITHUB_BRANCH,
    }

    r = requests.put(
        GITHUB_API,
        headers=headers(),
        json=payload,
        timeout=20,
    )
    r.raise_for_status()


def make_key():
    alphabet = string.ascii_uppercase + string.digits
    groups = [
        "".join(secrets.choice(alphabet) for _ in range(4))
        for _ in range(3)
    ]
    return "EASY-" + "-".join(groups)


def admin(message):
    return message.from_user.id in ADMIN_IDS


@bot.message_handler(commands=["start"])
def start(message):
    if not admin(message):
        bot.reply_to(message, "❌ Admin only.")
        return

    bot.reply_to(
        message,
        "👋 License Manager\n\n"
        "အသုံးပြုပုံ:\n"
        "/addpoint HARDWARE_ID YYYY-MM-DD HH:MM:SS\n\n"
        "ဥပမာ:\n"
        "/addpoint EASY-1234-ABCD 2030-12-31 23:59:59"
    )


@bot.message_handler(commands=["addpoint"])
def addpoint(message):
    if not admin(message):
        bot.reply_to(message, "❌ Admin only.")
        return

    parts = message.text.split()

    if len(parts) != 4:
        bot.reply_to(
            message,
            "❌ Format မမှန်ပါ။\n\n"
            "/addpoint HARDWARE_ID YYYY-MM-DD HH:MM:SS\n\n"
            "ဥပမာ:\n"
            "/addpoint EASY-1234-ABCD 2030-12-31 23:59:59"
        )
        return

    hardware_id = parts[1]
    date_text = parts[2]
    time_text = parts[3]

    try:
        expire = datetime.strptime(
            f"{date_text} {time_text}",
            "%Y-%m-%d %H:%M:%S",
        )
    except ValueError:
        bot.reply_to(
            message,
            "❌ Date/Time မမှန်ပါ။ ဥပမာ: 2030-12-31 23:59:59"
        )
        return

    if expire <= datetime.now():
        bot.reply_to(message, "❌ Expire time က အနာဂတ်ဖြစ်ရပါမယ်။")
        return

    try:
        data, sha = get_data()

        for item in data["licenses"]:
            if item.get("hardware_id") == hardware_id:
                bot.reply_to(message, "⚠️ ဒီ Hardware ID ရှိပြီးသားပါ။")
                return

        keys = {item.get("license_key") for item in data["licenses"]}
        key = make_key()
        while key in keys:
            key = make_key()

        item = {
            "hardware_id": hardware_id,
            "license_key": key,
            "expire_date": expire.strftime("%Y-%m-%d %H:%M:%S"),
        }

        data["licenses"].append(item)
        save_data(data, sha)

        bot.reply_to(
            message,
            "✅ License created\n\n"
            f"ID: {hardware_id}\n"
            f"KEY: {key}\n"
            f"EXPIRE: {item['expire_date']}"
        )

    except requests.HTTPError as e:
        bot.reply_to(message, f"❌ GitHub error: {e.response.status_code}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")


@bot.message_handler(commands=["licenses"])
def licenses(message):
    if not admin(message):
        bot.reply_to(message, "❌ Admin only.")
        return

    try:
        data, _ = get_data()

        if not data["licenses"]:
            bot.reply_to(message, "📭 License မရှိသေးပါ။")
            return

        text = "📋 Licenses:\n\n"
        for i, item in enumerate(data["licenses"], 1):
            text += (
                f"{i}. {item.get('hardware_id', '-')}\n"
                f"KEY: {item.get('license_key', '-')}\n"
                f"EXPIRE: {item.get('expire_date', '-')}\n\n"
            )

        bot.send_message(message.chat.id, text[:4000])

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")


def run_web():
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    from threading import Thread

    Thread(target=run_web, daemon=True).start()
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)

