# PROJECT_ROOT: charts/chart_seasonal_patterns.py
from charts.base_chart import BaseChart


class ChartSeasonalPatterns(BaseChart):
    """Heatmap сезонных паттернов по месяцам и магазинам"""

    def __init__(self, chart_id='chart_seasonal_patterns', default_show_labels=False, **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)
        self.default_show_labels = default_show_labels
        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерирует селекторы для выбора метрики, фильтров и отображения меток"""
        checkbox_checked = 'checked' if self.default_show_labels else ''

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap; align-items: center;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="Сумма в чеке" selected>Сумма в чеке</option>
                    <option value="Число чеков">Число чеков</option>
                    <option value="Количество в чеке">Количество в чеке</option>
                    <option value="Наценка продажи в чеке">Наценка продажи в чеке</option>
                    <option value="revenue_per_m2">Выручка на м²</option>
                    <option value="profit_per_m2">Прибыль на м²</option>
                    <option value="margin">Маржинальность (%)</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Группировка:</label>
                <select id="{self.chart_id}_groupby" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="Магазин" selected>Магазин</option>
                    <option value="Тип">Тип</option>
                    <option value="Товар">Товар</option>
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
        css = self._merge_css_styles()
        style_str = '; '.join([f'{k}: {v}' for k, v in css.items()])

        view_switcher_html = self._generate_view_switcher_html()
        llm_comment_html = self._generate_llm_comment_html()
        chart_selectors_html = self._generate_chart_selectors_html()

        return f'''
        <div class="chart-wrapper" style="{style_str}">
            {view_switcher_html}
            {chart_selectors_html}

            <div id="{self.chart_id}_llm_result" class="llm-result" style="display: none;">
                <div class="llm-result-controls">
                    <button class="llm-result-toggle" onclick="this.closest('.llm-result').querySelector('.llm-result-text').classList.toggle('collapsed'); this.textContent = this.textContent === '−' ? '+' : '−'">−</button>
                    <button class="llm-result-close" onclick="document.getElementById('{self.chart_id}_llm_result').style.display='none'">✕</button>
                </div>
                <div class="llm-result-text {self.ai_view_mode}" style="--max-lines: {self.ai_max_lines};"></div>
            </div>
            <div id="{self.chart_id}_llm_loading" class="llm-loading" style="display: none;">Генерация ответа...</div>

            <div id="{self.chart_id}" style="width: 100%; height: 100%;"></div>
            <div id="{self.chart_id}_table" class="chart-table-container" style="display: none;"></div>
            <div id="{self.chart_id}_prompt" class="prompt-container" style="display: none;">
                <div class="prompt-header">
                    <div class="provider-selector">
                        <label><input type="radio" name="provider_{self.chart_id}" value="ollama" checked> Ollama</label>
                        <label><input type="radio" name="provider_{self.chart_id}" value="lmstudio"> LM Studio</label>
                    </div>
                    <div class="model-selector">
                        <label>Модель:</label>
                        <select id="{self.chart_id}_model" class="model-select">
                            <option value="qwen2.5:7b" selected>qwen2.5:7b</option>
                            <option value="qwen2.5-coder:7b">qwen2.5-coder:7b</option>
                            <option value="qwen3:14b">qwen3:14b</option>
                        </select>
                    </div>
                    <div class="prompt-rows-selector">
                        <label>Строк:</label>
                        <select id="{self.chart_id}_rows_limit" class="model-select">
                            <option value="10">10</option>
                            <option value="50">50</option>
                            <option value="all" selected>Все</option>
                        </select>
                    </div>
                </div>
                <textarea id="{self.chart_id}_prompt_text" class="prompt-textarea" rows="12"></textarea>
                <div class="prompt-actions">
                    <button class="btn-prompt-action btn-send" onclick="sendPrompt_{self.chart_id}()">Отправить</button>
                    <button class="btn-prompt-action btn-save" onclick="savePrompt_{self.chart_id}()">Сохранить</button>
                    <button class="btn-prompt-action btn-reset" onclick="resetPrompt_{self.chart_id}()">Сбросить</button>
                </div>
                <div id="{self.chart_id}_save_status" class="save-status" style="display: none;"></div>
            </div>
            {llm_comment_html}
        </div>
        '''

    def get_js_code(self):
        return f"""
        function update{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const groupBySelect = document.getElementById('{self.chart_id}_groupby');
            const showLabelsCheckbox = document.getElementById('{self.chart_id}_show_labels');

            const selectedMetric = metricSelect.value;
            const groupBy = groupBySelect ? groupBySelect.value : 'Магазин';
            const showLabels = showLabelsCheckbox ? showLabelsCheckbox.checked : false;

            // Группировка: groupKey -> period (01.MM.YYYY) -> данные
            const groupPeriodData = {{}};
            const allPeriods = new Set();

            data.forEach(row => {{
                const groupKey = row[groupBy];
                const dateStr = row['Дата'];
                if (!groupKey || !dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const month = parts[1].padStart(2, '0');
                const year = parts[2];
                const period = `01.${{month}}.${{year}}`;
                allPeriods.add(period);

                const revenue = parseFloat(row['Сумма в чеке']) || 0;
                const profit = parseFloat(row['Наценка продажи в чеке']) || 0;
                // Используем глобальный хелпер для получения корректного значения чеков
                const checks = getChecksValue(row, groupBy);
                const quantity = parseFloat(row['Количество в чеке']) || 0;
                const area = parseFloat(row['Торговая площадь магазина']) || 0;

                if (!groupPeriodData[groupKey]) {{
                    groupPeriodData[groupKey] = {{}};
                }}
                if (!groupPeriodData[groupKey][period]) {{
                    groupPeriodData[groupKey][period] = {{ revenue: [], profit: [], checks: [], quantity: [], area: area }};
                }}

                groupPeriodData[groupKey][period].revenue.push(revenue);
                groupPeriodData[groupKey][period].profit.push(profit);
                groupPeriodData[groupKey][period].checks.push(checks);
                groupPeriodData[groupKey][period].quantity.push(quantity);
            }});

            // Сортируем периоды хронологически
            const periods = [...allPeriods].sort((a, b) => {{
                const [d1, m1, y1] = a.split('.');
                const [d2, m2, y2] = b.split('.');
                return (parseInt(y1) * 12 + parseInt(m1)) - (parseInt(y2) * 12 + parseInt(m2));
            }});

            // Сортируем группы
            const groups = Object.keys(groupPeriodData).sort((a, b) => {{
                if (groupBy === 'Магазин') {{
                    const numA = parseInt(a.match(/\\d+/)) || 0;
                    const numB = parseInt(b.match(/\\d+/)) || 0;
                    return numA - numB;
                }}
                return a.localeCompare(b, 'ru');
            }});

            // Вычисляем средние значения
            const zValues = [];
            const hoverTexts = [];

            groups.forEach(group => {{
                const row = [];
                const hoverRow = [];

                periods.forEach(period => {{
                    const periodData = groupPeriodData[group][period];

                    if (!periodData) {{
                        row.push(null);
                        hoverRow.push(`<b>${{group}}</b><br>Период: ${{period}}<br>Нет данных`);
                        return;
                    }}

                    const area = periodData.area;
                    let values;

                    if (selectedMetric === 'Сумма в чеке') {{
                        values = periodData.revenue;
                    }} else if (selectedMetric === 'Число чеков') {{
                        values = periodData.checks;
                    }} else if (selectedMetric === 'Количество в чеке') {{
                        values = periodData.quantity;
                    }} else if (selectedMetric === 'Наценка продажи в чеке') {{
                        values = periodData.profit;
                    }} else if (selectedMetric === 'revenue_per_m2') {{
                        values = area > 0 ? periodData.revenue.map(r => r / area) : [];
                    }} else if (selectedMetric === 'profit_per_m2') {{
                        values = area > 0 ? periodData.profit.map(p => p / area) : [];
                    }} else {{ // margin
                        values = periodData.revenue.map((r, i) => {{
                            return r > 0 ? (periodData.profit[i] / r) * 100 : 0;
                        }});
                    }}

                    // Для чеков используем сумму, для остальных метрик - среднее
                    const totalValue = values.length > 0 ? values.reduce((a, b) => a + b, 0) : 0;
                    const resultValue = selectedMetric === 'Число чеков'
                        ? totalValue
                        : (values.length > 0 ? totalValue / values.length : 0);
                    row.push(resultValue);
                    hoverRow.push(`<b>${{group}}</b><br>Період: ${{period}}<br>Значение: ${{resultValue.toFixed(1)}}`);
                }});

                zValues.push(row);
                hoverTexts.push(hoverRow);
            }});

            const metricNames = {{
                'Сумма в чеке': 'Сумма в чеке',
                'Число чеков': 'Число чеков',
                'Количество в чеке': 'Количество в чеке',
                'Наценка продажи в чеке': 'Наценка продажи в чеке',
                'revenue_per_m2': 'Выручка на м²',
                'profit_per_m2': 'Прибыль на м²',
                'margin': 'Маржинальность (%)'
            }};

            // Создаём аннотации для отображения значений в ячейках
            const annotations = [];
            if (showLabels) {{
                const allValues = zValues.flat().filter(v => v !== null && !isNaN(v));
                const minVal = Math.min(...allValues);
                const maxVal = Math.max(...allValues);
                const range = maxVal - minVal;

                function getFontColor(normalizedVal) {{
                    // RdYlGn: красный(0) -> жёлтый(0.5) -> зелёный(1)
                    // Красная зона (0-0.35) - тёмный фон, нужен белый шрифт
                    // Жёлтая зона (0.35-0.65) - светлый фон, нужен чёрный шрифт
                    // Зелёная зона (0.65-1) - тёмный фон, нужен белый шрифт
                    if (normalizedVal <= 0.35) return 'white';
                    if (normalizedVal >= 0.65) return 'white';
                    return 'black';
                }}

                // Проверяем, является ли метрика процентной
                const isPercent = selectedMetric === 'margin';

                groups.forEach((group, i) => {{
                    periods.forEach((period, j) => {{
                        const val = zValues[i][j];
                        if (val === null) return;

                        let displayVal;
                        if (Math.abs(val) >= 1000000) {{
                            displayVal = (val / 1000000).toFixed(1) + 'M';
                        }} else if (Math.abs(val) >= 1000) {{
                            displayVal = (val / 1000).toFixed(1) + 'K';
                        }} else if (isPercent) {{
                            displayVal = val.toFixed(1) + '%';
                        }} else {{
                            displayVal = Math.round(val);
                        }}

                        const normalizedVal = range > 0 ? (val - minVal) / range : 0.5;
                        const fontColor = getFontColor(normalizedVal);

                        annotations.push({{
                            x: period,
                            y: group,
                            text: displayVal,
                            showarrow: false,
                            font: {{ color: fontColor, size: 9 }}
                        }});
                    }});
                }});
            }}

            // Определяем min и max для colorscale
            const allValidValues = zValues.flat().filter(v => v !== null && !isNaN(v));
            const zMin = Math.min(...allValidValues);
            const zMax = Math.max(...allValidValues);

            const trace = {{
                x: periods,
                y: groups,
                z: zValues,
                type: 'heatmap',
                colorscale: 'RdYlGn',
                zmin: zMin,
                zmax: zMax,
                hoverinfo: 'text',
                text: hoverTexts,
                colorbar: {{ title: metricNames[selectedMetric] }}
            }};

            const layout = {{
                title: `Сезонные паттерны: ${{metricNames[selectedMetric]}} (среднее) | по ${{groupBy}}`,
                xaxis: {{ title: 'Период', type: 'category', tickangle: -45 }},
                yaxis: {{ title: groupBy, type: 'category', autorange: 'reversed' }},
                height: 600,
                annotations: annotations
            }};

            Plotly.newPlot('{self.chart_id}', [trace], layout, {{responsive: true}});

            // Обновляем таблицу если открыта
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none') {{
                generateTable_{self.chart_id}();
            }}
        }}

        function getTableData_{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const groupBySelect = document.getElementById('{self.chart_id}_groupby');

            const selectedMetric = metricSelect.value;
            const groupBy = groupBySelect ? groupBySelect.value : 'Магазин';

            const groupPeriodData = {{}};
            const allPeriods = new Set();

            data.forEach(row => {{
                const groupKey = row[groupBy];
                const dateStr = row['Дата'];
                if (!groupKey || !dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const month = parts[1].padStart(2, '0');
                const year = parts[2];
                const period = `01.${{month}}.${{year}}`;
                allPeriods.add(period);

                const revenue = parseFloat(row['Сумма в чеке']) || 0;
                const profit = parseFloat(row['Наценка продажи в чеке']) || 0;
                // Используем глобальный хелпер для получения корректного значения чеков
                const checks = getChecksValue(row, groupBy);
                const quantity = parseFloat(row['Количество в чеке']) || 0;
                const area = parseFloat(row['Торговая площадь магазина']) || 0;

                if (!groupPeriodData[groupKey]) {{
                    groupPeriodData[groupKey] = {{}};
                }}
                if (!groupPeriodData[groupKey][period]) {{
                    groupPeriodData[groupKey][period] = {{ revenue: [], profit: [], checks: [], quantity: [], area: area }};
                }}

                groupPeriodData[groupKey][period].revenue.push(revenue);
                groupPeriodData[groupKey][period].profit.push(profit);
                groupPeriodData[groupKey][period].checks.push(checks);
                groupPeriodData[groupKey][period].quantity.push(quantity);
            }});

            const periods = [...allPeriods].sort((a, b) => {{
                const [d1, m1, y1] = a.split('.');
                const [d2, m2, y2] = b.split('.');
                return (parseInt(y1) * 12 + parseInt(m1)) - (parseInt(y2) * 12 + parseInt(m2));
            }});

            const groups = Object.keys(groupPeriodData).sort((a, b) => {{
                if (groupBy === 'Магазин') {{
                    const numA = parseInt(a.match(/\\d+/)) || 0;
                    const numB = parseInt(b.match(/\\d+/)) || 0;
                    return numA - numB;
                }}
                return a.localeCompare(b, 'ru');
            }});

            const tableData = groups.map(group => {{
                const row = {{}};
                row[groupBy] = group;

                periods.forEach(period => {{
                    const periodData = groupPeriodData[group][period];
                    if (!periodData) {{
                        row[period] = null;
                        return;
                    }}

                    const area = periodData.area;
                    let values;

                    if (selectedMetric === 'Сумма в чеке') {{
                        values = periodData.revenue;
                    }} else if (selectedMetric === 'Число чеков') {{
                        values = periodData.checks;
                    }} else if (selectedMetric === 'Количество в чеке') {{
                        values = periodData.quantity;
                    }} else if (selectedMetric === 'Наценка продажи в чеке') {{
                        values = periodData.profit;
                    }} else if (selectedMetric === 'revenue_per_m2') {{
                        values = area > 0 ? periodData.revenue.map(r => r / area) : [];
                    }} else if (selectedMetric === 'profit_per_m2') {{
                        values = area > 0 ? periodData.profit.map(p => p / area) : [];
                    }} else {{
                        values = periodData.revenue.map((r, i) => {{
                            return r > 0 ? (periodData.profit[i] / r) * 100 : 0;
                        }});
                    }}

                    const avgValue = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
                    row[period] = Math.round(avgValue * 100) / 100;
                }});

                return row;
            }});

            return tableData;
        }}
        """
