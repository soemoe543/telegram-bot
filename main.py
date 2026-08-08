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

# Flask Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 AIDEN Point License Manager Bot\n\nCommands:\n/addpoint <Device_ID> <Points>")

@bot.message_handler(commands=['addpoint'])
def add_point(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ ခွင့်ပြုချက်မရှိပါ။")
        return
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "❌ ဥပမာ - /addpoint GHOST-7D0C0D8 1")
            return
        
        device_id = args[1]
        points = args[2]
        
        # AB-JVXXEV ပုံစံမျိုး Key ထုတ်ပေးခြင်း
        part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        part2 = points
        part3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        generated_key = f"{part1}-{part2}-{part3}"
        
        bot.reply_to(message, f"✅ Success!\nDevice: {device_id}\nPoints: {points}\nKey: {generated_key}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

if __name__ == '__main__':
    Thread(target=run).start()
    bot.polling()
