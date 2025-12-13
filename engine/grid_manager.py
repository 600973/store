# PROJECT_ROOT: engine/grid_manager.py
"""
Управление сеткой (grid) графиков на дашборде
"""
from typing import List
from charts.base_chart import BaseChart


class GridRow:
    """
    Строка с графиками
    """

    def __init__(self, charts: List[BaseChart], height: int = 600):
        """
        Args:
            charts: Список графиков в строке
            height: Высота строки в пикселях
        """
        self.charts = charts
        self.height = height

        # Проверка суммы ширин
        total_width = sum(chart.width for chart in charts)
        if total_width > 100:
            raise ValueError(f"Сумма ширин графиков в строке > 100%: {total_width}%")

    def get_html(self) -> str:
        """
        Генерирует HTML для строки графиков

        Returns:
            HTML строка
        """
        charts_html = ""

        for chart in self.charts:
            chart_container = chart.get_html_container()
            charts_html += f'''
            <div style="flex: 0 0 {chart.width}%; min-width: 0; overflow-x: auto;">
                {chart_container}
            </div>
            '''

        return f'''
        <div class="chart-row" style="display: flex; gap: 20px; margin-bottom: 30px;">
            {charts_html}
        </div>
        '''


class GridLayout:
    """
    Полный layout дашборда (набор строк)
    """

    def __init__(self, rows: List[GridRow]):
        """
        Args:
            rows: Список строк (GridRow)
        """
        self.rows = rows

    def get_html(self) -> str:
        """
        Генерирует HTML для всего layout

        Returns:
            HTML строка
        """
        rows_html = ""
        for row in self.rows:
            rows_html += row.get_html()

        return rows_html

    def get_all_charts(self) -> List[BaseChart]:
        """
        Возвращает список всех графиков в layout

        Returns:
            Список графиков
        """
        charts = []
        for row in self.rows:
            charts.extend(row.charts)
        return charts

    def get_all_js_code(self) -> str:
        """
        Собирает весь JS код от всех графиков

        Returns:
            JS код
        """
        js_code = ""
        for chart in self.get_all_charts():
            js_code += f"\n// ===== График: {chart.chart_id} =====\n"

            # Функция детализации
            detail_js = chart._generate_detail_level_js()
            if detail_js:
                js_code += detail_js
                js_code += "\n"

            # Основной код графика
            js_code += chart.get_js_code()
            js_code += "\n"

            # Добавляем JS локальных фильтров
            local_filters_js = chart._generate_local_filters_js()
            if local_filters_js:
                js_code += f"\n// Локальные фильтры для {chart.chart_id}\n"
                js_code += local_filters_js
                js_code += "\n"

            # Добавляем JS таблиц
            table_js = chart._generate_table_js()
            if table_js:
                js_code += f"\n// Таблица для {chart.chart_id}\n"
                js_code += table_js
                js_code += "\n"

        return js_code

    def get_all_css_styles(self) -> str:
        """
        Собирает все дополнительные CSS стили от графиков

        Returns:
            CSS код
        """
        css_code = ""
        for chart in self.get_all_charts():
            chart_css = chart.get_css_styles()
            if chart_css:
                css_code += f"\n/* График: {chart.chart_id} */\n"
                css_code += chart_css
                css_code += "\n"

        return css_code
