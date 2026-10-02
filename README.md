# TashTech — Onboarding & Foundation Program Portal

Zamonaviy muhandislik universiteti **Tashkent University of Technology (TashTech)** uchun ishlab chiqilgan onboarding va Foundation dasturiga ariza qabul qilish veb-platformasi.

Ushbu loyiha [Google Forms arizasi](https://docs.google.com/forms/d/e/1FAIpQLSfbMVmGdrnzRwBDCIGefSdBgP4sYjhBtTGZh9eGhu3v1Z5SDw/viewform) va [TashTech rasmiy veb-sayti](https://tashkenttech-edu.uz/ru) dizayn tili, to'q sariq (orange `#E54519`) muhandislik mavzusi, aylanuvchi mexanik tishli g'ildiraklar (gears), suzuvchi fizik-matematik formulalar hamda interaktiv texnologik animatsiyalar asosida to'liq yangilandi.

---

## 🚀 Texnologiyalar (Tech Stack)

- **Frontend**:
  - React 19 + Vite
  - Tailwind CSS (TashTech custom orange theme, blueprint grid, glassmorphism)
  - **Premium Engineering Canvas**: Aylanuvchi mexanik tishli g'ildiraklar (precision gears), suzuvchi formulalar (\(E=mc^2\), \(F=ma\), \(\int f(x)dx\), \(V=IR\)), atom modellari, mikrosxemalar va kursorga reaktiv to'r.
  - Lucide React piktogrammalari
  - Trilingual i18n (O'zbek, Rus va Ingliz tillari, localStorage bilan)
  - `canvas-confetti` (ariza muvaffaqiyatli topshirilganda interaktiv animatsiya)
- **Backend**:
  - Python 3.11+ / 3.14 (FastAPI)
  - **aiogram 3** (Telegram Bot API orqali guruh chatiga xabarlarni HTML formatda yetkazish)
  - SQLAlchemy ORM & SQLite (ma'lumotlarni ishonchli saqlash)
- **Konteynerizatsiya**:
  - Docker & Docker Compose (Frontend Nginx + Backend Uvicorn)

---

## 📋 Qabul qilinadigan maydonlar (Form Fields)

1. **F.I.Sh / Ф.И.О**: To'liq ism-familiya (Namunaviy: `Ibrokhimov Numonjon Nozimjon o'g'li`)
2. **Telefon raqam / Телефон**: `+998 XX XXX XX XX`
3. **Telegram User Name**: Masalan `@TT_foundation_ibrohimov`
4. **Viloyat / Hudud**: O'zbekistonning 14 ta ma'muriy hududidan biri (tanlov ro'yxati)
5. **Qaysi maktab / litseyda o'qiysiz?**: Maktab yoki litsey nomi
6. **Savol yoki izoh (Ixtiyoriy)**: Abituriyentning qo'shimcha savollari

---

## ⚡ Ishga tushirish (Qo'llanma)

### 1-usul: Docker & Docker Compose orqali

```powershell
docker compose up --build
```

- **Frontend**: [http://localhost:5173](http://localhost:5173) yoki [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

### 2-usul: Mahalliy (Local Native) ishlab chiqish

#### Backend (FastAPI + aiogram):
```powershell
cd backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API holatini tekshirish: `http://127.0.0.1:8000/api/health`

#### Frontend (React + Vite):
```powershell
cd frontend
npm install
npm run dev
```
Sayt: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## 🤖 Telegram Bot Guruhini Sozlash (aiogram)

`.env` faylida kiritilgan ma'lumotlar:
- `TELEGRAM_BOT_TOKEN=8543006786:AAHpw0uiRweH6a8EeTi0VjZeNmmN0VsnoYw`
- `TELEGRAM_CHAT_ID=-1005554437713`

> **Muhim eslatma:** Bot guruhga xabar yuborishi uchun Telegram guruhingiz a'zolari ro'yxatiga botni qo'shib, unga **Administrator** huquqini berishingiz kerak. Shunda Telegram serveri `chat not found` xatosini bermasdan arizalarni to'g'ridan-to'g'ri guruhga yetkazadi.
