from pydantic import BaseModel
from typing import Optional

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    class Config:
        orm_mode = True

class DriverBase(BaseModel):
    full_name: str
    driver_exp: int
    driver_license: str

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    id: int
    class Config:
        orm_mode = True

class CarBase(BaseModel):
    mark: str
    number_plate: str
    firm_id: Optional[int] = None
    body_type_id: Optional[int] = None

class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    id: int
    class Config:
        orm_mode = True