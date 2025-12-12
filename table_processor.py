"""
Скрипт для преобразования таблицы из широкого формата (wide) в плоский (flat).

Входные данные: Excel файл со структурой:
- Заголовок 1: Магазин 1, Магазин 2, ..., Магазин 20
- Заголовок 2: Число чеков, Количество в чеке, Сумма в чеке, Наценка продажи в чеке (для каждого магазина)
- Данные: Год → Месяц → Товар + Тип → значения по магазинам

Выходные данные: Плоская таблица с колонками:
Год, Месяц, Товар, Тип, Магазин, Число чеков, Количество в чеке, Сумма в чеке, Наценка продажи в чеке
"""

import pandas as pd
import numpy as np
from pathlib import Path


def read_wide_table(file_path: str, sheet_name: str = 0) -> pd.DataFrame:
    """
    Читает таблицу с мультиуровневыми заголовками.

    Args:
        file_path: путь к Excel файлу
        sheet_name: название или индекс листа

    Returns:
        DataFrame с исходными данными
    """
    # Читаем БЕЗ заголовков, обработаем вручную
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    return df


def parse_headers(df: pd.DataFrame) -> dict:
    """
    Парсит заголовки из первых двух строк.

    Строка 0: [пусто] [пусто] [Магазин 1] [пусто] [пусто] [пусто] [Магазин 2] ...
    Строка 1: [Название строк] [Тип] [Число чеков] [Количество] [Сумма] [Наценка] [Число чеков] ...

    Returns:
        dict с mapping: {col_index: (store_name, metric_name)}
    """
    row_stores = df.iloc[0]  # Первая строка - магазины
    row_metrics = df.iloc[1]  # Вторая строка - метрики

    # Создаем mapping: индекс колонки -> (магазин, метрика)
    column_mapping = {}
    current_store = None

    # Пропускаем первые 2 колонки (Название строк, Тип)
    for col_idx in range(2, len(df.columns)):
        # Проверяем магазин
        store_val = row_stores.iloc[col_idx]
        if not pd.isna(store_val) and str(store_val).strip():
            current_store = str(store_val).strip()

        # Получаем метрику
        metric_val = row_metrics.iloc[col_idx]
        if not pd.isna(metric_val):
            metric_name = str(metric_val).strip()
            column_mapping[col_idx] = (current_store, metric_name)

    return column_mapping


def transform_to_flat(df: pd.DataFrame, input_file: str) -> pd.DataFrame:
    """
    Преобразует широкую таблицу в плоскую.

    Args:
        df: исходная таблица
        input_file: путь к входному файлу (для логирования)

    Returns:
        Плоская таблица
    """
    print(f"📊 Обработка файла: {input_file}")
    print(f"   Размер исходной таблицы: {df.shape}")

    # Парсим заголовки (первые 2 строки)
    column_mapping = parse_headers(df)

    # Получаем уникальные магазины и метрики
    stores = sorted(set(store for store, _ in column_mapping.values()))
    metrics = sorted(set(metric for _, metric in column_mapping.values()))

    print(f"   Найдено магазинов: {len(stores)}")
    print(f"   Магазины: {stores[:3]}...") if len(stores) > 3 else print(f"   Магазины: {stores}")
    print(f"   Найдено метрик: {len(metrics)}")
    print(f"   Метрики: {metrics}")

    # Список для накопления результатов
    result_rows = []

    # Текущий год и месяц (для парсинга иерархии)
    current_year = None
    current_month = None

    # Начинаем обработку с 3-й строки (индекс 2), первые 2 - заголовки
    for row_idx in range(2, len(df)):
        # Первая колонка (индекс 0) - Название строки (Год/Месяц/Товар)
        # Вторая колонка (индекс 1) - Тип товара
        col_name = df.iloc[row_idx, 0]
        col_type = df.iloc[row_idx, 1]

        # Пропускаем пустые строки
        if pd.isna(col_name):
            continue

        name_str = str(col_name).strip()

        # Проверяем, это год?
        if name_str.isdigit() and len(name_str) == 4:
            current_year = int(name_str)
            current_month = None
            continue

        # Проверяем, это месяц?
        months_ru = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        if name_str in months_ru:
            current_month = name_str
            continue

        # Иначе это товар
        tovar = name_str
        tip = str(col_type).strip() if not pd.isna(col_type) else ""

        # Проверяем, что год и месяц определены
        if current_year is None or current_month is None:
            continue

        # Группируем данные по магазинам
        store_data = {}
        for col_idx, (store, metric) in column_mapping.items():
            value = df.iloc[row_idx, col_idx]
            value = value if not pd.isna(value) else 0

            if store not in store_data:
                store_data[store] = {}
            store_data[store][metric] = value

        # Создаём записи для каждого магазина
        for store, metrics_dict in store_data.items():
            row_data = {
                'Год': current_year,
                'Месяц': current_month,
                'Товар': tovar,
                'Тип': tip,
                'Магазин': store
            }
            row_data.update(metrics_dict)
            result_rows.append(row_data)

    # Создаём итоговый DataFrame
    df_flat = pd.DataFrame(result_rows)

    print(f"✅ Преобразование завершено!")
    print(f"   Размер плоской таблицы: {df_flat.shape}")
    if not df_flat.empty:
        print(f"   Колонки: {list(df_flat.columns)}")

    return df_flat


