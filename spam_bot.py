import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! .env faylni tekshiring.")

SPAM_KEYWORDS = [
    "profilimga kir",
    "profilimga qarang",
    "profilimga qara",
    "profilimga o'ting",
    "profilimga oting",
    "profilimga kirgin",
    "profilimga kirib",
    "profilimga bir kir",
    "profilimga kiraver",
    "profilimga kirip",
    "profilimga kirip ko'r",
    "profilimga kirib ko'ring",
    "profilimni ko'ring",
    "profilimni kor",
    "profilimni oching",
    "profilimni och",
    "profilga kir",
    "profilga qarang",
    "profilga qara",
    "profilga kirib",

    "kanalimga kir",
    "kanalimga o'ting",
    "kanalimga oting",
    "kanalimga qarang",
    "kanalimga qara",
    "kanalimga kirgin",
    "kanalimga kirib",
    "kanalimni ko'r",
    "kanalimni kor",
    "kanalga kir",
    "kanalga o'ting",
    "kanalga oting",

    "ko'ring 😘",
    "ko'ring 🥰",
    "ko'ring 😍",
    "ko'ring 😏",
    "ko'ring 🔥",
    "ko'ring ❤",
    "ko'ring 💋",
    "koring 😘",
    "koring 🥰",
    "koring 😍",
    "ko'rib qoling",
    "korib qoling",

    "salom, profilimga",
    "salom profilimga",
    "salom, profilga",
    "salom profilga",

    "mening profilimga",
    "mening sahifamga",
    "sahifamga kir",
    "sahifamga qarang",
    "sahifamga qara",
    "akkauntimga kir",
    "akkauntimga qarang",
    "bio'imga qara",
    "bioimga qara",
    "bioga qara",
    "bio ga qara",
    "tasvir bor",
    "rasm bor profilimda",
    "rasmlarim bor",
    "videolarim bor",
    "qiziq narsa bor",
    "yashirin kontent",

    "зайди в профиль",
    "зайди ко мне",
    "зайди на профиль",
    "загляни в профиль",
    "загляни ко мне",
    "посмотри профиль",
    "посмотри мой профиль",
    "глянь профиль",
    "глянь ко мне",
    "перейди в профиль",
    "заходи в профиль",
    "смотри профиль",
    "кликни на профиль",
    "открой профиль",

    "зайди на канал",
    "зайди в канал",
    "перейди на канал",
    "посмотри канал",
    "загляни на канал",
    "подпишись на канал",
    "мой канал",

    "привет, зайди",
    "привет зайди",
    "привет, посмотри",
    "привет посмотри",
    "привет, загляни",
    "салам, зайди",
    "салам зайди",

    "есть интересное",
    "есть кое-что интересное",
    "там есть видео",
    "там интересное",
    "загляни ко мне в профиль",
    "смотри мой профиль",

    "check my profile",
    "visit my profile",
    "go to my profile",
    "look at my profile",
    "see my profile",
    "check my channel",
    "visit my channel",
    "join my channel",
    "open my profile",
    "click my profile",
    "😘 profilimga",
    "🥰 profilimga",
    "😍 profilimga",
    "🔥 profilimga",
    "💋 profilimga",
    "👆 profilimga",
    "☝️ profilimga",
    "profilimga 👆",
    "profilimga ☝️",
    "profilimga 👉",
    "👉 profilimga",
    "😘 профиль",
    "🔞 profilimda",
    "18+ profilimda",
    "18+ profilimga",
]

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

def has_spam_keyword(text: str) -> bool:
    text_lower = text.lower()
    for kw in SPAM_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False

