# Конвертер валют

За основу взяты котировки с сайта [ecb.europa](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml)

## Что сделано

1. Написан консольная команда для импорта данных из [ecb.europa](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml):
[import_eurofxref](scripts/import_eurofxref.py)
2. Создано API для получения списка импортированных котировок, для их удаления и редактирования: 
[currency_converter_api](src/currency_converter_api)
3. API так же поддерживает конвертацию валют из одной любой в другую
4. Реализован калькулятор в виде отдельного WEB сервера для конвертации одной валюты в другую через API: [currency_converter_server](src/currency_converter_server)

## Достоинства

1. Проект докерезирован, смотри: [docker](docker)
2. Проект полностью покрыт тестами, смотри: [tests](tests) и результаты утилиты `coverage`
3. Сборка и тесты запускаются одной командой (Через `pytest` и `poetry`)
