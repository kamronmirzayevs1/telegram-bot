# 🎓 Test Platformasi Bot

Sessiya testlari uchun professional Telegram bot.

---

## 📁 Fayl tuzilmasi

```
telegram_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Sozlamalar
├── database.py         # Ma'lumotlar bazasi
├── keyboards.py        # Tugmalar
├── requirements.txt    # Kutubxonalar
├── Procfile            # Railway uchun
├── .env.example        # .env namunasi
└── handlers/
    ├── __init__.py
    ├── user_handlers.py   # Foydalanuvchi handlerlari
    └── admin_handlers.py  # Admin handlerlari
```

---

## 🚀 BOSQICHMA-BOSQICH O'RNATISH

### 1-QADAM: Bot token olish

1. Telegramda **@BotFather** ga o'ting
2. `/newbot` yozing
3. Bot nomini kiriting (masalan: `Sessiya Test Bot`)
4. Bot username kiriting (masalan: `sessiya_test_bot`)
5. BotFather sizga **token** beradi — uni saqlang!
   - Ko'rinishi: `7123456789:AAF-xxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2-QADAM: Admin ID olish

1. Telegramda **@userinfobot** ga o'ting
2. `/start` bosing
3. U sizga **ID** beradi (masalan: `987654321`)
4. Bu sizning admin ID ingiz

### 3-QADAM: Railway.app da joylash (BEPUL)

1. **https://railway.app** ga kiring
2. GitHub bilan ro'yxatdan o'ting
3. **"New Project"** bosing
4. **"Deploy from GitHub repo"** tanlang
5. Bu papkani GitHub ga yuklang (quyida ko'rsatilgan)
6. Railway loyihani tanlang

### 4-QADAM: GitHub ga yuklash

Agar GitHub bilmasangiz, **quyidagi oddiy yo'l**:

1. **https://github.com** ga kiring va ro'yxatdan o'ting
2. **"New repository"** bosing, nom bering
3. Barcha fayllarni yuklang

Yoki terminal orqali:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/bot.git
git push -u origin main
```

### 5-QADAM: Railway Variables (muhim!)

Railway dashboard da **"Variables"** bo'limiga o'ting va quyidagilarni kiriting:

| Kalit | Qiymat | Izoh |
|-------|--------|------|
| `BOT_TOKEN` | `7123456789:AAF-xxx...` | BotFather dan olgan token |
| `ADMIN_IDS` | `987654321` | Sizning Telegram ID ingiz |
| `DATABASE_URL` | `bot_database.db` | O'zgartirmang |

Agar bir nechta admin bo'lsa: `987654321,111222333`

### 6-QADAM: Deploy

Railway avtomatik deploy qiladi. Logs bo'limida:
```
Bot ishga tushdi!
```
yozuvini ko'rsangiz — muvaffaqiyat! ✅

---

## 🎮 FOYDALANISH

### 👤 Foydalanuvchi uchun:
- `/start` — Botni ishga tushirish
- **📚 Fanlar** — Barcha kategoriyalarni ko'rish
- **📊 Natijalarim** — O'z natijalarini ko'rish
- **ℹ️ Ma'lumot** — Bot haqida

### 🛠 Admin uchun:
- `/admin` — Admin panelni ochish
- **📂 Kategoriyalar** — Fan qo'shish/o'chirish
  - Har bir fanga bo'limlar qo'shing
  - Har bir bo'limga 25 ta savol qo'shing
- **📊 Statistika** — Umumiy hisobot
- **👤 Foydalanuvchilar** — Barcha userlar
- **📨 Xabar yuborish** — Broadcast (hammaga xabar)

### 📝 Savol qo'shish tartibi:
1. `/admin` → **📂 Kategoriyalar**
2. Kategoriya tanlang yoki yangi qo'shing
3. **📝 Bo'limlar** → Bo'lim qo'shing
4. Bo'limni tanlang → **➕ Savol qo'shish**
5. Savol matnini kiriting
6. A, B, C, D variantlarini kiriting
7. To'g'ri javobni kiriting (A, B, C yoki D)

---

## 🏗 BOT IMKONIYATLARI

- ✅ Kategoriyalar (Fanlar)
- ✅ Bo'limlar (har fanda)
- ✅ 25 ta savol (A/B/C/D)
- ✅ Savollar tasodifiy tartibda
- ✅ Natijalar saqlanadi
- ✅ TOP-10 reyting
- ✅ Admin panel
- ✅ Broadcast (hammaga xabar)
- ✅ Statistika
- ✅ Progress bar (test paytida)

---

## ❓ MUAMMOLAR

**Bot ishlamayapti?**
- Token to'g'ri kiritilganini tekshiring
- Railway logs ni tekshiring

**Admin panel ko'rinmayapti?**
- ADMIN_IDS ga o'z Telegram ID ingizni kiriting
- `/admin` buyrug'ini yozing

**Savollar ko'rinmayapti?**
- Avval kategoriya, keyin bo'lim, keyin savol qo'shing

---

## 📞 Texnik ma'lumot

- **Til:** Python 3.11+
- **Framework:** Aiogram 3.7
- **DB:** SQLite (aiosqlite)
- **Hosting:** Railway.app
