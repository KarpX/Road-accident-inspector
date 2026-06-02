import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from database import database
from models import BaseModel, UserModel
from auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine_test, 
    expire_on_commit=False
)

database.engine = engine_test
database.sessionmaker = TestingSessionLocal

async def override_session_getter():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[database.session_getter] = override_session_getter

@pytest_asyncio.fixture(autouse=True, scope="module")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        pwd_hash = get_password_hash("admin123")
        admin = UserModel(
            username="TEST-ADMIN",
            fio="Тестовый Админ",
            hashed_password=pwd_hash,
            role="admin"
        )
        session.add(admin)
        await session.commit()

    yield
    
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture
async def inspector_token(async_client: AsyncClient):
    async with TestingSessionLocal() as session:
        pwd_hash = get_password_hash("insp123")
        inspector = UserModel(
            username="TEST-INSP",
            fio="Тестовый Инспектор",
            hashed_password=pwd_hash,
            role="inspector"
        )
        session.add(inspector)
        await session.commit()
        
    response = await async_client.post(
        "/api/auth/login",
        data={"username": "TEST-INSP", "password": "insp123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def admin_token(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/login",
        data={"username": "TEST-ADMIN", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_issue_key_and_register(async_client: AsyncClient, admin_token: dict):
    '''регистрация инспектора по ключу и попытка повтроной регистрации'''
    res_key = await async_client.post(
        "/api/auth/issue-key",
        json={"fio": "Иванов Иван"},
        headers=admin_token
    )
    assert res_key.status_code == 200
    key_value = res_key.json()["key_value"]
    assert key_value.startswith("MVD-")

    res_reg = await async_client.post(
        "/api/auth/register",
        json={"inspector_key": key_value, "password": "inspector_pass"}
    )
    assert res_reg.status_code == 200
    assert "access_token" in res_reg.json()

    res_reg_fail = await async_client.post(
        "/api/auth/register",
        json={"inspector_key": key_value, "password": "new_pass"}
    )
    assert res_reg_fail.status_code == 400
    assert "уже был использован" in res_reg_fail.json()["detail"]


@pytest.mark.asyncio
async def test_crud_driver(async_client: AsyncClient, admin_token: dict):
    '''CRUD операции с водителем'''
    driver_data = {
        "full_name": "Петров Петр",
        "driver_exp": 5,
        "driver_license": "77 00 123456"
    }
    res_unauth = await async_client.post("/api/drivers/", json=driver_data)
    assert res_unauth.status_code == 401

    res_create = await async_client.post("/api/drivers/", json=driver_data, headers=admin_token)
    assert res_create.status_code == 200
    driver_id = res_create.json()["id"]

    res_get = await async_client.get("/api/drivers/", headers=admin_token)
    assert res_get.status_code == 200
    assert len(res_get.json()) > 0
    assert res_get.json()[0]["full_name"] == "Петров Петр"

    res_del = await async_client.delete(f"/api/drivers/{driver_id}", headers=admin_token)
    assert res_del.status_code == 200


@pytest.mark.asyncio
async def test_create_department(async_client: AsyncClient, admin_token: dict):
    """создание отдела ГИБДД"""
    dept_data = {"name": "Тестовый отдел ГИБДД"}
    
    res = await async_client.post("/api/departments/", json=dept_data, headers=admin_token)
    assert res.status_code == 200
    assert res.json()["name"] == "Тестовый отдел ГИБДД"

@pytest.mark.asyncio
async def test_4_login_success(async_client: AsyncClient):
    res = await async_client.post("/api/auth/login", data={"username": "TEST-ADMIN", "password": "admin123"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert res.status_code == 200
    assert "access_token" in res.json()

@pytest.mark.asyncio
async def test_5_login_wrong_password(async_client: AsyncClient):
    res = await async_client.post("/api/auth/login", data={"username": "TEST-ADMIN", "password": "wrong"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_6_auth_me(async_client: AsyncClient, admin_token: dict):
    res = await async_client.get("/api/auth/me", headers=admin_token)
    assert res.status_code == 200
    assert res.json()["role"] == "admin"
    assert res.json()["username"] == "TEST-ADMIN"

@pytest.mark.asyncio
async def test_7_delete_key_as_admin(async_client: AsyncClient, admin_token: dict):
    res_key = await async_client.post("/api/auth/issue-key", json={"fio": "Удаляемый"}, headers=admin_token)
    key_id = res_key.json()["id"]
    res_del = await async_client.delete(f"/api/auth/keys/{key_id}", headers=admin_token)
    assert res_del.status_code == 200

@pytest.mark.asyncio
async def test_8_delete_key_as_inspector_forbidden(async_client: AsyncClient, inspector_token: dict):
    res_del = await async_client.delete("/api/auth/keys/1", headers=inspector_token)
    assert res_del.status_code == 403

@pytest.mark.asyncio
async def test_9_get_departments(async_client: AsyncClient, admin_token: dict):
    res = await async_client.get("/api/departments/", headers=admin_token)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

@pytest.mark.asyncio
async def test_10_get_department_by_id(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/departments/", json={"name": "Отдел 10"}, headers=admin_token)
    dept_id = res_create.json()["id"]
    res_get = await async_client.get(f"/api/departments/{dept_id}", headers=admin_token)
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Отдел 10"

@pytest.mark.asyncio
async def test_11_update_department(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/departments/", json={"name": "Старое имя"}, headers=admin_token)
    dept_id = res_create.json()["id"]
    res_put = await async_client.put(f"/api/departments/{dept_id}", json={"name": "Новое имя"}, headers=admin_token)
    assert res_put.status_code == 200
    assert res_put.json()["name"] == "Новое имя"

@pytest.mark.asyncio
async def test_12_delete_department(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/departments/", json={"name": "Удаляемый отдел"}, headers=admin_token)
    dept_id = res_create.json()["id"]
    res_del = await async_client.delete(f"/api/departments/{dept_id}", headers=admin_token)
    assert res_del.status_code == 200

@pytest.mark.asyncio
async def test_13_get_driver_by_id(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/drivers/", json={"full_name": "Тест 13", "driver_exp": 1, "driver_license": "13"}, headers=admin_token)
    driver_id = res_create.json()["id"]
    res_get = await async_client.get(f"/api/drivers/{driver_id}", headers=admin_token)
    assert res_get.status_code == 200
    assert res_get.json()["full_name"] == "Тест 13"

@pytest.mark.asyncio
async def test_14_update_driver(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/drivers/", json={"full_name": "Старый", "driver_exp": 1, "driver_license": "14"}, headers=admin_token)
    driver_id = res_create.json()["id"]
    res_put = await async_client.put(f"/api/drivers/{driver_id}", json={"full_name": "Новый", "driver_exp": 2, "driver_license": "14"}, headers=admin_token)
    assert res_put.status_code == 200
    assert res_put.json()["full_name"] == "Новый"

@pytest.mark.asyncio
async def test_15_delete_driver_not_found(async_client: AsyncClient, admin_token: dict):
    res = await async_client.delete("/api/drivers/99999", headers=admin_token)
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_16_create_car(async_client: AsyncClient, admin_token: dict):
    car_data = {"mark": "Lada", "number_plate": "А111АА 77"}
    res = await async_client.post("/api/cars/", json=car_data, headers=admin_token)
    assert res.status_code == 200
    assert res.json()["mark"] == "Lada"

@pytest.mark.asyncio
async def test_17_get_cars(async_client: AsyncClient, admin_token: dict):
    res = await async_client.get("/api/cars/", headers=admin_token)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

@pytest.mark.asyncio
async def test_18_get_car_by_id(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/cars/", json={"mark": "BMW", "number_plate": "В222ВВ 77"}, headers=admin_token)
    car_id = res_create.json()["id"]
    res_get = await async_client.get(f"/api/cars/{car_id}", headers=admin_token)
    assert res_get.status_code == 200
    assert res_get.json()["mark"] == "BMW"

@pytest.mark.asyncio
async def test_19_update_car(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/cars/", json={"mark": "Kia", "number_plate": "С333СС 77"}, headers=admin_token)
    car_id = res_create.json()["id"]
    res_put = await async_client.put(f"/api/cars/{car_id}", json={"mark": "Hyundai", "number_plate": "С333СС 77"}, headers=admin_token)
    assert res_put.status_code == 200
    assert res_put.json()["mark"] == "Hyundai"

@pytest.mark.asyncio
async def test_20_delete_car(async_client: AsyncClient, admin_token: dict):
    res_create = await async_client.post("/api/cars/", json={"mark": "Audi", "number_plate": "Е444ЕЕ 77"}, headers=admin_token)
    car_id = res_create.json()["id"]
    res_del = await async_client.delete(f"/api/cars/{car_id}", headers=admin_token)
    assert res_del.status_code == 200

@pytest.mark.asyncio
async def test_21_get_firms(async_client: AsyncClient):
    res = await async_client.get("/api/additional/firms/")
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_22_get_bodies(async_client: AsyncClient):
    res = await async_client.get("/api/additional/bodies/")
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_23_get_accident_types(async_client: AsyncClient):
    res = await async_client.get("/api/additional/accident/types")
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_24_get_accident_reasons(async_client: AsyncClient):
    res = await async_client.get("/api/additional/accident/reasons")
    assert res.status_code == 200

@pytest_asyncio.fixture
async def act_dependencies(async_client: AsyncClient, admin_token: dict):  
    dept = await async_client.post("/api/departments/", json={"name": "Деп"}, headers=admin_token)
    dept_id = dept.json().get("id", 1) 
    
    async with TestingSessionLocal() as session:
        from models import AccidentTypeModel, AccidentReasonModel
        from sqlalchemy import select
        
        res_type = await session.execute(select(AccidentTypeModel).where(AccidentTypeModel.name == "Тестовый тип ДТП"))
        type_obj = res_type.scalar_one_or_none()
        if not type_obj:
            type_obj = AccidentTypeModel(name="Тестовый тип ДТП")
            session.add(type_obj)
            
        res_reason = await session.execute(select(AccidentReasonModel).where(AccidentReasonModel.name == "Тестовая причина"))
        reason_obj = res_reason.scalar_one_or_none()
        if not reason_obj:
            reason_obj = AccidentReasonModel(name="Тестовая причина")
            session.add(reason_obj)
            
        await session.commit()
        
        if type_obj.id is None:
             await session.refresh(type_obj)
        if reason_obj.id is None:
             await session.refresh(reason_obj)

    return {"dept_id": dept_id, "type_id": type_obj.id, "reason_id": reason_obj.id}
@pytest.mark.asyncio
async def test_25_create_act(async_client: AsyncClient, admin_token: dict, act_dependencies: dict):
    act_data = {
        "department_id": act_dependencies["dept_id"],
        "place": "ул. Ленина 10",
        "victims": 2,
        "accident_type_id": act_dependencies["type_id"],
        "accident_reason_id": act_dependencies["reason_id"],
        "date": "2026-05-23T12:00:00Z"
    }
    res = await async_client.post("/api/acts/", json=act_data, headers=admin_token)
    assert res.status_code == 200
    assert res.json()["place"] == "ул. Ленина 10"

@pytest.mark.asyncio
async def test_26_get_acts(async_client: AsyncClient, admin_token: dict):
    res = await async_client.get("/api/acts/", headers=admin_token)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

@pytest.mark.asyncio
async def test_27_get_act_by_id(async_client: AsyncClient, admin_token: dict, act_dependencies: dict):
    act_data = {
        "department_id": act_dependencies["dept_id"],
        "place": "ул. Пушкина 5",
        "victims": 0,
        "accident_type_id": act_dependencies["type_id"],
        "accident_reason_id": act_dependencies["reason_id"],
        "date": "2026-05-23T12:00:00Z"
    }
    res_create = await async_client.post("/api/acts/", json=act_data, headers=admin_token)
    act_id = res_create.json()["id"]
    
    res_get = await async_client.get(f"/api/acts/{act_id}", headers=admin_token)
    assert res_get.status_code == 200
    assert res_get.json()["place"] == "ул. Пушкина 5"

@pytest.mark.asyncio
async def test_28_update_act(async_client: AsyncClient, admin_token: dict, act_dependencies: dict):
    act_data = {
        "department_id": act_dependencies["dept_id"],
        "place": "Старое место",
        "victims": 0,
        "accident_type_id": act_dependencies["type_id"],
        "accident_reason_id": act_dependencies["reason_id"],
        "date": "2026-05-23T12:00:00Z"
    }
    res_create = await async_client.post("/api/acts/", json=act_data, headers=admin_token)
    act_id = res_create.json()["id"]
    
    act_update = act_data.copy()
    act_update["place"] = "Новое место"
    res_put = await async_client.put(f"/api/acts/{act_id}", json=act_update, headers=admin_token)
    assert res_put.status_code == 200
    assert res_put.json()["place"] == "Новое место"

@pytest.mark.asyncio
async def test_29_delete_act(async_client: AsyncClient, admin_token: dict, act_dependencies: dict):
    act_data = {
        "department_id": act_dependencies["dept_id"],
        "place": "Удаляемое место",
        "victims": 0,
        "accident_type_id": act_dependencies["type_id"],
        "accident_reason_id": act_dependencies["reason_id"],
        "date": "2026-05-23T12:00:00Z"
    }
    res_create = await async_client.post("/api/acts/", json=act_data, headers=admin_token)
    act_id = res_create.json()["id"]
    
    res_del = await async_client.delete(f"/api/acts/{act_id}", headers=admin_token)
    assert res_del.status_code == 200

@pytest.mark.asyncio
async def test_30_analytics_endpoints_status(async_client: AsyncClient, admin_token: dict):
    """проверяем, что все аналитические эндпоинты работают"""
    res1 = await async_client.get("/api/analytics/repeat-offenders", headers=admin_token)
    assert res1.status_code == 200
    
    res2 = await async_client.get("/api/analytics/max-victims-acts", headers=admin_token)
    assert res2.status_code == 200
    
    res3 = await async_client.get("/api/analytics/pedestrian-accidents", headers=admin_token)
    assert res3.status_code == 200
    
    res4 = await async_client.get("/api/analytics/reason-stats", headers=admin_token)
    assert res4.status_code == 200