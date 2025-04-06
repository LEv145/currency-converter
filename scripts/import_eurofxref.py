from os import getenv

import requests


API_URL = getenv("CCS_API_URL", "http://localhost:8000")


resource = requests.post(f"{API_URL}/import_eurofxref")
if resource.ok:
    print("Данные успешно импортированы!")
else:
    print("Произошла ошибка при импорте данных :(")
