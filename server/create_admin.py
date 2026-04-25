import asyncio
import os
from database import database
import models
from auth import get_password_hash
from dotenv import load_dotenv

load_dotenv()

async def create_master_admin():
    print("Подключение к базе данных...")
    await database.connect()
    
    async with database.get_session() as session:
        admin_username = "MASTER-ADMIN"
        admin_password = "imanimepsycho"
        admin_fio = "Начальник УГИБДД"
        
        from sqlalchemy import select
        result = await session.execute(select(models.UserModel).where(models.UserModel.username == admin_username))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"Администратор {admin_username} уже существует.")
            print(f"Логин: {admin_username}")
            print(f"Пароль: {admin_password}")
        else:
            new_admin = models.UserModel(
                username=admin_username,
                fio=admin_fio,
                hashed_password=get_password_hash(admin_password),
                role="admin"
            )
            session.add(new_admin)
            await session.commit()
            print(f"--- УСПЕХ ---")
            print(f"Логин: {admin_username}")
            print(f"Пароль: {admin_password}")
            print("Теперь вы можете войти в систему и генерировать ключи для сотрудников.")

    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(create_master_admin())