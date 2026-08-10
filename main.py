import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8535512510:AAHXuG6Vp4ATkF1hqSGlOa56vagz0Cruh6c"
ADMIN_USER_ID = 1801787123  # သင့်ရဲ့ Telegram User ID

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 AIDEN Point License Manager Bot\n\n"
        "Commands:\n"
        "/addpoint <Device_ID> <Points>"
    )

# Add Point / License Command
async def addpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ ဒီ Command ကို သုံးခွင့်မရှိပါ။")
        return
        
    # ဥပမာ - /addpoint GHOST-26F5999A 2 လို့ ရိုက်လိုက်ရင်
    if len(context.args) < 2:
        await update.message.reply_text("❌ ပုံစံမမှန်ပါ။ ဤကဲ့သို့ ရိုက်ပါ:\n`/addpoint <Device_ID> <Points>`", parse_mode="Markdown")
        return
        
    device_id = context.args[0]
    points = context.args[1]
    
    try:
        # api.json ဖိုင်ကို ဖတ်ခြင်း (မရှိသေးရင် အသစ်စတည်ခြင်း)
        try:
            with open('api.json', 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"licenses": []}
            
        # ဒေတာအသစ် ထည့်ရန်
        new_entry = {
            "device_id": device_id,
            "points": points
        }
        data['licenses'].append(new_entry)
        
        # api.json ဖိုင်ထဲသို့ ပြန်သိမ်းခြင်း
        with open('api.json', 'w') as file:
            json.dump(data, file, indent=4)
            
        await update.message.reply_text(
            f"✅ Success!\n"
            f"Device: `{device_id}`\n"
            f"Points: `{points}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားအယွင်းရှိသည်: {e}")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers များ ချိတ်ဆက်ခြင်း
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addpoint", addpoint))

    print("🤖 Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()

if __name__ == '__main__':
    main()
