FROM python:3.12

# POETRY SETUP
ENV \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR="/var/cache/pypoetry" \
  POETRY_HOME="/usr/local" \
  POETRY_VERSION=2.1.2

RUN curl -sSL https://install.python-poetry.org | python3 -


WORKDIR /code/
COPY poetry.lock pyproject.toml /code/
RUN poetry install --only=main --no-interaction --no-ansi
COPY src/currency_converter_api/ /code/currency_converter_api/

EXPOSE 80
CMD ["uvicorn", "currency_converter_api.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
