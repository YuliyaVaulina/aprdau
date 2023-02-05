import requests
import json
from tqdm import tqdm
from decimal import Decimal
from tokens import token_tenjin

# Функция для получения данных о количестве пользователей
def DAU(min_users, day_start, day_end):
    url = "https://api.tenjin.com/v2/reports/spend"
    token = f'Bearer {token_tenjin}'
    headers = {'Accept' :'application/json', "Authorization" :token}
    app_ids = ['4f750466-0609-418b-8a0e-a8691e1c6fa1,35722403-4003-4562-887c-f1bed5a1e73c']
    per_page = 1000  # количество записей на кажной странице

    # В парамерты передаем даты начала и окончания периода, импортированные из модуля date.py,
    # токен, импортированный из модуля tokens.py, список app_ids с id приложения (для android и ios).

    params = {'per_page' :per_page,
            'start_date' :str(day_start),
            'end_date' :str(day_end),
            'granularity':'daily',
            'group_by' :'campaign,country',
            'metrics' :'users',
            'app_ids':app_ids}
    response = requests.get(url=url, headers=headers, params=params)

    # Для того, чтобы узнать, какое количество страниц необходимо загрузить, заводим переменную total_pages.
    # Ее значение будет равняться количеству полученных записей (из данных 'meta'),
    # деленного на указанное количество записей на странице (per page)

    total_pages = response.json()['meta']['count'] // per_page + 1
    result= []
    print(f'Зaгрузка данных за период {day_start}-{day_end}:')
    for page in tqdm(range(1, total_pages)):
        params['page'] = page
        r = requests.get(url=url, headers=headers, params=params)
        result += r.json()['data']
    DAU_search = []

    # Циклом сохраняем в список DAU_search списки со страной, наименованием платформы, датой и суммой выручки.
    # Для того, чтобы последующие вычисления были корректными для количества пользователей используем функцию Decimal().

    for data in result:
            DAU_search.append([data['attributes']['country'].upper(),
                        data['attributes']['platform'].lower(),
                        data['attributes']['date'],
                        Decimal(data['attributes']['users'])])

    # Функция возвращает список с данными, которые используются для расчетов в модуле arpdau.py
    return DAU_search


