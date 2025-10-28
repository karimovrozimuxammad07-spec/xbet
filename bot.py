import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === 🔐 BOT TOKEN ===
BOT_TOKEN = "8214638722:AAFJFQj716vEqqgmH98lP9XWxXrYF8MxHTk"
ADMIN_ID = 7930223003  # <-- Проверь! Это должен быть настоящий Telegram ID админа
ADMIN_USERNAME = "@Xop002"

# === 📱 BUKMEKERLAR ===
BOOKMAKER_INFO = {
    "1xbet": {
        "name": "1xBet",
        "desc": "📘 Mashhur bukmeker. Keng tanlovdagi sport o'yinlariga tikish imkoniyati.",
        "apk": "https://t.me/kuzbet0lma/5"
    },
    "linnbet": {
        "name": "LinnBet",
        "desc": "🟩 Ishonchli bukmeker. Yuqori koeffitsiyentlar va qulay interfeys.",
        "apk": "https://t.me/kuzbet0lma/6"
    },
    "melbet": {
        "name": "MelBet",
        "desc": "🟧 Foydalanish oson bo‘lgan ilova. Tez to‘lovlar va yangi foydalanuvchilar uchun bonuslar mavjud.",
        "apk": "https://t.me/kuzbet0lma/7"
    }
}

# === 🧩 TUGMALAR ===
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[ 
        InlineKeyboardButton(text="🟦 1xBet", callback_data="bookmaker_1xbet"),
        InlineKeyboardButton(text="🟩 LinnBet", callback_data="bookmaker_linnbet"),
        InlineKeyboardButton(text="🟧 MelBet", callback_data="bookmaker_melbet")
    ]])

def new_signal_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Yangi signal olish", callback_data="new_signal")]
    ])

def approve_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"approve_{user_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{user_id}")]
    ])

# === 🔄 HOLAT SAQLASH ===
user_state = {}
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === 🚀 START KOMANDASI ===
@dp.message(CommandStart())
async def start(message: types.Message):
    user_state[message.from_user.id] = {"step": "choose_bookmaker"}
    await message.answer(
        "👋 Salom! Quyidagi bukmekerlardan birini tanlang va davom eting 👇",
        reply_markup=main_keyboard()
    )

# === 🏦 BUKMEKER TANLASH ===
@dp.callback_query(F.data.startswith("bookmaker_"))
async def bookmaker_choice(callback: types.CallbackQuery):
    bookmaker_key = callback.data.split("_")[1]
    info = BOOKMAKER_INFO.get(bookmaker_key)
    user_state[callback.from_user.id] = {"bookmaker": bookmaker_key, "step": "ask_id"}

    text_apk = (
        f"🏦 <b>{info['name']}</b>\n\n"
        f"{info['desc']}\n\n"
        f"⬇️ Yuklab olish uchun havola: {info['apk']}"
    )
    await callback.message.answer(text_apk, parse_mode="HTML")

    text_instr = (
        "🤖 BOT SERVERGA ULANISHI UCHUN ID RAQAMINGIZNI YUBORING ❗✍️\n\n"
        "Bot aniq ishlashi uchun shartlarni bajaring:👇\n"
        "1️⃣ Telefon raqam ulangan bo‘lishi kerak.\n"
        "2️⃣ Promokod kiritilgan bo‘lishi kerak!\n"
        "3️⃣ Deposit minimal 10 $ dan ko‘p bo‘lishi kerak.\n"
        "4️⃣ O‘yinlar oralig‘i 15 daqiqadan kam bo‘lmasin.\n"
        "5️⃣ ID yuborilgandan so‘ng 1–2 soat kutib o‘yinni boshlang.\n"
        "Bot kombinatsiyalarida faqat oxirgi sonni tanlang❗\n\n"
        "🍎 Apple of Fortuna o‘yinini boshlash uchun ID raqamingizni shu yerga yozib ✍️ yuboring!"
    )
    await callback.message.answer(text_instr)
    await callback.answer()

# === 🆔 ID QABUL QILISH ===
@dp.message()
async def handle_id(message: types.Message):
    uid = message.from_user.id
    state = user_state.get(uid)

    if not state or state.get("step") != "ask_id":
        await message.answer("Iltimos, avval /start ni bosing va bukmekerni tanlang.")
        return

    user_state[uid]["id"] = message.text.strip()
    user_state[uid]["step"] = "waiting_approval"

    text_for_admin = (
        f"👤 <b>Yangi foydalanuvchi ID yubordi!</b>\n\n"
        f"🧾 ID: <code>{message.text.strip()}</code>\n"
        f"📱 Username: @{message.from_user.username or 'yo‘q'}\n"
        f"🆔 Telegram ID: <code>{uid}</code>\n"
        f"🏦 Bukmeker: {BOOKMAKER_INFO[state['bookmaker']]['name']}\n\n"
        f"Adminga: foydalanuvchiga ruxsat berish yoki rad etish 👇"
    )

    try:
        await bot.send_message(ADMIN_ID, text_for_admin, parse_mode="HTML", reply_markup=approve_keyboard(uid))
        await message.answer("🕓 Sizning ID admin tekshiruvidan o‘tmoqda. Iltimos, kuting...")
    except Exception as e:
        print(f"❌ Admin'ga yuborilmadi: {e}")
        await message.answer(
            f"⚠️ Admin bilan aloqa o‘rnatilmadi.\n"
            f"Iltimos, admin {ADMIN_USERNAME} bilan bog‘laning."
        )

# === 👮‍♂️ ADMIN TASDIQLASH / RAD ETISH ===
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    if user_id not in user_state:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return
    user_state[user_id]["step"] = "signals"
    await bot.send_message(
        user_id,
        "✅ Admin tomonidan tasdiqlandi!\n\nEndi siz botdan foydalanishingiz mumkin ✅"
    )
    await send_random_signal(user_id)
    await callback.message.edit_text("✅ Foydalanuvchi tasdiqlandi.")
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    user_state[user_id] = {"step": "rejected"}
    await bot.send_message(
        user_id,
        (
            "❌ Sizning so‘rovingiz rad etildi.\n\n"
            "Agar sizda KUZ11 promokodi bo‘lsa, uni kiriting.\n"
            "Promokodni yuboring (masalan: KUZ11) Admin bilan Aloqa @Xop002 "
        )
    )
    await callback.message.edit_text("❌ Foydalanuvchi rad etildi.")
    await callback.answer()

# === ПРОМОКОД KUZBET11 ===
@dp.message(F.text.regexp(r"(?i)^KUZBET11$"))
async def promo_accept(message: types.Message):
    user_state[message.from_user.id] = {"step": "signals"}
    await message.answer(
        "✅ Promokod KUZBET11 tasdiqlandi!\nEndi siz botdan foydalanishingiz mumkin ✅"
    )
    await send_random_signal(message.from_user.id)

# === 🍎 SIGNAL YUBORISH ===
async def send_random_signal(chat_id: int):
    number = random.randint(1, 5)
    await bot.send_message(
        chat_id,
        f"📶 Signal\n👉 {number}-chi olmani tanlang 🍎",
        reply_markup=new_signal_button()
    )

# === ♻️ “Yangi signal olish” ===
@dp.callback_query(F.data == "new_signal")
async def next_signal(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if user_state.get(uid, {}).get("step") != "signals":
        await callback.answer("❌ Sizga hali ruxsat berilmagan!", show_alert=True)
        return
    await send_random_signal(uid)
    await callback.answer()

# === ▶️ ISHGA TUSHURISH ===
async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
