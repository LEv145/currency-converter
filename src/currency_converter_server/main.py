from os import getenv

from flask import Flask, render_template, request
import requests


API_URL = getenv("CCS_API_URL", "http://localhost:8000")
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    converted_amount = None
    error = None

    if request.method == "POST":
        amount = request.form["amount"]
        from_currency = request.form["from_currency"].upper()
        to_currency = request.form["to_currency"].upper()

        try:
            response = requests.post(
                f"{API_URL}/convert",
                params={
                    "amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency
                }
            )

            if response.status_code == 200:
                converted_amount = response.json()
            else:
                error = f"Ошибка при запросе: {response.text}"
        except Exception as e:
            error = f"Ошибка соединения: {e}"

    return render_template("index.html", converted_amount=converted_amount, error=error)


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, port=5000)
