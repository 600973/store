# PROJECT_ROOT: engine/data_processor.py
import pandas as pd
import numpy as np


def create_date_column(df, year_col='Год', month_col='Месяц', date_col=None):
    """
    Create formatted Дата column from year+month OR existing date column

    Args:
        df: DataFrame
        year_col: Year column name (default 'Год')
        month_col: Month column name (default 'Месяц')
        date_col: Optional single date column name

    Returns:
        DataFrame with Дата column in format DD.MM.YYYY or 01.MM.YYYY
    """
    MONTH_MAP = {
        'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4,
        'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
        'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12
    }

    if date_col and date_col in df.columns:
        # Single date column scenario
        df['Дата'] = pd.to_datetime(df[date_col]).dt.strftime('%d.%m.%Y')
    elif year_col in df.columns and month_col in df.columns:
        # Year + Month scenario
        df['Месяц_num'] = df[month_col].map(MONTH_MAP)
        # Создаем временный DataFrame с нужными названиями столбцов для pd.to_datetime
        date_df = pd.DataFrame({
            'year': df[year_col],
            'month': df['Месяц_num'],
            'day': 1
        })
        df['Дата'] = pd.to_datetime(date_df).dt.strftime('01.%m.%Y')
        df.drop('Месяц_num', axis=1, inplace=True)

    return df


def load_sales_data(file_path='final_flat_clean.xlsx', column_mapping=None):
    """
    Загружает данные из Excel как есть.

    Args:
        file_path: путь к файлу
        column_mapping: dict для переименования колонок, например:
                       {'Сумма в чеках продажи': 'Выручка'}
    """
    df = pd.read_excel(file_path)

    # Применяем маппинг колонок если задан
    if column_mapping:
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df[new_name] = df[old_name]

    # Создаем форматированный столбец Дата (если есть Год и Месяц)
    df = create_date_column(df)

    return df


def get_unique_values(df: pd.DataFrame, column: str) -> list:
    """Get unique values from column, sorted"""
    if column not in df.columns:
        return []
    values = df[column].dropna().unique().tolist()
    return sorted(values, key=str)


def merge_store_area(df, area_file_path='store.xlsx'):
    df_area = pd.read_excel(area_file_path)
    df_merged = df.merge(df_area, on='Магазин', how='left')
    return df_merged


def load_checks_by_type(file_path='final_flat_clean_chek_type.xlsx'):
    """
    Загружает данные о количестве чеков по типам.

    Ожидаемая структура (long-формат):
    | Тип   | Год  | Месяц   | Магазин  | Чеки_по_типу |

    Типы: сп, непрод, скоропорт, товар, всего
    """
    df = pd.read_excel(file_path)
    return df


def merge_checks_by_type(df, checks_file_path='final_flat_clean_chek_type.xlsx'):
    """
    Присоединяет корректное количество чеков по типам к основным данным.

    Добавляет колонку 'Чеки_по_типу' - число чеков данного типа за месяц по магазину.
    ВАЖНО: Значение только в первой строке группы Магазин+Год+Месяц+Тип, остальные = 0.
    """
    df_checks = load_checks_by_type(checks_file_path)

    # Джойним по Тип, Год, Месяц, Магазин
    df_merged = df.merge(
        df_checks,
        on=['Тип', 'Год', 'Месяц', 'Магазин'],
        how='left'
    )

    # Значение только в первой строке группы, остальные = 0
    if 'Чеки_по_типу' in df_merged.columns:
        first_row_mask = ~df_merged.duplicated(subset=['Магазин', 'Год', 'Месяц', 'Тип'], keep='first')
        original_values = df_merged['Чеки_по_типу'].copy()
        df_merged['Чеки_по_типу'] = original_values.where(first_row_mask, 0)
        df_merged['Чеки_по_типу'] = df_merged['Чеки_по_типу'].fillna(0)

    return df_merged


