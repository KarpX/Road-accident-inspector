from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

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
    firm_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    body_type_id: Mapped[int] = mapped_column(Integer, nullable=True)