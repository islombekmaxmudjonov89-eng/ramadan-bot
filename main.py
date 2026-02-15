import logging
import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

# 1. ASOSIY MA'LUMOTLAR
API_TOKEN = '8397694302:AAFPxWQ21td-aOgE5zSLeF8Tl-rQvxoNQt8'
QURAN_CLIENT_ID = 'b0eb12dd-3ea6-4b74-93f6-521375f312b1'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchi salovatlarini saqlash uchun lug'at
user_salovats = {}

# --- YANGI QO'SHIMCHA: IBRATLI MA'LUMOTLAR ---
IBRATLI_QISSALAR = {
    "firavn": (
        "🌊 **Fir'avn va uning saqlanib qolgan jasadi**\n\n"
        "Fir'avn o'zini Xudo deb e'lon qilib, kibrda haddidan oshgan edi. "
        "Alloh uni va uning qo'shinini Qizil dengizda g'arq qildi.\n\n"
        "📖 **Qur'on mo'jizasi:**\n"
        "Alloh taolo Yunus surasi 92-oyatida: *'Sizdan keyingilarga belgi (ibrat) bo'lishingiz uchun bugun sizning tanangizni (qirg'oqqa) chiqaramiz'*, deb marhamat qilgan.\n\n"
        "🔍 **Haqiqat:**\n"
        "Bugungi kunda Misr muzeyida saqlanayotgan Fir'avn jasadi ming yillar o'tsa ham chirib ketmagan. "
        "Uning tanasida dengiz tuzi qoldiqlari topilgan. "
        "Yer ham, dengiz ham uni qabul qilmagani butun insoniyat uchun katta ibratdir."
    )
}

# SURA NOMLARI RO'YXATI
SURAH_NAMES = {
    1: "Fotiha", 2: "Baqara", 3: "Oli Imron", 4: "Niso", 5: "Moida",
    18: "Kahf", 19: "Maryam", 36: "Yosin", 55: "Ar-Rohman", 56: "Voqea",
    67: "Mulk", 78: "Naba", 97: "Qadr", 112: "Ixlos", 113: "Falaq", 114: "Nos"
}

# 2. OYAT TARJIMASI
async def get_ayah_translation(ayah_key):
    url = f"https://api.quran.com/api/v4/quran/translations/101?ayah_key={ayah_key}"
    headers = {'Accept': 'application/json', 'x-client-id': QURAN_CLIENT_ID}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'translations' in data and data['translations']:
                        return data['translations'][0]['text']
                return None
        except: return None

# 3. BITTA OYAT AUDIO
async def get_ayah_audio(ayah_key):
    try:
        sura, oyat = ayah_key.split(':')
        return f"https://everyayah.com/data/Alafasy_128kbps/{sura.zfill(3)}{oyat.zfill(3)}.mp3"
    except: return None

# 4. NAMOZ VAQTLARI
async def get_prayer_times(city="Tashkent"):
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Uzbekistan&method=3"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['data']['timings']
        except: return None

# ASOSIY MENYU TUGMALARI (Ibratli qissalar qo'shildi)
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(
                text="🌙 Ramadan Mubarak 2026", 
                web_app=WebAppInfo(url="https://bit.ly/Ramazon01")
            )],
            [types.KeyboardButton(text="📜 Suralar (Nomi va Raqami)")],
            [types.KeyboardButton(text="📖 Oyatlar (Mashhurlari)")],
            [types.KeyboardButton(text="📿 Salovatlar va Tasbeh")],
            [types.KeyboardButton(text="🌊 Ibratli Qissalar")], # YANGI TUGMA
            [types.KeyboardButton(text="🏙 /namoz")]
        ],
        resize_keyboard=True
    )
    return keyboard

# TASBEH TUGMASI
def tasbeh_inline_menu(count=0):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=f"📿 Salovat aytish: {count}", callback_data="add_salovat"))
    builder.add(InlineKeyboardButton(text="🔄 Nollash", callback_data="reset_salovat"))
    builder.adjust(1)
    return builder.as_markup()

# 5. START HANDLER
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Assalomu alaykum!\n\n"
        "🌙 **Ramazon Mubarak 2026** Mini App-imiz ishga tushdi!\n\n"
        "🔢 **Sura raqami** (masalan: 36)\n"
        "🔢 **Oyat** (masalan: 2:255)\n"
        "🏙 /namoz\n\n"
        "Quyidagi menyudan foydalanishingiz mumkin:",
        reply_markup=main_menu()
    )

# SURALAR RO'YXATI
@dp.message(F.text == "📜 Suralar (Nomi va Raqami)")
async def surah_list(message: types.Message):
    text = "📖 **Asosiy suralar ro'yxati:**\n\n"
    for num, name in SURAH_NAMES.items():
        text += f"**{num}** - {name}\n"
    text += "\n_Eshitish uchun sura raqamini botga yuboring (masalan: 36)_"
    await message.answer(text, parse_mode="Markdown")

