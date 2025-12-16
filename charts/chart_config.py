# PROJECT_ROOT: charts/chart_config.py
# charts/chart_config.py
"""
Конфигурация для графиков дашборда
"""

# Глобальные настройки для всех графиков
GLOBAL_SETTINGS = {
    'ai_view_mode': 'collapsed',  # 'collapsed' или 'full'
    'ai_max_lines': 5,  # Количество строк при collapsed режиме
    'ai_context': {
        'company_context': True,
        'filters_context': True,
        'dashboard_metrics': True
    }
}

# Специфичные настройки для отдельных графиков
CHART_CONFIGS = {
    # Пример конфигурации для конкретного графика
    # 'chart_id': {
    #     'ai_view_mode': 'full',
    #     'ai_max_lines': 10,
    #     'ai_context': {
    #         'company_context': True,
    #         'filters_context': False,
    #         'dashboard_metrics': True
    #     }
    # }
}


def get_chart_config(chart_id: str) -> dict:
    """
    Получить конфигурацию для конкретного графика

    Args:
        chart_id: ID графика

    Returns:
        Словарь с настройками графика
    """
    return CHART_CONFIGS.get(chart_id, {})