def get_total_checks(checks_file_path='final_flat_clean_chek_type.xlsx'):
    """
    Возвращает DataFrame с общим количеством чеков (Тип='всего'/'Всего') по магазинам и месяцам.

    Результат:
    | Год | Месяц | Магазин | Чеки_всего |
    """
    df_checks = load_checks_by_type(checks_file_path)

    # Фильтруем "всего" без учёта регистра
    df_total = df_checks[df_checks['Тип'].str.lower() == 'всего'].copy()
    df_total = df_total.rename(columns={'Чеки_по_типу': 'Чеки_всего'})
    df_total = df_total.drop('Тип', axis=1)

    return df_total


def merge_total_checks(df, checks_file_path='final_flat_clean_chek_type.xlsx'):
    """
    Присоединяет общее количество чеков ('всего') к основным данным.

    Добавляет колонку 'Чеки_всего' - общее число чеков за месяц по магазину.
    ВАЖНО: Заменяет 'Число чеков' так, чтобы значение было только в одной строке
    для каждой комбинации Магазин+Год+Месяц. Это гарантирует правильную сумму
    при группировке (не будет дублирования).
    """
    df_total = get_total_checks(checks_file_path)

    df_merged = df.merge(
        df_total,
        on=['Год', 'Месяц', 'Магазин'],
        how='left'
    )

    # Сохраняем оригинальное значение чеков для группировки по товару
    if 'Число чеков' in df_merged.columns:
        df_merged['Чеки_оригинал'] = df_merged['Число чеков'].copy()

    # Заменяем 'Число чеков' на корректное значение только в ПЕРВОЙ строке
    # для каждой комбинации Магазин+Год+Месяц, остальные = 0
    # Это гарантирует что сумма чеков при группировке будет правильной
    if 'Чеки_всего' in df_merged.columns and 'Число чеков' in df_merged.columns:
        # Создаём маску: True только для первой строки в каждой группе
        first_row_mask = ~df_merged.duplicated(subset=['Магазин', 'Год', 'Месяц'], keep='first')
        # В первой строке группы - корректное значение, в остальных - 0
        df_merged['Число чеков'] = df_merged['Чеки_всего'].where(first_row_mask, 0)
        df_merged['Число чеков'] = df_merged['Число чеков'].fillna(0)

    return df_merged


def merge_writeoffs(df, writeoffs_file_path):
    df_writeoffs = pd.read_excel(writeoffs_file_path)
    df_merged = df.merge(
        df_writeoffs,
        on=['Год', 'Месяц', 'Товар', 'Тип', 'Магазин'],
        how='left'
    )
    return df_merged


def aggregate_by_store(df):
    """
    Агрегация по магазинам.

    Если есть колонка 'Чеки_всего' - использует её для расчёта среднего чека.
    Иначе использует 'Число чеков' (старое поведение).
    """
    agg_dict = {'Выручка': 'sum'}

    # Определяем колонку для чеков
    if 'Чеки_всего' in df.columns:
        # Суммируем уникальные значения чеков по месяцам (не дублируем)
        # Группируем сначала по Магазин+Год+Месяц, берём first, потом суммируем
        checks_by_month = df.groupby(['Магазин', 'Год', 'Месяц'])['Чеки_всего'].first().reset_index()
        total_checks = checks_by_month.groupby('Магазин')['Чеки_всего'].sum().reset_index()
        total_checks.columns = ['Магазин', 'Число_чеков_корр']
        use_corrected = True
    else:
        agg_dict['Число чеков'] = 'sum'
        use_corrected = False

    store_agg = df.groupby('Магазин').agg(agg_dict).reset_index()

    if use_corrected:
        store_agg = store_agg.merge(total_checks, on='Магазин', how='left')
        store_agg['Средний_чек'] = store_agg['Выручка'] / store_agg['Число_чеков_корр']
    else:
        store_agg['Средний_чек'] = store_agg['Выручка'] / store_agg['Число чеков']

    return store_agg


