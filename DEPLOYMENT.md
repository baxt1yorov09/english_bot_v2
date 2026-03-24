# Render.com Deployment Guide

## 🚀 **Botni Render.com ga Joylash**

### **1. Git Repository Tayyorlash:**
```bash
git init
git add .
git commit -m "Initial commit - Telegram Bot"
```

### **2. Render.com ga Kirish:**
- [render.com](https://render.com) ga kiring
- **GitHub** orqali ro'yxatdan o'ting
- **New +** -> **Web Service** ni bosing

### **3. Repository Qo'shish:**
- **Build & deploy from a Git repository** ni tanlang
- GitHub repositoryingizni qo'shing

### **4. Environment Variables:**
**Environment** bo'limiga quyidagilarni kiriting:

```
BOT_TOKEN=8673101909:AAF7JLVe4lwPA1ZUKTCz4Av1Lyqcr5OwEx8
ADMIN_ID=5475526744,5687217504
MANDATORY_CHANNELS=SirojiddinovAcademy
DATABASE_URL=sqlite:///./bot.db
SPEAKING_PARTNER_LINK=https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice#demo
READING_LINK=https://jamesclear.com/articles
LISTENING_LINK=https://www.podcastsinenglish.com/
```

### **5. Runtime Configuration:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements_render.txt`
- **Start Command**: `python bot.py`
- **Instance Type**: `Free` ($0/oy)

### **6. Database Sozlamalari:**
Render.com da **PostgreSQL** bepul:
- **New +** -> **PostgreSQL**
- **Database Name**: `telegram_bot`
- **User**: `render_user`
- **URL**: Render beradi

### **7. Final Environment Variables:**
```
DATABASE_URL=postgresql://render_user:password@host:5432/telegram_bot
```

## 📱 **Test Qilish:**
1. Render.com botni deploy qiladi (5-10 daqiqa)
2. **Webhook** avtomatik o'rnatiladi
3. Bot ishga tushadi va test qilish mumkin

## 🔧 **Qo'shimcha Sozlamalar:**

### **Health Check:**
```python
# bot.py ga qo'shing
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now()})

if __name__ == "__main__":
    # Bot va Flask birga ishlashi
    import threading
    bot_thread = threading.Thread(target=bot.run)
    bot_thread.start()
    app.run(host='0.0.0.0', port=10000)
```

### **Debug Mode:**
```python
# .env ga qo'shing
DEBUG=False
LOG_LEVEL=INFO
```

## 💰 **Narxlar:**
- **Free Plan**: 750 soat/oy (bot uchun yetarli)
- **PostgreSQL**: Bepul
- **Bandwidth**: 100GB/oy (bot uchun yetarli)

## 🎯 **Alternative Platformlar:**
1. **Heroku** (Free plan yo'q)
2. **Railway** ($5/oy)
3. **PythonAnywhere** ($5/oy)
4. **VPS** ($5-10/oy)

## ✅ **Tavsiya:**
**Render.com** eng yaxshi tanlov - bepul va oson!
