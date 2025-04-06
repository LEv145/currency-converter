import pytest

from currency_converter_api.utils.currency import convert_currency


RATES = {
    "EUR": 1.0,
    "USD": 1.1057,
    "JPY": 160.56,
    "BGN": 1.9558,
}


def test_convert_currency():
    assert round(convert_currency(1, "BGN", "BGN", RATES), 5) == 1.0
    assert round(convert_currency(1, "EUR", "USD", RATES), 5) == 1.1057
    assert round(convert_currency(1, "EUR", "JPY", RATES), 5) == 160.56
    assert round(convert_currency(1, "USD", "JPY", RATES), 5) == 145.21118
    assert round(convert_currency(1, "JPY", "BGN", RATES), 5) == 0.01218

    assert round(convert_currency(1_000, "USD", "JPY", RATES)) == 145_211
    assert round(convert_currency(1_000, "EUR", "JPY", RATES)) == 160_560


def test_convert_currency_missing():
    with pytest.raises(ValueError):
        convert_currency(1, "MEOW", "EUR", RATES)

    with pytest.raises(ValueError):
        convert_currency(1, "EUR", "MEOW", RATES)
