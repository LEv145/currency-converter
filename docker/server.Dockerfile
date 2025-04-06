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
COPY src/currency_converter_server/ /code/currency_converter_server/

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "currency_converter_server.main:app"]
