# Qarzlarni Hisoblash va Monitoring Qilish Tizimi (Debt Manager Backend API)

Biror kishidan qarz olayotgan yoki qarz berayotgan holatlarni yozib boradigan, valyutalar va har bir inson bo'yicha alohida qarzlarni kuzatib borish imkonini beruvchi Bekend API tizimi.

---

## Ishlatilgan Texnologiyalar

- **Python 3.10+ / 3.13**
- **FastAPI** — yuqori unumdorlikka ega zamonaviy veb freymvork
- **SQLAlchemy 2.0** — ORM ma'lumotlar bazasi bilan ishlash uchun
- **PostgreSQL** (va `psycopg2-binary`, shuningdek local ishlab chiqish va testlar uchun SQLite)
- **PyJWT & Bcrypt** — xavfsiz autentifikatsiya va parollarni shifrlash
- **Pytest** — barcha endpointlar uchun to'liq unit testlar to'plami
- **Pydantic v2** — ma'lumotlarni validatsiya qilish va sxemalashtirish

---

## Loyihani O'rnatish va Ishga Tushirish

### 1. Bog'liqliklarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Muhit o'zgaruvchilarini sozlash (.env)
Loyihada `.env` fayli mavjud. PostgreSQL ulanishini quyidagicha sozlashingiz mumkin:
```env
PROJECT_NAME="Debt Management API"
VERSION="1.0.0"
API_V1_STR="/api"

# PostgreSQL ulanishi:
# DATABASE_URL=postgresql://postgres:parol@localhost:5432/debt_db
# Yoki SQLite (standart):
DATABASE_URL=sqlite:///./debts.db

SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Serverni ishga tushirish
```bash
uvicorn app.main:app --reload
```
Server ishga tushgach:
- **Interaktiv API Hujjatlari (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Muqobil Hujjatlar (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpointlar Ro'yxati

### 1. Autentifikatsiya (Login / Registratsiya)
| Metod | Endpoint | Tavsif |
|---|---|---|
| `POST` | `/api/auth/register` | Yangi foydalanuvchini ro'yxatdan o'tkazish |
| `POST` | `/api/auth/login` | Tizimga kirish va JWT token olish (`access_token`) |
| `GET` | `/api/auth/me` | Joriy tizimga kirgan foydalanuvchi ma'lumotlari |

### 2. Sozlamalar (Profile / Settings)
| Metod | Endpoint | Tavsif |
|---|---|---|
| `GET` | `/api/settings/` | Foydalanuvchi sozlamalarini olish (asosiy valyuta, eslatma vaqti va kunlari) |
| `PUT` / `PATCH` | `/api/settings/` | Sozlamalarni o'zgartirish (UPDATE) |

**Sozlamalarni o'zgartirish tanasi (JSON misol):**
```json
{
  "default_currency": "USD",
  "reminder_time": "10:00",
  "reminder_days_before": 2,
  "notifications_enabled": true
}
```

### 3. Monitoring va Dashboard
| Metod | Endpoint | Tavsif |
|---|---|---|
| `GET` | `/api/monitoring/` | Asosiy sahifa statistikasi: umumiy berilgan qarz, umumiy olingan qarz, joriy balans va valyutalar bo'yicha tahlil |

**Monitoring javob misoli:**
```json
{
  "default_currency": "UZS",
  "total_owed_to": 1200000.0,
  "total_owed_by": 500000.0,
  "current_balance": 700000.0,
  "currency_breakdown": [
    {
      "currency": "UZS",
      "total_owed_to": 1200000.0,
      "total_owed_by": 500000.0,
      "net_balance": 700000.0,
      "active_debts_count": 3,
      "paid_debts_count": 1
    }
  ],
  "total_debts_count": 4,
  "active_debts_count": 3,
  "paid_debts_count": 1,
  "overdue_debts_count": 0
}
```

### 4. Qarzlar Boshqaruvi (Debts Management)
| Metod | Endpoint | Tavsif |
|---|---|---|
| `POST` | `/api/debts/` | Yangi qarz qo'shish |
| `GET` | `/api/debts/` | Barcha qarzlar ro'yxati (yoki filtrlar bo'yicha) |
| `GET` | `/api/debts/{debt_id}` | Bitta qarzning to'liq ma'lumotlarini olish |
| `PUT` / `PATCH` | `/api/debts/{debt_id}` | Qarzni o'zgartirish (UPDATE) |
| `DELETE` | `/api/debts/{debt_id}` | Qarzni o'chirish (DELETE) |

#### Qarz qo'shish uchun so'rov tanasi (JSON):
```json
{
  "person_name": "Azamat",
  "debt_type": "owed_to",
  "amount": 600000.0,
  "currency": "UZS",
  "description": "Loyiha xarajatlari uchun",
  "is_paid": false,
  "date_incurred": "2024-04-27T10:00:00Z",
  "date_due": "2024-05-27T18:00:00Z",
  "reminder_enabled": true
}
```

#### Qarzlar ro'yxatini 3 ta filtr bo'yicha olish:

1. **Berilgan qarzlar ("Owed To Me")**:
   ```http
   GET /api/debts/?debt_type=owed_to
   ```
2. **Olingan qarzlar ("Owed By Me")**:
   ```http
   GET /api/debts/?debt_type=owed_by
   ```
3. **Individual hisobot (har bir inson kesimida jamlangan balans)**:
   ```http
   GET /api/debts/?debt_type=individual
   ```
   **Individual filtr javob misoli:**
   ```json
   [
     {
       "person_name": "Azamat",
       "currency": "UZS",
       "total_owed_to": 1100000.0,
       "total_owed_by": 1786000.0,
       "net_balance": -686000.0,
       "debts_count": 2,
       "debts": [ ... ]
     },
     {
       "person_name": "Besulton",
       "currency": "UZS",
       "total_owed_to": 80000.0,
       "total_owed_by": 0.0,
       "net_balance": 80000.0,
       "debts_count": 1,
       "debts": [ ... ]
     }
   ]
   ```

---

## Unit Testlarni Ishga Tushirish

Barcha API endpointlari uchun kamida 20 ta to'liq qamrovli avtomatlashtirilgan unit testlar yozilgan:

```bash
pytest -v tests/
```

Testlar quyidagilarni o'z ichiga oladi:
- `test_auth.py` — Foydalanuvchi registratsiyasi, login, noto'g'ri parol, takroriy username bloklanishi, JWT token tekshiruvi.
- `test_settings.py` — Standart sozlamalarni olish, valyuta va eslatmalarni yangilash (PUT va PATCH), ruxsatsiz kirish bloklanishi.
- `test_debts.py` — Qarz yaratish (POST), `owed_to` va `owed_by` bo'yicha filtrlash, individual hisob-kitob balansi (`debt_type=individual`), qarzni tahrirlash (UPDATE), o'chirish (DELETE) va xavfsizlik izolyatsiyasi.
- `test_monitoring.py` — Dashboard monitoring summalari, olingan va berilgan qarzlar yig'indisi, farq (balans) hisob-kitobi va ko'p valyutali monitoring.