# OYATLAR RO'YXATI
@dp.message(F.text == "📖 Oyatlar (Mashhurlari)")
async def ayah_list(message: types.Message):
    text = (
        "✨ **Mashhur oyatlar raqamlari:**\n\n"
        "🔹 **Oyatul Kursiy** - `2:255`\n"
        "🔹 **Amenerrasulü** - `2:285`\n"
        "🔹 **La yastavi** - `59:21`\n"
        "🔹 **Kahf (avvalgi 10 oyat)** - `18:1`\n\n"
        "_Tarjimasi va audiosini olish uchun raqamni yozib yuboring._"
    )
    await message.answer(text, parse_mode="Markdown")

# --- YANGI HANDLER: IBRATLI QISSALAR ---
@dp.message(F.text == "🌊 Ibratli Qissalar")
async def qissalar_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🌊 Fir'avn jasadi mo'jizasi", callback_data="qissa_firavn"))
    await message.answer(
        "✨ **Tarixdagi ibratli voqealar:**\n\n"
        "Bilim olish va iymonni mustahkamlash uchun tanlang:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "qissa_firavn")
async def show_qissa_firavn(callback: types.CallbackQuery):
    await callback.message.answer(IBRATLI_QISSALAR["firavn"], parse_mode="Markdown")
    await callback.answer()

# SALOVATLAR VA TASBEH BO'LIMI
@dp.message(F.text == "📿 Salovatlar va Tasbeh")
async def salovat_section(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_salovats:
        user_salovats[user_id] = 0
        
    text = (
        "❤️ **Payg'ambarimiz Muhammad (s.a.v)ga salovat aytish**\n\n"
        "Payg'ambarimiz (s.a.v) aytganlar: *'Kim menga bir marta salovat aytsa, Alloh unga o'nta rahmat yo'llaydi.'*\n\n"
        "**Aytilishi:** `Sollallohu alayhi vasallam` yoki `Allohumma solli ala Muhammad`\n\n"
        "Pastdagi tugmani har bir aytganingizda bosing:"
    )
    await message.answer(text, reply_markup=tasbeh_inline_menu(user_salovats[user_id]), parse_mode="Markdown")

# TASBEH TUGMALARI ISHLASHI
@dp.callback_query(F.data == "add_salovat")
async def add_salovat_cb(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_salovats[user_id] = user_salovats.get(user_id, 0) + 1
    await callback.message.edit_reply_markup(reply_markup=tasbeh_inline_menu(user_salovats[user_id]))
    await callback.answer("Alloh qabul qilsin! ✨")

@dp.callback_query(F.data == "reset_salovat")
async def reset_salovat_cb(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_salovats[user_id] = 0
    await callback.message.edit_reply_markup(reply_markup=tasbeh_inline_menu(0))
    await callback.answer("Hisoblagich nollab qo'yildi.")

@dp.message(Command("namoz"))
async def namoz_handler(message: types.Message):
    t = await get_prayer_times()
    if t:
        await message.answer(f"🏙 **Toshkent namoz vaqtlari:**\n\nBomdod: {t['Fajr']}\nPeshin: {t['Dhuhr']}\nAsr: {t['Asr']}\nShom: {t['Maghrib']}\nXufton: {t['Isha']}", parse_mode="Markdown")

# ASOSIY XABARLARNI QAYTA ISHLASH
@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()
    
    if ":" in text:
        wait = await message.answer("Oyat yuklanmoqda...")
        tr = await get_ayah_translation(text)
        au = await get_ayah_audio(text)
        if tr:
            await message.answer(f"📖 **{text}-oyat:**\n\n{re.sub('<[^<]+?>', '', tr)}")
        if au:
            try:
                await message.answer_audio(URLInputFile(au, filename=f"{text}.mp3"))
            except:
                await message.answer("Audioda xatolik.")
        await wait.delete()

    elif text.isdigit():
        num = int(text)
        if 1 <= num <= 114:
            wait = await message.answer(f"📦 {num}-sura yuklanmoqda...")
            audio_url = f"https://server8.mp3quran.net/afs/{text.zfill(3)}.mp3"
            try:
                audio_file = URLInputFile(audio_url, filename=f"Surah_{text}.mp3")
                await message.answer_audio(audio_file, caption=f"📖 {num}-sura (To'liq)")
            except Exception:
                alt_url = f"https://download.quranicaudio.com/quran/mishari_rashid_alafasy/{text.zfill(3)}.mp3"
                try:
                    await message.answer_audio(URLInputFile(alt_url), caption=f"📖 {num}-sura (Muqobil)")
                except:
                    await message.answer("Kechirasiz, audio fayl juda katta yoki topilmadi.")
            await wait.delete()
        else:
            await message.answer("1-114 gacha son yozing.")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    async def run_bot():
        try:
            await main()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Bot to'xtatildi")

    asyncio.run(run_bot())
