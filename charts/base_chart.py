# PROJECT_ROOT: charts/base_chart.py
"""
Базовый класс для всех графиков дашборда
"""
from typing import Dict, Optional, Any
import json


class BaseChart:
    """
    Базовый класс графика с настройками дизайна и фильтрами
    """

    # Базовые CSS стили для контейнера графика
    DEFAULT_CSS = {
        'background': 'white',
        'padding': '20px',
        'border-radius': '10px',
        'box-shadow': '0 2px 10px rgba(0,0,0,0.1)',
        'min-width': '0',
        'box-sizing': 'border-box'
    }

    # Базовые настройки Plotly layout
    DEFAULT_PLOTLY_LAYOUT = {
        'plot_bgcolor': '#f8f9fa',
        'xaxis': {'gridcolor': '#e9ecef'},
        'yaxis': {'gridcolor': '#e9ecef'},
        'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50},
        'hovermode': 'x unified'
    }

    def __init__(
            self,
            chart_id: str,
            width: int = 100,
            css_style: Optional[Dict[str, str]] = None,
            plotly_layout: Optional[Dict[str, Any]] = None,
            plotly_traces: Optional[Dict[str, Any]] = None,
            local_filters: Optional[Dict[str, Any]] = None,
            llm_comment: Optional[str] = None,
            show_table: bool = False,
            show_prompt: bool = True,
            ai_view_mode: Optional[str] = None,
            ai_max_lines: Optional[int] = None,
            ai_context_config: Optional[Dict[str, bool]] = None
    ):
        """
        Инициализация графика

        Args:
            chart_id: Уникальный ID графика
            width: Ширина в процентах (для GridRow)
            css_style: Кастомные CSS стили (переопределяют DEFAULT_CSS)
            plotly_layout: Кастомные настройки Plotly layout
            plotly_traces: Настройки trace (bar_color, line_width и т.д.)
            local_filters: Локальные фильтры графика
            llm_comment: Комментарий от LLM
            show_table: Показывать переключатель График/Таблица
            show_prompt: Показывать вкладку Промпт
            ai_view_mode: Режим отображения AI-ответа ('collapsed', 'full')
            ai_max_lines: Количество строк при collapsed режиме
            ai_context_config: Конфигурация AI-контекста для этого графика
                {'company_context': True, 'filters_context': True, 'dashboard_metrics': True}
        """
        # Загружаем настройки из конфига если не переданы
        from charts.chart_config import GLOBAL_SETTINGS, get_chart_config

        self.chart_id = chart_id
        self.width = width
        self.css_style = css_style or {}
        self.plotly_layout = plotly_layout or {}
        self.plotly_traces = plotly_traces or {}
        self.local_filters = local_filters or {}
        self.llm_comment = llm_comment
        self.show_table = show_table
        self.show_prompt = show_prompt
        self.ai_view_mode = ai_view_mode if ai_view_mode is not None else GLOBAL_SETTINGS.get('ai_view_mode', 'collapsed')
        self.ai_max_lines = ai_max_lines if ai_max_lines is not None else GLOBAL_SETTINGS.get('ai_max_lines', 5)

        # Конфигурация AI-контекста: сначала глобальная, потом из конфига графика, потом из параметра
        self.ai_context_config = GLOBAL_SETTINGS.get('ai_context', {
            'company_context': True,
            'filters_context': True,
            'dashboard_metrics': True
        }).copy()

        # Переопределяем из конфига графика
        chart_config = get_chart_config(chart_id)
        if 'ai_context' in chart_config:
            self.ai_context_config.update(chart_config['ai_context'])

        # Переопределяем из параметра конструктора
        if ai_context_config:
            self.ai_context_config.update(ai_context_config)

        # Хранилище для контекста (будет установлен из DashboardEngine)
        self.analysis_context = None

    def set_analysis_context(self, analysis_context):
        """
        Установить объект AnalysisContext для этого графика
        Вызывается из DashboardEngine

        Args:
            analysis_context: Экземпляр AnalysisContext
        """
        self.analysis_context = analysis_context

    def _get_plotly_icon(self, name: str) -> str:
        """
        Возвращает JS объект с Plotly-совместимой SVG иконкой

        Args:
            name: Имя иконки

        Returns:
            JS объект для Plotly icon
        """
        icons = {
            "settings": """{
                width: 1000,
                height: 1000,
                path: 'M500,200c-165.7,0-300,134.3-300,300s134.3,300,300,300s300-134.3,300-300S665.7,200,500,200z M500,700c-110.5,0-200-89.5-200-200s89.5-200,200-200s200,89.5,200,200S610.5,700,500,700z M950,450h-100c-13.8-57.9-37.9-110.9-70.7-156.6l70.7-70.7c19.5-19.5,19.5-51.2,0-70.7s-51.2-19.5-70.7,0l-70.7,70.7C662.9,187.9,609.9,163.8,552,150V50c0-27.6-22.4-50-50-50h-4c-27.6,0-50,22.4-50,50v100c-57.9,13.8-110.9,37.9-156.6,70.7l-70.7-70.7c-19.5-19.5-51.2-19.5-70.7,0s-19.5,51.2,0,70.7l70.7,70.7C187.9,337.1,163.8,390.1,150,448H50c-27.6,0-50,22.4-50,50v4c0,27.6,22.4,50,50,50h100c13.8,57.9,37.9,110.9,70.7,156.6l-70.7,70.7c-19.5,19.5-19.5,51.2,0,70.7s51.2,19.5,70.7,0l70.7-70.7c45.7,32.8,98.7,56.9,156.6,70.7v100c0,27.6,22.4,50,50,50h4c27.6,0,50-22.4,50-50V850c57.9-13.8,110.9-37.9,156.6-70.7l70.7,70.7c19.5,19.5,51.2,19.5,70.7,0s19.5-51.2,0-70.7l-70.7-70.7c32.8-45.7,56.9-98.7,70.7-156.6h100c27.6,0,50-22.4,50-50v-4C1000,472.4,977.6,450,950,450z',
                transform: 'matrix(1 0 0 -1 0 1000)'
            }""",

            "labels": """{
                width: 1000,
                height: 1000,
                path: 'M500 450L100 900h800z',
                transform: 'matrix(1 0 0 -1 0 1000)'
            }""",

            "eye_off": """{
                width: 1000,
                height: 1000,
                path: 'M916 650q0-17-12-30l-49-49q-13-13-30-13t-30 13l-102 102q-42-20-90-20-75 0-128 53t-53 128 53 128 128 53q48 0 90-20l102 102q13 13 30 13t30-13l49-49q12-12 12-30 0-17-12-30l-486-486q-13-13-30-13t-30 13l-49 49q-12 13-12 30 0 18 12 30l79 79q-51 44-85 106-28 50-28 106 0 75 53 128t128 53q56 0 106-28 62-34 106-85l79 79q13 12 30 12 18 0 30-12l49-49q13-13 13-30z',
                transform: 'matrix(1 0 0 -1 0 1000)'
            }"""
        }

        return icons.get(name, icons["settings"])

    def _generate_modebar_settings_button(self) -> str:
        """
        Генерирует JS код для кнопки-шестерёнки в modebar

        Returns:
            JS код для добавления в modeBarButtonsToAdd
        """
        icon_js = self._get_plotly_icon("settings")

        return f"""
        {{
            name: 'Настройки',
            title: 'Показать/скрыть панель управления',
            icon: {icon_js},
            click: function(gd) {{
                const panel = document.getElementById('panel_{self.chart_id}');
                if (panel) {{
                    panel.classList.toggle('collapsed');
                }}
            }}
        }}
        """

    def _wrap_in_collapsible_panel(self, inner_html: str) -> str:
        """
        Оборачивает переданный HTML в сворачиваемую панель
        (одинаковый вид для всех графиков)
        """
        return f'''
        <div class="chart-panel collapsed" id="panel_{self.chart_id}">
            {inner_html}
        </div>
        '''

    def get_html_container(self) -> str:
        css = self._merge_css_styles()
        style_str = '; '.join([f'{k}: {v}' for k, v in css.items()])

        detail_selector_html = self._generate_detail_selector_html()
        local_filters_html = self._generate_local_filters_html()
        view_switcher_html = self._generate_view_switcher_html()
        llm_comment_html = self._generate_llm_comment_html()

        return f'''
        <div class="chart-wrapper" style="{style_str}">
            {view_switcher_html}
            {detail_selector_html}
            {local_filters_html}

            <!-- ОТВЕТ LLM - ВСЕГДА ВИДЕН -->
            <div id="{self.chart_id}_llm_result" class="llm-result" style="display: none;">
                <div class="llm-result-controls">
                    <button class="llm-result-toggle" onclick="this.closest('.llm-result').querySelector('.llm-result-text').classList.toggle('collapsed'); this.textContent = this.textContent === '−' ? '+' : '−'">−</button>
                    <button class="llm-result-close" onclick="document.getElementById('{self.chart_id}_llm_result').style.display='none'">✕</button>
                </div>
                <div class="llm-result-text {self.ai_view_mode}" style="--max-lines: {self.ai_max_lines};"></div>
            </div>
            <div id="{self.chart_id}_llm_loading" class="llm-loading" style="display: none;">⳩ Генерация ответа...</div>

            <div id="{self.chart_id}" style="width: 100%; height: 100%;"></div>
            <div id="{self.chart_id}_table" class="chart-table-container" style="width: 100%; min-width: 0; max-width: 100%; box-sizing: border-box; display: none;"></div>
            <div id="{self.chart_id}_prompt" class="prompt-container" style="display: none;">
                <div class="prompt-header">
                    <div class="provider-selector">
                        <label><input type="radio" name="provider_{self.chart_id}" value="ollama" checked> Ollama</label>
                        <label><input type="radio" name="provider_{self.chart_id}" value="lmstudio"> LM Studio</label>
                    </div>
                    <div class="model-selector" id="model_selector_{self.chart_id}">
                        <label>Модель:</label>
                        <select id="{self.chart_id}_model" class="model-select">
                            <option value="qwen2.5:7b" selected>qwen2.5:7b</option>
                            <option value="qwen2.5-coder:7b">qwen2.5-coder:7b</option>
                            <option value="qwen3:14b">qwen3:14b</option>
                            <option value="qwen3:latest">qwen3:latest</option>
                        </select>
                    </div>
                    <div class="prompt-rows-selector">
                        <label>Строк данных:</label>
                        <select id="{self.chart_id}_rows_limit" class="model-select">
                            <option value="10">10</option>
                            <option value="50">50</option>
                            <option value="100">100</option>
                            <option value="all" selected>Все</option>
                        </select>
                    </div>
                </div>
                <textarea id="{self.chart_id}_prompt_text" class="prompt-textarea" rows="12" placeholder="Загрузка промпта..."></textarea>
                <div class="prompt-actions">
                    <button class="btn-prompt-action btn-send" onclick="sendPrompt_{self.chart_id}()">🚀 Отправить в LLM</button>
                    <button class="btn-prompt-action btn-save" onclick="savePrompt_{self.chart_id}()">💾 Сохранить промпт</button>
                    <button class="btn-prompt-action btn-reset" onclick="resetPrompt_{self.chart_id}()">🔄 Сбросить</button>
                </div>
                <div id="{self.chart_id}_save_status" class="save-status" style="display: none;"></div>
            </div>
            {llm_comment_html}
        </div>
        '''

    def get_js_code(self) -> str:
        """
        Генерирует JS код для отрисовки графика
        ДОЛЖЕН быть переопределён в наследниках

        Returns:
            JS код
        """
        raise NotImplementedError("Метод get_js_code должен быть переопределён в наследнике")

    def get_css_styles(self) -> str:
        """
        Возвращает дополнительные CSS стили (если нужны)

        Returns:
            CSS строка
        """
        css = '''
        .chart-panel {
            padding: 8px 10px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            margin-bottom: 12px;
            transition: all 0.2s ease;
        }

        .chart-panel.collapsed {
            display: none;
        }

        .detail-selector {
            display: flex;
            gap: 4px;
            margin-bottom: 12px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }

        .detail-btn {
            padding: 6px 14px;
            border: 1px solid #dee2e6;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s;
            color: #495057;
        }

        .detail-btn:hover {
            background: #e9ecef;
        }

        .detail-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .detail-btn.disabled {
            background: #f0f0f0;
            color: #bbb;
            border-color: #ddd;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .detail-btn.disabled:hover {
            background: #f0f0f0;
        }

        .view-switcher {
            display: flex;
            gap: 4px;
            margin-bottom: 12px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }

        .view-btn {
            padding: 6px 14px;
            border: 1px solid #dee2e6;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s;
            color: #495057;
        }

        .view-btn:hover {
            background: #e9ecef;
        }

        .view-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .top-controls-row {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
            align-items: flex-start;
        }

        .top-controls-row .view-switcher,
        .top-controls-row .detail-selector {
            margin-bottom: 0;
        }

        .chart-table-container {
            display: grid;
            grid-template-columns: minmax(0, 1fr);
            width: 100%;
            min-width: 0;
            max-width: 100%;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-sizing: border-box;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch; /* плавный скролл на iOS */
            overflow-y: visible;
            position: relative;
        }

        .table-scroll-wrapper {
            width: 100%;
            min-width: 0;
            max-height: 600px;
            overflow: visible;
            box-sizing: border-box;
            position: relative;
        }

        .chart-table {
            width: 100%;
            min-width: 600px; /* минимальная ширина таблицы для горизонтального скролла */
            border-collapse: collapse;
            font-size: 13px;
            table-layout: auto; /* auto вместо fixed для правильного распределения столбцов */
        }

        .chart-table thead {
            position: sticky;
            top: 0;
            background: #f8f9fa;
            z-index: 10;
        }

        .chart-table th {
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            min-width: 80px; /* уменьшена минимальная ширина */
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .chart-table th:hover {
            background: #e9ecef;
        }

        .chart-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #e9ecef;
            color: #212529;
            white-space: nowrap;
            min-width: 80px; /* уменьшена минимальная ширина */
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .chart-table tbody tr:hover {
            background: #f8f9fa;
        }

        .chart-table tfoot {
            position: sticky;
            bottom: 0;
            background: #f8f9fa;
            font-weight: 600;
            z-index: 10;
        }

        .chart-table tfoot th {
            background: #f8f9fa;
            border-top: 2px solid #dee2e6;
            border-bottom: 1px solid #dee2e6;
        }

        .table-controls {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 6px;
            width: 100%;
            min-width: 0;
            box-sizing: border-box;
            flex-shrink: 0;
        }

        .table-info {
            font-size: 12px;
            color: #6c757d;
            flex-shrink: 0;
        }

        .export-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            min-width: 0;
        }

        .export-btn {
            padding: 4px 12px;
            border: 1px solid #dee2e6;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s;
            color: #495057;
        }

        .export-btn:hover {
            background: #e9ecef;
        }

        .transpose-btn {
            padding: 4px 12px;
            border: 1px solid #667eea;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s;
            color: #667eea;
            margin-right: 8px;
        }

        .transpose-btn:hover {
            background: #667eea;
            color: white;
        }

        .sort-indicator {
            margin-left: 4px;
            font-size: 10px;
        }

        /* ПРОМПТ СТИЛИ */
        .prompt-container {
            padding: 20px;
            background: #f8f9fa;
        }

        .prompt-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        }

        .provider-selector {
            display: flex;
            gap: 15px;
        }

        .provider-selector label {
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
        }

        .model-selector {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .model-selector label {
            font-size: 13px;
            font-weight: 500;
        }

        .model-select {
            padding: 4px 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 13px;
        }

        .prompt-textarea {
            width: 100%;
            padding: 15px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            line-height: 1.6;
            resize: vertical;
            background: white;
            color: #212529;
        }

        .prompt-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        .btn-prompt-action {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s;
        }

        .btn-send {
            background: #4a90e2;
            color: white;
        }

        .btn-send:hover {
            background: #357abd;
        }

        .btn-save {
            background: #5cb85c;
            color: white;
        }

        .btn-save:hover {
            background: #4cae4c;
        }

        .btn-reset {
            background: #f0ad4e;
            color: white;
        }

        .btn-reset:hover {
            background: #ec971f;
        }

        .llm-result {
            margin-top: 20px;
            background: white;
            border-left: 4px solid #4a90e2;
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }

        .llm-result-controls {
            position: absolute;
            top: 8px;
            right: 8px;
            display: flex;
            gap: 4px;
            z-index: 10;
        }

        .llm-result-toggle,
        .llm-result-close {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            width: 24px;
            height: 24px;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            transition: all 0.2s;
            padding: 0;
        }

        .llm-result-toggle:hover {
            background: #e3f2fd;
            color: #1976d2;
            border-color: #1976d2;
        }

        .llm-result-close:hover {
            background: #ffebee;
            color: #d32f2f;
            border-color: #d32f2f;
        }

        .llm-result-text.collapsed {
            max-height: 0 !important;
            overflow: hidden;
            padding: 0 !important;
            margin: 0 !important;
        }

        .llm-result-header {
            padding: 12px 15px;
            background: #e3f2fd;
            font-weight: 600;
            color: #1976d2;
            font-size: 14px;
        }

        .llm-result-text {
            padding: 12px 16px;
            color: #2c3e50;
            line-height: 1.5;
            font-size: 13px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }

        .llm-result-text h1,
        .llm-result-text h2,
        .llm-result-text h3 {
            margin: 12px 0 6px 0;
            line-height: 1.3;
        }

        .llm-result-text h1 {
            font-size: 17px;
            font-weight: 700;
            color: #1a202c;
        }

        .llm-result-text h2 {
            font-size: 15px;
            font-weight: 600;
            color: #2d3748;
        }

        .llm-result-text h3 {
            font-size: 14px;
            font-weight: 600;
            color: #4a5568;
        }

        .llm-result-text strong {
            font-weight: 600;
            color: #1a202c;
        }

        .llm-result-text em {
            font-style: italic;
            color: #4a5568;
        }

        .llm-result-text ul,
        .llm-result-text ol {
            margin: 6px 0;
            padding-left: 20px;
        }

        .llm-result-text li {
            margin-bottom: 3px;
            line-height: 1.4;
        }

        .llm-result-text br {
            line-height: 0.8;
        }

        .llm-result-text.collapsed {
            max-height: calc(1.5em * var(--max-lines, 5));
            overflow-y: auto;
        }

        .llm-result-text.full {
            max-height: none;
            overflow-y: visible;
        }

        .llm-loading {
            margin-top: 15px;
            padding: 12px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 6px;
            color: #856404;
            font-weight: 500;
        }

        .save-status {
            margin-top: 10px;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }

        .save-status.success {
            background: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
        }

        .save-status.error {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
        }
        '''

        if not self.local_filters:
            return css

        return css + '''
        .local-filters {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }

        .local-filters-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: #495057;
            font-size: 14px;
        }

        .local-filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 10px;
        }

        .local-filter-group {
            display: flex;
            flex-direction: column;
        }

        .local-filter-group label {
            font-weight: 500;
            margin-bottom: 5px;
            color: #6c757d;
            font-size: 13px;
        }

        .local-filter-input,
        .local-filter-select {
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background: white;
            font-size: 13px;
        }

        .local-filter-checkbox {
            flex-direction: row;
            align-items: center;
        }

        .local-filter-checkbox label {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
            cursor: pointer;
        }

        .local-filter-checkbox-input {
            width: auto;
            cursor: pointer;
        }

        .btn-apply-local {
            padding: 8px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .btn-apply-local:hover {
            background: #5568d3;
            transform: translateY(-1px);
        }
        '''

    def _merge_css_styles(self) -> Dict[str, str]:
        """Слияние базовых и кастомных CSS стилей"""
        return {**self.DEFAULT_CSS, **self.css_style}

    def _merge_plotly_layout(self) -> Dict[str, Any]:
        """Слияние базовых и кастомных Plotly layout"""
        return self._deep_merge(self.DEFAULT_PLOTLY_LAYOUT, self.plotly_layout)

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Глубокое слияние словарей"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _generate_view_switcher_html(self) -> str:
        """
        Генерирует HTML переключателя График/Таблица/Промпт

        Returns:
            HTML строка
        """
        if not self.show_table and not self.show_prompt:
            return ""

        buttons = '<button class="view-btn active" onclick="toggleView_{0}(\'chart\')">График</button>'.format(
            self.chart_id)

        if self.show_table:
            buttons += '<button class="view-btn" onclick="toggleView_{0}(\'table\')">Таблица</button>'.format(
                self.chart_id)

        if self.show_prompt:
            buttons += '<button class="view-btn" onclick="toggleView_{0}(\'prompt\')">Промпт</button>'.format(
                self.chart_id)

        return f'''
        <div class="view-switcher">
            {buttons}
        </div>
        '''

    def _generate_detail_selector_html(self) -> str:
        """
        Генерирует HTML переключателя детализации с локальным переопределением.

        Логика:
        - По умолчанию кнопки синхронизируются с глобальным фильтром
        - При клике на локальную кнопку - устанавливается локальный уровень только для этого графика
        - Глобальный фильтр не меняется, соседние графики не затрагиваются

        Returns:
            HTML строка
        """
        return f'''
        <div class="detail-selector" id="detail_selector_{self.chart_id}">
            <button class="detail-btn" data-level="year" onclick="setLocalDetailLevel_{self.chart_id}('year')">Год</button>
            <button class="detail-btn active" data-level="month" onclick="setLocalDetailLevel_{self.chart_id}('month')">Месяц</button>
            <button class="detail-btn" data-level="week" onclick="setLocalDetailLevel_{self.chart_id}('week')">Неделя</button>
            <button class="detail-btn" data-level="day" onclick="setLocalDetailLevel_{self.chart_id}('day')">День</button>
        </div>
        '''

    def _generate_top_controls_row_html(self) -> str:
        """
        Генерирует HTML верхней строки с основными контролами:
        - График/Таблица/Промпт
        - Год/Месяц/Неделя/День

        Returns:
            HTML строка
        """
        view_switcher = self._generate_view_switcher_html()
        detail_selector = self._generate_detail_selector_html()

        if not view_switcher and not detail_selector:
            return ""

        return f'''
        <div class="top-controls-row">
            {view_switcher}
            {detail_selector}
        </div>
        '''

    def _generate_local_filters_html(self) -> str:
        """
        Генерирует HTML для локальных фильтров

        Типы фильтров:
        - date_range: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
        - select: {'options': [...], 'multiple': bool, 'label': str}
        - checkbox: {'label': str, 'checked': bool}
        - buttons: {'options': [...], 'labels': {...}, 'default': str}
        - custom: {'html': str}
        """
        if not self.local_filters:
            return ""

        filters_html = '<div class="local-filters">'
        filters_html += '<div class="local-filters-title">Фильтры графика:</div>'
        filters_html += '<div class="local-filters-grid">'

        has_buttons_only = len(self.local_filters) == 1 and list(self.local_filters.values())[0].get('type') == 'buttons'

        for filter_name, filter_config in self.local_filters.items():
            filter_id = f"{self.chart_id}_{filter_name}"

            # Date range
            if filter_name == 'date_range' or filter_config.get('type') == 'date_range':
                filters_html += f'''
                <div class="local-filter-group">
                    <label>Дата начала:</label>
                    <input type="date" id="{filter_id}_start" class="local-filter-input">
                </div>
                <div class="local-filter-group">
                    <label>Дата окончания:</label>
                    <input type="date" id="{filter_id}_end" class="local-filter-input">
                </div>
                '''

            # Select
            elif filter_config.get('type') == 'select':
                label = filter_config.get('label', filter_name)
                options = filter_config.get('options', [])
                multiple = 'multiple' if filter_config.get('multiple', False) else ''
                size = f"size=\"{filter_config.get('size', 3)}\"" if multiple else ''

                options_html = '<option value="">Все</option>'
                for opt in options:
                    options_html += f'<option value="{opt}">{opt}</option>'

                filters_html += f'''
                <div class="local-filter-group">
                    <label>{label}:</label>
                    <select id="{filter_id}" class="local-filter-select" {multiple} {size}>
                        {options_html}
                    </select>
                </div>
                '''

            # Checkbox
            elif filter_config.get('type') == 'checkbox':
                label = filter_config.get('label', filter_name)
                checked = 'checked' if filter_config.get('checked', False) else ''

                filters_html += f'''
                <div class="local-filter-group local-filter-checkbox">
                    <label>
                        <input type="checkbox" id="{filter_id}" class="local-filter-checkbox-input" {checked}>
                        {label}
                    </label>
                </div>
                '''

            # Buttons (for detail levels, etc)
            elif filter_config.get('type') == 'buttons':
                label = filter_config.get('label', filter_name)
                options = filter_config.get('options', [])
                labels = filter_config.get('labels', {})
                default = filter_config.get('default', options[0] if options else '')

                buttons_html = ''
                for opt in options:
                    active_class = ' active' if opt == default else ''
                    button_label = labels.get(opt, opt)
                    buttons_html += f'<button class="detail-btn{active_class}" data-level="{opt}" onclick="setLocalDetailLevel_{self.chart_id}(\'{opt}\')">{button_label}</button>'

                filters_html += f'''
                <div class="local-filter-group local-filter-buttons">
                    <span class="detail-label">{label}:</span>
                    <div class="detail-selector">
                        {buttons_html}
                    </div>
                </div>
                '''

            # Custom HTML
            elif filter_config.get('type') == 'custom':
                custom_html = filter_config.get('html', '')
                filters_html += f'<div class="local-filter-group">{custom_html}</div>'

        filters_html += '</div>'

        # Кнопка "Применить" только если есть фильтры кроме buttons
        if not has_buttons_only:
            filters_html += f'<button class="btn-apply-local" onclick="applyLocalFilters_{self.chart_id}()">Применить</button>'

        filters_html += '</div>'

        return filters_html

    def _generate_llm_comment_html(self) -> str:
        """
        Генерирует HTML блок с LLM комментарием
        Будет реализовано в ЭТАПЕ 5
        """
        if not self.llm_comment:
            return ""

        # TODO: Полная реализация в ЭТАПЕ 5
        return f'''
        <div class="llm-comment" style="background: #f0f8ff; border-left: 4px solid #4a90e2;
             padding: 15px; margin-top: 15px; border-radius: 8px;">
            <div style="display: flex; align-items: start; gap: 10px;">
                <div style="font-size: 20px;">💬</div>
                <div style="flex: 1; color: #2c3e50;">{self.llm_comment}</div>
            </div>
        </div>
        '''

    def _get_plotly_layout_json(self) -> str:
        """Возвращает Plotly layout в JSON формате"""
        layout = self._merge_plotly_layout()
        return json.dumps(layout, ensure_ascii=False)

    def _generate_detail_level_js(self) -> str:
        """
        Генерирует JS функции для переключения детализации.

        Локальная детализация:
        - setLocalDetailLevel_{chart_id}(level) - устанавливает локальный уровень для этого графика
        - getDetailLevel_{chart_id}() - возвращает актуальный уровень (локальный или глобальный)

        Returns:
            JS код функций
        """
        return f'''
        /**
         * Устанавливает ЛОКАЛЬНЫЙ уровень детализации для графика {self.chart_id}.
         * Не влияет на глобальный фильтр и другие графики.
         */
        function setLocalDetailLevel_{self.chart_id}(level) {{
            // Сохраняем локальный уровень в window
            window.localDetailLevel_{self.chart_id} = level;

            // Обновляем только кнопки этого графика
            const container = document.getElementById('detail_selector_{self.chart_id}');
            if (container) {{
                container.querySelectorAll('.detail-btn').forEach(btn => {{
                    btn.classList.toggle('active', btn.dataset.level === level);
                }});
            }}

            // Перерисовываем график
            if (typeof update{self.chart_id} === 'function') {{
                update{self.chart_id}();
            }}

            // Если открыта вкладка "Таблица" - пересчитываем таблицу
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none' && typeof generateTable_{self.chart_id} === 'function') {{
                generateTable_{self.chart_id}();
            }}

            console.log('🎯 Локальная детализация {self.chart_id}:', level);
        }}

        /**
         * Возвращает актуальный уровень детализации для графика {self.chart_id}.
         * Приоритет: локальный > глобальный > 'month'
         */
        function getDetailLevel_{self.chart_id}() {{
            return window.localDetailLevel_{self.chart_id} || window.globalDetailLevel || 'month';
        }}
        '''

    def _generate_local_filters_js(self) -> str:
        """
        Генерирует JS код для работы локальных фильтров

        Returns:
            JS код функции applyLocalFilters_{chart_id}
        """
        if not self.local_filters:
            return ""

        filter_logic = []

        for filter_name, filter_config in self.local_filters.items():
            filter_id = f"{self.chart_id}_{filter_name}"

            # Date range
            if filter_name == 'date_range' or filter_config.get('type') == 'date_range':
                filter_logic.append(f'''
                const startDate_{self.chart_id} = document.getElementById('{filter_id}_start').value;
                const endDate_{self.chart_id} = document.getElementById('{filter_id}_end').value;

                if (startDate_{self.chart_id}) {{
                    const start = new Date(startDate_{self.chart_id});
                    localData = localData.filter(row => {{
                        if (row.dateFired) {{
                            return row.dateFired >= start;
                        }}
                        return row.dateHired >= start;
                    }});
                }}

                if (endDate_{self.chart_id}) {{
                    const end = new Date(endDate_{self.chart_id});
                    localData = localData.filter(row => {{
                        if (row.dateFired) {{
                            return row.dateFired <= end;
                        }}
                        return row.dateHired <= end;
                    }});
                }}
                ''')

            # Select
            elif filter_config.get('type') == 'select':
                field = filter_config.get('field', filter_name)
                multiple = filter_config.get('multiple', False)

                if multiple:
                    filter_logic.append(f'''
                    const selected_{filter_name} = Array.from(document.getElementById('{filter_id}').selectedOptions)
                        .map(opt => opt.value)
                        .filter(v => v !== "");

                    if (selected_{filter_name}.length > 0) {{
                        localData = localData.filter(row => {{
                            const value = String(row['{field}']);
                            return selected_{filter_name}.includes(value);
                        }});
                    }}
                    ''')
                else:
                    filter_logic.append(f'''
                    const selected_{filter_name} = document.getElementById('{filter_id}').value;
                    if (selected_{filter_name}) {{
                        localData = localData.filter(row => String(row['{field}']) === selected_{filter_name});
                    }}
                    ''')

            # Checkbox
            elif filter_config.get('type') == 'checkbox':
                action = filter_config.get('action', '')
                if action:
                    filter_logic.append(f'''
                    const checked_{filter_name} = document.getElementById('{filter_id}').checked;
                    if (checked_{filter_name}) {{
                        {action}
                    }}
                    ''')

        filters_js = '\n'.join(filter_logic)

        return f'''
        function applyLocalFilters_{self.chart_id}() {{
            let localData = filteredData.slice(); // Копия глобально отфильтрованных данных

            {filters_js}

            console.log('🔍 Локальные фильтры {self.chart_id}:', localData.length, 'записей');

            // Сохраняем локально отфильтрованные данные
            window.localData_{self.chart_id} = localData;

            // Перерисовываем график
            update{self.chart_id.capitalize()}();
        }}
        '''

    def _generate_table_js(self) -> str:
        """
        Генерирует JS код для работы с таблицами и промптами

        Returns:
            JS код функций toggleView, generateTable, exportTable, промпт-функции
        """
        if not self.show_table and not self.show_prompt:
            return ""

        natural_sort_js = self._get_natural_sort_js()

        return f'''
        {natural_sort_js}

        function toggleView_{self.chart_id}(view) {{
            const chartDiv = document.getElementById('{self.chart_id}');
            const tableDiv = document.getElementById('{self.chart_id}_table');
            const promptDiv = document.getElementById('{self.chart_id}_prompt');

            const buttons = document.querySelectorAll('.chart-wrapper .view-btn');
            buttons.forEach(btn => btn.classList.remove('active'));

            if (view === 'chart') {{
                chartDiv.style.display = 'block';
                tableDiv.style.display = 'none';
                promptDiv.style.display = 'none';
                buttons[0].classList.add('active');
            }} else if (view === 'table') {{
                chartDiv.style.display = 'none';
                tableDiv.style.display = 'block';
                promptDiv.style.display = 'none';
                buttons[1].classList.add('active');
                // Сбрасываем кеш сортировки при переключении на таблицу
                window.sortedTableData_{self.chart_id} = null;
                currentSortColumn_{self.chart_id} = null;
                currentSortOrder_{self.chart_id} = 'asc';
                generateTable_{self.chart_id}();
            }} else if (view === 'prompt') {{
                chartDiv.style.display = 'none';
                tableDiv.style.display = 'none';
                promptDiv.style.display = 'block';
                const lastBtn = buttons[buttons.length - 1];
                lastBtn.classList.add('active');
                loadPrompt_{self.chart_id}();
            }}
        }}

        let isTransposed_{self.chart_id} = false;
        let currentSortColumn_{self.chart_id} = null;
        let currentSortOrder_{self.chart_id} = 'asc';

        function generateTable_{self.chart_id}() {{
            if (typeof getTableData_{self.chart_id} !== 'function') {{
                console.error('getTableData_{self.chart_id} function not defined');
                return;
            }}

            // Используем отсортированные данные если есть, иначе получаем новые
            const tableData = window.sortedTableData_{self.chart_id} || getTableData_{self.chart_id}();
            if (!tableData || tableData.length === 0) {{
                document.getElementById('{self.chart_id}_table').innerHTML = '<p style="padding: 20px;">Нет данных для отображения</p>';
                return;
            }}

            let html = '<div class="table-controls">';
            html += '<div class="table-info">' + (isTransposed_{self.chart_id} ? 'Транспонированный' : 'Строк: ' + tableData.length) + '</div>';
            html += '<div class="export-buttons">';
            html += '<button class="transpose-btn' + (isTransposed_{self.chart_id} ? ' active' : '') + '" onclick="transposeTable_{self.chart_id}()">⇄ Транспонировать</button>';
            html += '<button class="export-btn" onclick="exportTableToCSV_{self.chart_id}()">📥 CSV</button>';
            html += '<button class="export-btn" onclick="exportTableToExcel_{self.chart_id}()">📊 Excel</button>';
            html += '</div>';
            html += '</div>';

            html += '<div class="table-scroll-wrapper">';
            html += '<table class="chart-table">';

            const columns = Object.keys(tableData[0]);

            if (isTransposed_{self.chart_id}) {{
                // Транспонированный режим
                columns.forEach(col => {{
                    html += '<tr>';
                    html += '<th>' + col + '</th>';
                    tableData.forEach(row => {{
                        const value = row[col];
                        const displayValue = typeof value === 'number' ? value.toLocaleString('ru-RU') : value;
                        html += '<td>' + displayValue + '</td>';
                    }});
                    html += '</tr>';
                }});
            }} else {{
                // Обычный режим
                html += '<thead><tr>';
                columns.forEach(col => {{
                    const sortIndicator = currentSortColumn_{self.chart_id} === col
                        ? (currentSortOrder_{self.chart_id} === 'asc' ? ' ▲' : ' ▼')
                        : '';
                    html += '<th onclick="sortTable_{self.chart_id}(\\'' + col + '\\')">' + col + sortIndicator + '</th>';
                }});
                html += '</tr></thead>';

                html += '<tbody>';
                tableData.forEach(row => {{
                    html += '<tr>';
                    columns.forEach(col => {{
                        const value = row[col];
                        const displayValue = typeof value === 'number' ? value.toLocaleString('ru-RU') : value;
                        html += '<td>' + displayValue + '</td>';
                    }});
                    html += '</tr>';
                }});
                html += '</tbody>';
            }}

            html += '</table>';
            html += '</div>';

            document.getElementById('{self.chart_id}_table').innerHTML = html;
        }}

        function transposeTable_{self.chart_id}() {{
            isTransposed_{self.chart_id} = !isTransposed_{self.chart_id};
            generateTable_{self.chart_id}();
        }}

        function sortTable_{self.chart_id}(column) {{
            if (currentSortColumn_{self.chart_id} === column) {{
                currentSortOrder_{self.chart_id} = currentSortOrder_{self.chart_id} === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSortColumn_{self.chart_id} = column;
                currentSortOrder_{self.chart_id} = 'asc';
            }}

            const tableData = getTableData_{self.chart_id}();
            tableData.sort((a, b) => {{
                let aVal = a[column];
                let bVal = b[column];

                if (typeof aVal === 'number' && typeof bVal === 'number') {{
                    return currentSortOrder_{self.chart_id} === 'asc' ? aVal - bVal : bVal - aVal;
                }} else if (column === 'Период' && typeof aVal === 'string' && typeof bVal === 'string') {{
                    // Специальная сортировка для дат в формате DD.MM.YYYY
                    const parseDate = (dateStr) => {{
                        const parts = dateStr.split('.');
                        if (parts.length === 3) {{
                            return new Date(parts[2], parts[1] - 1, parts[0]);
                        }}
                        return new Date(0);
                    }};
                    const dateA = parseDate(aVal);
                    const dateB = parseDate(bVal);
                    return currentSortOrder_{self.chart_id} === 'asc' ? dateA - dateB : dateB - dateA;
                }} else {{
                    const comparison = naturalSort(aVal, bVal);
                    return currentSortOrder_{self.chart_id} === 'asc' ? comparison : -comparison;
                }}
            }});

            // Перезаписываем результат getTableData
            window.sortedTableData_{self.chart_id} = tableData;
            generateTable_{self.chart_id}();
        }}

        function exportTableToCSV_{self.chart_id}() {{
            const tableData = window.sortedTableData_{self.chart_id} || getTableData_{self.chart_id}();
            if (!tableData || tableData.length === 0) return;

            const columns = Object.keys(tableData[0]);
            let csv = columns.join(',') + '\\n';

            tableData.forEach(row => {{
                const values = columns.map(col => {{
                    const value = row[col];
                    return typeof value === 'string' && value.includes(',') ? '"' + value + '"' : value;
                }});
                csv += values.join(',') + '\\n';
            }});

            const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '{self.chart_id}_data.csv';
            link.click();
        }}

        function exportTableToExcel_{self.chart_id}() {{
            const tableData = window.sortedTableData_{self.chart_id} || getTableData_{self.chart_id}();
            if (!tableData || tableData.length === 0) return;

            const columns = Object.keys(tableData[0]);
            let html = '<table>';
            html += '<tr>' + columns.map(col => '<th>' + col + '</th>').join('') + '</tr>';

            tableData.forEach(row => {{
                html += '<tr>' + columns.map(col => '<td>' + row[col] + '</td>').join('') + '</tr>';
            }});
            html += '</table>';

            const blob = new Blob([html], {{ type: 'application/vnd.ms-excel' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '{self.chart_id}_data.xls';
            link.click();
        }}

        function loadPrompt_{self.chart_id}() {{
            // Используем встроенные промпты из promptTemplates
            let promptText = (typeof promptTemplates !== 'undefined' && promptTemplates['{self.chart_id}'])
                ? promptTemplates['{self.chart_id}']
                : 'Промпт не найден для этого графика';

            // Сразу подставляем данные в промпт
            const rowsLimit = document.getElementById('{self.chart_id}_rows_limit')?.value || '50';
            let tableData = typeof getTableData_{self.chart_id} === 'function' ? getTableData_{self.chart_id}() : [];
            if (rowsLimit !== 'all') {{
                tableData = tableData.slice(0, parseInt(rowsLimit));
            }}

            const dataStr = JSON.stringify(tableData, null, 2);
            const contextStr = typeof buildLLMContext === 'function' ? buildLLMContext('{self.chart_id}') : '';

            // Заменяем плейсхолдеры
            promptText = promptText
                .replace('{{context}}', contextStr)
                .replace('{{data}}', dataStr);

            document.getElementById('{self.chart_id}_prompt_text').value = promptText;
        }}

        function sendPrompt_{self.chart_id}() {{
            const promptText = document.getElementById('{self.chart_id}_prompt_text').value;
            const provider = document.querySelector('input[name="provider_{self.chart_id}"]:checked').value;
            const model = document.getElementById('{self.chart_id}_model').value;
            const rowsLimit = document.getElementById('{self.chart_id}_rows_limit').value;

            let tableData = getTableData_{self.chart_id}();
            if (rowsLimit !== 'all') {{
                tableData = tableData.slice(0, parseInt(rowsLimit));
            }}

            const dataStr = JSON.stringify(tableData, null, 2);
            // Используем функцию buildLLMContext для формирования контекста
            const contextStr = typeof buildLLMContext === 'function'
                ? buildLLMContext('{self.chart_id}')
                : '';

            const finalPrompt = promptText
                .replace('{{{{data}}}}', dataStr)
                .replace('{{{{context}}}}', contextStr);

            const apiUrl = provider === 'ollama'
                ? 'http://localhost:11434/api/generate'
                : 'http://localhost:1234/v1/chat/completions';

            document.getElementById('{self.chart_id}_llm_loading').style.display = 'block';
            document.getElementById('{self.chart_id}_llm_result').style.display = 'none';

            if (provider === 'ollama') {{
                fetch(apiUrl, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        model: model,
                        prompt: finalPrompt,
                        stream: false
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('{self.chart_id}_llm_loading').style.display = 'none';
                    document.getElementById('{self.chart_id}_llm_result').style.display = 'block';
                    document.getElementById('{self.chart_id}_llm_result').querySelector('.llm-result-text').innerHTML = window.formatMarkdown(data.response);
                }})
                .catch(error => {{
                    document.getElementById('{self.chart_id}_llm_loading').style.display = 'none';
                    console.error('Ошибка LLM:', error);
                    alert('Ошибка подключения к LLM: ' + error.message);
                }});
            }} else {{
                fetch(apiUrl, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        model: model,
                        messages: [{{ role: 'user', content: finalPrompt }}],
                        temperature: 0.7
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('{self.chart_id}_llm_loading').style.display = 'none';
                    document.getElementById('{self.chart_id}_llm_result').style.display = 'block';
                    document.getElementById('{self.chart_id}_llm_result').querySelector('.llm-result-text').innerHTML = window.formatMarkdown(data.choices[0].message.content);
                }})
                .catch(error => {{
                    document.getElementById('{self.chart_id}_llm_loading').style.display = 'none';
                    console.error('Ошибка LLM:', error);
                    alert('Ошибка подключения к LLM: ' + error.message);
                }});
            }}
        }}

        function savePrompt_{self.chart_id}() {{
            const promptText = document.getElementById('{self.chart_id}_prompt_text').value;
            const statusDiv = document.getElementById('{self.chart_id}_save_status');

            statusDiv.textContent = 'Сохранение промпта в файл prompts.json невозможно из браузера. Скопируйте текст вручную.';
            statusDiv.className = 'save-status error';
            statusDiv.style.display = 'block';

            setTimeout(() => {{
                statusDiv.style.display = 'none';
            }}, 3000);
        }}

        function resetPrompt_{self.chart_id}() {{
            loadPrompt_{self.chart_id}();
        }}
        '''

    def _get_natural_sort_js(self) -> str:
        """
        Генерирует JavaScript функцию для естественной сортировки
        (правильная сортировка текста с числами: Магазин 1, Магазин 2, ..., Магазин 10)

        Returns:
            JS код функции naturalSort
        """
        return '''
        function naturalSort(a, b) {
            const regex = /(\\d+)|(\\D+)/g;
            const aParts = String(a).match(regex) || [];
            const bParts = String(b).match(regex) || [];

            for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
                const aPart = aParts[i] || '';
                const bPart = bParts[i] || '';

                const aNum = parseInt(aPart);
                const bNum = parseInt(bPart);

                // Оба части - числа
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    if (aNum !== bNum) return aNum - bNum;
                }
                // Обычная строковая сортировка
                else {
                    if (aPart !== bPart) {
                        return aPart.localeCompare(bPart);
                    }
                }
            }

            return 0;
        }
        '''
