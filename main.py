# PROJECT_ROOT: main.py
import pandas as pd
import webbrowser
from engine.data_processor import (
    load_sales_data, merge_store_area,
    merge_checks_by_type, merge_total_checks
)
from engine.dashboard import DashboardEngine
from engine.grid_manager import GridLayout, GridRow
from charts.chart_revenue_dynamics import ChartRevenueDynamics
from charts.chart_lifecycle_phases import ChartLifecyclePhases
from charts.chart_small_multiples import ChartSmallMultiples
from charts.chart_marginal_analysis import ChartMarginalAnalysis
from charts.chart_regression_analysis import ChartRegressionAnalysis
from charts.chart_cluster_analysis import ChartClusterAnalysis
from charts.chart_lifecycle_from_zero import ChartLifecycleFromZero
from charts.chart_dea_analysis import ChartDEAAnalysis
from charts.chart_time_decomposition import ChartTimeDecomposition
from charts.chart_seasonal_patterns import ChartSeasonalPatterns
from charts.chart_yoy_comparison import ChartYoYComparison
from charts.chart_optimal_area_trend import ChartOptimalAreaTrend
from charts.chart_store_cards import ChartStoreCards


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

    print("\n2.1. Мердж с корректными чеками по типам...")
    print(f"   До мерджа - колонки: {list(df.columns)}")
    print(f"   До мерджа - строк: {len(df)}")
    print(f"   Уникальные Тип в df: {df['Тип'].unique().tolist()}")
    print(f"   Уникальные Месяц в df: {df['Месяц'].unique().tolist()[:3]}...")

    # Загружаем чеки для диагностики
    from engine.data_processor import load_checks_by_type
    df_checks = load_checks_by_type('final_flat_clean_chek_type.xlsx')
    print(f"   Чеки - строк: {len(df_checks)}")
    print(f"   Чеки - колонки: {list(df_checks.columns)}")
    print(f"   Уникальные Тип в чеках: {df_checks['Тип'].unique().tolist()}")
    print(f"   Уникальные Месяц в чеках: {df_checks['Месяц'].unique().tolist()[:3]}...")

    df = merge_checks_by_type(df, 'final_flat_clean_chek_type.xlsx')
    print(f"   После merge_checks_by_type - строк: {len(df)}")
    print(f"   Чеки_по_типу NaN: {df['Чеки_по_типу'].isna().sum() if 'Чеки_по_типу' in df.columns else 'колонки нет'}")

    df = merge_total_checks(df, 'final_flat_clean_chek_type.xlsx')
    print(f"   После merge_total_checks - строк: {len(df)}")
    print(f"   Чеки_всего NaN: {df['Чеки_всего'].isna().sum() if 'Чеки_всего' in df.columns else 'колонки нет'}")

    if 'Чеки_по_типу' in df.columns and 'Чеки_всего' in df.columns:
        print(f"   Добавлены колонки: Чеки_по_типу, Чеки_всего")
        print(f"   Пример данных:")
        print(df[['Магазин', 'Год', 'Месяц', 'Тип', 'Чеки_по_типу', 'Чеки_всего']].head(5).to_string())
    else:
        print(f"   ВНИМАНИЕ: Чеки не загружены, используются данные из основного файла")

    print("\n3. Определение уровней детализации...")
    # Определяем доступные уровни на основе данных
    from engine.filters import GlobalFilters
    temp_filters = GlobalFilters(df)
    available_levels = temp_filters.available_detail_levels
    print(f"   Доступные уровни детализации: {available_levels}")

    print("\n4. Создание графиков...")
    chart_revenue_dynamics = ChartRevenueDynamics(
        chart_id='chart_revenue_dynamics',
        width=100,
        available_detail_levels=available_levels,
        default_group_by='Тип',
        default_display_mode='percent',
        default_show_labels=True
    )
    print("   График динамики выручки")

    # chart_lifecycle = ChartLifecyclePhases(
    #     chart_id='chart_lifecycle_phases',
    #     width=100,
    #     available_detail_levels=available_levels,
    #     default_show_labels=True
    # )
    # print("   График жизненного цикла магазинов")

    chart_small_multiples = ChartSmallMultiples(
        chart_id='chart_small_multiples',
        width=100,
        available_detail_levels=available_levels
    )
    print("   Шпалера (small multiples)")

    chart_lifecycle_zero = ChartLifecycleFromZero(
        chart_id='chart_lifecycle_from_zero',
        width=100,
        default_show_labels=True
    )
    print("   Жизненный цикл с нулевой точки")

    chart_marginal = ChartMarginalAnalysis(
        chart_id='chart_marginal_analysis',
        width=100
    )
    print("   Метод 3: Маржинальный анализ")

    chart_regression = ChartRegressionAnalysis(
        chart_id='chart_regression_analysis',
        width=100
    )
    print("   Метод 2: Регрессионный анализ")

    chart_cluster = ChartClusterAnalysis(
        chart_id='chart_cluster_analysis',
        width=100
    )
    print("   Метод 4: Кластерный анализ + Бенчмаркинг")

    chart_dea = ChartDEAAnalysis(
        chart_id='chart_dea_analysis',
        width=100
    )
    print("   Метод 5: DEA анализ границы эффективности")

    chart_time_decomposition = ChartTimeDecomposition(
        chart_id='chart_time_decomposition',
        width=100
    )
    print("   График 1: Декомпозиция временных рядов")

    chart_seasonal_patterns = ChartSeasonalPatterns(
        chart_id='chart_seasonal_patterns',
        default_show_labels=True,
        width=100
    )
    print("   График 2: Сезонные паттерны")

    # chart_yoy = ChartYoYComparison(
    #     chart_id='chart_yoy_comparison',
    #     width=100
    # )
    # print("   График 3: Year-over-Year сравнение")

    chart_optimal_area = ChartOptimalAreaTrend(
        chart_id='chart_optimal_area_trend',
        width=100
    )
    print("   График 4: Тренд оптимальной площади")

    chart_store_cards = ChartStoreCards(
        chart_id='chart_store_cards',
        width=100
    )
    print("   Карточки магазинов")

    print("\n5. Создание layout...")
    layout_tab1 = GridLayout([
        GridRow([chart_revenue_dynamics], height=600),
        # GridRow([chart_lifecycle], height=600),
        GridRow([chart_seasonal_patterns], height=650),
        GridRow([chart_lifecycle_zero], height=550),
        GridRow([chart_small_multiples], height=800),
        GridRow([chart_time_decomposition], height=750)
    ])

    layout_tab2 = GridLayout([
        GridRow([chart_marginal], height=600),
        GridRow([chart_regression], height=550),
        GridRow([chart_cluster], height=650),
        GridRow([chart_dea], height=650),
        GridRow([chart_optimal_area], height=550)
        # GridRow([chart_seasonal_patterns], height=650),
        # GridRow([chart_yoy], height=550),
        # GridRow([chart_optimal_area], height=550)
    ])

    layout_tab3 = GridLayout([
        GridRow([chart_store_cards], height=None)  # Высота автоматическая
    ])

    tabs = {
        'tab1': {
            'name': 'Основная аналитика',
            'layout': layout_tab1
        },
        'tab2': {
            'name': 'Анализ площади',
            'layout': layout_tab2
        },
        'tab3': {
            'name': 'Обзор магазинов',
            'layout': layout_tab3
        }
    }

    print(f"   Вкладок: {len(tabs)}")

    print("\n6. Генерация HTML...")
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

    print("\n7. Открытие в браузере...")
    webbrowser.open(output_file)


if __name__ == '__main__':
    main()
