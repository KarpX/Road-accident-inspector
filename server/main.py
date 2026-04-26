from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import List
import secrets

from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import delete, select, func, cast, Date
from sqlalchemy.orm import joinedload
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

@app.post("/api/auth/issue-key", response_model=schemas.KeyResponse, tags=["Auth"])
async def issue_inspector_key(key_data: schemas.KeyCreate, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, 
                detail="Недостаточно прав. Только администратор (начальник) может выдавать ключи."
            )

        random_part = secrets.token_hex(8).upper() 
        current_date = datetime.datetime.now()
        
        generated_key = f"MVD-{current_date.year}-{random_part}"

        new_key = models.InspectorKeyModel(
            key_value=generated_key, 
            fio=key_data.fio
        )
        session.add(new_key)
        await session.commit()
        await session.refresh(new_key)
        
        return new_key

@app.post("/api/auth/register", response_model=schemas.Token, tags=["Auth"])
async def register_user(user: schemas.UserCreate):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.InspectorKeyModel).where(models.InspectorKeyModel.key_value == user.inspector_key)
        )
        db_key = result.scalar_one_or_none()

        if not db_key:
            raise HTTPException(status_code=400, detail="Недействительный ключ")
        if db_key.is_used:
            raise HTTPException(status_code=400, detail="Этот ключ уже был использован для регистрации")

        hashed_password = get_password_hash(user.password)
        new_user = models.UserModel(
            username=db_key.key_value,
            fio=db_key.fio,            
            hashed_password=hashed_password
        )
        session.add(new_user)

        db_key.is_used = True
        await session.commit()
        
        access_token = create_access_token(data={"sub": new_user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
@app.get("/api/auth/me", response_model=schemas.UserResponse, tags=["Auth"])
async def get_current_user_info(current_user: models.UserModel = Depends(get_current_user)):
    return current_user


@app.post("/api/auth/login", response_model=schemas.Token, tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    async with database.get_session() as session:
        result = await session.execute(select(models.UserModel).where(models.UserModel.username == form_data.username))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
@app.delete("/api/auth/keys/{key_id}", tags=["Auth"])
async def delete_inspector_key(key_id: int, current_user: models.UserModel = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Только администратор может удалять ключи")
        
    async with database.get_session() as session:
        result = await session.execute(select(models.InspectorKeyModel).where(models.InspectorKeyModel.id == key_id))
        key = result.scalar_one_or_none()
        if not key:
            raise HTTPException(status_code=404, detail="Ключ не найден")
        
        await session.delete(key)
        await session.commit()
        return {"message": "Ключ успешно удален"}


@app.post("/api/drivers/", response_model=schemas.DriverResponse, tags=["Drivers"])
async def create_driver(driver: schemas.DriverCreate, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        db_driver = models.DriverModel(**driver.model_dump())
        session.add(db_driver)
        await session.commit()
        await session.refresh(db_driver)
        return db_driver
    
@app.get("/api/drivers/", response_model=List[schemas.DriverResponse], tags=["Drivers"])
async def read_drivers(limit: int | None = None, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        query = select(models.DriverModel)
    
        if limit is not None:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()

@app.get("/api/drivers/{driver_id}", response_model=schemas.DriverResponse, tags=["Drivers"])
async def read_driver(driver_id: int, current_user: models.UserModel = Depends(get_current_user)):
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
async def delete_driver(driver_id: int, current_user: models.UserModel = Depends(get_current_user)):
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
    
@app.put("/api/drivers/{driver_id}", response_model=schemas.DriverResponse, tags=["Drivers"])
async def update_driver(
    driver_id: int, 
    driver_update: schemas.DriverCreate, 
    current_user: models.UserModel = Depends(get_current_user)
):
    async with database.get_session() as session:
        result = await session.execute(select(models.DriverModel).where(models.DriverModel.id == driver_id))
        db_driver = result.scalar_one_or_none()
        
        if db_driver is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Водитель не найден")
        
        update_data = driver_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_driver, key, value)
            
        await session.commit()
        await session.refresh(db_driver)
        return db_driver

@app.post("/api/cars/", response_model=schemas.CarResponse, tags=["Cars"])
async def create_car(car: schemas.CarCreate, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        new_car = models.CarModel(**car.model_dump())
        session.add(new_car)
        await session.commit()
        await session.refresh(new_car)
        return new_car
    
@app.get("/api/cars/", response_model=List[schemas.CarResponse], tags=["Cars"])
async def read_cars(limit: int | None = None, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        query = select(models.CarModel)

        if limit is not None:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()
    
@app.get("/api/cars/{car_id}", response_model=schemas.CarResponse, tags=["Cars"])
async def read_car(car_id: int, current_user: models.UserModel = Depends(get_current_user)):
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
async def delete_car(car_id: int, current_user: models.UserModel = Depends(get_current_user)):
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
    
@app.put("/api/cars/{car_id}", response_model=schemas.CarResponse, tags=["Cars"])
async def update_car(
    car_id: int, 
    car_update: schemas.CarCreate, 
    current_user: models.UserModel = Depends(get_current_user)
):
    async with database.get_session() as session:
        result = await session.execute(select(models.CarModel).where(models.CarModel.id == car_id))
        db_car = result.scalar_one_or_none()
        
        if db_car is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Машина не найдена")
        
        update_data = car_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_car, key, value)
            
        await session.commit()
        await session.refresh(db_car)
        return db_car
        
        
@app.post("/api/departments/", response_model=schemas.DepartmentResponse, tags=["Departments"])
async def create_department(department: schemas.DepartmentCreate, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        new_department = models.DepartmentModel(**department.model_dump())
        session.add(new_department)
        await session.commit()
        await session.refresh(new_department)
        return new_department

@app.get("/api/departments/", response_model=List[schemas.DepartmentResponse], tags=["Departments"])
async def get_departments(limit: int | None = None, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        query = select(models.DepartmentModel)

        if limit is not None:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()
    
@app.get("/api/departments/{department_id}", response_model=schemas.DepartmentResponse, tags=["Departments"])
async def get_department(department_id: int, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.DepartmentModel)
            .where(models.DepartmentModel.id == department_id)
        )

        department = result.scalar_one_or_none()

        if department is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Отдел ГИБДД не найден")
        return department
    
@app.delete("/api/departments/{department_id}", response_model=schemas.DepartmentResponse, tags=["Departments"])
async def delete_department(department_id: int, current_user: models.UserModel = Depends(get_current_user)):
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
    
@app.put("/api/departments/{department_id}", response_model=schemas.DepartmentResponse, tags=["Department"])
async def update_department(
    department_id: int, 
    dept_update: schemas.DepartmentCreate, 
    current_user: models.UserModel = Depends(get_current_user)
):
    async with database.get_session() as session:
        result = await session.execute(select(models.DepartmentModel).where(models.DepartmentModel.id == department_id))
        db_dept = result.scalar_one_or_none()
        
        if db_dept is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Отдел ГИБДД не найден")
        
        update_data = dept_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dept, key, value)
            
        await session.commit()
        await session.refresh(db_dept)
        return db_dept
    
@app.post("/api/acts/", response_model=schemas.ActResponse, tags=["Acts"])
async def create_act(act: schemas.ActCreate, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        new_act = models.ActModel(**act.model_dump())
        session.add(new_act)
        await session.commit()
        await session.refresh(new_act)
        return new_act

@app.get("/api/acts/", response_model=List[schemas.ActDetailResponse], tags=["Acts"])
async def read_acts(limit: int | None = None, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        query = (
            select(models.ActModel)
            .options(
                joinedload(models.ActModel.department),
                joinedload(models.ActModel.accident_type),
                joinedload(models.ActModel.accident_reason),
                joinedload(models.ActModel.participants).joinedload(models.AccidentParticipantModel.driver),
                joinedload(models.ActModel.participants).joinedload(models.AccidentParticipantModel.car)
            )
        )
        if limit is not None:
            query = query.limit(limit)
            
        result = await session.execute(query)
        return result.unique().scalars().all()

@app.get("/api/acts/{act_id}", response_model=schemas.ActResponse, tags=["Acts"])
async def read_act(act_id: int, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.ActModel)
            .where(models.ActModel.id == act_id)
            .options(
                joinedload(models.ActModel.department),
                joinedload(models.ActModel.accident_type),
                joinedload(models.ActModel.accident_reason),
                joinedload(models.ActModel.participants).joinedload(models.AccidentParticipantModel.driver),
                joinedload(models.ActModel.participants).joinedload(models.AccidentParticipantModel.car)
            )
        )
        act = result.scalar_one_or_none()
        if act is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Акт не найден")
        return act

@app.delete("/api/acts/{act_id}", response_model=schemas.ActResponse, tags=["Acts"])
async def delete_act(act_id: int, current_user: models.UserModel = Depends(get_current_user)):
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
    
@app.put("/api/acts/{act_id}", response_model=schemas.ActDetailResponse, tags=["Acts"])
async def update_act(
    act_id: int, 
    act_update: schemas.ActCreate, 
    current_user: models.UserModel = Depends(get_current_user)
):
    async with database.get_session() as session:
        result = await session.execute(select(models.ActModel).where(models.ActModel.id == act_id))
        db_act = result.scalar_one_or_none()
        
        if db_act is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Акт не найден")
            
        update_data = act_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_act, key, value)
            
        await session.commit()
        
        fresh_result = await session.execute(
            select(models.ActModel)
            .where(models.ActModel.id == act_id)
            .options(
                joinedload(models.ActModel.department),
                joinedload(models.ActModel.accident_type),
                joinedload(models.ActModel.accident_reason),
                joinedload(models.ActModel.participants).joinedload(models.AccidentParticipantModel.driver),
                joinedload(models.ActModel.participants).joinedload(models.AccidentParticipantModel.car)
            )
        )
        fresh_act = fresh_result.unique().scalar_one()
        
        return fresh_act
    

@app.post("/api/participants/", response_model=schemas.ParticipantResponse, tags=["Participants"])
async def add_participant(participant: schemas.ParticipantCreate, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        new_participant = models.AccidentParticipantModel(**participant.model_dump())
        session.add(new_participant)
        await session.commit()
        await session.refresh(new_participant)
        return new_participant

@app.get("/api/participants/", response_model=List[schemas.ParticipantResponse], tags=["Participants"])
async def get_participants(current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.AccidentParticipantModel)
        )
        
        return result.scalars().all()
    
@app.get("/api/participants/{id}", response_model=schemas.ParticipantResponse, tags=["Participants"])
async def get_participant(id: int, current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        result = await session.execute(
            select(models.AccidentParticipantModel)
            .where(models.AccidentParticipantModel.id == id)
        )

        participant = result.scalar_one_or_none()

        if participant is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Участник ДТП не найден")
        
        return participant
    
@app.delete("/api/participants/by-act/{act_id}", tags=["Participants"])
async def delete_participants_by_act(
    act_id: int, 
    current_user: models.UserModel = Depends(get_current_user)
):
    async with database.get_session() as session:
        await session.execute(
            delete(models.AccidentParticipantModel)
            .where(models.AccidentParticipantModel.act_id == act_id)
        )
        await session.commit()
        return {"message": "Участники успешно удалены"}
    

@app.get("/api/analytics/repeat-offenders", response_model=List[schemas.DriverResponse], tags=["Analytics"])
async def get_repeat_offenders(current_user: models.UserModel = Depends(get_current_user)):
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
async def get_drivers_by_place(place: str, current_user: models.UserModel = Depends(get_current_user)):
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
async def get_drivers_by_date(target_date: datetime.date, current_user: models.UserModel = Depends(get_current_user)):
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
async def get_acts_with_max_victims(current_user: models.UserModel = Depends(get_current_user)):
    async with database.get_session() as session:
        subq = select(func.max(models.ActModel.victims)).scalar_subquery()
        
        query = select(models.ActModel).where(models.ActModel.victims == subq)
        
        result = await session.execute(query)
        return result.scalars().all()


@app.get("/api/analytics/pedestrian-accidents", response_model=List[schemas.DriverResponse], tags=["Analytics"])
async def get_pedestrian_accident_drivers(current_user: models.UserModel = Depends(get_current_user)):
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
async def get_reason_statistics(current_user: models.UserModel = Depends(get_current_user)):
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
