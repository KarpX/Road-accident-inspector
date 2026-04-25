from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy import select, func, cast, Date
import datetime
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Водитель не найден")
        return driver
    
@app.delete("/api/drivers/{driver_id}", response_model=schemas.DriverResponse, tags=["Drivers"])
async def delete_driver(driver_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.DriverModel)
            .where(models.DriverModel.id == driver_id)
        )

        driver = result.scalar_one_or_none()

        if driver is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Водитель не найден")

        await session.delete(driver)
        await session.commit()
        return driver

@app.post("/api/cars/", response_model=schemas.CarResponse, tags=["Cars"])
async def create_car(car: schemas.CarCreate):
    async with database.get_session() as session:
        new_car = models.CarModel(**car.model_dump())
        session.add(new_car)
        await session.commit()
        await session.refresh(new_car)
        return new_car
    
@app.get("/api/cars/", response_model=List[schemas.CarResponse], tags=["Cars"])
async def read_cars(limit: int | None = None):
    async with database.get_session() as session:
        query = select(models.CarModel)

        if limit is not None:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()
    
@app.get("/api/cars/{car_id}", response_model=schemas.CarResponse, tags=["Cars"])
async def read_car(car_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.CarModel)
            .where(models.CarModel.id == car_id)
        )

        car = result.scalar_one_or_none()

        if car is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Машина не найдена")
        return car
    
@app.delete("/api/cars/{car_id}", response_model=schemas.CarResponse, tags=["Cars"])
async def delete_car(car_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.CarModel)
            .where(models.CarModel.id == car_id)
        )

        car = result.scalar_one_or_none()

        if car is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Машина не найдена")
        
        await session.delete(car)
        await session.commit()
        return car
        
        
@app.post("/api/department/", response_model=schemas.DepartmentResponse, tags=["Department"])
async def create_department(department: schemas.DepartmentCreate):
    async with database.get_session() as session:
        new_department = models.DepartmentModel(**department.model_dump())
        session.add(new_department)
        await session.commit()
        await session.refresh(new_department)
        return new_department

@app.get("/api/department/", response_model=List[schemas.DepartmentResponse], tags=["Department"])
async def get_departments(limit: int | None = None):
    async with database.get_session() as session:
        query = select(models.DepartmentModel)

        if limit is not None:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()
    
@app.get("/api/department/{department_id}", response_model=schemas.DepartmentResponse, tags=["Department"])
async def get_department(department_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.DepartmentModel)
            .where(models.DepartmentModel.id == department_id)
        )

        department = result.scalar_one_or_none()

        if department is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Отдел ГИБДД не найден")
        return department
    
@app.delete("/api/department/{department_id}", response_model=schemas.DepartmentResponse, tags=["Department"])
async def delete_department(department_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.DepartmentModel)
            .where(models.DepartmentModel.id == department_id)
        )

        department = result.scalar_one_or_none()

        if department is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Отдел ГИБДД не найден")
        
        await session.delete(department)
        await session.commit()
        return department
    
@app.post("/api/acts/", response_model=schemas.ActResponse, tags=["Acts"])
async def create_act(act: schemas.ActCreate):
    async with database.get_session() as session:
        new_act = models.ActModel(**act.model_dump())
        session.add(new_act)
        await session.commit()
        await session.refresh(new_act)
        return new_act

@app.get("/api/acts/", response_model=List[schemas.ActResponse], tags=["Acts"])
async def read_acts(limit: int | None = None):
    async with database.get_session() as session:
        query = select(models.ActModel)
        if limit is not None:
            query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

@app.get("/api/acts/{act_id}", response_model=schemas.ActResponse, tags=["Acts"])
async def read_act(act_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.ActModel).where(models.ActModel.id == act_id)
        )
        act = result.scalar_one_or_none()
        if act is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Акт не найден")
        return act

@app.delete("/api/acts/{act_id}", response_model=schemas.ActResponse, tags=["Acts"])
async def delete_act(act_id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.ActModel).where(models.ActModel.id == act_id)
        )
        act = result.scalar_one_or_none()
        if act is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Акт не найден")
        
        await session.delete(act)
        await session.commit()
        return act
    

@app.post("/api/participants/", response_model=schemas.ParticipantResponse, tags=["Participants"])
async def add_participant(participant: schemas.ParticipantCreate):
    async with database.get_session() as session:
        new_participant = models.AccidentParticipantModel(**participant.model_dump())
        session.add(new_participant)
        await session.commit()
        await session.refresh(new_participant)
        return new_participant

@app.get("/api/participants/", response_model=List[schemas.ParticipantResponse], tags=["Participants"])
async def get_participants():
    async with database.get_session() as session:
        result = await session.execute(
            select(models.AccidentParticipantModel)
        )
        
        return result.scalars().all()
    
