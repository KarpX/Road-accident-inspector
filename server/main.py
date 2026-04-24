from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy import select

import models, schemas
from database import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Подключение к базе данных...")
    await database.connect()
    
    yield
    
    print("Отключение от базы данных...")
    await database.disconnect()

app = FastAPI(title="ГИБДД Аналитика API", lifespan=lifespan)

@app.post("/api/drivers/", response_model=schemas.DriverResponse, tags=["Drivers"])
async def create_driver(driver: schemas.DriverCreate):
    async with database.get_session() as session:
        db_driver = models.DriverModel(**driver.model_dump())
        session.add(db_driver)
        await session.commit()
        await session.refresh(db_driver)
        return db_driver
    
@app.get("/api/drivers/", response_model=List[schemas.DriverResponse], tags=["Drivers"])
async def read_drivers(limit: int | None = None):
    async with database.get_session() as session:
        query = select(models.DriverModel)
    
        if limit is not None:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()

@app.get("/api/drivers/{driver_id}", response_model=schemas.DriverResponse, tags=["Drivers"])
async def read_driver(driver_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.DriverModel)
            .where(models.DriverModel.id == driver_id)
        )

        driver = result.scalar_one_or_none()
        if driver is None:
            raise HTTPException(status_code=404, detail="Водитель не найден")
        return driver