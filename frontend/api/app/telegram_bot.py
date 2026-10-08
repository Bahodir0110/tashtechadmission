import html
import json
import re
import logging
from typing import Optional, Tuple
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.exceptions import TelegramAPIError

from .config import settings
from .database import SessionLocal
from .models import Submission, BotSession, UserQuestion
from .initial_leads import seed_initial_data

logger = logging.getLogger("tashtech.telegram")

bot: Optional[Bot] = None
dp = Dispatcher()

def get_bot() -> Optional[Bot]:
    global bot
    token = settings.TELEGRAM_BOT_TOKEN
    if token and "YOUR_" not in token and len(token.strip()) > 10:
        if bot is None:
            bot = Bot(
                token=token.strip(),
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
        return bot
    return None


# =====================================================================
# Multilingual Dictionaries & Texts
# =====================================================================

TEXTS = {
    "uz": {
        "welcome": (
            "Assalomu alaykum! 🏛\n"
            "<b>Tashkent University of Technology (TashTech)</b> Foundation dasturi rasmiy botiga xush kelibsiz!\n\n"
            "Iltimos, muloqot tilini tanlang:\n\n"
            "Здравствуйте! 🏛\n"
            "Добро пожаловать в официальный бот программы Foundation <b>TashTech</b>!\n\n"
            "Пожалуйста, выберите язык общения:\n\n"
            "Welcome! 🏛\n"
            "Welcome to the official <b>TashTech</b> Foundation program bot!\n\n"
            "Please choose your preferred language:"
        ),
        "lang_selected": "🇺🇿 O'zbek tili tanlandi.\n\nKerakli bo'limni tanlang:",
        "main_menu_prompt": "Kerakli bo'limni tanlang:",
        "btn_apply": "📝 Ariza yuborish",
        "btn_question": "❓ Savol yuborish",
        "btn_change_lang": "🌐 Tilni o'zgartirish",
        "btn_cancel": "❌ Bekor qilish",
        "btn_share_contact": "📱 Telefon raqamni ulashish",
        "btn_skip": "➡️ O'tkazib yuborish",
        "cancelled": "Amal bekor qilindi. Bosh menyudasiz:",
        "step_name": (
            "👤 <b>1/5. Ism, familiya va sharifingizni kiriting:</b>\n"
            "<i>(Masalan: Ibrokhimov Numonjon Nozimjon o'g'li)</i>"
        ),
        "invalid_name": "Iltimos, ism va familiyangizni to'liq kiriting:",
        "step_phone": (
            "📞 <b>2/5. Telefon raqamingizni kiriting yoki pastdagi tugmani bosing:</b>\n"
            "<i>(Masalan: +998901234567)</i>"
        ),
        "invalid_phone": "Iltimos, to'g'ri telefon raqam kiriting (masalan: +998901234567):",
        "step_tg": (
            "✈️ <b>3/5. Telegram username yoki profilingiz:</b>\n"
            "<i>(Masalan: @username)</i>"
        ),
        "step_region": "📍 <b>4/5. Yashash viloyatingiz / hududingizni tanlang:</b>",
        "step_region_sub": "Quyidagi ro'yxatdan o'z hududingizni bosing:",
        "region_selected": "📍 Hudud tanlandi: <b>{region}</b>",
        "step_school": (
            "🏫 <b>5/5. Qaysi maktab yoki akademik litseyda o'qiysiz?</b>\n"
            "<i>(Masalan: 110-sonli ixtisoslashtirilgan maktab)</i>"
        ),
        "invalid_school": "Iltimos, maktab yoki litsey nomini to'liq kiriting:",
        "step_comment": (
            "💬 <b>Qo'shimcha savol yoki izohingiz bormi?</b>\n"
            "<i>(Ixtiyoriy. Agar bo'lmasa, '➡️ O'tkazib yuborish' tugmasini bosing)</i>"
        ),
        "apply_success": (
            "🎉 <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
            "🆔 <b>Ariza raqami:</b> #{id}\n"
            "👤 <b>F.I.Sh:</b> {name}\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "📍 <b>Hudud:</b> {region}\n"
            "🏫 <b>Maktab/Litsey:</b> {school}\n\n"
            "Tashkent University of Technology qabul komissiyasi tez orada siz bilan bog'lanadi! 🏛"
        ),
        "ask_question_prompt": (
            "❓ <b>TashTech Foundation kursi bo'yicha savolingizni yozib qoldiring:</b>\n\n"
            "Savolingiz to'g'ridan-to'g'ri qabul komissiyasiga yetkaziladi va mutaxassislarimiz shu bot orqali sizga javob yozishadi."
        ),
        "question_success": (
            "✅ <b>Savolingiz qabul komissiyasiga muvaffaqiyatli yetkazildi!</b>\n\n"
            "Mutaxassislarimiz savolingizga javob berishi bilan sizga shu bot orqali xabar yetkaziladi."
        ),
        "staff_header": "🏛 <b>Tashkent University of Technology (Qabul komissiyasi):</b>",
        "your_question_label": "💬 <i>Sizning savolingiz:</i>",
        "answer_label": "📩 <b>Javob:</b>",
        "answered_by_label": "👤 <i>Javob berdi:</i>"
    },
    "ru": {
        "welcome": (
            "Assalomu alaykum! 🏛\n"
            "<b>Tashkent University of Technology (TashTech)</b> Foundation dasturi rasmiy botiga xush kelibsiz!\n\n"
            "Iltimos, muloqot tilini tanlang:\n\n"
            "Здравствуйте! 🏛\n"
            "Добро пожаловать в официальный бот программы Foundation <b>TashTech</b>!\n\n"
            "Пожалуйста, выберите язык общения:\n\n"
            "Welcome! 🏛\n"
            "Welcome to the official <b>TashTech</b> Foundation program bot!\n\n"
            "Please choose your preferred language:"
        ),
        "lang_selected": "🇷🇺 Выбран русский язык.\n\nВыберите нужный раздел:",
        "main_menu_prompt": "Выберите нужный раздел:",
        "btn_apply": "📝 Подать заявку",
        "btn_question": "❓ Задать вопрос",
        "btn_change_lang": "🌐 Сменить язык",
        "btn_cancel": "❌ Отмена",
        "btn_share_contact": "📱 Поделиться контактом",
        "btn_skip": "➡️ Пропустить",
        "cancelled": "Действие отменено. Вы в главном меню:",
        "step_name": (
            "👤 <b>1/5. Введите ваши Ф.И.О.:</b>\n"
            "<i>(Например: Иброхимов Нумонжон Нозимжон угли)</i>"
        ),
        "invalid_name": "Пожалуйста, введите ваше полное имя и фамилию:",
        "step_phone": (
            "📞 <b>2/5. Введите номер телефона или нажмите кнопку ниже:</b>\n"
            "<i>(Например: +998901234567)</i>"
        ),
        "invalid_phone": "Пожалуйста, введите правильный номер телефона (например: +998901234567):",
        "step_tg": (
            "✈️ <b>3/5. Ваш Telegram username или профиль:</b>\n"
            "<i>(Например: @username)</i>"
        ),
        "step_region": "📍 <b>4/5. Выберите ваш регион проживания:</b>",
        "step_region_sub": "Нажмите на ваш регион из списка ниже:",
        "region_selected": "📍 Регион выбран: <b>{region}</b>",
        "step_school": (
            "🏫 <b>5/5. В какой школе или академическом лицее вы учитесь?</b>\n"
            "<i>(Например: Специализированная школа №110)</i>"
        ),
        "invalid_school": "Пожалуйста, введите полное название школы или лицея:",
        "step_comment": (
            "💬 <b>Есть ли у вас дополнительный вопрос или комментарий?</b>\n"
            "<i>(Необязательно. Если нет, нажмите '➡️ Пропустить')</i>"
        ),
        "apply_success": (
            "🎉 <b>Ваша заявка успешно принята!</b>\n\n"
            "🆔 <b>Номер заявки:</b> #{id}\n"
            "👤 <b>Ф.И.О.:</b> {name}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "📍 <b>Регион:</b> {region}\n"
            "🏫 <b>Школа/Лицей:</b> {school}\n\n"
            "Приемная комиссия Tashkent University of Technology скоро свяжется с вами! 🏛"
        ),
        "ask_question_prompt": (
            "❓ <b>Напишите ваш вопрос по курсу TashTech Foundation:</b>\n\n"
            "Ваш вопрос будет передан напрямую в приемную комиссию, и наши специалисты ответят вам через этот бот."
        ),
        "question_success": (
            "✅ <b>Ваш вопрос успешно отправлен в приемную комиссию!</b>\n\n"
            "Как только специалисты ответят, вы получите уведомление в этом боте."
        ),
        "staff_header": "🏛 <b>Tashkent University of Technology (Приемная комиссия):</b>",
        "your_question_label": "💬 <i>Ваш вопрос:</i>",
        "answer_label": "📩 <b>Ответ:</b>",
        "answered_by_label": "👤 <i>Ответил:</i>"
    },
    "en": {
        "welcome": (
            "Assalomu alaykum! 🏛\n"
            "<b>Tashkent University of Technology (TashTech)</b> Foundation dasturi rasmiy botiga xush kelibsiz!\n\n"
            "Iltimos, muloqot tilini tanlang:\n\n"
            "Здравствуйте! 🏛\n"
            "Добро пожаловать в официальный бот программы Foundation <b>TashTech</b>!\n\n"
            "Пожалуйста, выберите язык общения:\n\n"
            "Welcome! 🏛\n"
            "Welcome to the official <b>TashTech</b> Foundation program bot!\n\n"
            "Please choose your preferred language:"
        ),
        "lang_selected": "🇬🇧 English language selected.\n\nPlease choose a section:",
        "main_menu_prompt": "Please select an option:",
        "btn_apply": "📝 Submit application",
        "btn_question": "❓ Ask a question",
        "btn_change_lang": "🌐 Change language",
        "btn_cancel": "❌ Cancel",
        "btn_share_contact": "📱 Share phone number",
        "btn_skip": "➡️ Skip",
        "cancelled": "Action cancelled. You are in the main menu:",
        "step_name": (
            "👤 <b>1/5. Enter your full name:</b>\n"
            "<i>(For example: Ibrokhimov Numonjon Nozimjon ugli)</i>"
        ),
        "invalid_name": "Please enter your full name:",
        "step_phone": (
            "📞 <b>2/5. Enter your phone number or click the button below:</b>\n"
            "<i>(For example: +998901234567)</i>"
        ),
        "invalid_phone": "Please enter a valid phone number (e.g., +998901234567):",
        "step_tg": (
            "✈️ <b>3/5. Your Telegram username or profile link:</b>\n"
            "<i>(For example: @username)</i>"
        ),
        "step_region": "📍 <b>4/5. Select your region of residence:</b>",
        "step_region_sub": "Click your region from the list below:",
        "region_selected": "📍 Region selected: <b>{region}</b>",
        "step_school": (
            "🏫 <b>5/5. Which school or academic lyceum do you study at?</b>\n"
            "<i>(For example: Specialized School No. 110)</i>"
        ),
        "invalid_school": "Please enter your school or lyceum name:",
        "step_comment": (
            "💬 <b>Do you have an additional question or comment?</b>\n"
            "<i>(Optional. If not, press '➡️ Skip')</i>"
        ),
        "apply_success": (
            "🎉 <b>Your application has been successfully submitted!</b>\n\n"
            "🆔 <b>Application ID:</b> #{id}\n"
            "👤 <b>Full Name:</b> {name}\n"
            "📞 <b>Phone:</b> {phone}\n"
            "📍 <b>Region:</b> {region}\n"
            "🏫 <b>School/Lyceum:</b> {school}\n\n"
            "The admissions committee of Tashkent University of Technology will contact you shortly! 🏛"
        ),
        "ask_question_prompt": (
            "❓ <b>Please write your question about the TashTech Foundation course:</b>\n\n"
            "Your question will be delivered directly to the admissions team, and our staff will reply to you through this bot."
        ),
        "question_success": (
            "✅ <b>Your question has been successfully submitted to admissions!</b>\n\n"
            "As soon as our specialists answer, you will receive a notification in this bot."
        ),
        "staff_header": "🏛 <b>Tashkent University of Technology (Admissions Office):</b>",
        "your_question_label": "💬 <i>Your question:</i>",
        "answer_label": "📩 <b>Answer:</b>",
        "answered_by_label": "👤 <i>Answered by:</i>"
    }
}

REGIONS = {
    "uz": [
        "Toshkent shahri", "Toshkent viloyati",
        "Samarqand viloyati", "Andijon viloyati",
        "Farg'ona viloyati", "Namangan viloyati",
        "Buxoro viloyati", "Xorazm viloyati",
        "Qashqadaryo viloyati", "Surxondaryo viloyati",
        "Jizzax viloyati", "Navoiy viloyati",
        "Sirdaryo viloyati", "Qoraqalpog'iston Resp."
    ],
    "ru": [
        "г. Ташкент", "Ташкентская область",
        "Самаркандская область", "Андижанская область",
        "Ферганская область", "Наманганская область",
        "Бухарская область", "Хорезмская область",
        "Кашкадарьинская область", "Сурхандарьинская область",
        "Джизакская область", "Навоийская область",
        "Сырдарьинская область", "Респ. Каракалпакстан"
    ],
    "en": [
        "Tashkent City", "Tashkent Region",
        "Samarkand Region", "Andijan Region",
        "Fergana Region", "Namangan Region",
        "Bukhara Region", "Khorezm Region",
        "Kashkadarya Region", "Surkhandarya Region",
        "Jizzakh Region", "Navoiy Region",
        "Sirdaryo Region", "Rep. of Karakalpakstan"
    ]
}

LANG_DISPLAY_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English"
}

