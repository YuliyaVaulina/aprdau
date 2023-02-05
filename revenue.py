import requests
from decimal import Decimal
from tokens import REPORTKEY

#Функция для получения данных из Applovin Max
def revenue(day_start, day_end):
    url = 'https://r.applovin.com/maxReport'

    # В парамерты передаем даты начала и окончания периода, импортированные из модуля date.py,
    # токен, импортированный из модуля tokens.py, имя пакета
    # и наименование платформы (сначала собираем ios, во втором цикле android).

    params = {'start' :str(day_start),
              'end' :str(day_end),
              'api_key' :REPORTKEY,
              'format': 'json',
              'columns' :'day,country,estimated_revenue',
              'filter_package_name' :'com.herocraft.game.cut.arcade.catchthecandy',
              'filter_platform' :'ios',
              'limit' :1000}

    # Создаем пустой список для сохранения данных о выручке
    response = []
    revenue = []
    response += requests.get(url=url, params=params).json()['results']

    # Циклом сохраняем в список revenue списки со строной, наименованием платформы, датой и суммой выручки.
    # Для того, чтобы последующие вычисления были корректными для суммы выручки используем функцию Decimal().

    for data in response:
       revenue.append([data['country'].upper(),
                       'ios',
                       data['day'],
                       Decimal(data['estimated_revenue'])])

    params = {'start' :str(day_start),
              'end' :str(day_end),
              'api_key' :REPORTKEY,
              'format': 'json',
              'columns' :'day,country,estimated_revenue',
              'filter_package_name' :'com.herocraft.game.cut.arcade.catchthecandy',
              'filter_platform' :'android',
              'limit' :1000}
    response = []
    response += requests.get(url=url, params=params).json()['results']
    for data in response:
       revenue.append([data['country'].upper(),
                       'android',
                       data['day'],
                       Decimal(data['estimated_revenue'])])

    # Функция возвращает список с данными, которые используются для расчетов в модуле arpdau.py
    return revenue

