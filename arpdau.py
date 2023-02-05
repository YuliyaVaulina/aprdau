import pandas as pd
import datetime
from datetime import timedelta
import requests
from revenue import revenue
from dau import DAU

try:
    week_search_end = datetime.date(2023, 1, 15)           #Датa окончания первой недели
    week_etalon_end = datetime.date(2023, 1, 31)           #Дата окончания второй недели
    minimal_users = 10                                      #Mинимальное число пользователей в день

    #Для расчета даты начала первой и второй недели заведена переменная delta, равная 7
    delta = timedelta(7)
    week_search_start = week_search_end - delta
    week_etalon_start = week_etalon_end - delta

    # Задаем названия колонок для будущих dataframe
    colums_DAU = ['country',
                  'platform',
                  'date',
                  'users']
    colums_revenue = ['country',
                      'platform',
                      'date',
                      'estimated_revenue']
    pd.options.mode.chained_assignment = None

    # Создаем таблицу с данными о количестве пользователей, обращаясь к функции DAU.
    # Oбъединяем строки с одинаковыми странами, платформами и датой, суммирая количество пользователей.
    # Отфильтровываем страны с количеством пользователей меньше заданного в модуле date.py minimal_users

    df_search = pd.DataFrame(DAU(minimal_users, week_search_start, week_search_end), index=None, columns=colums_DAU)
    df_DAU_search = df_search.groupby(['country', 'platform', 'date'])[['users']].sum().reset_index()
    df_DAU_search_min = df_DAU_search.query('users > @minimal_users')

    df_etalon = pd.DataFrame(DAU(minimal_users, week_etalon_start, week_etalon_end), index=None, columns=colums_DAU)
    df_DAU_etalon = df_etalon.groupby(['country', 'platform', 'date'])[['users']].sum().reset_index()
    df_DAU_etalon_min = df_DAU_etalon.query('users > @minimal_users')

    # Создаем таблицу с данными о выручке, обращаясь к функции revenue.
    # Oбъединяем 2 таблицы и далее убираем строки, в которых после объединения в колонках
    # users или estimated_revenue нет значений.
    # Добавляем в таблицу столбец ARPDAU с расчетом

    df_revenue_search = pd.DataFrame(revenue(week_search_start, week_search_end), index=None, columns=colums_revenue)
    df_revenue_search_gr = df_revenue_search.groupby(['country', 'platform', 'date'])[
                                                        ['estimated_revenue']].sum().reset_index()
    pivot_search = df_DAU_search_min.merge(df_revenue_search_gr, on = ['country', 'platform', 'date'])
    pivot_search_min = pivot_search.query('users >0 & estimated_revenue >0')
    pivot_search_min['ARPDAU'] = pivot_search['estimated_revenue'] / pivot_search['users']

    df_revenue_etalon = pd.DataFrame(revenue(week_etalon_start, week_etalon_end), index=None, columns=colums_revenue)
    df_revenue_etalon_gr = df_revenue_etalon.groupby(['country', 'platform', 'date'])[
                                                        ['estimated_revenue']].sum().reset_index()
    pivot_etalon = df_DAU_etalon.merge(df_revenue_etalon_gr, on = ['country', 'platform', 'date'])
    pivot_etalon_min = pivot_etalon.query('users >0 & estimated_revenue >0')
    pivot_etalon_min['ARPDAU_etalon'] = pivot_etalon_min['estimated_revenue'] / pivot_etalon['users']

    # Создаем таблицы для разных платформ.
    # Объединяем строки в таблицах по странам с подсчетом среднего в колонке ARPDAU/ARPDAU_etalon

    res_ios_search = pivot_search_min.query('platform == "ios"')
    result_ios_search = res_ios_search.groupby('country')['ARPDAU'].mean()
    res_android_search = pivot_search_min.query('platform == "android"')
    result_android_search = res_android_search.groupby('country')['ARPDAU'].mean()

    res_ios_etalon = pivot_etalon_min.query('platform == "ios"')
    result_ios_etalon = res_ios_etalon.groupby('country')['ARPDAU_etalon'].mean()
    res_android_etalon = pivot_etalon_min.query('platform == "android"')
    result_android_etalon = res_android_etalon.groupby('country')['ARPDAU_etalon'].mean()

    # Объединяем значения 1й недели с данными 2й недели отдельно по каждой платформе
    # Добавляем колонку Delta ARPDAU, % с расчетом изменения средней выручки:
    # (ARPDAU 1й недели - ARPDAU эталонной недели) *100 / ARPDAU эталонной недели

    ios_searching = result_ios_search.to_frame().merge(result_ios_etalon, on = ['country'])
    ios_searching['Delta ARPDAU, %'] = (ios_searching['ARPDAU'] -
                                        ios_searching['ARPDAU_etalon']) * 100/ios_searching['ARPDAU_etalon']
    android_searching = result_android_search.to_frame().merge(result_android_etalon, on = ['country'])
    android_searching['Delta ARPDAU, %'] = (android_searching['ARPDAU'] -
                                        android_searching['ARPDAU_etalon']) * 100/android_searching['ARPDAU_etalon']

    print(ios_searching)
    print(android_searching)

    # Записываем данные в файл arpdau.xlsx на листы iOS и Android
    writer = pd.ExcelWriter('arpdau.xlsx', engine='xlsxwriter')
    ios_searching.to_excel(writer, sheet_name='iOS')
    android_searching.to_excel(writer, sheet_name='Android')
    writer.close()

except pd.errors.UndefinedVariableError:
    print('Нет данных за один из периодов')
except ValueError:
    print('Проверьте корректность ввода даты')
except requests.exceptions.JSONDecodeError:
    print('Нет данных за один из периодов')