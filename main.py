import telebot
import os

TOKEN = "8535512510:AAFYDZfmxeIP7enJ8pk6iNQg2ef30KPjPlg"
bot = telebot.TeleBot(TOKEN)

ADMIN_IDS = [1801787123]
devices_db = {}

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
            bot.reply_to(message, "❌ ဥပမာ - /addpoint ABC12345 5")
            return
        device_id = args[1]
        points = int(args[2])
        if device_id not in devices_db:
            devices_db[device_id] = {"credits": 0}
        devices_db[device_id]["credits"] += points
        bot.reply_to(message, f"✅ Success! လက်ကျန်ပွိုင့် - {devices_db[device_id]['credits']}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

print("Bot is running...")
bot.infinity_polling()
