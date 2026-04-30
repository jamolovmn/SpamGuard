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

# .env fayldan tokenlarni yuklash
load_dotenv()

# ─── SOZLAMALAR ──────────────────────────────────────────────────────────────

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! .env faylni tekshiring.")

# Kalit so'zlar (kichik harfda yozing, bot avtomatik kichiklashtiradi)
SPAM_KEYWORDS = [
    # ── UZBEKCHA: "profilimga" ──────────────────────────────────────────────
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

    # ── UZBEKCHA: "kanalimga" ───────────────────────────────────────────────
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

    # ── UZBEKCHA: "ko'ring" ─────────────────────────────────────────────────
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

    # ── UZBEKCHA: "salom" bilan boshlanuvchi ────────────────────────────────
    "salom, profilimga",
    "salom profilimga",
    "salom, profilga",
    "salom profilga",
    "assalomu alaykum, profilimga",
    "assalomu alaykum profilimga",

    # ── UZBEKCHA: umumiy iboralar ────────────────────────────────────────────
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

    # ── RUSCHA: "профиль" ────────────────────────────────────────────────────
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

    # ── RUSCHA: "канал" ──────────────────────────────────────────────────────
    "зайди на канал",
    "зайди в канал",
    "перейди на канал",
    "посмотри канал",
    "загляни на канал",
    "подпишись на канал",
    "мой канал",

    # ── RUSCHA: "привет" bilan ───────────────────────────────────────────────
    "привет, зайди",
    "привет зайди",
    "привет, посмотри",
    "привет посмотри",
    "привет, загляни",
    "салам, зайди",
    "салам зайди",

    # ── RUSCHA: umumiy ───────────────────────────────────────────────────────
    "есть интересное",
    "есть кое-что интересное",
    "там есть видео",
    "там интересное",
    "загляни ко мне в профиль",
    "смотри мой профиль",

    # ── INGLIZCHA ────────────────────────────────────────────────────────────
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

    # ── EMOJI + IBORA (tilsiz) ───────────────────────────────────────────────
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

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ─── YORDAMCHI FUNKSIYALAR ────────────────────────────────────────────────────

def has_spam_keyword(text: str) -> bool:
    """Xabarda spam kalit so'z bormi?"""
    text_lower = text.lower()
    for kw in SPAM_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


async def get_profile_photo_count(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Foydalanuvchi profil rasmlar sonini qaytaradi."""
    try:
        photos = await context.bot.get_user_profile_photos(user_id, limit=2)
        return photos.total_count
    except Exception as e:
        log.warning(f"Profil rasm tekshirishda xato ({user_id}): {e}")
        return -1  # Tekshirib bo'lmadi → shubhali emas deb hisoblaymiz


async def ban_user(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini guruhdan ban qiladi."""
    try:
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    except Exception as e:
        log.error(f"Ban qilishda xato: {e}")


async def delete_message(chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Spam xabarni o'chiradi."""
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        log.warning(f"Xabarni o'chirishda xato: {e}")

# ─── ASOSIY HANDLER ───────────────────────────────────────────────────────────

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har bir xabarni tekshiradi."""
    message = update.message
    if not message or not message.text:
        return

    user = message.from_user
    chat = message.chat

    # 1-belgi: Kalit so'z bormi?
    if not has_spam_keyword(message.text):
        return

    log.info(f"Kalit so'z topildi | User: {user.id} | Chat: {chat.id}")

    # 2-belgi: Username yo'qmi?
    no_username = not user.username

    # 3-belgi: Profil rasm soni == 1?
    photo_count = await get_profile_photo_count(user.id, context)
    one_photo = (photo_count == 1)

    log.info(
        f"Tekshirish → username_yoq={no_username} | "
        f"rasm_soni={photo_count} | bir_rasm={one_photo}"
    )

    # Uchala shart bajarilsa → SPAM
    if no_username and one_photo:
        log.warning(f"🚨 SPAM aniqlandi! User: {user.id} (@{user.username}) | Chat: {chat.id}")

        # Xabarni o'chir
        await delete_message(chat.id, message.message_id, context)

        # Ban
        await ban_user(chat.id, user.id, context)

        # Adminga xabar (ixtiyoriy)
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
            # 60 sekunddan keyin xabarni o'chirish
            asyncio.create_task(delete_message_after_delay(chat.id, msg.message_id, context, 60))
        except Exception as e:
            log.warning(f"Xabar yuborishda xato: {e}")
    else:
        # Kalit so'z bor lekin boshqa belgilar yo'q → adminga ogohlantirish
        log.info(f"Shubhali xabar lekin to'liq spam emas → e'tiborsiz qoldirildi")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi uchun handler."""
    bot = await context.bot.get_me()
    chat = update.effective_chat
    chat_type = chat.type

    # Admin huquqlari bilan birga qo'shish linki
    admin_link = (
        f"https://t.me/{bot.username}?startgroup=true"
        f"&admin=delete_messages+restrict_members+pin_messages+invite_users"
    )

    if chat_type == "private":
        keyboard = [[InlineKeyboardButton("🛡 Guruhga qo'shish", url=admin_link)]]
        text = "🛡 <b>SpamKuzatchi</b> botini guruhga qo'shish uchun pastdagi tugmani bosing:"
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        # Guruh ichida bo'lsa, botning adminligini tekshiramiz
        try:
            member = await chat.get_member(bot.id)
            if member.status == "administrator":
                text = "✅ <b>Bot faol!</b>"
                msg = await update.message.reply_text(text, parse_mode="HTML")
                # 10 sekunddan keyin o'chirish
                asyncio.create_task(delete_message_after_delay(chat.id, msg.message_id, context, 10))
            else:
                # Admin bo'lmasa
                keyboard = [[InlineKeyboardButton("🛡 Admin huquqini berish", url=admin_link)]]
                text = "🛡 Bot ishlashi uchun unga <b>Admin</b> huquqini berishingiz kerak:"
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        except Exception as e:
            log.warning(f"Guruhda adminlikni tekshirishda xato: {e}")


async def on_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot guruhga qo'shilganda yoki admin bo'lganda ishlaydi."""
    result = update.my_chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    # 1. Bot guruhga yangi qo'shildi (oddiy a'zo sifatida)
    if (old_status in ["left", "kicked"] or old_status is None) and new_status == "member":
        bot = await context.bot.get_me()
        admin_link = (
            f"https://t.me/{bot.username}?startgroup=true"
            f"&admin=delete_messages+restrict_members+pin_messages+invite_users"
        )
        keyboard = [[InlineKeyboardButton("🛡 Admin huquqini berish", url=admin_link)]]
        
        text = (
            "🤖 Rahmat! Meni guruhga qo'shdingiz.\n\n"
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

    # 2. Bot adminlik huquqini oldi
    elif new_status == "administrator":
        text = "✅ <b>Bot muvaffaqiyatli faollashtirildi!</b>"
        
        try:
            msg = await context.bot.send_message(
                chat_id=result.chat.id,
                text=text,
                parse_mode="HTML"
            )
            # 10 sekunddan keyin xabarni o'chirish
            asyncio.create_task(delete_message_after_delay(result.chat.id, msg.message_id, context, 10))
        except Exception as e:
            log.warning(f"Aktivatsiya xabarini yuborishda xato: {e}")


async def delete_message_after_delay(chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE, delay: int):
    """Xabarni ma'lum vaqtdan keyin o'chiradi."""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# ─── BOTNI ISHGA TUSHIRISH ────────────────────────────────────────────────────

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Bot guruhga qo'shilganda
    app.add_handler(ChatMemberHandler(on_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER))

    # Start komandasi
    app.add_handler(CommandHandler("start", start))

    # Faqat guruh/supergroup xabarlarini tekshiradi
    app.add_handler(
        MessageHandler(
            filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP),
            check_message,
        )
    )

    log.info("Bot ishga tushdi ✅")
    app.run_polling()


if __name__ == "__main__":
    main()
