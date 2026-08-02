import asyncio
import re
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен из твоего HTML-кода
BOT_TOKEN = '8098284771:AAHHkybTZ6a_mMB8dF52EY9JlLIEiAqPXzI'

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Данные об автомобилях (из твоего HTML) - полный список...
CARS_DATA = {
    'Низкий класс': [
        {'name': 'BMW M5 E28', 'price': 500000},
        # ... все остальные автомобили
    ],
    # ... все категории
}

# Создаем словарь для быстрого поиска
CAR_PRICES = {}
for category, cars in CARS_DATA.items():
    for car in cars:
        car_name_lower = car['name'].lower()
        CAR_PRICES[car_name_lower] = car['price']
        CAR_PRICES[car_name_lower.replace(' ', '')] = car['price']

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply(
        "🚗 Привет! Я бот для проверки цен на автомобили.\n\n"
        "Чтобы узнать цену, напиши:\n"
        "Каскад, сколько стоит [модель авто]\n\n"
        "Например:\n"
        "Каскад, сколько стоит bmw x5m"
    )

@dp.message()
async def handle_message(message: Message):
    text = message.text
    if not text:
        return
    
    pattern = r'каскад[,]?\s*сколько\s*стоит\s*(.+)'
    match = re.search(pattern, text.lower())
    
    if match:
        car_query = match.group(1).strip()
        
        # Ищем автомобиль
        found_price = None
        found_name = None
        found_category = None
        
        # Прямой поиск
        if car_query in CAR_PRICES:
            found_price = CAR_PRICES[car_query]
            found_name = car_query
            for category, cars in CARS_DATA.items():
                for car in cars:
                    if car['name'].lower() == car_query:
                        found_category = category
                        break
                if found_category:
                    break
        else:
            # Поиск по частичному совпадению
            best_match = None
            best_match_length = 0
            
            for car_name, price in CAR_PRICES.items():
                if car_query in car_name or car_name in car_query:
                    match_length = min(len(car_query), len(car_name))
                    if match_length > best_match_length:
                        best_match_length = match_length
                        best_match = (car_name, price)
            
            if best_match:
                found_name, found_price = best_match
                for category, cars in CARS_DATA.items():
                    for car in cars:
                        if car['name'].lower() == found_name:
                            found_category = category
                            break
                    if found_category:
                        break
        
        if found_price is not None and found_name is not None:
            formatted_price = f"{found_price:,}".replace(',', ' ')
            formatted_name = found_name.title()
            
            response = f"💰 {formatted_name} — {formatted_price} ₽"
            if found_category:
                response += f"\n📂 Класс: {found_category}"
            
            await message.reply(response)
        else:
            await message.reply(
                f"❌ Автомобиль '{car_query}' не найден в базе.\n\n"
                "Попробуйте уточнить название или использовать /help"
            )

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