def aggregate_by_month(df):
    """
    Агрегация по месяцам.

    Если есть колонка 'Чеки_всего' - использует её для расчёта среднего чека.
    """
    df = df.copy()
    df['Дата'] = pd.to_datetime(df[['Год', 'Месяц']].assign(DAY=1))

    agg_dict = {'Выручка': 'sum'}

    if 'Чеки_всего' in df.columns:
        # Суммируем уникальные чеки по магазинам за каждый месяц
        checks_by_month = df.groupby(['Дата', 'Магазин'])['Чеки_всего'].first().reset_index()
        total_checks = checks_by_month.groupby('Дата')['Чеки_всего'].sum().reset_index()
        total_checks.columns = ['Дата', 'Число_чеков_корр']
        use_corrected = True
    else:
        agg_dict['Число чеков'] = 'sum'
        use_corrected = False

    monthly_agg = df.groupby('Дата').agg(agg_dict).reset_index()

    if use_corrected:
        monthly_agg = monthly_agg.merge(total_checks, on='Дата', how='left')
        monthly_agg['Средний_чек'] = monthly_agg['Выручка'] / monthly_agg['Число_чеков_корр']
    else:
        monthly_agg['Средний_чек'] = monthly_agg['Выручка'] / monthly_agg['Число чеков']

    return monthly_agg


def aggregate_by_product(df):
    product_agg = df.groupby('Товар').agg({
        'Выручка': 'sum',
        'Валовая_прибыль': 'sum',
        'Число чеков': 'sum'
    }).reset_index()

    product_agg['Маржа_%'] = (product_agg['Валовая_прибыль'] / product_agg['Выручка'] * 100).round(2)

    return product_agg


def aggregate_by_type(df):
    """
    Агрегация по типам товаров.

    Если есть колонка 'Чеки_по_типу' - использует её для расчёта среднего чека по типу.
    """
    agg_dict = {
        'Выручка': 'sum',
        'Валовая_прибыль': 'sum',
        'Маржа_%': 'mean'
    }

    if 'Чеки_по_типу' in df.columns:
        # Суммируем уникальные чеки по типам (по магазинам и месяцам)
        checks_by_type = df.groupby(['Тип', 'Год', 'Месяц', 'Магазин'])['Чеки_по_типу'].first().reset_index()
        total_checks = checks_by_type.groupby('Тип')['Чеки_по_типу'].sum().reset_index()
        total_checks.columns = ['Тип', 'Число_чеков_корр']
        use_corrected = True
    else:
        agg_dict['Число чеков'] = 'sum'
        use_corrected = False

    type_agg = df.groupby('Тип').agg(agg_dict).reset_index()

    if use_corrected:
        type_agg = type_agg.merge(total_checks, on='Тип', how='left')
        type_agg['Средний_чек'] = type_agg['Выручка'] / type_agg['Число_чеков_корр']
    else:
        type_agg['Средний_чек'] = type_agg['Выручка'] / type_agg['Число чеков']

    type_agg['Gross_Margin_%'] = (type_agg['Валовая_прибыль'] / type_agg['Выручка'] * 100).round(2)

    return type_agg


def get_unique_values(df, column):
    return sorted(df[column].dropna().unique().tolist())


def aggregate_store_performance(df):
    """
    Агрегация по магазинам с расчётом метрик на м²

    Args:
        df: DataFrame с колонками Магазин, Выручка, Валовая_прибыль, Торговая площадь магазина

    Returns:
        DataFrame с колонками:
        - Магазин, Площадь_м2
        - Выручка, Прибыль, Выручка_на_м2, Прибыль_на_м2
    """
    # Агрегируем по магазинам
    store_agg = df.groupby('Магазин').agg({
        'Выручка': 'sum',
        'Валовая_прибыль': 'sum',
        'Торговая площадь магазина': 'first'  # площадь одинаковая для магазина
    }).reset_index()

    store_agg.columns = ['Магазин', 'Выручка', 'Прибыль', 'Площадь_м2']

    # Расчёт метрик на м²
    store_agg['Выручка_на_м2'] = (store_agg['Выручка'] / store_agg['Площадь_м2']).round(0)
    store_agg['Прибыль_на_м2'] = (store_agg['Прибыль'] / store_agg['Площадь_м2']).round(0)

    # Извлекаем номер магазина для отображения
    store_agg['Store_ID'] = store_agg['Магазин'].str.extract(r'(\d+)').astype(int)

    return store_agg
