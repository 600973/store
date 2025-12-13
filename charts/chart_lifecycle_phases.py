# PROJECT_ROOT: charts/chart_lifecycle_phases.py
from charts.base_chart import BaseChart


class ChartLifecyclePhases(BaseChart):
    """Тепловая карта жизненного цикла магазинов (Индекс от пика)"""

    def __init__(self, chart_id='chart_lifecycle_phases', available_detail_levels=None,
                 metric_options=None, **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        self.available_detail_levels = available_detail_levels or ['year', 'month']
        self.metric_options = metric_options or [
            'Сумма в чеке', 'Число чеков', 'Количество в чеке', 'Наценка продажи в чеке'
        ]

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        metric_options_html = ''.join([
            f'<option value="{m}">{m}</option>' for m in self.metric_options
        ])

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {metric_options_html}
                </select>
            </div>
        </div>
        '''

    def get_html_container(self) -> str:
        css = self._merge_css_styles()
        style_str = '; '.join([f'{k}: {v}' for k, v in css.items()])

        detail_selector_html = self._generate_detail_selector_html()
        view_switcher_html = self._generate_view_switcher_html()
        llm_comment_html = self._generate_llm_comment_html()
        chart_selectors_html = self._generate_chart_selectors_html()

        return f'''
        <div class="chart-wrapper" style="{style_str}">
            {view_switcher_html}
            {chart_selectors_html}
            {detail_selector_html}

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
        {self._generate_detail_level_js()}

        const monthNameToNum_{self.chart_id} = {{
            'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4,
            'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
            'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12
        }};

        // Хранилище данных для таблицы
        window.heatmapData_{self.chart_id} = null;

        function update{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const level = getDetailLevel_{self.chart_id}();
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const metricField = metricSelect ? metricSelect.value : 'Сумма в чеке';

            // Агрегация: магазин -> период -> сумма метрики
            const storeData = {{}};

            data.forEach(row => {{
                const store = row['Магазин'];
                const year = parseInt(row['Год']);
                const monthName = row['Месяц'];
                const month = monthNameToNum_{self.chart_id}[monthName] || 1;
                const value = parseFloat(row[metricField]) || 0;

                if (!store || !year) return;

                let periodKey;
                if (level === 'year') {{
                    periodKey = `${{year}}`;
                }} else {{
                    periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;
                }}

                if (!storeData[store]) storeData[store] = {{}};
                if (!storeData[store][periodKey]) storeData[store][periodKey] = 0;
                storeData[store][periodKey] += value;
            }});

            // Сортировка магазинов по номеру
            const stores = Object.keys(storeData).sort((a, b) => {{
                const numA = parseInt(a.match(/\\d+/)) || 0;
                const numB = parseInt(b.match(/\\d+/)) || 0;
                return numA - numB;
            }});

            // Сортировка периодов
            const allPeriods = new Set();
            Object.values(storeData).forEach(periods => {{
                Object.keys(periods).forEach(p => allPeriods.add(p));
            }});

            const periods = [...allPeriods].sort((a, b) => {{
                if (level === 'year') return parseInt(a) - parseInt(b);
                const [d1, m1, y1] = a.split('.');
                const [d2, m2, y2] = b.split('.');
                return (parseInt(y1) * 12 + parseInt(m1)) - (parseInt(y2) * 12 + parseInt(m2));
            }});

            // Расчёт индекса от пика для каждого магазина
            const zValues = [];
            const hoverTexts = [];

            stores.forEach(store => {{
                const values = periods.map(p => storeData[store][p] || 0);
                const peak = Math.max(...values);

                const row = [];
                const hoverRow = [];

                periods.forEach((period, i) => {{
                    const val = values[i];
                    const index = peak > 0 ? (val / peak) * 100 : 0;
                    row.push(index);
                    hoverRow.push(`<b>${{store}}</b><br>Период: ${{period}}<br>${{metricField}}: ${{val.toLocaleString('ru-RU')}}<br>Индекс от пика: ${{index.toFixed(1)}}%`);
                }});

                zValues.push(row);
                hoverTexts.push(hoverRow);
            }});

            // Сохраняем для таблицы
            window.heatmapData_{self.chart_id} = {{
                stores: stores,
                periods: periods,
                zValues: zValues,
                metricField: metricField
            }};

            const trace = {{
                x: periods,
                y: stores,
                z: zValues,
                type: 'heatmap',
                colorscale: 'RdYlGn',
                zmin: 50,
                zmax: 100,
                hoverinfo: 'text',
                text: hoverTexts,
                colorbar: {{
                    title: '% от пика',
                    ticksuffix: '%'
                }}
            }};

            const layout = {{
                title: `Жизненный цикл магазинов (Индекс от пика: ${{metricField}})`,
                xaxis: {{ title: null, type: 'category' }},
                yaxis: {{ title: null, type: 'category', autorange: 'reversed' }},
                height: 550
            }};

            Plotly.newPlot('{self.chart_id}', [trace], layout, {{responsive: true}});

            // Обновляем таблицу если открыта
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none') {{
                generateTable_{self.chart_id}();
            }}
        }}

        function getTableData_{self.chart_id}() {{
            const hd = window.heatmapData_{self.chart_id};
            if (!hd) return [];

            const tableData = [];
            hd.stores.forEach((store, i) => {{
                const row = {{ 'Магазин': store }};
                hd.periods.forEach((period, j) => {{
                    // Храним как число для правильной сортировки
                    row[period] = Math.round(hd.zValues[i][j] * 10) / 10;
                }});
                tableData.push(row);
            }});

            return tableData;
        }}
        """
