import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === 🔐 BOT TOKEN ===
BOT_TOKEN = "8214638722:AAFJFQj716vEqqgmH98lP9XWxXrYF8MxHTk"
ADMIN_ID = 7930223003
ADMIN_USERNAME = "@Xop002"

# === 📱 BUKMEKERLAR ===
BOOKMAKER_INFO = {
    "1xbet": {
        "name": "1xBet",
        "desc": "📘 Mashhur bukmeker. Keng tanlovdagi sport o'yinlariga tikish imkoniyati.",
        "apk": "https://t.me/bonusliilova1/4"
    },
    "linnbet": {
        "name": "LinnBet",
        "desc": "🟩 Ishonchli bukmeker. Yuqori koeffitsiyentlar va qulay interfeys.",
        "apk": "https://t.me/bonusliilova1/2"
    },
    "melbet": {
        "name": "MelBet",
        "desc": "🟧 Foydalanish oson bo'lgan ilova. Tez to'lovlar va yangi foydalanuvchilar uchun bonuslar mavjud.",
        "apk": "https://t.me/bonusliilova1/3"
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
    
    if not info:
        await callback.answer("❌ Bukmeker topilmadi")
        return
        
    user_state[callback.from_user.id] = {
        "bookmaker": bookmaker_key, 
        "step": "ask_id",
        "bookmaker_name": info['name']
    }

    text_apk = (
        f"🏦 <b>{info['name']}</b>\n\n"
        f"{info['desc']}\n\n"
        f"⬇️ Yuklab olish uchun havola: {info['apk']}"
    )
    await callback.message.answer(text_apk, parse_mode="HTML")

    # ОБНОВЛЕННЫЙ ТЕКСТ - сразу просит ID и скриншот
    text_instr = (
        "🤖 BOT SERVERGA ULANISHI UCHUN QUYIDAGILARNI YUBORING:\n\n"
        "Bot to'g'ri ishlashi uchun quyidagi shartlarni bajaring 👇:\n\n"
        "1️⃣ Akkount ochishda KUZ11 promokodi kiritilgan bo'lishi kerak\n"
        "2️⃣ Minimal depozit 5$ – 10$ dan yuqori bo'lishi kerak\n"
        "3️⃣ ID yuborgandan so'ng, o'yin boshlanishidan oldin 1–2 soat kuting\n\n"
        "🍎 Apple of Fortuna o'yinini boshlash uchun:\n\n"
        "✍️ Avvalo, ID raqamingizni yuboring:\n"
    )
    await callback.message.answer(text_instr)
    await callback.answer()

# === 🆔 ID QABUL QILISH ===
@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    state = user_state.get(uid)
    
    # Agar promokod yuborilsa
    if message.text.strip().upper() == "KUZBET11":
        await promo_accept(message)
        return

    if not state:
        await message.answer("❌ Iltimos, avval /start ni bosing va bukmekerni tanlang.")
        return

    if state.get("step") == "ask_id":
        # ID ni saqlaymiz
        user_state[uid]["id"] = message.text.strip()
        user_state[uid]["step"] = "waiting_screenshot"
        
        # ОБНОВЛЕННЫЙ ТЕКСТ - просит скриншот с промокодом KUZ11
        await message.answer(
            "✅ ID qabul qilindi!\n\n"
            "📸 Endi KUZ11 promokodini kirganligingizni tasdiqlovchi SKRINSHOTNI yuboring:\n\n"
            "Skrinshotda KUZ11 promokodi ko'rinishi kerak!\n\n"
            "Skrinshotni shu yerga yuboring:"
        )
    
    elif state.get("step") == "waiting_screenshot":
        await message.answer("❌ Iltimos, skrinshot yuboring, matn emas!")
    
    elif state.get("step") == "rejected":
        await message.answer("❌ Sizning so'rovingiz rad etilgan. Admin bilan bog'laning.")
    
    else:
        await message.answer("❌ Noma'lum xatolik. /start ni bosing.")

# === 📸 SKRINSHOT QABUL QILISH ===
@dp.message(F.photo)
async def handle_screenshot(message: types.Message):
    uid = message.from_user.id
    state = user_state.get(uid)

    if not state or state.get("step") != "waiting_screenshot":
        if state and state.get("step") == "ask_id":
            await message.answer("❌ Iltimos, avval ID raqamingizni yuboring.")
        else:
            await message.answer("❌ Iltimos, avval /start ni bosing va bukmekerni tanlang.")
        return

    # Skrinshotni saqlaymiz
    user_state[uid]["screenshot"] = message.photo[-1].file_id
    user_state[uid]["step"] = "waiting_approval"

    # Admin uchun matn tayyorlaymiz
    text_for_admin = (
        f"👤 <b>Yangi foydalanuvchi ID va skrinshot yubordi!</b>\n\n"
        f"🧾 ID: <code>{state['id']}</code>\n"
        f"📱 Username: @{message.from_user.username or 'yoq'}\n"
        f"🆔 Telegram ID: <code>{uid}</code>\n"
        f"🏦 Bukmeker: {state.get('bookmaker_name', 'Noma lum')}\n\n"
        f"Foydalanuvchini tasdiqlaysizmi?"
    )

    try:
        # Admin'ga matn va skrinshotni yuboramiz
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=state['screenshot'],
            caption=text_for_admin,
            parse_mode="HTML",
            reply_markup=approve_keyboard(uid)
        )
        await message.answer(
            "✅ Sizning ID va skrinshot admin tekshiruviga yuborildi!\n"
            "🕓 Tasdiqlanishini kuting...\n\n"
            "Admin sizni tez orada tasdiqlaydi."
        )
        
    except Exception as e:
        error_msg = f"❌ Admin'ga yuborishda xatolik: {type(e).__name__}: {str(e)}"
        print(error_msg)
        
        await message.answer(
            f"⚠️ Ma'lumotlaringiz adminga yuborilmadi.\n\n"
            f"Iltimos, keyinroq qayta urinib ko'ring yoki admin {ADMIN_USERNAME} bilan bog'laning."
        )

# === 👮‍♂️ ADMIN TASDIQLASH / RAD ETISH ===
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: types.CallbackQuery):
    try:
        user_id = int(callback.data.split("_")[1])
        
        if user_id not in user_state:
            await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)
            return
            
        user_state[user_id]["step"] = "signals"
        
        await bot.send_message(
            user_id,
            "🎉 Tabriklaymiz! ✅ Admin tomonidan tasdiqlandi!\n\n"
            "Endi siz botdan to'liq foydalanishingiz mumkin ✅\n\n"
            "Birinchi signalni olish uchun quyidagi tugmani bosing 👇"
        )
        await send_random_signal(user_id)
        
        await callback.message.edit_text(
            f"✅ Foydalanuvchi tasdiqlandi!\n"
            f"User ID: {user_id}\n"
            f"Username: @{callback.from_user.username or 'yoq'}"
        )
        await callback.answer("✅ Foydalanuvchi tasdiqlandi")
        
    except Exception as e:
        await callback.answer(f"❌ Xatolik: {str(e)}", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: types.CallbackQuery):
    try:
        user_id = int(callback.data.split("_")[1])
        user_state[user_id] = {"step": "rejected"}
        
        await bot.send_message(
            user_id,
            "❌ Sizning so'rovingiz rad etildi.\n\n"
            "Agar sizda KUZ11 promokodi bo'lsa, uni kiriting:\n"
            "Yozing: KUZBET11\n\n"
            "Yoki admin bilan bog'laning: @Xop002"
        )
        
        await callback.message.edit_text(
            f"❌ Foydalanuvchi rad etildi.\n"
            f"User ID: {user_id}\n"
            f"Username: @{callback.from_user.username or 'yoq'}"
        )
        await callback.answer("❌ Foydalanuvchi rad etildi")
        
    except Exception as e:
        await callback.answer(f"❌ Xatolik: {str(e)}", show_alert=True)

