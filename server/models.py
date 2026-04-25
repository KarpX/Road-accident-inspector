from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import BaseModel


class DepartmentModel(BaseModel):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

class DriverModel(BaseModel):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    driver_exp: Mapped[int] = mapped_column(Integer, nullable=False)
    driver_license: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

class CarModel(BaseModel):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    mark: Mapped[str] = mapped_column(String(255), nullable=False)
    number_plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=True)
    body_type_id: Mapped[int] = mapped_column(ForeignKey("bodies.id"), nullable=True)

class FirmModel(BaseModel):
    __tablename__ = "firms"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

class BodyModel(BaseModel):
    __tablename__ = "bodies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

class AccidentTypeModel(BaseModel):
    __tablename__ = "accident_types"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

class AccidentReasonModel(BaseModel):
    __tablename__ = "accident_reasons"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

class ActModel(BaseModel):
    __tablename__ = "acts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    place: Mapped[str] = mapped_column(String(500), nullable=False)
    victims: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accident_type_id: Mapped[int] = mapped_column(ForeignKey("accident_types.id"), nullable=False)
    accident_reason_id: Mapped[int] = mapped_column(ForeignKey("accident_reasons.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    department: Mapped["DepartmentModel"] = relationship()
    accident_type: Mapped["AccidentTypeModel"] = relationship()
    accident_reason: Mapped["AccidentReasonModel"] = relationship()
    
    participants: Mapped[list["AccidentParticipantModel"]] = relationship(back_populates="act", lazy="selectin")

class AccidentParticipantModel(BaseModel):
    __tablename__ = "accident_participants"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id", ondelete="CASCADE"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)

    act: Mapped["ActModel"] = relationship(back_populates="participants")
    driver: Mapped["DriverModel"] = relationship()
    car: Mapped["CarModel"] = relationship()


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False) 
    fio: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="inspector")

class InspectorKeyModel(BaseModel):
    __tablename__ = "inspector_keys"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key_value: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False) # Тот самый токен
    fio: Mapped[str] = mapped_column(String(255), nullable=False) # ФИО работника
    is_used: Mapped[bool] = mapped_column(Boolean, default=False) # Использован ли ключ?