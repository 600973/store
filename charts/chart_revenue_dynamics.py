# PROJECT_ROOT: charts/chart_revenue_dynamics.py
from charts.base_chart import BaseChart
import json


class ChartRevenueDynamics(BaseChart):
    def __init__(self, chart_id='chart_revenue_dynamics', available_detail_levels=None,
                 metric_options=None, group_by_options=None,
                 default_group_by=None, default_display_mode='absolute', default_show_labels=False,
                 **kwargs):
        """
        Args:
            metric_options: список колонок для выбора метрики, например ['Число чеков', 'Сумма в чеках продажи']
            group_by_options: список колонок для группировки, например ['Магазин', 'Товар', 'Тип']
            default_group_by: начальное значение группировки (по умолчанию первый из group_by_options)
            default_display_mode: 'absolute' или 'percent' (по умолчанию 'absolute')
            default_show_labels: показывать значения по умолчанию (по умолчанию False)
        """
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        self.available_detail_levels = available_detail_levels or ['year', 'month']
        self.metric_options = metric_options or ['Число чеков', 'Количество в чеке', 'Сумма в чеке', 'Наценка продажи в чеке']
        self.group_by_options = group_by_options or ['Товар', 'Тип', 'Магазин']
        self.default_group_by = default_group_by or self.group_by_options[0]
        self.default_display_mode = default_display_mode
        self.default_show_labels = default_show_labels

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерирует HTML для выпадающих списков метрики и группировки"""
        metric_options_html = ''.join([
            f'<option value="{m}">{m}</option>' for m in self.metric_options
        ])

        group_options_html = ''.join([
            f'<option value="{g}"{"selected" if g == self.default_group_by else ""}>{g}</option>' for g in self.group_by_options
        ])

        absolute_selected = 'selected' if self.default_display_mode == 'absolute' else ''
        percent_selected = 'selected' if self.default_display_mode == 'percent' else ''
        checkbox_checked = 'checked' if self.default_show_labels else ''

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Группировка:</label>
                <select id="{self.chart_id}_groupby" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {group_options_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {metric_options_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Отображение:</label>
                <select id="{self.chart_id}_display_mode" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="absolute" {absolute_selected}>Абсолютные значения</option>
                    <option value="percent" {percent_selected}>Доля (%)</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="display: flex; align-items: center; gap: 6px; font-weight: 500; font-size: 13px; color: #495057; cursor: pointer;">
                    <input type="checkbox" id="{self.chart_id}_show_labels" onchange="update{self.chart_id}()" {checkbox_checked} style="width: 16px; height: 16px; cursor: pointer;">
                    Показать значения
                </label>
            </div>
        </div>
        '''

    def get_html_container(self) -> str:
        """Переопределяем для добавления селекторов"""
        css = self._merge_css_styles()
        style_str = '; '.join([f'{k}: {v}' for k, v in css.items()])

        detail_selector_html = self._generate_detail_selector_html()
        local_filters_html = self._generate_local_filters_html()
        view_switcher_html = self._generate_view_switcher_html()
        llm_comment_html = self._generate_llm_comment_html()
        chart_selectors_html = self._generate_chart_selectors_html()

        return f'''
        <div class="chart-wrapper" style="{style_str}">
            {view_switcher_html}
            {chart_selectors_html}
            {detail_selector_html}
            {local_filters_html}

            <!-- ОТВЕТ LLM -->
            <div id="{self.chart_id}_llm_result" class="llm-result" style="display: none;">
                <div class="llm-result-controls">
                    <button class="llm-result-toggle" onclick="this.closest('.llm-result').querySelector('.llm-result-text').classList.toggle('collapsed'); this.textContent = this.textContent === '−' ? '+' : '−'">−</button>
                    <button class="llm-result-close" onclick="document.getElementById('{self.chart_id}_llm_result').style.display='none'">✕</button>
                </div>
                <div class="llm-result-text {self.ai_view_mode}" style="--max-lines: {self.ai_max_lines};"></div>
            </div>
            <div id="{self.chart_id}_llm_loading" class="llm-loading" style="display: none;">Генерация ответа...</div>

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
                    <button class="btn-prompt-action btn-send" onclick="sendPrompt_{self.chart_id}()">Отправить в LLM</button>
                    <button class="btn-prompt-action btn-save" onclick="savePrompt_{self.chart_id}()">Сохранить промпт</button>
                    <button class="btn-prompt-action btn-reset" onclick="resetPrompt_{self.chart_id}()">Сбросить</button>
                </div>
                <div id="{self.chart_id}_save_status" class="save-status" style="display: none;"></div>
            </div>
            {llm_comment_html}
        </div>
        '''

    def get_js_code(self):
        return f"""
        {self._generate_detail_level_js()}

        function update{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const level = getDetailLevel_{self.chart_id}();

            // Получаем выбранные значения из селекторов
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const groupBySelect = document.getElementById('{self.chart_id}_groupby');
            const displayModeSelect = document.getElementById('{self.chart_id}_display_mode');

            const metricField = metricSelect ? metricSelect.value : 'Число чеков';
            const groupByField = groupBySelect ? groupBySelect.value : 'Товар';
            const displayMode = displayModeSelect ? displayModeSelect.value : 'absolute';

            const showLabelsCheckbox = document.getElementById('{self.chart_id}_show_labels');
            const showLabels = showLabelsCheckbox ? showLabelsCheckbox.checked : false;

            console.log('update{self.chart_id}: данных:', data.length, 'метрика:', metricField, 'группировка:', groupByField, 'режим:', displayMode, 'метки:', showLabels);

            // Группировка по периодам и выбранному полю
            const periodData = {{}};
            const periodTotals = {{}};

            data.forEach(row => {{
                const dateStr = row['Дата'];
                const groupValue = row[groupByField];
                // Для метрики "Число чеков" используем хелпер с учётом группировки
                const metricValue = metricField === 'Число чеков'
                    ? getChecksValue(row, groupByField)
                    : (parseFloat(row[metricField]) || 0);

                if (!dateStr || !groupValue) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const day = parseInt(parts[0]);
                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);
                const date = new Date(year, month - 1, day);

                let periodKey;
                switch(level) {{
                    case 'year':
                        periodKey = `01.01.${{year}}`;
                        break;
                    case 'week':
                        const weekNum = window.getWeekNumber ? window.getWeekNumber(date) : Math.ceil((day + new Date(year, month - 1, 1).getDay()) / 7);
                        const firstDayOfWeek = new Date(year, 0, 1 + (weekNum - 1) * 7);
                        periodKey = `${{String(firstDayOfWeek.getDate()).padStart(2, '0')}}.${{String(firstDayOfWeek.getMonth() + 1).padStart(2, '0')}}.${{firstDayOfWeek.getFullYear()}}`;
                        break;
                    case 'day':
                        periodKey = dateStr;
                        break;
                    case 'month':
                    default:
                        periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;
                        break;
                }}

                if (!periodData[periodKey]) {{
                    periodData[periodKey] = {{}};
                    periodTotals[periodKey] = 0;
                }}

                if (!periodData[periodKey][groupValue]) {{
                    periodData[periodKey][groupValue] = 0;
                }}

                periodData[periodKey][groupValue] += metricValue;
                periodTotals[periodKey] += metricValue;
            }});

            // Сортируем периоды
            const periods = Object.keys(periodData).sort((a, b) => {{
                const parseDate = (dateStr) => {{
                    const parts = dateStr.split('.');
                    if (parts.length === 3) return new Date(parts[2], parts[1] - 1, parts[0]);
                    return new Date(0);
                }};
                return parseDate(a) - parseDate(b);
            }});

            // Получаем уникальные значения группировки
            const groups = [...new Set(data.map(r => r[groupByField]).filter(v => v))].sort((a, b) => {{
                const numA = parseInt(String(a).match(/\\d+/));
                const numB = parseInt(String(b).match(/\\d+/));
                if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
                return String(a).localeCompare(String(b));
            }});

            // Создаём traces для stacked area
            const traces = groups.map((group, groupIndex) => {{
                const yValues = periods.map(period => {{
                    const val = periodData[period][group] || 0;
                    if (displayMode === 'percent') {{
                        const total = periodTotals[period] || 1;
                        return (val / total) * 100;
                    }}
                    return val;
                }});

                // Сохраняем абсолютные значения для hover
                const absValues = periods.map(period => periodData[period][group] || 0);

                return {{
                    x: periods,
                    y: yValues,
                    customdata: absValues,
                    type: 'scatter',
                    mode: 'lines',
                    fill: 'tonexty',
                    stackgroup: 'one',
                    groupnorm: displayMode === 'percent' ? 'percent' : '',
                    name: String(group),
                    hovertemplate: displayMode === 'percent'
                        ? '<b>%{{fullData.name}}</b><br>Период: %{{x}}<br>Доля: %{{y:.1f}}%<br>' + metricField + ': %{{customdata:,.0f}}<extra></extra>'
                        : '<b>%{{fullData.name}}</b><br>Период: %{{x}}<br>' + metricField + ': %{{y:,.0f}}<extra></extra>'
                }};
            }});

            // Добавляем аннотации для меток в центре каждого сектора
            const annotations = [];
            if (showLabels) {{
                periods.forEach((period, periodIndex) => {{
                    let cumulative = 0;
                    groups.forEach(group => {{
                        const val = periodData[period][group] || 0;
                        const total = periodTotals[period] || 1;

                        let height, midPoint;
                        if (displayMode === 'percent') {{
                            height = (val / total) * 100;
                            midPoint = cumulative + height / 2;
                        }} else {{
                            height = val;
                            midPoint = cumulative + height / 2;
                        }}

                        // Показываем метку только если сектор достаточно большой
                        const minHeight = displayMode === 'percent' ? 5 : (Math.max(...Object.values(periodTotals)) * 0.03);
                        if (height > minHeight) {{
                            const labelText = displayMode === 'percent'
                                ? height.toFixed(1) + '%'
                                : val.toLocaleString('ru-RU');

                            annotations.push({{
                                x: period,
                                y: midPoint,
                                text: labelText,
                                showarrow: false,
                                font: {{
                                    size: 10,
                                    color: '#333'
                                }},
                                xanchor: 'center',
                                yanchor: 'middle'
                            }});
                        }}

                        cumulative += height;
                    }});
                }});
            }}

            const levelNames = {{
                'year': 'по годам',
                'month': 'по месяцам',
                'week': 'по неделям',
                'day': 'по дням'
            }};

            const modeLabel = displayMode === 'percent' ? ', доля %' : '';

            const layout = {{
                title: `Динамика "${{metricField}}" по "${{groupByField}}" (${{levelNames[level] || 'по месяцам'}}${{modeLabel}})`,
                xaxis: {{
                    type: 'category'
                }},
                yaxis: {{
                    tickformat: displayMode === 'percent' ? '.0f' : ',.0f',
                    range: displayMode === 'percent' ? [0, 100] : undefined
                }},
                margin: {{
                    t: 50,
                    b: 50
                }},
                hovermode: 'x unified',
                showlegend: true,
                legend: {{
                    orientation: 'v',
                    x: 1.02,
                    y: 1,
                    bgcolor: 'rgba(255,255,255,0.8)'
                }},
                annotations: annotations
            }};

            Plotly.newPlot('{self.chart_id}', traces, layout, {{responsive: true}});

            // Обновляем таблицу если открыта
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none') {{
                generateTable_{self.chart_id}();
            }}
        }}

        function getTableData_{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const level = getDetailLevel_{self.chart_id}();

            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const groupBySelect = document.getElementById('{self.chart_id}_groupby');

            const metricField = metricSelect ? metricSelect.value : 'Число чеков';
            const groupByField = groupBySelect ? groupBySelect.value : 'Товар';

            const periodData = {{}};

            data.forEach(row => {{
                const dateStr = row['Дата'];
                const groupValue = row[groupByField];
                // Для метрики "Число чеков" используем хелпер с учётом группировки
                const metricValue = metricField === 'Число чеков'
                    ? getChecksValue(row, groupByField)
                    : (parseFloat(row[metricField]) || 0);

                if (!dateStr || !groupValue) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const day = parseInt(parts[0]);
                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);
                const date = new Date(year, month - 1, day);

                let periodKey;
                switch(level) {{
                    case 'year':
                        periodKey = `01.01.${{year}}`;
                        break;
                    case 'week':
                        const weekNum = window.getWeekNumber ? window.getWeekNumber(date) : Math.ceil((day + new Date(year, month - 1, 1).getDay()) / 7);
                        const firstDayOfWeek = new Date(year, 0, 1 + (weekNum - 1) * 7);
                        periodKey = `${{String(firstDayOfWeek.getDate()).padStart(2, '0')}}.${{String(firstDayOfWeek.getMonth() + 1).padStart(2, '0')}}.${{firstDayOfWeek.getFullYear()}}`;
                        break;
                    case 'day':
                        periodKey = dateStr;
                        break;
                    case 'month':
                    default:
                        periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;
                        break;
                }}

                if (!periodData[periodKey]) {{
                    periodData[periodKey] = {{}};
                }}

                if (!periodData[periodKey][groupValue]) {{
                    periodData[periodKey][groupValue] = 0;
                }}

                periodData[periodKey][groupValue] += metricValue;
            }});

            const periods = Object.keys(periodData).sort((a, b) => {{
                const parseDate = (dateStr) => {{
                    const parts = dateStr.split('.');
                    if (parts.length === 3) return new Date(parts[2], parts[1] - 1, parts[0]);
                    return new Date(0);
                }};
                return parseDate(a) - parseDate(b);
            }});

            const groups = [...new Set(data.map(r => r[groupByField]).filter(v => v))].sort((a, b) => {{
                const numA = parseInt(String(a).match(/\\d+/));
                const numB = parseInt(String(b).match(/\\d+/));
                if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
                return String(a).localeCompare(String(b));
            }});

            const tableData = periods.map(period => {{
                const row = {{'Период': period}};
                groups.forEach(group => {{
                    row[group] = periodData[period][group] || 0;
                }});
                return row;
            }});

            return tableData;
        }}
        """