# === ПРОМОКОД KUZBET11 ===
@dp.message(F.text.regexp(r"(?i)^KUZBET11$"))
async def promo_accept(message: types.Message):
    user_state[message.from_user.id] = {"step": "signals"}
    await message.answer(
        "✅ Promokod KUZBET11 tasdiqlandi!\n\n"
        "🎉 Endi siz botdan to'liq foydalanishingiz mumkin ✅\n\n"
        "Birinchi signalni olish uchun quyidagi tugmani bosing 👇"
    )
    await send_random_signal(message.from_user.id)

# === 🍎 SIGNAL YUBORISH ===
async def send_random_signal(chat_id: int):
    number = random.randint(1, 5)
    await bot.send_message(
        chat_id,
        f"📶 <b>Yangi signal</b>\n\n"
        f"👉 <b>{number}-chi</b> olmani tanlang 🍎\n\n"
        f"Keyingi signalni olish uchun tugmani bosing 👇",
        parse_mode="HTML",
        reply_markup=new_signal_button()
    )

# === ♻️ YANGI SIGNAL OLISH ===
@dp.callback_query(F.data == "new_signal")
async def next_signal(callback: types.CallbackQuery):
    uid = callback.from_user.id
    state = user_state.get(uid, {})
    
    if state.get("step") != "signals":
        await callback.answer("❌ Sizga hali ruxsat berilmagan!", show_alert=True)
        return
        
    await send_random_signal(uid)
    await callback.answer("✅ Yangi signal yuborildi!")

# === ▶️ ISHGA TUSHURISH ===
async def main():
    print("🤖 Bot ishga tushdi...")
    print(f"🔧 Admin ID: {ADMIN_ID}")
    print("⏳ Yangi foydalanuvchilarni kutish...")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Bot ishga tushmadi: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

