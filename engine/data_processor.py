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


def load_sales_data(file_path='final_flat_clean.xlsx'):
    df = pd.read_excel(file_path)

    df['Выручка'] = df['Число чеков'] * df['Сумма в чеке']
    df['Валовая_прибыль'] = df['Число чеков'] * df['Наценка продажи в чеке']
    df['Маржа_%'] = (df['Наценка продажи в чеке'] / df['Сумма в чеке'] * 100).round(2)

    # Создаем форматированный столбец Дата
    df = create_date_column(df)

    return df


def merge_store_area(df, area_file_path='store.xlsx'):
    df_area = pd.read_excel(area_file_path)
    df_merged = df.merge(df_area, on='Магазин', how='left')
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
    store_agg = df.groupby('Магазин').agg({
        'Выручка': 'sum',
        'Валовая_прибыль': 'sum',
        'Число чеков': 'sum',
        'Количество в чеке': 'mean',
        'Сумма в чеке': 'mean',
        'Маржа_%': 'mean'
    }).reset_index()

    store_agg['Средний_чек'] = store_agg['Выручка'] / store_agg['Число чеков']
    store_agg['Gross_Margin_%'] = (store_agg['Валовая_прибыль'] / store_agg['Выручка'] * 100).round(2)

    return store_agg


def aggregate_by_month(df):
    df['Дата'] = pd.to_datetime(df[['Год', 'Месяц']].assign(DAY=1))

    monthly_agg = df.groupby('Дата').agg({
        'Выручка': 'sum',
        'Валовая_прибыль': 'sum',
        'Число чеков': 'sum',
        'Маржа_%': 'mean'
    }).reset_index()

    monthly_agg['Средний_чек'] = monthly_agg['Выручка'] / monthly_agg['Число чеков']
    monthly_agg['Gross_Margin_%'] = (monthly_agg['Валовая_прибыль'] / monthly_agg['Выручка'] * 100).round(2)

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
    type_agg = df.groupby('Тип').agg({
        'Выручка': 'sum',
        'Валовая_прибыль': 'sum',
        'Число чеков': 'sum',
        'Маржа_%': 'mean'
    }).reset_index()

    type_agg['Средний_чек'] = type_agg['Выручка'] / type_agg['Число чеков']
    type_agg['Gross_Margin_%'] = (type_agg['Валовая_прибыль'] / type_agg['Выручка'] * 100).round(2)

    return type_agg


def get_unique_values(df, column):
    return sorted(df[column].dropna().unique().tolist())
