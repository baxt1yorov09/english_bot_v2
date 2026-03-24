# Render.com Deployment

## 🚀 **Qadam-baqadam Joylash:**

### **1. Git Repository Tayyorlash:**
```bash
# Bot papkasida
git init
git add .
git commit -m "Telegram Bot - Ready for deployment"
```

### **2. GitHub ga Yuklash:**
```bash
# GitHub da yangi repository oching
git remote add origin https://github.com/username/telegram-bot.git
git push -u origin main
```

### **3. Render.com ga Kirish:**
1. [render.com](https://render.com) ga kiring
2. **Sign up** -> **GitHub** bilan ulaning
3. **Dashboard** -> **New +** -> **Web Service**

### **4. Repository Tanlash:**
- **GitHub** repositoryingizni tanlang
- **Name**: `english-learning-bot`
- **Region**: Eng yaqin region (EU)

### **5. Build Settings:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements_render.txt`
- **Start Command**: `python bot.py`
- **Instance Type**: `Free`

### **6. Environment Variables:**
**Environment** bo'limiga quyidagilarni kiriting:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | `8673101909:AAF7JLVe4lwPA1ZUKTCz4Av1Lyqcr5OwEx8` |
| `ADMIN_ID` | `5475526744,5687217504` |
| `MANDATORY_CHANNELS` | `SirojiddinovAcademy` |
| `DATABASE_URL` | `sqlite:///./bot.db` |
| `SPEAKING_PARTNER_LINK` | `https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice#demo` |
| `READING_LINK` | `https://jamesclear.com/articles` |
| `LISTENING_LINK` | `https://www.podcastsinenglish.com/` |

### **7. PostgreSQL (Ixtiyoriy):**
Agar PostgreSQL xohlasangiz:
- **New +** -> **PostgreSQL**
- **Name**: `telegram-bot-db`
- **Database URL** ni `.env` ga qo'shing

### **8. Deploy Qilish:**
- **Create Web Service** ni bosing
- Render avtomatik deploy qiladi (5-10 daqiqa)
- Loglarni kuzatib boring

## 🔧 **Troubleshooting:**

### **Agar bot ishlamasa:**
1. **Logs** ni tekshiring
2. **Environment Variables** ni tekshiring
3. **BOT_TOKEN** to'g'riligini tekshiring
4. **Port** muammosi bo'lsa, webhook kerak bo'ladi

### **Webhook uchun:**
```python
# bot.py ga qo'shing
import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = Update.de_json(request.get_json(), bot)
        bot.process_update(update)
        return 'OK'
    return 'Bad Request', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
```

## 📱 **Test Qilish:**
1. Deploy tugagach, **Logs** ni tekshiring
2. Botga `/start` yuboring
3. Admin panelni tekshiring
4. Kanal tekshiruvini tekshiring

## 💰 **Narxlar:**
- **Free Plan**: 750 soat/oy (bot uchun yetarli)
- **PostgreSQL**: Bepul
- **Bandwidth**: 100GB/oy

## 🎯 **Tavsiya:**
**Render.com** eng yaxshi tanlov:
- ✅ Bepul
- ✅ Oson joylash
- ✅ PostgreSQL support
- ✅ Auto-deploy
- ✅ Good documentation

Endi botingizni serverga joylashingiz mumkin! 🚀
