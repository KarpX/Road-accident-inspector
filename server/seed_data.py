import asyncio
import os
from sqlalchemy import select
from database import database
import models
from dotenv import load_dotenv

load_dotenv()

async def seed_dictionaries():
    print("🚀 Запуск процесса наполнения базы данных...")
    await database.connect()
    
    async with database.get_session() as session:
        # --- 1. ФИРМЫ АВТОМОБИЛЕЙ ---
        firms_data = [
            "Lada (ВАЗ)", "Toyota", "Kia", "Hyundai", "Volkswagen", 
            "BMW", "Nissan", "Subaru", "Mercedes-Benz", "Ford", 
            "Honda", "Renault", "Skoda", "Chevrolet", "Audi", "Mazda"
        ]
        
        # --- 2. ТИПЫ КУЗОВА ---
        bodies_data = [
            "Седан", "Хэтчбек", "Универсал", "Кроссовер", 
            "Внедорожник", "Пикап", "Минивэн", "Купе", "Фургон"
        ]
        
        # --- 3. ВИДЫ ДТП (из PDF задания) ---
        types_data = [
            "Наезд на пешехода", "Наезд на препятствие", 
            "Столкновение", "Опрокидывание", "Наезд на велосипедиста",
            "Падение пассажира", "Наезд на стоящее ТС"
        ]
        
        # --- 4. ПРИЧИНЫ ДТП (из PDF задания) ---
        reasons_data = [
            "Выезд на полосу встречного движения",
            "Состояние водителя (опьянение/усталость)",
            "Неисправность автомобиля",
            "Нарушение ПДД (несоблюдение знаков/светофора)",
            "Превышение установленной скорости",
            "Несоблюдение дистанции",
            "Неудовлетворительные дорожные условия"
        ]

        # Универсальная функция для вставки данных без дубликатов
        async def insert_if_not_exists(model, data_list, field_name="name"):
            count = 0
            for item_name in data_list:
                # Проверяем, есть ли уже такая запись
                query = select(model).where(getattr(model, field_name) == item_name)
                result = await session.execute(query)
                if not result.scalar_one_or_none():
                    new_item = model(**{field_name: item_name})
                    session.add(new_item)
                    count += 1
            await session.commit()
            return count

        # Выполняем вставку
        f_count = await insert_if_not_exists(models.FirmModel, firms_data)
        b_count = await insert_if_not_exists(models.BodyModel, bodies_data)
        t_count = await insert_if_not_exists(models.AccidentTypeModel, types_data)
        r_count = await insert_if_not_exists(models.AccidentReasonModel, reasons_data)

        print(f"✅ Добавлено фирм: {f_count}")
        print(f"✅ Добавлено типов кузова: {b_count}")
        print(f"✅ Добавлено видов ДТП: {t_count}")
        print(f"✅ Добавлено причин ДТП: {r_count}")

    await database.disconnect()
    print("🏁 Наполнение завершено!")

if __name__ == "__main__":
    asyncio.run(seed_dictionaries())