@app.get("/api/participants/{id}", response_model=schemas.ParticipantResponse, tags=["Participants"])
async def get_participants(id: int):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.AccidentParticipantModel)
            .where(models.AccidentParticipantModel.id == id)
        )

        participant = result.scalar_one_or_none()

        if participant is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Участник ДТП не найден")
        
        return participant
    

# ==========================================
# АНАЛИТИЧЕСКИЕ ЗАПРОСЫ (ПО ЗАДАНИЮ МВД)
# ==========================================

@app.get("/api/analytics/repeat-offenders", response_model=List[schemas.DriverResponse], tags=["Analytics"])
async def get_repeat_offenders():
    async with database.get_session() as session:
        query = (
            select(models.DriverModel)
            .join(models.AccidentParticipantModel, models.DriverModel.id == models.AccidentParticipantModel.driver_id)
            .group_by(models.DriverModel.id)
            .having(func.count(models.AccidentParticipantModel.act_id) > 1)
        )
        result = await session.execute(query)
        return result.scalars().all()


@app.get("/api/analytics/drivers-by-place", response_model=List[schemas.DriverResponse], tags=["Analytics"])
async def get_drivers_by_place(place: str):
    async with database.get_session() as session:
        query = (
            select(models.DriverModel)
            .join(models.AccidentParticipantModel)
            .join(models.ActModel)
            .where(models.ActModel.place.ilike(f"%{place}%"))
        ).distinct()
        
        result = await session.execute(query)
        return result.scalars().all()


@app.get("/api/analytics/drivers-by-date", response_model=List[schemas.DriverResponse], tags=["Analytics"])
async def get_drivers_by_date(target_date: datetime.date):
    async with database.get_session() as session:
        query = (
            select(models.DriverModel)
            .join(models.AccidentParticipantModel)
            .join(models.ActModel)
            .where(cast(models.ActModel.date, Date) == target_date)
        ).distinct()
        
        result = await session.execute(query)
        return result.scalars().all()


@app.get("/api/analytics/max-victims-acts", response_model=List[schemas.ActResponse], tags=["Analytics"])
async def get_acts_with_max_victims():
    async with database.get_session() as session:
        subq = select(func.max(models.ActModel.victims)).scalar_subquery()
        
        query = select(models.ActModel).where(models.ActModel.victims == subq)
        
        result = await session.execute(query)
        return result.scalars().all()


@app.get("/api/analytics/pedestrian-accidents", response_model=List[schemas.DriverResponse], tags=["Analytics"])
async def get_pedestrian_accident_drivers():
    async with database.get_session() as session:
        query = (
            select(models.DriverModel)
            .join(models.AccidentParticipantModel)
            .join(models.ActModel)
            .join(models.AccidentTypeModel, models.ActModel.accident_type_id == models.AccidentTypeModel.id)
            .where(models.AccidentTypeModel.name.ilike("%пешеход%"))
        ).distinct()
        
        result = await session.execute(query)
        return result.scalars().all()


@app.get("/api/analytics/reason-stats", response_model=List[schemas.ReasonStatsResponse], tags=["Analytics"])
async def get_reason_statistics():
    async with database.get_session() as session:
        query = (
            select(
                models.AccidentReasonModel.name.label("reason"),
                func.count(models.ActModel.id).label("count")
            )
            .outerjoin(models.ActModel, models.ActModel.accident_reason_id == models.AccidentReasonModel.id)
            .group_by(models.AccidentReasonModel.id)
            .order_by(func.count(models.ActModel.id).desc())
        )
        
        result = await session.execute(query)
        return result.all()
    
@app.get("/api/additional/firms/", response_model=List[schemas.FirmResposne], tags=["Additional"])
async def get_firms():
    async with database.get_session() as session:
        result = await session.execute(
            select(models.FirmModel)
        )

        return result.scalars().all()
    
@app.get("/api/additional/bodies/", response_model=List[schemas.BodyResponse], tags=["Additional"])
async def get_bodies():
    async with database.get_session() as session:
        result = await session.execute(
            select(models.BodyModel)
        )

        return result.scalars().all()
    
@app.get("/api/additional/accident/types", response_model=List[schemas.AccidentTypeResponse], tags=["Additional"])
async def get_accident_types():
    async with database.get_session() as session:
        result = await session.execute(
            select(models.AccidentTypeModel)
        )

        return result.scalars().all()
    
@app.get("/api/additional/accident/reasons", response_model=List[schemas.AccidentReasonResponse], tags=["Additional"])
async def get_accident_reasons():
    async with database.get_session() as session:
        result = await session.execute(
            select(models.AccidentReasonModel)
        )

        return result.scalars().all()