APPLY_BUTTONS = {"📝 Ariza yuborish", "📝 Подать заявку", "📝 Submit application", "/apply"}
QUESTION_BUTTONS = {"❓ Savol yuborish", "❓ Задать вопрос", "❓ Ask a question", "/question"}
CHANGE_LANG_BUTTONS = {"🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change language", "/lang"}
CANCEL_BUTTONS = {"❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "/cancel"}
SKIP_BUTTONS = {"➡️ O'tkazib yuborish", "➡️ Пропустить", "➡️ Skip"}


# =====================================================================
# Keyboards & Helpers
# =====================================================================

def get_language_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for 3 languages."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")]
    ])

def get_main_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Main menu keyboard for private chat in selected language."""
    t = TEXTS.get(lang, TEXTS["uz"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_apply"])],
            [KeyboardButton(text=t["btn_question"])],
            [KeyboardButton(text=t["btn_change_lang"])]
        ],
        resize_keyboard=True,
        persistent=True
    )

def get_cancel_keyboard(
    lang: str = "uz",
    with_contact: bool = False, 
    with_skip: bool = False, 
    username: Optional[str] = None
) -> ReplyKeyboardMarkup:
    """Helper keyboard with cancel, language awareness, and optional shortcuts."""
    t = TEXTS.get(lang, TEXTS["uz"])
    rows = []
    if with_contact:
        rows.append([KeyboardButton(text=t["btn_share_contact"], request_contact=True)])
    if username:
        rows.append([KeyboardButton(text=f"@{username.lstrip('@')}")])
    if with_skip:
        rows.append([KeyboardButton(text=t["btn_skip"])])
    rows.append([KeyboardButton(text=t["btn_cancel"])])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def get_regions_inline_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Inline keyboard for 14 regions of Uzbekistan in selected language."""
    region_list = REGIONS.get(lang, REGIONS["uz"])
    buttons = []
    for i in range(0, len(region_list), 2):
        row = [InlineKeyboardButton(text=region_list[i], callback_data=f"reg:{i}")]
        if i + 1 < len(region_list):
            row.append(InlineKeyboardButton(text=region_list[i+1], callback_data=f"reg:{i+1}"))
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_status_keyboard(submission_id: int, current_status: Optional[str] = None) -> InlineKeyboardMarkup:
    """3 status buttons in 3 separate lines (rows) for admissions staff in group."""
    t1 = "✅ Aloqaga chiqildi (Tanlangan)" if current_status == "Aloqaga chiqildi" else "✅ Aloqaga chiqildi"
    t2 = "🟡 Telefon ko'tarilmadi (Tanlangan)" if current_status == "Telefon ko'tarilmadi" else "🟡 Telefon ko'tarilmadi"
    t3 = "❌ Bekor qildi (Tanlangan)" if current_status == "Bekor qildi" else "❌ Bekor qildi"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t1, callback_data=f"status:contacted:{submission_id}")],
        [InlineKeyboardButton(text=t2, callback_data=f"status:no_answer:{submission_id}")],
        [InlineKeyboardButton(text=t3, callback_data=f"status:cancelled:{submission_id}")],
    ])

