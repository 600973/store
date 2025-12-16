"""
Преобразование final_flat_clean_chek_type из wide в long формат
"""
import pandas as pd


def convert_chek_type_to_long(input_file='final_flat_clean_chek_type_flat.xlsx',
                               output_file='final_flat_clean_chek_type.xlsx'):
    """
    Преобразует данные из wide-формата в long-формат.

    Исходная структура:
    | Тип       | год месяц  | Магазин1 | Магазин2 | ...
    |-----------|------------|----------|----------|
    | сп        | 2022       |          |          |     <- строка года (пропускаем)
    | сп        | январь     | 150      | 200      |     <- данные

    Результат:
    | Тип   | Год  | Месяц   | Магазин  | Чеки_по_типу |
    |-------|------|---------|----------|--------------|
    | сп    | 2022 | Январь  | Магазин1 | 150          |
    """
    # Читаем Excel без заголовков
    df = pd.read_excel(input_file, header=None)

    print(f"Загружено: {df.shape[0]} строк, {df.shape[1]} колонок")
    print(f"\nПервые 5 строк исходного файла:")
    print(df.head().to_string())

    # Первая строка - заголовки (Тип, год месяц, Магазин1, Магазин2, ...)
    # Названия магазинов из первой строки, начиная с 3-й колонки
    store_names = df.iloc[0, 2:].tolist()
    print(f"\nМагазины: {store_names[:5]}... (всего {len(store_names)})")

    # Переименовываем колонки
    df.columns = ['Тип', 'Период'] + store_names

    # Убираем строку заголовков
    df = df.iloc[1:].reset_index(drop=True)

    # Добавляем колонку Год - заполняем вниз от строк с годом
    current_year = None
    years = []
    for period in df['Период']:
        period_str = str(period).strip().lower()
        # Проверяем - это год (число) или месяц
        if period_str.isdigit() or (period_str.replace('.', '').isdigit()):
            current_year = int(float(period_str))
            years.append(None)  # Строку года пропустим
        else:
            years.append(current_year)

    df['Год'] = years

    # Фильтруем только строки с месяцами (убираем строки с годами)
    df = df[df['Год'].notna()].copy()
    print(f"\nСтрок с данными (без строк годов): {len(df)}")

    # Приводим месяц к нормальному виду (с заглавной буквы)
    df['Месяц'] = df['Период'].str.strip().str.capitalize()

    # Убираем колонку Период
    df = df.drop('Период', axis=1)

    # Преобразуем в long-формат (melt)
    id_vars = ['Тип', 'Год', 'Месяц']

    df_long = df.melt(
        id_vars=id_vars,
        value_vars=store_names,
        var_name='Магазин',
        value_name='Чеки_по_типу'
    )

    # Приводим типы
    df_long['Год'] = df_long['Год'].astype(int)
    df_long['Чеки_по_типу'] = pd.to_numeric(df_long['Чеки_по_типу'], errors='coerce').fillna(0).astype(int)

    # Приводим Тип к нормальному виду
    df_long['Тип'] = df_long['Тип'].str.strip()

    # Сортируем для удобства
    df_long = df_long.sort_values(['Тип', 'Год', 'Месяц', 'Магазин']).reset_index(drop=True)

    # Сохраняем результат
    df_long.to_excel(output_file, index=False)

    print(f"\n{'='*60}")
    print(f"Результат:")
    print(f"  Строк: {len(df_long)}")
    print(f"  Типов: {df_long['Тип'].nunique()} - {df_long['Тип'].unique().tolist()}")
    print(f"  Магазинов: {df_long['Магазин'].nunique()}")
    print(f"  Лет: {sorted(df_long['Год'].unique())}")
    print(f"\nПервые 10 строк результата:")
    print(df_long.head(10).to_string())
    print(f"\nСохранено в: {output_file}")

    return df_long


if __name__ == '__main__':
    df_long = convert_chek_type_to_long(
        input_file='final_flat_clean_chek_type_flat.xlsx',
        output_file='final_flat_clean_chek_type.xlsx'
    )