async def get_profile_photo_count(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        photos = await context.bot.get_user_profile_photos(user_id, limit=2)
        return photos.total_count
    except Exception as e:
        log.warning(f"Profil rasm tekshirishda xato ({user_id}): {e}")
        return -1  

async def ban_user(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    except Exception as e:
        log.error(f"Ban qilishda xato: {e}")

async def delete_message(chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        log.warning(f"Xabarni o'chirishda xato: {e}")

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    user = message.from_user
    chat = message.chat

    if not has_spam_keyword(message.text):
        return

    log.info(f"Kalit so'z topildi | User: {user.id} | Chat: {chat.id}")

    no_username = not user.username
    photo_count = await get_profile_photo_count(user.id, context)
    one_photo = (photo_count == 1)

    log.info(
        f"Tekshirish → username_yoq={no_username} | "
        f"rasm_soni={photo_count} | bir_rasm={one_photo}"
    )

    if no_username and one_photo:
        log.warning(f"🚨 SPAM aniqlandi! User: {user.id} (@{user.username}) | Chat: {chat.id}")
        await delete_message(chat.id, message.message_id, context)
        await ban_user(chat.id, user.id, context)
        try:
            msg = await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"🚫 <b>Spam foydalanuvchi aniqlandi va ban qilindi!</b>\n\n"
                    f"👤 <b>Ism:</b> {user.full_name}\n"
                    f"🆔 <b>ID:</b> <code>{user.id}</code>"
                ),
                parse_mode="HTML",
            )
            asyncio.create_task(delete_message_after_delay(chat.id, msg.message_id, context, 60))
        except Exception as e:
            log.warning(f"Xabar yuborishda xato: {e}")
    else:
        log.info(f"Shubhali xabar lekin to'liq spam emas → e'tiborsiz qoldirildi")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = await context.bot.get_me()
    chat = update.effective_chat
    user = update.effective_user
    chat_type = chat.type

    admin_link = (
        f"https://t.me/{bot.username}?startgroup=true"
        f"&admin=delete_messages+restrict_members+pin_messages+invite_users"
    )

    if chat_type == "private":
        keyboard = [[InlineKeyboardButton("+ Guruhga qo'shish", url=admin_link)]]
        text = "+ <b>SpamKuzatchi</b> botini guruhga qo'shish uchun pastdagi tugmani bosing:"
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        try:
            member_info = await chat.get_member(user.id)
            if member_info.status not in ["administrator", "creator"]:
                log.info(f"Admin bo'lmagan foydalanuvchi /start bosdi: {user.id}")
                return
        except Exception as e:
            log.warning(f"Foydalanuvchini tekshirishda xato: {e}")
            return
    
        try:
            member = await chat.get_member(bot.id)
            if member.status == "administrator":
                text = "✅ <b>Bot faol!</b>"
                msg = await update.message.reply_text(text, parse_mode="HTML")
                asyncio.create_task(delete_message_after_delay(chat.id, msg.message_id, context, 10))
            else:
                keyboard = [[InlineKeyboardButton("+ Admin huquqini berish", url=admin_link)]]
                text = "+ Bot ishlashi uchun unga <b>Admin</b> huquqini berishingiz kerak:"
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        except Exception as e:
            log.warning(f"Guruhda adminlikni tekshirishda xato: {e}")

async def manual_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.reply_to_message:
        return

    chat = update.effective_chat
    user = update.effective_user

    try:
        member_info = await chat.get_member(user.id)
        if member_info.status not in ["administrator", "creator"]:
            return
    except Exception as e:
        log.warning(f"Adminlikni tekshirishda xato: {e}")
        return

    target_user = message.reply_to_message.from_user
    bot_info = await context.bot.get_me()
    if target_user.id == bot_info.id:
        return

    try:
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=target_user.id)
        msg = await message.reply_text(
            f"🚫 <b>{target_user.full_name}</b> guruhdan ban qilindi!", 
            parse_mode="HTML"
        )
        asyncio.create_task(delete_message_after_delay(chat.id, msg.message_id, context, 15))
        asyncio.create_task(delete_message_after_delay(chat.id, message.message_id, context, 15))
    except Exception as e:
        log.error(f"Manual ban xatosi: {e}")

async def on_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    if (old_status in ["left", "kicked"] or old_status is None) and new_status == "member":
        bot = await context.bot.get_me()
        admin_link = (
            f"https://t.me/{bot.username}?startgroup=true"
            f"&admin=delete_messages+restrict_members+pin_messages+invite_users"
        )
        keyboard = [[InlineKeyboardButton("+ Admin huquqini berish", url=admin_link)]]
        
        text = (
            "🤖Meni guruhga qo'shdingiz.\n\n"
            "Endi spamdan himoya qilishim uchun pastdagi tugmani bosib menga <b>Admin</b> huquqini bering:"
        )
        
        try:
            await context.bot.send_message(
                chat_id=result.chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        except Exception as e:
            log.warning(f"Xabar yuborishda xato: {e}")

    elif new_status == "administrator":
        text = "✅ <b>Bot muvaffaqiyatli faollashtirildi!</b>"
        try:
            msg = await context.bot.send_message(
                chat_id=result.chat.id,
                text=text,
                parse_mode="HTML"
            )
            asyncio.create_task(delete_message_after_delay(result.chat.id, msg.message_id, context, 10))
        except Exception as e:
            log.warning(f"Aktivatsiya xabarini yuborishda xato: {e}")

async def delete_message_after_delay(chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE, delay: int):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatMemberHandler(on_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", manual_ban))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\.ban'), manual_ban))
    app.add_handler(
        MessageHandler(
            filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & ~filters.COMMAND & ~filters.Regex(r'^\.ban'),
            check_message,
        )
    )
    log.info("Bot ishga tushdi ✅")
    app.run_polling()

if __name__ == "__main__":
    main()