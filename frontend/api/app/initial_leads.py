import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .models import Submission, BotSession

logger = logging.getLogger("tashtech.initial_leads")

INITIAL_LEADS = [
    {
        "id": 1,
        "full_name": "Jaloliddinov Salohiddin Ziyodulla o'g'li",
        "phone": "+998 997110938",
        "telegram_username": "@jaloliddinovff",
        "region": "Toshkent shahri",
        "school": "300-DIUM ni bitirgan",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-06 15:31:07",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 2,
        "full_name": "Mamatkulov Aziz Ilhomovich",
        "phone": "+998 508725842",
        "telegram_username": "@Azizjon_7o7",
        "region": "Samarqand viloyati",
        "school": "13-Maktab",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-06 15:45:53",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 3,
        "full_name": "Mardonova Mahliyo Davronovna",
        "phone": "+998 932118177",
        "telegram_username": "@Kaktus_br",
        "region": "Surxondaryo viloyati",
        "school": "23-umumiy o'rta ta'lim maktabi",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-06 16:18:51",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 4,
        "full_name": "Жиянов Шохрух Максудович",
        "phone": "+998 903224538",
        "telegram_username": "@Shoxch1k_1",
        "region": "г. Ташкент",
        "school": "280",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-06 18:06:44",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 5,
        "full_name": "Жиянов Шохрух Максудович",
        "phone": "+998 903224535",
        "telegram_username": "@Shxoch1k_1",
        "region": "г. Ташкент",
        "school": "280",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-06 18:07:56",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 6,
        "full_name": "Jabborov Abbos Axtamovich",
        "phone": "+998 873006022",
        "telegram_username": "@Abbos",
        "region": "Qashqadaryo viloyati",
        "school": "6 maktab",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-06 21:34:22",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 7,
        "full_name": "Muhammadsafo Xasanjonov",
        "phone": "+998 979591619",
        "telegram_username": "@khasanjonov_m",
        "region": "Toshkent shahri",
        "school": "Shaykhontohur TIM",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-07 02:12:22",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 8,
        "full_name": "Шадаминов Ратмир Ренатович",
        "phone": "+998 998889044",
        "telegram_username": "@RatmirShadaminov",
        "region": "г. Ташкент",
        "school": "260 школа",
        "question_text": "Включены ли участия в олимпиадах в курсы математики и физики? На каком языке будет проходить обучение? какое время будут проходить занятия по всем предметам и в какие дни.",
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-07 06:05:30",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 9,
        "full_name": "Иброхимов Мухаммадхабиб Еркинбек уг’ли",
        "phone": "+998 958281011",
        "telegram_username": "@Aston_McMissile",
        "region": "г. Ташкент",
        "school": "17-ая школа",
        "question_text": "Здравствуйте ТТ.\nЕсли у вас есть время на ответ , то можно ли задать вопрос ?\nЯ недавно закончил НТ «программирование» и хотелось спросить мы будем ли изучать программирование, так как это базовая часть инженера.\nЗаранее благодарю!",
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-07 07:15:49",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 10,
        "full_name": "Azimjanov Behruz",
        "phone": "+998 942272739",
        "telegram_username": "@slimli01m07@gmail.com",
        "region": "Toshkent shahri",
        "school": "185",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-07 14:27:19",
        "user_agent": "Telegram Bot (UZ)"
    },
    {
        "id": 11,
        "full_name": "Hasanov Abdurahmon Racshanovich",
        "phone": "+998 917175775",
        "telegram_username": "@abdurahmon_hasanov",
        "region": "Surxondaryo viloyati",
        "school": "78-maktab",
        "question_text": None,
        "status": "Yangi",
        "is_contacted": False,
        "contacted_by": None,
        "contacted_at": None,
        "created_at": "2026-10-07 14:54:56",
        "user_agent": "Telegram Bot (UZ)"
    }
]

SEED_VERSION_KEY = "__SEEDED_V5_11_LEADS__"

def seed_initial_data(db: Session, force: bool = False):
    try:
        flag = db.query(BotSession).filter(BotSession.user_id == SEED_VERSION_KEY).first()
        if flag and not force:
            count = db.query(Submission).count()
            return count, None

        for item in INITIAL_LEADS:
            existing = db.query(Submission).filter(Submission.phone == item["phone"]).first()
            if not existing:
                c_at = None
                if item.get("created_at"):
                    try:
                        c_at = datetime.fromisoformat(item["created_at"])
                    except Exception:
                        pass
                cont_at = None
                if item.get("contacted_at"):
                    try:
                        cont_at = datetime.fromisoformat(item["contacted_at"])
                    except Exception:
                        pass

                sub = Submission(
                    id=item.get("id"),
                    full_name=item.get("full_name", ""),
                    phone=item.get("phone", ""),
                    telegram_username=item.get("telegram_username", ""),
                    region=item.get("region", ""),
                    school=item.get("school", ""),
                    question_text=item.get("question_text"),
                    telegram_sent=True,
                    telegram_message_id="",
                    telegram_error=None,
                    status=item.get("status", "Yangi"),
                    is_contacted=bool(item.get("is_contacted", False)),
                    contacted_by=item.get("contacted_by"),
                    contacted_at=cont_at,
                    created_at=c_at or datetime.now(timezone.utc),
                    user_agent=item.get("user_agent", "Telegram Bot")
                )
                db.add(sub)

        if not flag:
            db.add(BotSession(user_id=SEED_VERSION_KEY, step="DONE", data="{}"))

        db.commit()
        cur_count = db.query(Submission).count()
        logger.info(f"Loaded initial leads. Current count: {cur_count}")
        return cur_count, None
    except Exception as e:
        db.rollback()
        logger.warning(f"Initial leads loader error: {e}")
        return 0, str(e)
