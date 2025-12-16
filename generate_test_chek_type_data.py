import pandas as pd
import numpy as np


def generate_test_chek_type_data(output_file='final_flat_clean_chek_type_flat.xlsx'):
    """
    Генерирует тестовые данные в формате final_flat_clean_chek_type
    20 магазинов, типы: сп, непрод, скоропорт, товар, всего
    """

    # Типы чеков
    types = ['Непрод', 'Скоропорт', 'Товар', 'Всего']

    # Годы и месяцы
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
              'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']

    # 20 магазинов
    stores = [f'Магазин {i}' for i in range(1, 21)]

    # Строим DataFrame
    rows = []

    # Заголовок: пустой Тип, пустой Период, названия магазинов
    header = ['Тип', 'год месяц'] + stores
    rows.append(header)

    np.random.seed(42)  # Для воспроизводимости

    for typ in types:
        for year in years:
            # Строка года (пустые значения для магазинов)
            year_row = [typ, str(year)] + ['' for _ in stores]
            rows.append(year_row)

            for month in months:
                # Генерируем случайные данные для каждого магазина
                if typ == 'всего':
                    # "всего" - сумма остальных типов (примерно)
                    base = np.random.randint(300, 600, size=len(stores))
                elif typ == 'сп':
                    base = np.random.randint(100, 200, size=len(stores))
                elif typ == 'непрод':
                    base = np.random.randint(50, 120, size=len(stores))
                elif typ == 'скоропорт':
                    base = np.random.randint(80, 150, size=len(stores))
                else:  # товар
                    base = np.random.randint(70, 140, size=len(stores))

                month_row = [typ, month] + base.tolist()
                rows.append(month_row)

    # Создаём DataFrame без заголовков (как в исходном файле)
    df = pd.DataFrame(rows[1:], columns=rows[0])

    # Сохраняем в Excel
    df.to_excel(output_file, index=False)
    print(f"Создан файл: {output_file}")
    print(f"Строк: {len(df)}, Колонок: {len(df.columns)}")

    return df


# Запуск
if __name__ == '__main__':
    df = generate_test_chek_type_data()
    print("\nПервые 15 строк:")
    print(df.head(15).to_string())
