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
# Keyboards & Helpers
# =====================================================================

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard for private chat."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Ariza yuborish")],
            [KeyboardButton(text="❓ Savol yuborish")]
        ],
        resize_keyboard=True,
        persistent=True
    )

def get_cancel_keyboard(with_contact: bool = False, with_skip: bool = False, username: Optional[str] = None) -> ReplyKeyboardMarkup:
    """Helper keyboard with cancel and optional shortcuts."""
    rows = []
    if with_contact:
        rows.append([KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)])
    if username:
        rows.append([KeyboardButton(text=f"@{username.lstrip('@')}")])
    if with_skip:
        rows.append([KeyboardButton(text="➡️ O'tkazib yuborish")])
    rows.append([KeyboardButton(text="❌ Bekor qilish")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def get_regions_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for 14 regions of Uzbekistan."""
    regions = [
        "Toshkent shahri", "Toshkent viloyati",
        "Samarqand viloyati", "Andijon viloyati",
        "Farg'ona viloyati", "Namangan viloyati",
        "Buxoro viloyati", "Xorazm viloyati",
        "Qashqadaryo viloyati", "Surxondaryo viloyati",
        "Jizzax viloyati", "Navoiy viloyati",
        "Sirdaryo viloyati", "Qoraqalpog'iston Resp."
    ]
    buttons = []
    for i in range(0, len(regions), 2):
        row = [InlineKeyboardButton(text=regions[i], callback_data=f"reg:{regions[i]}")]
        if i + 1 < len(regions):
            row.append(InlineKeyboardButton(text=regions[i+1], callback_data=f"reg:{regions[i+1]}"))
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_status_keyboard(submission_id: int, current_status: Optional[str] = None) -> InlineKeyboardMarkup:
    """
    3 status buttons in 3 separate lines (rows):
    Line 1: ✅ Aloqaga chiqildi
    Line 2: 🟡 Telefon ko'tarilmadi
    Line 3: ❌ Bekor qildi
    """
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
    status_at: Optional[datetime] = None
) -> str:
    """Format submission data cleanly without divider lines, with chosen status badge."""
    date_str = (created_at or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    
    clean_name = html.escape(full_name)
    clean_phone = html.escape(phone)
    clean_username = html.escape(telegram_username)
    clean_region = html.escape(region)
    clean_school = html.escape(school)
    
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
    sess = db.query(BotSession).filter(BotSession.user_id == user_id).first()
    if not sess:
        sess = BotSession(user_id=user_id, step="IDLE", data="{}")
        db.add(sess)
        db.commit()
        db.refresh(sess)
    return sess

def update_session(db, user_id: str, step: str, data: Optional[dict] = None):
    sess = db.query(BotSession).filter(BotSession.user_id == user_id).first()
    if not sess:
        sess = BotSession(user_id=user_id, step=step, data=json.dumps(data or {}))
        db.add(sess)
    else:
        sess.step = step
        if data is not None:
            sess.data = json.dumps(data)
        sess.updated_at = datetime.now(timezone.utc)
    db.commit()

def get_session_data(sess: BotSession) -> dict:
    try:
        return json.loads(sess.data or "{}")
    except Exception:
        return {}


# =====================================================================
# Private Chat Handlers: /start, Ariza yuborish & Savol yuborish
# =====================================================================

@dp.message(F.chat.type == "private", F.text.in_({"/start", "/menu"}))
async def on_private_start(message: Message):
    """Handle /start command in private chat."""
    db = SessionLocal()
    try:
        update_session(db, str(message.from_user.id), "IDLE", {})
    finally:
        db.close()

    full_name = html.escape(message.from_user.full_name)
    welcome_text = (
        f"Assalomu alaykum, <b>{full_name}</b>! 🏛\n\n"
        f"<b>Tashkent University of Technology (TashTech)</b> "
        f"Foundation dasturi rasmiy botiga xush kelibsiz!\n\n"
        f"Kerakli bo'limni tanlang:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@dp.message(F.chat.type == "private", F.text == "❌ Bekor qilish")
async def on_cancel(message: Message):
    """Cancel current operation and return to main menu."""
    db = SessionLocal()
    try:
        update_session(db, str(message.from_user.id), "IDLE", {})
    finally:
        db.close()
    await message.answer(
        "Amal bekor qilindi. Bosh menyudasiz:",
        reply_markup=get_main_menu_keyboard()
    )


@dp.message(F.chat.type == "private", F.text == "📝 Ariza yuborish")
async def on_start_application(message: Message):
    """Start application intake flow in private chat."""
    db = SessionLocal()
    try:
        update_session(db, str(message.from_user.id), "NAME", {})
    finally:
        db.close()

    await message.answer(
        "👤 <b>1/5. Ism, familiya va sharifingizni kiriting:</b>\n"
        "<i>(Masalan: Ibrokhimov Numonjon Nozimjon o'g'li)</i>",
        reply_markup=get_cancel_keyboard()
    )


@dp.message(F.chat.type == "private", F.text == "❓ Savol yuborish")
async def on_start_question(message: Message):
    """Start question asking flow in private chat."""
    db = SessionLocal()
    try:
        update_session(db, str(message.from_user.id), "ASK_QUESTION", {})
    finally:
        db.close()

    await message.answer(
        "❓ <b>TashTech Foundation kursi bo'yicha savolingizni yozib qoldiring:</b>\n\n"
        "Savolingiz to'g'ridan-to'g'ri qabul komissiyasiga yetkaziladi va mutaxassislarimiz shu bot orqali sizga javob yozishadi.",
        reply_markup=get_cancel_keyboard()
    )


@dp.callback_query(F.data.startswith("reg:"))
async def on_region_callback(callback: CallbackQuery):
    """Handle choosing a region from inline buttons."""
    region_name = callback.data.split("reg:", 1)[1]
    user_id = str(callback.from_user.id)

    db = SessionLocal()
    try:
        sess = get_or_create_session(db, user_id)
        if sess.step == "REGION":
            data = get_session_data(sess)
            data["region"] = region_name
            update_session(db, user_id, "SCHOOL", data)

            await callback.answer(f"Tanlandi: {region_name}")
            if callback.message:
                await callback.message.edit_text(
                    f"📍 Hudud tanlandi: <b>{html.escape(region_name)}</b>"
                )

            current_bot = get_bot()
            if current_bot:
                await current_bot.send_message(
                    chat_id=callback.from_user.id,
                    text=(
                        "🏫 <b>5/5. Qaysi maktab yoki akademik litseyda o'qiysiz?</b>\n"
                        "<i>(Masalan: 110-sonli ixtisoslashtirilgan maktab)</i>"
                    ),
                    reply_markup=get_cancel_keyboard()
                )
        else:
            await callback.answer()
    finally:
        db.close()


@dp.message(F.chat.type == "private")
async def on_private_message(message: Message):
    """Handle message input across all application / question steps."""
    user_id = str(message.from_user.id)
    db = SessionLocal()
    try:
        sess = get_or_create_session(db, user_id)
        step = sess.step
        data = get_session_data(sess)

        if step == "NAME":
            name = (message.text or "").strip()
            if len(name) < 3:
                await message.answer("Iltimos, ism va familiyangizni to'liq kiriting:")
                return
            data["full_name"] = name
            update_session(db, user_id, "PHONE", data)
            await message.answer(
                "📞 <b>2/5. Telefon raqamingizni kiriting yoki pastdagi tugmani bosing:</b>\n"
                "<i>(Masalan: +998901234567)</i>",
                reply_markup=get_cancel_keyboard(with_contact=True)
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
                await message.answer("Iltimos, to'g'ri telefon raqam kiriting (masalan: +998901234567):")
                return

            data["phone"] = phone
            update_session(db, user_id, "TG", data)

            user_tg = message.from_user.username
            await message.answer(
                "✈️ <b>3/5. Telegram username yoki profilingiz:</b>\n"
                "<i>(Masalan: @username)</i>",
                reply_markup=get_cancel_keyboard(username=user_tg)
            )

        elif step == "TG":
            tg = (message.text or "").strip()
            if not tg.startswith("@") and not tg.startswith("https://t.me/"):
                tg = "@" + tg
            data["telegram_username"] = tg
            update_session(db, user_id, "REGION", data)

            await message.answer(
                "📍 <b>4/5. Yashash viloyatingiz / hududingizni tanlang:</b>",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "Quyidagi ro'yxatdan o'z hududingizni bosing:",
                reply_markup=get_regions_inline_keyboard()
            )

        elif step == "SCHOOL":
            school = (message.text or "").strip()
            if len(school) < 2:
                await message.answer("Iltimos, maktab yoki litsey nomini to'liq kiriting:")
                return
            data["school"] = school
            update_session(db, user_id, "QUESTION", data)

            await message.answer(
                "💬 <b>Qo'shimcha savol yoki izohingiz bormi?</b>\n"
                "<i>(Ixtiyoriy. Agar bo'lmasa, '➡️ O'tkazib yuborish' tugmasini bosing)</i>",
                reply_markup=get_cancel_keyboard(with_skip=True)
            )

        elif step == "QUESTION":
            q_text = (message.text or "").strip()
            if q_text == "➡️ O'tkazib yuborish" or not q_text:
                q_text = None

            # Create Submission in Database
            new_sub = Submission(
                full_name=data.get("full_name", ""),
                phone=data.get("phone", ""),
                telegram_username=data.get("telegram_username", f"@{message.from_user.username or user_id}"),
                region=data.get("region", "Toshkent shahri"),
                school=data.get("school", ""),
                question_text=q_text,
                user_agent="Telegram Bot"
            )
            db.add(new_sub)
            db.commit()
            db.refresh(new_sub)

            # Send to group with the 3 inline buttons
            tg_ok, msg_id, tg_err = await send_to_telegram(
                submission_id=new_sub.id,
                full_name=new_sub.full_name,
                phone=new_sub.phone,
                telegram_username=new_sub.telegram_username,
                region=new_sub.region,
                school=new_sub.school,
                question_text=new_sub.question_text,
                created_at=new_sub.created_at
            )
            new_sub.telegram_sent = tg_ok
            new_sub.telegram_message_id = msg_id
            new_sub.telegram_error = tg_err
            db.commit()

            update_session(db, user_id, "IDLE", {})

            await message.answer(
                f"🎉 <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
                f"🆔 <b>Ariza raqami:</b> #{new_sub.id}\n"
                f"👤 <b>F.I.Sh:</b> {html.escape(new_sub.full_name)}\n"
                f"📞 <b>Telefon:</b> {html.escape(new_sub.phone)}\n"
                f"📍 <b>Hudud:</b> {html.escape(new_sub.region)}\n"
                f"🏫 <b>Maktab/Litsey:</b> {html.escape(new_sub.school)}\n\n"
                f"Tashkent University of Technology qabul komissiyasi tez orada siz bilan bog'lanadi! 🏛",
                reply_markup=get_main_menu_keyboard()
            )

        elif step == "ASK_QUESTION":
            question_text = (message.text or "").strip()
            if not question_text or question_text == "❌ Bekor qilish":
                update_session(db, user_id, "IDLE", {})
                await message.answer("Bosh menyudasiz:", reply_markup=get_main_menu_keyboard())
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

                user_link = (
                    f"<a href=\"https://t.me/{message.from_user.username}\">{username}</a>"
                    if message.from_user.username
                    else f"<a href=\"tg://user?id={user_id}\">{escaped_name}</a>"
                )

                group_text = (
                    f"❓ <b>YANGI SAVOL: TashTech Foundation</b>\n\n"
                    f"👤 <b>Kimdan:</b> {escaped_name} ({user_link})\n"
                    f"🆔 <b>Foydalanuvchi ID:</b> <code>{user_id}</code>\n"
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

            update_session(db, user_id, "IDLE", {})

            await message.answer(
                "✅ <b>Savolingiz qabul komissiyasiga muvaffaqiyatli yetkazildi!</b>\n\n"
                "Mutaxassislarimiz savolingizga javob berishi bilan sizga shu bot orqali xabar yetkaziladi.",
                reply_markup=get_main_menu_keyboard()
            )

        else:
            await message.answer(
                "Quyidagi bo'limlardan birini tanlang:",
                reply_markup=get_main_menu_keyboard()
            )
    finally:
        db.close()


# =====================================================================
# Group Reply Handler: Staff replies to student's question in group
# =====================================================================

@dp.message(F.chat.type.in_({"group", "supergroup"}), F.reply_to_message)
async def on_group_reply(message: Message):
    """
    When staff in the group replies to a question message from the bot,
    deliver the answer directly back to the student in private chat!
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
            staff_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
            staff_reply = html.escape(message.text.strip())

            user_msg = (
                f"🏛 <b>Tashkent University of Technology (Qabul komissiyasi):</b>\n\n"
                + (f"💬 <i>Sizning savolingiz:</i>\n«{html.escape(original_q_text)}»\n\n" if original_q_text else "")
                + f"📩 <b>Javob:</b>\n{staff_reply}\n\n"
                f"👤 <i>Javob berdi: {html.escape(staff_name)}</i>"
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
                    status_at=now
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
    created_at: Optional[datetime] = None
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
        status_label=None
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
