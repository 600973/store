import pandas as pd
import numpy as np


def load_sales_data(file_path='final_flat_clean.xlsx'):
    df = pd.read_excel(file_path)

    df['Выручка'] = df['Число чеков'] * df['Сумма в чеке']
    df['Валовая_прибыль'] = df['Число чеков'] * df['Наценка продажи в чеке']
    df['Маржа_%'] = (df['Наценка продажи в чеке'] / df['Сумма в чеке'] * 100).round(2)

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
