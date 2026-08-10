import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8535512510:AAHXuG6Vp4ATkF1hqSGlOa56vagz0Cruh6c"
ADMIN_USER_ID = 1801787123  # သင့်ရဲ့ Telegram ID

# /add Command ဖြင့် လိုင်စင်အသစ်ထည့်ရန်
async def add_license(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin ဟုတ်မဟုတ် စစ်ဆေးခြင်း
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ ဒီ Command ကို သုံးခွင့်မရှိပါ။")
        return
        
    # လိုအပ်သော အချက်အလက် ပါမပါ စစ်ဆေးခြင်း
    # ဥပမာ - /add EASY-XXXX-XXXX EASY-TO-XXXX 2030-12-31
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ ပုံစံမမှန်ပါ။ ဤကဲ့သို့ ရိုက်ထည့်ပါ:\n\n"
            "`/add <Hardware_ID> <License_Key> <Expire_Date>`\n\n"
            "ဥပမာ: `/add EASY-1234-5678 EASY-TO-KEY 2030-12-31`",
            parse_mode="Markdown"
        )
        return
        
    new_hw = context.args[0]
    new_key = context.args[1]
    new_expire = context.args[2]
    
    try:
        # 1. ရှိပြီးသား api.json ဖိုင်ကို ဖတ်ခြင်း
        with open('api.json', 'r') as file:
            data = json.load(file)
            
        # 2. ဒေတာအသစ် ထည့်ရန် ဖန်တီးခြင်း
        new_entry = {
            "hardware_id": new_hw,
            "license_key": new_key,
            "expire_date": new_expire
        }
        
        # 3. licenses array ထဲသို့ အသစ်ထည့်ခြင်း
        data['licenses'].append(new_entry)
        
        # 4. api.json ဖိုင်ထဲသို့ ပြန်လည် သိမ်းဆည်းခြင်း
        with open('api.json', 'w') as file:
            json.dump(data, file, indent=4)
            
        await update.message.reply_text(
            f"✅ **လိုင်စင်အသစ် အောင်မြင်စွာ ထည့်သွင်းပြီးပါပြီ!**\n\n"
            f"💻 Hardware ID: `{new_hw}`\n"
            f"🔑 Key: `{new_key}`\n"
            f"📅 Expire: `{new_expire}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားအယွင်းရှိသည်: {e}")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("add", add_license))

    print("🤖 Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()

if __name__ == '__main__':
    main()
