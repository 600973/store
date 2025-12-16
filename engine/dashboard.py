# PROJECT_ROOT: engine/dashboard.py
"""
Движок дашборда - генерация HTML из данных и графиков
"""
import pandas as pd
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from .grid_manager import GridLayout
from .filters import GlobalFilters


class DashboardEngine:
    """
    Основной движок для генерации self-contained HTML дашборда
    """

    def __init__(self, df: pd.DataFrame, tabs: dict = None, layout: GridLayout = None,
                 enable_context: bool = True, context_config: Optional[Dict[str, bool]] = None,
                 filter_config: dict = None):
        """
        Args:
            df: DataFrame с данными
            tabs: dict вкладок {'tab1': {'name': str, 'layout': GridLayout}, ...}
            layout: GridLayout (legacy, для обратной совместимости)
            enable_context: Включить AI-контекст для анализа
            context_config: Глобальная конфигурация контекста (можно переопределить в конкретных графиках)
            filter_config: Конфиг фильтров {'column': {'type': 'multiselect', 'label': 'Label'}}
        """
        self.df = df
        self.enable_context = enable_context

        if tabs:
            self.tabs = tabs
        elif layout:
            self.tabs = {'tab1': {'name': 'Основная аналитика', 'layout': layout}}
        else:
            raise ValueError("Укажите tabs или layout")

        self.filters = GlobalFilters(df)
        
        # Инициализация контекста для AI-анализа
        if self.enable_context:
            from context_builder import AnalysisContext
            self.analysis_context = AnalysisContext(df, context_config)
            # Устанавливаем контекст для всех графиков
            self._inject_context_to_charts()
        else:
            self.analysis_context = None

    def _inject_context_to_charts(self):
        """Внедрить AnalysisContext во все графики"""
        for tab_data in self.tabs.values():
            layout = tab_data['layout']
            for chart in layout.get_all_charts():
                chart.set_analysis_context(self.analysis_context)
    
    def set_dashboard_metrics(self, metrics: Dict[str, Any]):
        """
        Установить ключевые метрики дашборда для контекста
        Вызывается из main.py после построения ключевых графиков
        
        Args:
            metrics: Словарь с метриками
        """
        if self.analysis_context:
            self.analysis_context.set_dashboard_metrics(metrics)

    def generate_html(self, output_file: str = 'dashboard.html') -> str:
        """
        Генерирует HTML файл дашборда

        Args:
            output_file: Путь к выходному файлу

        Returns:
            Путь к созданному файлу
        """
        # Подготовка данных
        data_json = self._prepare_data_json()

        # Сборка HTML компонентов для всех вкладок
        tabs_html = {}
        all_js = []
        all_css = []
        
        for tab_id, tab_data in self.tabs.items():
            layout = tab_data['layout']
            tabs_html[tab_id] = layout.get_html()
            all_js.append(layout.get_all_js_code())
            all_css.append(layout.get_all_css_styles())
        
        charts_js = '\n'.join(all_js)
        charts_css = '\n'.join(all_css)

        # Загрузка шаблона
        template_path = os.path.join(
            os.path.dirname(__file__),
            '..', 'templates', 'dashboard_template.html'
        )

        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()

        from prompt_loader import get_prompts_js
        prompts_js = get_prompts_js()
        
        # Генерация контекстных данных для JS
        context_data_js = self._generate_context_data_js()

        # Генерация кнопок вкладок
        tabs_buttons = []
        tabs_content = []
        for i, (tab_id, tab_data) in enumerate(self.tabs.items()):
            active_class = ' active' if i == 0 else ''
            tab_name = tab_data.get('name', f'Вкладка {i+1}')
            tabs_buttons.append(
                f'<button class="tab-btn{active_class}" onclick="switchTab(\'{tab_id}\')">{tab_name}</button>'
            )
            tabs_content.append(
                f'<div id="{tab_id}" class="tab-content{active_class}">\n'
            )
            tabs_content.append(f'    {tabs_html[tab_id]}\n</div>')

        # Замена плейсхолдеров
        html_content = html_template.replace('{{DATA_JSON}}', data_json)
        available_levels_json = json.dumps(self.filters.available_detail_levels)
        html_content = html_content.replace('{{AVAILABLE_DETAIL_LEVELS}}', available_levels_json)
        html_content = html_content.replace('{{PROMPTS_JSON}}', prompts_js)
        html_content = html_content.replace('{{CONTEXT_DATA_JS}}', context_data_js)
        html_content = html_content.replace('{{CHARTS_JS}}', charts_js)
        html_content = html_content.replace('{{CHARTS_CSS}}', charts_css)
        html_content = html_content.replace('{{FILTERS_HTML}}', self._get_filters_html())
        html_content = html_content.replace('{{FILTERS_JS}}', self._get_filters_js())

        # Генерация динамических вкладок
        html_content = html_content.replace('{{TABS_BUTTONS}}', '\n            '.join(tabs_buttons))
        html_content = html_content.replace('{{TABS_CONTENT}}', '\n        '.join(tabs_content))

        # Запись файла
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        file_size = os.path.getsize(output_file)
        total_charts = sum(len(tab['layout'].get_all_charts()) for tab in self.tabs.values())
        
        print(f"\n{'=' * 80}")
        print(f"HTML создан: {output_file}")
        print(f"Размер: {file_size / 1024 / 1024:.2f} МБ")
        print(f"Записей: {len(self.df)}")
        print(f"Вкладок: {len(self.tabs)}")
        print(f"Графиков: {total_charts}")
        print(f"{'=' * 80}\n")

        return os.path.abspath(output_file)

    def _prepare_data_json(self) -> str:
        """
        Подготовка данных в JSON формат

        Returns:
            JSON строка
        """
        df_export = self.df.copy()

        # Расчёт возрастных групп
        if 'Дата рождения' in df_export.columns:
            df_export['Возраст'] = df_export.apply(
                lambda row: calculate_age(
                    row['Дата рождения'],
                    row['Дата увольнения'] if pd.notnull(row.get('Дата увольнения')) else datetime.now()
                ),
                axis=1
            )
            df_export['Возрастная группа'] = df_export['Возраст'].apply(get_age_group)

        # Расчёт стажа
        if 'Дата приема' in df_export.columns:
            df_export['Стаж (месяцы)'] = df_export.apply(
                lambda row: calculate_tenure_months(
                    row['Дата приема'],
                    row['Дата увольнения'] if pd.notnull(row.get('Дата увольнения')) else datetime.now()
                ),
                axis=1
            )
            df_export['Диапазон стажа'] = df_export['Стаж (месяцы)'].apply(get_tenure_range)

        # Конвертация дат
        for col in df_export.columns:
            if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                df_export[col] = df_export[col].apply(
                    lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None
                )

        # Замена NaN на None
        df_export = df_export.where(pd.notnull(df_export), None)

        # Конвертация в JSON
        data_json = df_export.to_json(orient='records', force_ascii=False)

        print(f"Размер JSON: {len(data_json) / 1024:.1f} KB")

        return data_json

    def _get_filters_html(self) -> str:
        """
        Генерирует HTML для глобальных фильтров

        Returns:
            HTML строка
        """
        return self.filters.get_html()

    def _get_filters_js(self) -> str:
        """
        Генерирует JS код для глобальных фильтров

        Returns:
            JS код
        """
        return self.filters.get_js_code()
    
    def _generate_context_data_js(self) -> str:
        """
        Генерирует JS код с контекстными данными для каждого графика
        
        Returns:
            JS код с инициализацией window.analysisContextData
        """
        if not self.enable_context or not self.analysis_context:
            return "window.analysisContextData = {};"
        
        # Собираем контекст для каждого графика
        context_data = {}
        
        for tab_data in self.tabs.values():
            layout = tab_data['layout']
            for chart in layout.get_all_charts():
                chart_id = chart.chart_id
                # Получаем конфигурацию контекста для конкретного графика
                chart_context_config = getattr(chart, 'ai_context_config', None)
                
                # Строим контекст с учетом конфига графика
                context_text = self.analysis_context.build_context(
                    chart_name=chart_id,
                    chart_specific_config=chart_context_config
                )
                
                context_data[chart_id] = context_text
        
        # Конвертируем в JSON и оборачиваем в JS
        context_json = json.dumps(context_data, ensure_ascii=False)
        
        return f"""
        // Контекстные данные для AI-анализа (динамически обновляются при изменении фильтров)
        window.analysisContextData = {context_json};
        """