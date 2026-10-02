import logging
from typing import Optional, Tuple
from datetime import datetime
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from .config import settings

logger = logging.getLogger("tashtech.telegram")

def format_telegram_message(
    submission_id: int,
    full_name: str,
    phone: str,
    telegram_username: str,
    region: str,
    school: str,
    question_text: Optional[str] = None,
    created_at: Optional[datetime] = None
) -> str:
    """Format submission data into a clean, modern HTML message for Telegram."""
    date_str = (created_at or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    
    # Escape HTML special chars
    clean_name = full_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_phone = phone.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_username = telegram_username.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_region = region.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_school = school.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    question_display = (
        f"<b>💬 Savol / Izoh:</b>\n<i>{question_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</i>\n"
        if question_text and question_text.strip()
        else "<b>💬 Savol / Izoh:</b> <i>Ko'rsatilmadi</i>\n"
    )

    message = (
        f"🚀 <b>YANGI ARIZA: TashTech Foundation</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Ariza raqami:</b> #{submission_id}\n"
        f"👤 <b>F.I.Sh:</b> {clean_name}\n"
        f"📞 <b>Telefon:</b> <a href=\"tel:{clean_phone}\">{clean_phone}</a>\n"
        f"✈️ <b>Telegram:</b> <a href=\"https://t.me/{clean_username.lstrip('@')}\">{clean_username}</a>\n"
        f"📍 <b>Hudud/Viloyat:</b> {clean_region}\n"
        f"🏫 <b>O'qiydigan maktab / litsey:</b> {clean_school}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{question_display}"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 <b>Sana va vaqt:</b> {date_str}\n"
        f"🏛 <b>Tashkent University of Technology</b>"
    )
    return message


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
    Send submission notification to Telegram group chat using aiogram Bot.
    Returns: (success: bool, message_id_or_simulated: Optional[str], error_message: Optional[str])
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    message_html = format_telegram_message(
        submission_id=submission_id,
        full_name=full_name,
        phone=phone,
        telegram_username=telegram_username,
        region=region,
        school=school,
        question_text=question_text,
        created_at=created_at
    )

    # Check if credentials are set
    is_configured = (
        bot_token 
        and chat_id 
        and "YOUR_" not in bot_token 
        and "YOUR_" not in str(chat_id)
        and len(bot_token.strip()) > 10
    )

    if not is_configured:
        logger.info(
            f"[TELEGRAM SIMULATION MODE] (Token/ChatID not set in .env)\n"
            f"Would send message for #{submission_id} ({full_name}):\n{message_html}"
        )
        return True, "simulated_local_mode", None

    bot = Bot(
        token=bot_token.strip(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    try:
        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=message_html,
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
    finally:
        await bot.session.close()
