import base64
import json
import logging
import random
import string
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8535512510:AAHXuG6Vp4ATkF1hqSGlOa56vagz0Cruh6c"
ADMIN_USER_ID = 1801787123

# GitHub ဆိုင်ရာ အချက်အလက်များ
GITHUB_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"  # သင့်ရဲ့ GitHub Token ထည့်ရန်
REPO_OWNER = "soemoe543"
REPO_NAME = "telegram-bot"
FILE_PATH = "api.json"

# မတူညီသော License Key အသစ် အလိုအလျောက် ဖန်တီးသည့် Function
def generate_unique_key():
    part1 = ''.join(random.choices(string.ascii_uppercase, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"EASY-{part1}-{part2}"

async def add_license(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ ဒီ Command ကို သုံးခွင့်မရှိပါ။")
        return
        
    # အသုံးပြုသူက ID နဲ့ Expire Date ကိုပဲ ထည့်ရပါမည် (Key က အလိုအလျောက် ထွက်မည်)
    # ဥပမာ: /add EASY-3C48-400C-CDAC 2030-12-31
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ ပုံစံမမှန်ပါ။ ဤကဲ့သို့ ရိုက်ပါ:\n\n"
            "`/add <Hardware_ID> <Expire_Date>`\n\n"
            "ဥပမာ: `/add EASY-3C48-400C-CDAC 2030-12-31`",
            parse_mode="Markdown"
        )
        return
        
    hardware_id = context.args[0]
    expire_date = context.args[1]
    
    # မတူညီသော Key အသစ်ကို အလိုအလျောက် ထုတ်ယူခြင်း
    generated_key = generate_unique_key()
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    
    try:
        # ၁။ GitHub ထဲက api.json ကို ဖတ်ခြင်း
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            await update.message.reply_text("❌ GitHub ထဲက ဖိုင်ကို ဆွဲယူ၍မရပါ။ Token စစ်ပါ။")
            return
            
        file_data = res.json()
        sha = file_data['sha']
        
        content_decoded = base64.b64decode(file_data['content']).decode('utf-8')
        json_data = json.loads(content_decoded)
        
        # ၂။ ဒေတာအသစ် ဖန်တီးခြင်း
        new_entry = {
            "hardware_id": hardware_id,
            "license_key": generated_key,
            "expire_date": expire_date
        }
        json_data['licenses'].append(new_entry)
        
        # ၃။ GitHub ထဲသို့ ပြန်လည် Commit တင်ခြင်း (api.json ကို ပုံစံအမှန်အတိုင်း Update လုပ်ရန်)
        updated_content_str = json.dumps(json_data, indent=4)
        updated_content_base64 = base64.b64encode(updated_content_str.encode('utf-8')).decode('utf-8')
        
        data_to_commit = {
            "message": f"Add license for {hardware_id} via Bot",
            "content": updated_content_base64,
            "sha": sha
        }
        
        put_res = requests.put(url, headers=headers, json=data_to_commit)
        
        if put_res.status_code in [200, 201]:
            # ၄။ ပြီးသွားလျှင် ထည့်ပြီးသား အချက်အလက်များကို Bot က ပြန်ပို့ပေးမည်
            await update.message.reply_text(
                f"✅ **GitHub `api.json` သို့ အောင်မြင်စွာ ထည့်သွင်းပြီးပါပြီ!**\n\n"
                f"💻 **Hardware ID:** `{hardware_id}`\n"
                f"🔑 **License Key:** `{generated_key}`\n"
                f"📅 **Expire Date:** `{expire_date}`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ GitHub သို့ တင်၍မရပါ: {put_res.text}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားအယွင်းရှိသည်: {e}")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("add", add_license))
    application.run_polling()

if __name__ == '__main__':
    main()
