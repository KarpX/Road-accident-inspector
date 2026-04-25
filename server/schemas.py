from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    class Config:
        from_attributes = True

class DriverBase(BaseModel):
    full_name: str
    driver_exp: int
    driver_license: str

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    id: int
    class Config:
        from_attributes = True

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
        from_attributes = True

class ActBase(BaseModel):
    department_id: int
    place: str
    victims: int
    accident_type_id: int
    accident_reason_id: int
    date: datetime

class ActCreate(ActBase):
    pass

class ActResponse(ActBase):
    id: int
    class Config:
        from_attributes = True

class ParticipantBase(BaseModel):
    act_id: int
    driver_id: int
    car_id: int

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantResponse(ParticipantBase):
    id: int
    class Config:
        from_attributes = True

class DictionaryBase(BaseModel):
    name: str

class DictionaryResponse(DictionaryBase):
    id: int
    class Config:
        from_attributes = True

class ReasonStatsResponse(BaseModel):
    reason: str
    count: int

    class Config:
        from_attributes = True

class FirmBase(BaseModel):
    name: str

class FirmResposne(FirmBase):
    id: int
    class Config:
        from_attributes = True

class BodyBase(BaseModel):
    name: str

class BodyResponse(BodyBase):
    id: int
    class Config:
        from_attributes = True

class AccidentTypeBase(BaseModel):
    name: str

class AccidentTypeResponse(AccidentTypeBase):
    id: int
    class Config:
        from_attributes = True
    
class AccidentReasonBase(BaseModel):
    name: str

class AccidentReasonResponse(AccidentReasonBase):
    id: int
    class Config:
        from_attributes = True

class ParticipantDetailResponse(BaseModel):
    id: int
    driver: DriverResponse
    car: CarResponse
    class Config:
        from_attributes = True

class ActDetailResponse(BaseModel):
    id: int
    place: str
    victims: int
    date: datetime
    department: DepartmentResponse
    accident_type: DictionaryResponse
    accident_reason: DictionaryResponse
    participants: List[ParticipantDetailResponse]
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    inspector_key: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class KeyCreate(BaseModel):
    fio: str

class KeyResponse(KeyCreate):
    id: int
    key_value: str
    is_used: bool
    class Config:
        from_attributes = True