def validate_flat_table(df: pd.DataFrame) -> bool:
    """
    Валидация плоской таблицы.

    Args:
        df: плоская таблица

    Returns:
        True если валидация прошла успешно
    """
    required_columns = [
        'Год', 'Месяц', 'Товар', 'Тип', 'Магазин',
        'Число чеков', 'Количество в чеке', 'Сумма в чеке', 'Наценка продажи в чеке'
    ]

    # Проверяем наличие всех колонок
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"❌ Отсутствуют колонки: {missing_cols}")
        return False

    # Проверяем наличие данных
    if df.empty:
        print("❌ Таблица пустая!")
        return False

    # Проверяем наличие NaN в критичных колонках
    critical_cols = ['Год', 'Месяц', 'Товар', 'Тип', 'Магазин']
    for col in critical_cols:
        if df[col].isna().any():
            print(f"❌ Найдены пустые значения в колонке: {col}")
            return False

    # Статистика
    print("\n📊 Статистика плоской таблицы:")
    print(f"   Строк: {len(df):,}")
    print(f"   Уникальных годов: {df['Год'].nunique()}")
    print(f"   Уникальных месяцев: {df['Месяц'].nunique()}")
    print(f"   Уникальных товаров: {df['Товар'].nunique()}")
    print(f"   Уникальных магазинов: {df['Магазин'].nunique()}")

    return True


def process_file(input_file: str, output_file: str, sheet_name: str = 0) -> bool:
    """
    Основная функция обработки файла.

    Args:
        input_file: путь к входному Excel файлу
        output_file: путь к выходному Excel файлу
        sheet_name: название или индекс листа

    Returns:
        True если обработка прошла успешно
    """
    try:
        # Проверяем существование входного файла
        if not Path(input_file).exists():
            print(f"❌ Файл не найден: {input_file}")
            return False

        print(f"\n{'='*80}")
        print("🔄 ПРЕОБРАЗОВАНИЕ ТАБЛИЦЫ: WIDE → FLAT")
        print(f"{'='*80}\n")

        # Читаем файл
        df_wide = read_wide_table(input_file, sheet_name)

        # Преобразуем в плоский формат
        df_flat = transform_to_flat(df_wide, input_file)

        # Валидируем результат
        if not validate_flat_table(df_flat):
            print("❌ Валидация не прошла!")
            return False

        # Сохраняем результат
        print(f"\n💾 Сохранение результата в: {output_file}")
        df_flat.to_excel(output_file, index=False)
        print("✅ Файл успешно сохранён!")

        # Выводим превью
        print("\n📋 Превью первых 10 строк:")
        print(df_flat.head(10).to_string())

        return True

    except Exception as e:
        print(f"❌ Ошибка при обработке: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Параметры по умолчанию
    INPUT_FILE = "raw_data.xlsx"  # Исходный файл в широком формате
    OUTPUT_FILE = "final_flat_clean.xlsx"  # Результат в плоском формате
    SHEET_NAME = 0  # Первый лист

    # Запускаем обработку
    success = process_file(INPUT_FILE, OUTPUT_FILE, SHEET_NAME)

    if success:
        print(f"\n{'='*80}")
        print("✅ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print("❌ ОБРАБОТКА ЗАВЕРШИЛАСЬ С ОШИБКАМИ")
        print(f"{'='*80}\n")
