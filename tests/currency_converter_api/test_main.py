import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from currency_converter_api.main import app, get_session, Currency


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_read_root():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_create_currency(client: TestClient):
    response = client.post("/currencies/", json={"name": "MEOW", "rate": 4.2})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "MEOW"
    assert data["rate"] == 4.2
    assert data["id"] == 1


def test_read_currencies(session: Session, client: TestClient):
    currency_1 = Currency(name="EUR", rate=1.0)
    currency_2 = Currency(name="USD", rate=1.1)
    session.add(currency_1)
    session.add(currency_2)
    session.commit()

    response = client.get("/currencies/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == currency_1.name
    assert data[0]["rate"] == currency_1.rate
    assert data[0]["id"] == currency_1.id
    assert data[1]["name"] == currency_2.name
    assert data[1]["rate"] == currency_2.rate
    assert data[1]["id"] == currency_2.id


def test_read_currency(session: Session, client: TestClient):
    currency = Currency(name="USD", rate=1.1)
    session.add(currency)
    session.commit()

    response = client.get(f"/currencies/{currency.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == currency.name
    assert data["rate"] == currency.rate
    assert data["id"] == currency.id


def test_read_currency_not_found(session: Session, client: TestClient):
    response = client.get(f"/currencies/1")
    assert response.status_code == 404


def test_update_currency(session: Session, client: TestClient):
    currency = Currency(name="USD", rate=1.1)
    session.add(currency)
    session.commit()

    response = client.patch(f"/currencies/{currency.id}", json={"rate": 1.2})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == currency.name
    assert data["rate"] == 1.2
    assert data["id"] == currency.id


def test_update_currency_not_found(session: Session, client: TestClient):
    response = client.patch(f"/currencies/1", json={"rate": 1.2})
    assert response.status_code == 404


def test_delete_currency(session: Session, client: TestClient):
    currency = Currency(name="USD", rate=1.1)
    session.add(currency)
    session.commit()

    response = client.delete(f"/currencies/{currency.id}")

    currency_in_db = session.get(Currency, currency.id)

    assert response.status_code == 200
    assert currency_in_db is None


def test_delete_currency_not_found(session: Session, client: TestClient):
    response = client.delete(f"/currencies/1")
    assert response.status_code == 404


def test_import_eurofxref(session: Session, client: TestClient):
    response = client.post(f"/import_eurofxref")
    currency_in_db = session.get(Currency, 1)

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert currency_in_db is not None


def test_convert(session: Session, client: TestClient):
    currency_1 = Currency(name="EUR", rate=1.0)
    currency_2 = Currency(name="USD", rate=1.1)
    session.add(currency_1)
    session.add(currency_2)
    session.commit()

    response = client.post(f"/convert", params={"amount": 2.5, "from_currency": "EUR", "to_currency": "USD"})

    assert response.status_code == 200
    assert response.json() == 2.75
