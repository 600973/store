import pandas as pd
import webbrowser
from engine.data_processor import load_sales_data, merge_store_area
from engine.dashboard import DashboardEngine
from engine.grid_manager import GridLayout, GridRow
from charts.chart_revenue_dynamics import ChartRevenueDynamics


def main():
    print("="*80)
    print("ГЕНЕРАЦИЯ ДАШБОРДА АНАЛИТИКИ МАГАЗИНОВ")
    print("="*80)

    print("\n1. Загрузка данных...")
    df = load_sales_data('final_flat_clean.xlsx')
    print(f"   Загружено строк: {len(df):,}")
    print(f"   Магазинов: {df['Магазин'].nunique()}")
    print(f"   Товаров: {df['Товар'].nunique()}")
    print(f"   Период: {df['Год'].min()}-{df['Год'].max()}")

    print("\n2. Мердж с площадью...")
    df = merge_store_area(df, 'store.xlsx')
    missing_area = df['Торговая площадь магазина'].isna().sum()
    if missing_area > 0:
        print(f"   Магазинов без площади: {missing_area}")
    else:
        print(f"   Площадь добавлена для всех магазинов")

    print("\n3. Создание графиков...")
    chart_revenue_dynamics = ChartRevenueDynamics(
        chart_id='chart_revenue_dynamics',
        width=100
    )
    print("   График динамики выручки")

    print("\n4. Создание layout...")
    layout_tab1 = GridLayout([
        GridRow([chart_revenue_dynamics], height=600)
    ])

    tabs = {
        'tab1': {
            'name': 'Основная аналитика',
            'layout': layout_tab1
        }
    }

    print(f"   Вкладок: {len(tabs)}")

    print("\n5. Генерация HTML...")
    filter_config = {
        'Магазин': {'type': 'multiselect', 'label': 'Магазин'},
        'Товар': {'type': 'multiselect', 'label': 'Товар'},
        'Тип': {'type': 'multiselect', 'label': 'Тип товара'},
        'Год': {'type': 'multiselect', 'label': 'Год'},
        'Месяц': {'type': 'multiselect', 'label': 'Месяц'}
    }
    engine = DashboardEngine(df, tabs=tabs, enable_context=False, filter_config=filter_config)
    output_file = 'store_dashboard.html'
    engine.generate_html(output_file)

    print(f"\n{'='*80}")
    print(f"ДАШБОРД СОЗДАН: {output_file}")
    print(f"{'='*80}")

    print("\n6. Открытие в браузере...")
    webbrowser.open(output_file)


if __name__ == '__main__':
    main()
