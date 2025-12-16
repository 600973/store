# PROJECT_ROOT: charts/chart_yoy_comparison.py
from charts.base_chart import BaseChart


class ChartYoYComparison(BaseChart):
    """Year-over-Year сравнение эффективности площади"""

    def __init__(self, chart_id='chart_yoy_comparison', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)
        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерирует селекторы для выбора магазина и метрики"""
        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Магазин:</label>
                <select id="{self.chart_id}_store" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="revenue_per_m2" selected>Выручка на м²</option>
                    <option value="profit_per_m2">Прибыль на м²</option>
                    <option value="margin">Маржинальность (%)</option>
                </select>
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
        const monthNames_{self.chart_id} = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
        const colors_{self.chart_id} = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51', '#8338EC', '#FB5607'];

        function update{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const storeSelect = document.getElementById('{self.chart_id}_store');
            const metricSelect = document.getElementById('{self.chart_id}_metric');

            // Заполняем список магазинов при первом запуске
            if (!storeSelect.options.length) {{
                const stores = [...new Set(data.map(r => r['Магазин']).filter(v => v))].sort((a, b) => {{
                    const numA = parseInt(a.match(/\\d+/)) || 0;
                    const numB = parseInt(b.match(/\\d+/)) || 0;
                    return numA - numB;
                }});

                stores.forEach(store => {{
                    const option = document.createElement('option');
                    option.value = store;
                    option.textContent = store;
                    storeSelect.appendChild(option);
                }});
            }}

            const selectedStore = storeSelect.value;
            const selectedMetric = metricSelect.value;

            if (!selectedStore) return;

            // Фильтруем данные по магазину
            const storeData = data.filter(r => r['Магазин'] === selectedStore);

            // Группировка по годам и месяцам
            const yearMonthData = {{}};

            storeData.forEach(row => {{
                const dateStr = row['Дата'];
                if (!dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);

                if (!yearMonthData[year]) {{
                    yearMonthData[year] = {{}};
                    for (let m = 1; m <= 12; m++) {{
                        yearMonthData[year][m] = {{
                            revenue: 0,
                            profit: 0,
                            area: parseFloat(row['Торговая площадь магазина']) || 0
                        }};
                    }}
                }}

                yearMonthData[year][month].revenue += parseFloat(row['Сумма в чеке']) || 0;
                yearMonthData[year][month].profit += parseFloat(row['Наценка продажи в чеке']) || 0;
            }});

            // Сортируем года
            const years = Object.keys(yearMonthData).sort();

            // Создаём trace для каждого года
            const traces = years.map((year, idx) => {{
                const xValues = [];
                const yValues = [];

                for (let m = 1; m <= 12; m++) {{
                    const d = yearMonthData[year][m];

                    let value;
                    if (selectedMetric === 'revenue_per_m2') {{
                        value = d.area > 0 ? d.revenue / d.area : 0;
                    }} else if (selectedMetric === 'profit_per_m2') {{
                        value = d.area > 0 ? d.profit / d.area : 0;
                    }} else {{ // margin
                        value = d.revenue > 0 ? (d.profit / d.revenue) * 100 : 0;
                    }}

                    xValues.push(monthNames_{self.chart_id}[m - 1]);
                    yValues.push(value);
                }}

                return {{
                    x: xValues,
                    y: yValues,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: year,
                    line: {{ color: colors_{self.chart_id}[idx % colors_{self.chart_id}.length], width: 3 }},
                    marker: {{ size: 8 }}
                }};
            }});

            const metricNames = {{
                'revenue_per_m2': 'Выручка на м²',
                'profit_per_m2': 'Прибыль на м²',
                'margin': 'Маржинальность (%)'
            }};

            const layout = {{
                title: `Year-over-Year: ${{metricNames[selectedMetric]}} - ${{selectedStore}}`,
                xaxis: {{ title: 'Месяц', type: 'category' }},
                yaxis: {{ title: metricNames[selectedMetric] }},
                hovermode: 'x unified',
                showlegend: true,
                legend: {{
                    orientation: 'h',
                    x: 0.5,
                    xanchor: 'center',
                    y: -0.15,
                    bgcolor: 'rgba(255,255,255,0.8)'
                }},
                height: 500
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
            const storeSelect = document.getElementById('{self.chart_id}_store');
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const selectedStore = storeSelect.value;
            const selectedMetric = metricSelect.value;

            if (!selectedStore) return [];

            const storeData = data.filter(r => r['Магазин'] === selectedStore);
            const yearMonthData = {{}};

            storeData.forEach(row => {{
                const dateStr = row['Дата'];
                if (!dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);

                if (!yearMonthData[year]) {{
                    yearMonthData[year] = {{}};
                    for (let m = 1; m <= 12; m++) {{
                        yearMonthData[year][m] = {{
                            revenue: 0,
                            profit: 0,
                            area: parseFloat(row['Торговая площадь магазина']) || 0
                        }};
                    }}
                }}

                yearMonthData[year][month].revenue += parseFloat(row['Сумма в чеке']) || 0;
                yearMonthData[year][month].profit += parseFloat(row['Наценка продажи в чеке']) || 0;
            }});

            const years = Object.keys(yearMonthData).sort();

            const tableData = [];
            for (let m = 1; m <= 12; m++) {{
                const row = {{ 'Месяц': monthNames_{self.chart_id}[m - 1] }};

                years.forEach(year => {{
                    const d = yearMonthData[year][m];

                    let value;
                    if (selectedMetric === 'revenue_per_m2') {{
                        value = d.area > 0 ? d.revenue / d.area : 0;
                    }} else if (selectedMetric === 'profit_per_m2') {{
                        value = d.area > 0 ? d.profit / d.area : 0;
                    }} else {{
                        value = d.revenue > 0 ? (d.profit / d.revenue) * 100 : 0;
                    }}

                    row[year] = Math.round(value * 100) / 100;
                }});

                tableData.push(row);
            }}

            return tableData;
        }}
        """
