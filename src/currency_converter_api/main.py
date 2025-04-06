from os import getenv
from typing import Annotated
from contextlib import asynccontextmanager

import requests
import xmltodict
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from currency_converter_api.tables import Currency, CurrencyPublic, CurrencyCreate, CurrencyUpdate
from currency_converter_api.utils.currency import convert_currency


EUROFXREF_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
DATABASE_URL = getenv("CCA_DATABASE_URL", "sqlite:///database.db")


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    SQLModel.metadata.create_all(engine)
    yield


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session


app = FastAPI(lifespan=lifespan)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/currencies/", response_model=CurrencyPublic)
def create_currency(currency: CurrencyCreate, session: SessionDep) -> Currency:
    db_currency = Currency.model_validate(currency)
    session.add(db_currency)
    session.commit()
    session.refresh(db_currency)
    return db_currency


@app.get("/currencies/", response_model=list[CurrencyPublic])
def read_currencies(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    currencies = session.exec(select(Currency).offset(offset).limit(limit)).all()
    return currencies


@app.get("/currencies/{currency_id}", response_model=CurrencyPublic)
def read_currency(currency_id: int, session: SessionDep):
    currency = session.get(Currency, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency


@app.patch("/currencies/{currency_id}", response_model=CurrencyPublic)
def update_currency(currency_id: int, currency: CurrencyUpdate, session: SessionDep):
    currency_db = session.get(Currency, currency_id)
    if not currency_db:
        raise HTTPException(status_code=404, detail="Currency not found")
    currency_data = currency.model_dump(exclude_unset=True)
    currency_db.sqlmodel_update(currency_data)
    session.add(currency_db)
    session.commit()
    session.refresh(currency_db)
    return currency_db


@app.delete("/currencies/{currency_id}")
def delete_currency(currency_id: int, session: SessionDep):
    currency = session.get(Currency, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    session.delete(currency)
    session.commit()
    return {"ok": True}


@app.post("/import_eurofxref")
def read_import_eurofxref(session: SessionDep) -> dict[str, bool]:
    response = requests.get(EUROFXREF_URL)
    raw_currencies = xmltodict.parse(response.text)["gesmes:Envelope"]["Cube"]["Cube"]["Cube"]

    session.add(Currency(name="EUR", rate=1.0))
    for raw_currency in raw_currencies:
        currency = Currency(name=raw_currency["@currency"], rate=float(raw_currency["@rate"]))
        session.add(currency)

    session.commit()

    return {"ok": True}


@app.post("/convert")
def convert(amount: float, from_currency: str, to_currency: str, session: SessionDep) -> float:
    currencies = session.exec(select(Currency)).all()
    rates = {currency.name: currency.rate for currency in currencies}

    result = convert_currency(amount, from_currency=from_currency, to_currency=to_currency, rates=rates)

    return result
