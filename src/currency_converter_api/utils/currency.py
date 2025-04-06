def convert_currency(amount: float, from_currency: str, to_currency: str, rates: dict[str, float]) -> float:
    if from_currency not in rates:
        raise ValueError(f"The currency {from_currency} is missing from the list of exchange rates.")
    if to_currency not in rates:
        raise ValueError(f"The currency {to_currency} is missing from the list of exchange rates.")

    conversion_rate = rates[to_currency] / rates[from_currency]
    return amount * conversion_rate
