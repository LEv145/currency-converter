from sqlmodel import Field, SQLModel


class CurrencyBase(SQLModel):
    name: str
    rate: float


class Currency(CurrencyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CurrencyPublic(CurrencyBase):
    id: int


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(CurrencyBase):
    name: str | None = None
    rate: float | None = None
