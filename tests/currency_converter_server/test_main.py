import pytest
import requests
from flask import Flask
from flask.testing import FlaskClient
from requests_mock.mocker import Mocker as RequestsMocker

from currency_converter_server.main import app as main_app


@pytest.fixture(name="app")
def app_fixture():
    main_app.config.update({
        "TESTING": True,
    })
    yield main_app


@pytest.fixture(name="client")
def client_fixture(app: Flask):
    return app.test_client()


@pytest.fixture(name="runner")
def runner_fixture(app: Flask):  # pragma: no cover
    return app.test_cli_runner()


def test_convert_form(client: FlaskClient, requests_mock: RequestsMocker):
    data = {"amount": 1, "from_currency": "EUR", "to_currency": "USD"}

    requests_mock.post("http://localhost:8000/convert", json=1_000)
    response = client.post("/", data=data)
    assert response.status_code == 200

    requests_mock.post("http://localhost:8000/convert", status_code=500)
    response = client.post("/", data=data)
    assert response.status_code == 200

    requests_mock.post("http://localhost:8000/convert", exc=requests.exceptions.ConnectTimeout)
    response = client.post("/", data=data)
    assert response.status_code == 200


def test_convert_request(client: FlaskClient):
    response = client.get("/")
    assert (
        b'<h2 class="text-2xl font-semibold text-center mb-4">\xf0\x9f\x92\xb1 Currency Converter</h2>'
        in response.data
    )