def format_telegram_message(
    submission_id: int,
    full_name: str,
    phone: str,
    telegram_username: str,
    region: str,
    school: str,
    question_text: Optional[str] = None,
    created_at: Optional[datetime] = None,
    status_label: Optional[str] = None,
    status_by: Optional[str] = None,
    status_at: Optional[datetime] = None,
    lang: Optional[str] = None
) -> str:
    """Format submission data cleanly without divider lines, with chosen status badge."""
    date_str = (created_at or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    
    clean_name = html.escape(full_name)
    clean_phone = html.escape(phone)
    clean_username = html.escape(telegram_username)
    clean_region = html.escape(region)
    clean_school = html.escape(school)
    lang_display = LANG_DISPLAY_NAMES.get(lang or "uz", "🇺🇿 O'zbekcha")
    
    question_display = (
        f"\n💬 <b>Savol / Izoh:</b>\n<i>{html.escape(question_text.strip())}</i>\n"
        if question_text and question_text.strip()
        else ""
    )

    status_badge = ""
    if status_label and status_by:
        s_time = (status_at or datetime.now()).strftime("%Y-%m-%d %H:%M")
        if status_label == "Aloqaga chiqildi":
            status_badge = (
                f"\n\n✅ <b>Holati:</b> Aloqaga chiqildi\n"
                f"👤 <b>Mas'ul xodim:</b> {status_by} ({s_time})"
            )
        elif status_label == "Telefon ko'tarilmadi":
            status_badge = (
                f"\n\n🟡 <b>Holati:</b> Telefon ko'tarilmadi\n"
                f"👤 <b>Tekshirdi:</b> {status_by} ({s_time})"
            )
        elif status_label == "Bekor qildi":
            status_badge = (
                f"\n\n❌ <b>Holati:</b> Bekor qildi\n"
                f"👤 <b>Mas'ul xodim:</b> {status_by} ({s_time})"
            )

    message = (
        f"🚀 <b>YANGI ARIZA: TashTech Foundation</b>\n\n"
        f"🆔 <b>Ariza raqami:</b> #{submission_id}\n"
        f"👤 <b>F.I.Sh:</b> {clean_name}\n"
        f"📞 <b>Telefon:</b> <a href=\"tel:{clean_phone}\">{clean_phone}</a>\n"
        f"✈️ <b>Telegram:</b> <a href=\"https://t.me/{clean_username.lstrip('@')}\">{clean_username}</a>\n"
        f"📍 <b>Hudud/Viloyat:</b> {clean_region}\n"
        f"🏫 <b>O'qiydigan maktab / litsey:</b> {clean_school}\n"
        f"🌐 <b>Muloqot tili:</b> {lang_display}\n"
        f"{question_display}\n"
        f"🕒 <b>Sana va vaqt:</b> {date_str}\n"
        f"🏛 <b>Tashkent University of Technology</b>"
        f"{status_badge}"
    )
    return message


# =====================================================================
# Database Session Helpers for Bot States
# =====================================================================

def get_or_create_session(db, user_id: str) -> BotSession:
    seed_initial_data(db)
    sess = db.query(BotSession).filter(BotSession.user_id == user_id).first()
    if not sess:
        sess = BotSession(user_id=user_id, step="IDLE", data=json.dumps({"lang": "uz"}))
        db.add(sess)
        db.commit()
        db.refresh(sess)
    return sess

def update_session(db, user_id: str, step: str, data: Optional[dict] = None):
    sess = db.query(BotSession).filter(BotSession.user_id == user_id).first()
    if not sess:
        sess = BotSession(user_id=user_id, step=step, data=json.dumps(data or {"lang": "uz"}))
        db.add(sess)
    else:
        sess.step = step
        if data is not None:
            sess.data = json.dumps(data)
        sess.updated_at = datetime.now(timezone.utc)
    db.commit()

def get_session_data(sess: BotSession) -> dict:
    try:
        data = json.loads(sess.data or "{}")
        if not isinstance(data, dict):
            return {"lang": "uz"}
        if "lang" not in data:
            data["lang"] = "uz"
        return data
    except Exception:
        return {"lang": "uz"}


# =====================================================================
# Private Chat Handlers: /start, Languages, Intake & Questions
# =====================================================================

@dp.message(F.chat.type == "private", F.text.in_({"/start", "/menu"}))
async def on_private_start(message: Message):
    """Handle /start command in private chat: show welcome and language buttons."""
    db = SessionLocal()
    try:
        sess = get_or_create_session(db, str(message.from_user.id))
        data = get_session_data(sess)
        update_session(db, str(message.from_user.id), "IDLE", data)
    finally:
        db.close()

    welcome_text = TEXTS["uz"]["welcome"]
    await message.answer(welcome_text, reply_markup=get_language_inline_keyboard())


@dp.callback_query(F.data.startswith("lang:"))
async def on_language_callback(callback: CallbackQuery):
    """Handle choosing language from inline buttons."""
    lang_code = callback.data.split("lang:", 1)[1]
    if lang_code not in ("uz", "ru", "en"):
        lang_code = "uz"

    user_id = str(callback.from_user.id)
    db = SessionLocal()
    try:
        sess = get_or_create_session(db, user_id)
        data = get_session_data(sess)
        data["lang"] = lang_code
        update_session(db, user_id, "IDLE", data)
    finally:
        db.close()

    t = TEXTS.get(lang_code, TEXTS["uz"])
    await callback.answer()

    if callback.message:
        try:
            await callback.message.delete()
        except Exception:
            pass

    current_bot = get_bot()
    if current_bot:
        await current_bot.send_message(
            chat_id=callback.from_user.id,
            text=t["lang_selected"],
            reply_markup=get_main_menu_keyboard(lang_code)
        )


@dp.message(F.chat.type == "private", F.text.in_(CHANGE_LANG_BUTTONS))
async def on_change_language_command(message: Message):
    """Prompt user to change language."""
    select_text = (
        "🇺🇿 Iltimos, tilni tanlang:\n\n"
        "🇷🇺 Пожалуйста, выберите язык:\n\n"
        "🇬🇧 Please select a language:"
    )
    await message.answer(select_text, reply_markup=get_language_inline_keyboard())


@dp.message(F.chat.type == "private", F.text.in_(CANCEL_BUTTONS))
async def on_cancel(message: Message):
    """Cancel current operation and return to main menu in user's language."""
    user_id = str(message.from_user.id)
    db = SessionLocal()
    lang = "uz"
    try:
        sess = get_or_create_session(db, user_id)
        data = get_session_data(sess)
        lang = data.get("lang", "uz")
        update_session(db, user_id, "IDLE", {"lang": lang})
    finally:
        db.close()

    t = TEXTS.get(lang, TEXTS["uz"])
    await message.answer(
        t["cancelled"],
        reply_markup=get_main_menu_keyboard(lang)
    )


@dp.message(F.chat.type == "private", F.text.in_(APPLY_BUTTONS))
async def on_start_application(message: Message):
    """Start application intake flow in private chat."""
    user_id = str(message.from_user.id)
    db = SessionLocal()
    lang = "uz"
    try:
        sess = get_or_create_session(db, user_id)
        data = get_session_data(sess)
        lang = data.get("lang", "uz")
        update_session(db, user_id, "NAME", {"lang": lang})
    finally:
        db.close()

    t = TEXTS.get(lang, TEXTS["uz"])
    await message.answer(
        t["step_name"],
        reply_markup=get_cancel_keyboard(lang=lang)
    )


@dp.message(F.chat.type == "private", F.text.in_(QUESTION_BUTTONS))
async def on_start_question(message: Message):
    """Start question asking flow in private chat."""
    user_id = str(message.from_user.id)
    db = SessionLocal()
    lang = "uz"
    try:
        sess = get_or_create_session(db, user_id)
        data = get_session_data(sess)
        lang = data.get("lang", "uz")
        update_session(db, user_id, "ASK_QUESTION", {"lang": lang})
    finally:
        db.close()

    t = TEXTS.get(lang, TEXTS["uz"])
    await message.answer(
        t["ask_question_prompt"],
        reply_markup=get_cancel_keyboard(lang=lang)
    )


@dp.callback_query(F.data.startswith("reg:"))
async def on_region_callback(callback: CallbackQuery):
    """Handle choosing a region from inline buttons."""
    reg_val = callback.data.split("reg:", 1)[1]
    user_id = str(callback.from_user.id)

    db = SessionLocal()
    try:
        sess = get_or_create_session(db, user_id)
        data = get_session_data(sess)
        lang = data.get("lang", "uz")
        t = TEXTS.get(lang, TEXTS["uz"])

        if sess.step == "REGION":
            # Map index or raw string
            if reg_val.isdigit():
                idx = int(reg_val)
                canonical_uz = REGIONS["uz"][idx] if idx < len(REGIONS["uz"]) else "Toshkent shahri"
                localized_name = REGIONS.get(lang, REGIONS["uz"])[idx] if idx < len(REGIONS.get(lang, REGIONS["uz"])) else canonical_uz
            else:
                canonical_uz = reg_val
                localized_name = reg_val

            data["region"] = canonical_uz
            update_session(db, user_id, "SCHOOL", data)

            await callback.answer(localized_name)
            if callback.message:
                await callback.message.edit_text(
                    t["region_selected"].format(region=html.escape(localized_name))
                )

            current_bot = get_bot()
            if current_bot:
                await current_bot.send_message(
                    chat_id=callback.from_user.id,
                    text=t["step_school"],
                    reply_markup=get_cancel_keyboard(lang=lang)
                )
        else:
            await callback.answer()
    finally:
        db.close()


@dp.message(F.chat.type == "private")
async def on_private_message(message: Message):
    """Handle message input across all application / question steps."""
    user_id = str(message.from_user.id)
    text = (message.text or "").strip()

    # Fast route for buttons
    if text in CANCEL_BUTTONS:
        return await on_cancel(message)
    if text in APPLY_BUTTONS:
        return await on_start_application(message)
    if text in QUESTION_BUTTONS:
        return await on_start_question(message)
    if text in CHANGE_LANG_BUTTONS:
        return await on_change_language_command(message)

    db = SessionLocal()
    try:
        sess = get_or_create_session(db, user_id)
        step = sess.step
        data = get_session_data(sess)
        lang = data.get("lang", "uz")
        t = TEXTS.get(lang, TEXTS["uz"])

        if step == "NAME":
            name = (message.text or "").strip()
            if len(name) < 3:
                await message.answer(t["invalid_name"])
                return
            data["full_name"] = name
            update_session(db, user_id, "PHONE", data)
            await message.answer(
                t["step_phone"],
                reply_markup=get_cancel_keyboard(lang=lang, with_contact=True)
            )

        elif step == "PHONE":
            phone = ""
            if message.contact:
                phone = message.contact.phone_number
                if not phone.startswith("+"):
                    phone = "+" + phone
            elif message.text:
                phone = message.text.strip()

            clean_digits = re.sub(r"\D", "", phone)
            if len(clean_digits) < 7:
                await message.answer(t["invalid_phone"])
                return

            data["phone"] = phone
            update_session(db, user_id, "TG", data)

            user_tg = message.from_user.username
            await message.answer(
                t["step_tg"],
                reply_markup=get_cancel_keyboard(lang=lang, username=user_tg)
            )

        elif step == "TG":
            tg = (message.text or "").strip()
            if not tg.startswith("@") and not tg.startswith("https://t.me/"):
                tg = "@" + tg
            data["telegram_username"] = tg
            update_session(db, user_id, "REGION", data)

            await message.answer(
                t["step_region"],
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                t["step_region_sub"],
                reply_markup=get_regions_inline_keyboard(lang=lang)
            )

        elif step == "SCHOOL":
            school = (message.text or "").strip()
            if len(school) < 2:
                await message.answer(t["invalid_school"])
                return
            data["school"] = school
            update_session(db, user_id, "QUESTION", data)

            await message.answer(
                t["step_comment"],
                reply_markup=get_cancel_keyboard(lang=lang, with_skip=True)
            )

        elif step == "QUESTION":
            q_text = (message.text or "").strip()
            if q_text in SKIP_BUTTONS or not q_text:
                q_text = None

            # Ensure baseline initial leads exist so submission IDs are sequential (12+)
            seed_initial_data(db)

            # Create Submission in Database
            new_sub = Submission(
                full_name=data.get("full_name", ""),
                phone=data.get("phone", ""),
                telegram_username=data.get("telegram_username", f"@{message.from_user.username or user_id}"),
                region=data.get("region", "Toshkent shahri"),
                school=data.get("school", ""),
                question_text=q_text,
                user_agent=f"Telegram Bot ({lang.upper()})"
            )
            db.add(new_sub)
            db.commit()
            db.refresh(new_sub)

            # Send to group with the 3 inline buttons and language tag
            tg_ok, msg_id, tg_err = await send_to_telegram(
                submission_id=new_sub.id,
                full_name=new_sub.full_name,
                phone=new_sub.phone,
                telegram_username=new_sub.telegram_username,
                region=new_sub.region,
                school=new_sub.school,
                question_text=new_sub.question_text,
                created_at=new_sub.created_at,
                lang=lang
            )
            new_sub.telegram_sent = tg_ok
            new_sub.telegram_message_id = msg_id
            new_sub.telegram_error = tg_err
            db.commit()

            # Preserve lang for future interactions
            update_session(db, user_id, "IDLE", {"lang": lang})

            success_msg = t["apply_success"].format(
                id=new_sub.id,
                name=html.escape(new_sub.full_name),
                phone=html.escape(new_sub.phone),
                region=html.escape(new_sub.region),
                school=html.escape(new_sub.school)
            )
            await message.answer(success_msg, reply_markup=get_main_menu_keyboard(lang))

        elif step == "ASK_QUESTION":
            question_text = (message.text or "").strip()
            if not question_text or question_text in CANCEL_BUTTONS:
                update_session(db, user_id, "IDLE", {"lang": lang})
                await message.answer(t["cancelled"], reply_markup=get_main_menu_keyboard(lang))
                return

            full_name = message.from_user.full_name
            username = f"@{message.from_user.username}" if message.from_user.username else "mavjud emas"
            now = datetime.now(timezone.utc)

            new_q = UserQuestion(
                user_id=user_id,
                username=username,
                full_name=full_name,
                question_text=question_text,
                created_at=now
            )
            db.add(new_q)
            db.commit()
            db.refresh(new_q)

            # Send question to Group Chat
            current_bot = get_bot()
            chat_id = settings.TELEGRAM_CHAT_ID
            if current_bot and chat_id:
                escaped_q = html.escape(question_text)
                escaped_name = html.escape(full_name)
                time_str = now.strftime("%Y-%m-%d %H:%M:%S")
                lang_display = LANG_DISPLAY_NAMES.get(lang, "🇺🇿 O'zbekcha")

                user_link = (
                    f"<a href=\"https://t.me/{message.from_user.username}\">{username}</a>"
                    if message.from_user.username
                    else f"<a href=\"tg://user?id={user_id}\">{escaped_name}</a>"
                )

                group_text = (
                    f"❓ <b>YANGI SAVOL: TashTech Foundation</b>\n\n"
                    f"👤 <b>Kimdan:</b> {escaped_name} ({user_link})\n"
                    f"🆔 <b>Foydalanuvchi ID:</b> <code>{user_id}</code>\n"
                    f"🌐 <b>Muloqot tili:</b> {lang_display}\n"
                    f"🕒 <b>Sana va vaqt:</b> {time_str}\n\n"
                    f"💬 <b>Savol matni:</b>\n<i>{escaped_q}</i>\n\n"
                    f"👉 <i>Ushbu savolga javob berish uchun, ushbu xabarga <b>Reply</b> qilib javob yozing.</i>"
                )

                sent_msg = await current_bot.send_message(
                    chat_id=chat_id,
                    text=group_text,
                    disable_web_page_preview=True
                )
                new_q.group_message_id = sent_msg.message_id
                db.commit()

            update_session(db, user_id, "IDLE", {"lang": lang})
            await message.answer(t["question_success"], reply_markup=get_main_menu_keyboard(lang))

        else:
            await message.answer(t["main_menu_prompt"], reply_markup=get_main_menu_keyboard(lang))
    finally:
        db.close()


# =====================================================================
# Group Reply Handler: Staff replies to student's question in group
# =====================================================================

@dp.message(F.chat.type.in_({"group", "supergroup"}), F.reply_to_message)
async def on_group_reply(message: Message):
    """
    When staff in the group replies to a question message from the bot,
    deliver the answer directly back to the student in private chat in student's language!
    """
    replied = message.reply_to_message
    if not replied or not message.text:
        return

    current_bot = get_bot()
    if not current_bot:
        return

    # Check if replied message is from our bot
    bot_info = await current_bot.get_me()
    if replied.from_user and bot_info and replied.from_user.id != bot_info.id:
        return

    text = replied.text or replied.caption or ""
    
    # Extract user_id from pattern: "🆔 Foydalanuvchi ID: <code>(\d+)</code>"
    target_user_id = None
    match = re.search(r"Foydalanuvchi ID:\s*<code>(\d+)</code>", text)
    if match:
        target_user_id = match.group(1)

    original_q_text = ""
    db = SessionLocal()
    try:
        q_record = db.query(UserQuestion).filter(UserQuestion.group_message_id == replied.message_id).first()
        if q_record:
            target_user_id = q_record.user_id
            original_q_text = q_record.question_text

        if target_user_id:
            # Check student's preferred language
            student_sess = db.query(BotSession).filter(BotSession.user_id == target_user_id).first()
            user_lang = "uz"
            if student_sess:
                user_lang = get_session_data(student_sess).get("lang", "uz")
            t = TEXTS.get(user_lang, TEXTS["uz"])

            staff_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
            staff_reply = html.escape(message.text.strip())

            user_msg = (
                f"{t['staff_header']}\n\n"
                + (f"{t['your_question_label']}\n«{html.escape(original_q_text)}»\n\n" if original_q_text else "")
                + f"{t['answer_label']}\n{staff_reply}\n\n"
                f"{t['answered_by_label']} {html.escape(staff_name)}"
            )

            await current_bot.send_message(
                chat_id=int(target_user_id),
                text=user_msg
            )

            if q_record:
                q_record.is_answered = True
                q_record.answer_text = message.text.strip()
                q_record.answered_by = staff_name
                db.commit()

            await message.reply(
                f"✅ <b>Javob abituriyentga muvaffaqiyatli yetkazildi!</b> (Foydalanuvchi ID: <code>{target_user_id}</code>)"
            )
            logger.info(f"Answer delivered to user {target_user_id} by staff {staff_name}")
    except Exception as e:
        logger.exception(f"Error delivering reply to user {target_user_id}: {e}")
        await message.reply(f"⚠️ Foydalanuvchiga yetkazishda xatolik yuz berdi: {e}")
    finally:
        db.close()


# =====================================================================
# Status Callback Handler (The 3 inline buttons in group)
# =====================================================================

@dp.callback_query(F.data.startswith("status:"))
async def on_status_callback(callback: CallbackQuery):
    """Handle clicking any of the 3 status buttons in the group chat."""
    try:
        parts = callback.data.split(":")
        action = parts[1]  # "contacted", "no_answer", "cancelled"
        submission_id = int(parts[2])
        
        from_user = callback.from_user
        user_name = f"@{from_user.username}" if from_user.username else from_user.full_name
        now = datetime.now(timezone.utc)
        
        db = SessionLocal()
        try:
            sub = db.query(Submission).filter(Submission.id == submission_id).first()
            if sub:
                if action == "contacted":
                    sub.status = "Aloqaga chiqildi"
                    sub.is_contacted = True
                    alert_text = "✅ Belgilandi: Aloqaga chiqildi!"
                elif action == "no_answer":
                    sub.status = "Telefon ko'tarilmadi"
                    sub.is_contacted = False
                    alert_text = "🟡 Belgilandi: Telefon ko'tarilmadi!"
                elif action == "cancelled":
                    sub.status = "Bekor qildi"
                    sub.is_contacted = False
                    alert_text = "❌ Belgilandi: Bekor qildi!"
                else:
                    alert_text = "Holat yangilandi"

                sub.contacted_by = user_name
                sub.contacted_at = now
                db.commit()
                db.refresh(sub)
                
                # Check user agent or language if available
                lang_code = "uz"
                if sub.user_agent and "(" in sub.user_agent and ")" in sub.user_agent:
                    raw_lang = sub.user_agent.split("(")[1].split(")")[0].lower()
                    if raw_lang in ("uz", "ru", "en"):
                        lang_code = raw_lang

                # Regenerate updated message
                new_text = format_telegram_message(
                    submission_id=sub.id,
                    full_name=sub.full_name,
                    phone=sub.phone,
                    telegram_username=sub.telegram_username,
                    region=sub.region,
                    school=sub.school,
                    question_text=sub.question_text,
                    created_at=sub.created_at,
                    status_label=sub.status,
                    status_by=user_name,
                    status_at=now,
                    lang=lang_code
                )
                
                if callback.message:
                    await callback.message.edit_text(
                        text=new_text,
                        reply_markup=get_status_keyboard(submission_id, current_status=sub.status),
                        disable_web_page_preview=True
                    )
                
                await callback.answer(alert_text, show_alert=False)
                logger.info(f"Submission #{submission_id} status updated to '{sub.status}' by {user_name}")
            else:
                await callback.answer("Ariza topilmadi.", show_alert=True)
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Error handling status callback: {e}")
        await callback.answer("Xatolik yuz berdi.", show_alert=True)


# =====================================================================
# Main Send Notification Function
# =====================================================================

async def send_to_telegram(
    submission_id: int,
    full_name: str,
    phone: str,
    telegram_username: str,
    region: str,
    school: str,
    question_text: Optional[str] = None,
    created_at: Optional[datetime] = None,
    lang: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Send submission notification to Telegram group with 3 inline status buttons in 3 lines.
    """
    current_bot = get_bot()
    chat_id = settings.TELEGRAM_CHAT_ID

    message_html = format_telegram_message(
        submission_id=submission_id,
        full_name=full_name,
        phone=phone,
        telegram_username=telegram_username,
        region=region,
        school=school,
        question_text=question_text,
        created_at=created_at,
        status_label=None,
        lang=lang
    )

    if not current_bot or not chat_id:
        logger.info(
            f"[TELEGRAM SIMULATION MODE] (Token/ChatID not set in .env)\n"
            f"Would send message for #{submission_id} ({full_name}):\n{message_html}"
        )
        return True, "simulated_local_mode", None

    try:
        keyboard = get_status_keyboard(submission_id, current_status=None)
        sent_message = await current_bot.send_message(
            chat_id=chat_id,
            text=message_html,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        msg_id = str(sent_message.message_id)
        logger.info(f"[aiogram] Successfully sent submission #{submission_id} with 3 buttons to Telegram chat {chat_id} (msg_id: {msg_id})")
        return True, msg_id, None
    except TelegramAPIError as e:
        logger.error(f"[aiogram] Telegram API error for #{submission_id}: {e}")
        return False, None, f"aiogram TelegramAPIError: {e.message}"
    except Exception as e:
        logger.exception(f"[aiogram] Exception sending submission #{submission_id} to Telegram: {e}")
        return False, None, str(e)
