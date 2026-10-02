import logging
from typing import Optional, Tuple
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from .config import settings
from .database import SessionLocal
from .models import Submission

logger = logging.getLogger("tashtech.telegram")

# Shared aiogram bot instance
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

def get_contact_keyboard(submission_id: int, is_contacted: bool = False) -> InlineKeyboardMarkup:
    """Create inline keyboard for applicant status tracking."""
    if is_contacted:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Aloqaga chiqilgan", callback_data=f"already_contacted:{submission_id}")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Aloqaga chiqildi", callback_data=f"contacted:{submission_id}")]
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
    is_contacted: bool = False,
    contacted_by: Optional[str] = None,
    contacted_at: Optional[datetime] = None
) -> str:
    """Format submission data cleanly without divider lines, with contact status."""
    date_str = (created_at or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    
    clean_name = full_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_phone = phone.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_username = telegram_username.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_region = region.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_school = school.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    question_display = (
        f"\n💬 <b>Savol / Izoh:</b>\n<i>{question_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</i>\n"
        if question_text and question_text.strip()
        else ""
    )

    status_badge = ""
    if is_contacted:
        c_time = (contacted_at or datetime.now()).strftime("%Y-%m-%d %H:%M")
        status_badge = (
            f"\n\n✅ <b>Holati:</b> Aloqaga chiqildi\n"
            f"👤 <b>Mas'ul xodim:</b> {contacted_by or 'Xodim'} ({c_time})"
        )

    # Clean formatted message without decorative lines
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


@dp.callback_query(F.data.startswith("contacted:"))
async def on_contacted_callback(callback: CallbackQuery):
    """Handle staff clicking 'Aloqaga chiqildi' button."""
    try:
        sub_id_str = callback.data.split(":")[1]
        submission_id = int(sub_id_str)
        
        # Determine who pressed the button
        from_user = callback.from_user
        user_name = f"@{from_user.username}" if from_user.username else from_user.full_name
        now = datetime.now(timezone.utc)
        
        # Update Database
        db = SessionLocal()
        try:
            sub = db.query(Submission).filter(Submission.id == submission_id).first()
            if sub:
                sub.is_contacted = True
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
                    is_contacted=True,
                    contacted_by=user_name,
                    contacted_at=now
                )
                
                # Edit message in Telegram with updated text and button
                if callback.message:
                    await callback.message.edit_text(
                        text=new_text,
                        reply_markup=get_contact_keyboard(submission_id, is_contacted=True),
                        disable_web_page_preview=True
                    )
                
                await callback.answer(f"✅ Qabul qilindi: {user_name} aloqaga chiqdi!", show_alert=False)
                logger.info(f"Submission #{submission_id} marked as contacted by {user_name}")
            else:
                await callback.answer("Ariza topilmadi.", show_alert=True)
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"Error handling contacted callback: {e}")
        await callback.answer("Xatolik yuz berdi.", show_alert=True)


@dp.callback_query(F.data.startswith("already_contacted:"))
async def on_already_contacted_callback(callback: CallbackQuery):
    """Alert user that this applicant has already been contacted."""
    await callback.answer("Ushbu abituriyent bilan allaqachon aloqaga chiqilgan!", show_alert=False)


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
    Send submission notification to Telegram group with inline keyboard button.
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
        is_contacted=False
    )

    if not current_bot or not chat_id:
        logger.info(
            f"[TELEGRAM SIMULATION MODE] (Token/ChatID not set in .env)\n"
            f"Would send message for #{submission_id} ({full_name}):\n{message_html}"
        )
        return True, "simulated_local_mode", None

    try:
        keyboard = get_contact_keyboard(submission_id, is_contacted=False)
        sent_message = await current_bot.send_message(
            chat_id=chat_id,
            text=message_html,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        msg_id = str(sent_message.message_id)
        logger.info(f"[aiogram] Successfully sent submission #{submission_id} to Telegram chat {chat_id} (msg_id: {msg_id})")
        return True, msg_id, None
    except TelegramAPIError as e:
        logger.error(f"[aiogram] Telegram API error for #{submission_id}: {e}")
        return False, None, f"aiogram TelegramAPIError: {e.message}"
    except Exception as e:
        logger.exception(f"[aiogram] Exception sending submission #{submission_id} to Telegram: {e}")
        return False, None, str(e)
