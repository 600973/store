# PROJECT_ROOT: charts/chart_weekly_sales.py
"""
График динамики продаж по неделям из одной точки роста
- Входной формат: Магазин | Нед 1 | Нед 2 | Нед 3 | ...
- Все магазины начинают с Недели 1 (момент открытия)
- Производные метрики: рост %, индекс роста, кумулятивная сумма, скользящее среднее
- Сравнительные линии: средняя, медиана, коридор min-max
"""
from charts.base_chart import BaseChart


class ChartWeeklySales(BaseChart):
    """
    Динамика продаж по неделям из одной точки роста
    """

    def __init__(self, chart_id='chart_weekly_sales', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        self.metric_options = [
            ('revenue', 'Выручка'),
            ('growth_pct', 'Рост к пред. неделе (%)'),
            ('growth_index', 'Индекс роста (%)'),
            ('cumulative', 'Кумулятивная сумма'),
            ('moving_avg', 'Скользящее среднее (4 нед)')
        ]

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        metric_html = ''.join([
            f'<option value="{val}"{" selected" if val == "revenue" else ""}>{label}</option>'
            for val, label in self.metric_options
        ])

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap; align-items: center;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {metric_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Недели:</label>
                <select id="{self.chart_id}_week_from" onchange="update{self.chart_id}()" style="padding: 4px 8px; border: 1px solid #ced4da; border-radius: 6px; font-size: 12px; background: white;"></select>
                <span style="color: #6c757d;">—</span>
                <select id="{self.chart_id}_week_to" onchange="update{self.chart_id}()" style="padding: 4px 8px; border: 1px solid #ced4da; border-radius: 6px; font-size: 12px; background: white;"></select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Магазины:</label>
                <select id="{self.chart_id}_stores" multiple onchange="update{self.chart_id}()" style="padding: 4px 8px; border: 1px solid #ced4da; border-radius: 6px; font-size: 12px; background: white; min-width: 150px; max-width: 300px; height: 60px;">
                </select>
                <button onclick="selectAllStores_{self.chart_id}()" style="padding: 4px 8px; font-size: 11px; border: 1px solid #ced4da; border-radius: 4px; background: #fff; cursor: pointer;">Все</button>
                <button onclick="clearStores_{self.chart_id}()" style="padding: 4px 8px; font-size: 11px; border: 1px solid #ced4da; border-radius: 4px; background: #fff; cursor: pointer;">Сброс</button>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 12px;">
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showMean" checked onchange="update{self.chart_id}()"> Средняя</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showMedian" onchange="update{self.chart_id}()"> Медиана</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showCorridor" onchange="update{self.chart_id}()"> Коридор</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showTrend" onchange="update{self.chart_id}()"> Тренд</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showLabels" onchange="update{self.chart_id}()"> Значения</label>
            </div>
        </div>
        '''

    def _generate_detail_selector_html(self) -> str:
        return ''

    def _generate_table_js(self) -> str:
        return ''

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
                    <button class="llm-result-close" onclick="document.getElementById('{self.chart_id}_llm_result').style.display='none'">x</button>
                </div>
                <div class="llm-result-text {self.ai_view_mode}" style="--max-lines: {self.ai_max_lines};"></div>
            </div>
            <div id="{self.chart_id}_llm_loading" class="llm-loading" style="display: none;">Генерация ответа...</div>

            <div id="{self.chart_id}" style="width: 100%; height: 500px;"></div>
            <div id="{self.chart_id}_table" class="chart-table-container" style="width: 100%; display: none;"></div>
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
                        </select>
                    </div>
                </div>
                <textarea id="{self.chart_id}_prompt_text" class="prompt-textarea" rows="12" placeholder="Загрузка промпта..."></textarea>
                <div class="prompt-actions">
                    <button class="btn-prompt-action btn-send" onclick="sendPrompt_{self.chart_id}()">Отправить в LLM</button>
                    <button class="btn-prompt-action btn-reset" onclick="resetPrompt_{self.chart_id}()">Сбросить</button>
                </div>
            </div>
            {llm_comment_html}
        </div>
        '''

    def get_js_code(self):
        return f"""
        // =====================================================
        // WEEKLY SALES CHART - Динамика по неделям
        // =====================================================

        // Данные загружаются из window.weeklySalesData
        // Формат: {{ stores: ['Магазин 1', ...], weeks: ['Нед 1', ...], data: [[val, val, ...], ...] }}

        window.weeklySalesInitialized_{self.chart_id} = false;

        const storeColors_{self.chart_id} = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
        ];

        // Natural sort для правильной сортировки магазинов
        function naturalSort_{self.chart_id}(a, b) {{
            const regex = /(\\d+)|(\\D+)/g;
            const aParts = String(a).match(regex) || [];
            const bParts = String(b).match(regex) || [];
            for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {{
                const aPart = aParts[i] || '';
                const bPart = bParts[i] || '';
                const aNum = parseInt(aPart);
                const bNum = parseInt(bPart);
                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    if (aNum !== bNum) return aNum - bNum;
                }} else {{
                    if (aPart !== bPart) return aPart.localeCompare(bPart, 'ru');
                }}
            }}
            return 0;
        }}

        // Рассчитываем производные метрики
        function calculateDerivedMetrics_{self.chart_id}(data) {{
            const n_stores = data.length;
            const n_weeks = data[0]?.length || 0;

            // Рост к предыдущей неделе (%)
            const growth_pct = data.map(row => {{
                return row.map((val, j) => {{
                    if (j === 0 || val === null || row[j-1] === null || row[j-1] === 0) return null;
                    return ((val - row[j-1]) / row[j-1]) * 100;
                }});
            }});

            // Индекс роста (100% = первая неделя)
            const growth_index = data.map(row => {{
                const firstVal = row.find(v => v !== null && v > 0);
                if (!firstVal) return row.map(() => null);
                return row.map(val => val !== null ? (val / firstVal) * 100 : null);
            }});

            // Кумулятивная сумма
            const cumulative = data.map(row => {{
                let sum = 0;
                return row.map(val => {{
                    if (val !== null) sum += val;
                    return val !== null ? sum : null;
                }});
            }});

            // Скользящее среднее (4 недели)
            const moving_avg = data.map(row => {{
                return row.map((val, j) => {{
                    if (j < 3) return null;
                    const window = row.slice(j - 3, j + 1);
                    if (window.some(v => v === null)) return null;
                    return window.reduce((a, b) => a + b, 0) / 4;
                }});
            }});

            return {{
                revenue: data,
                growth_pct: growth_pct,
                growth_index: growth_index,
                cumulative: cumulative,
                moving_avg: moving_avg
            }};
        }}

        // Статистика по неделям
        function getAggregateStats_{self.chart_id}(data, storeIndices) {{
            const n_weeks = data[0]?.length || 0;
            const stats = {{ mean: [], median: [], min: [], max: [] }};

            for (let j = 0; j < n_weeks; j++) {{
                const values = storeIndices
                    .map(i => data[i]?.[j])
                    .filter(v => v !== null && v !== undefined && !isNaN(v));

                if (values.length > 0) {{
                    stats.mean.push(values.reduce((a, b) => a + b, 0) / values.length);
                    stats.median.push(values.sort((a, b) => a - b)[Math.floor(values.length / 2)]);
                    stats.min.push(Math.min(...values));
                    stats.max.push(Math.max(...values));
                }} else {{
                    stats.mean.push(null);
                    stats.median.push(null);
                    stats.min.push(null);
                    stats.max.push(null);
                }}
            }}
            return stats;
        }}

        // Линейная регрессия для тренда
        function linearRegression_{self.chart_id}(xArr, yArr) {{
            const n = xArr.length;
            if (n < 2) return null;

            let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
            for (let i = 0; i < n; i++) {{
                sumX += xArr[i];
                sumY += yArr[i];
                sumXY += xArr[i] * yArr[i];
                sumXX += xArr[i] * xArr[i];
            }}

            const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
            const intercept = (sumY - slope * sumX) / n;

            // R²
            const yMean = sumY / n;
            let ssRes = 0, ssTot = 0;
            for (let i = 0; i < n; i++) {{
                const yPred = slope * xArr[i] + intercept;
                ssRes += (yArr[i] - yPred) ** 2;
                ssTot += (yArr[i] - yMean) ** 2;
            }}
            const r2 = ssTot > 0 ? 1 - ssRes / ssTot : 0;

            return {{ slope, intercept, r2 }};
        }}

        // Инициализация селекторов
        function initSelectors_{self.chart_id}() {{
            const wsData = window.weeklySalesData;
            if (!wsData) return;

            const storesSelect = document.getElementById('{self.chart_id}_stores');
            const weekFromSelect = document.getElementById('{self.chart_id}_week_from');
            const weekToSelect = document.getElementById('{self.chart_id}_week_to');

            if (!window.weeklySalesInitialized_{self.chart_id}) {{
                // Магазины
                storesSelect.innerHTML = '';
                wsData.stores.sort(naturalSort_{self.chart_id}).forEach((store, idx) => {{
                    const opt = document.createElement('option');
                    opt.value = idx;
                    opt.textContent = store;
                    opt.selected = idx < 5; // первые 5 по умолчанию
                    storesSelect.appendChild(opt);
                }});

                // Недели
                weekFromSelect.innerHTML = '';
                weekToSelect.innerHTML = '';
                wsData.weeks.forEach((week, idx) => {{
                    const optFrom = document.createElement('option');
                    optFrom.value = idx;
                    optFrom.textContent = week;
                    weekFromSelect.appendChild(optFrom);

                    const optTo = document.createElement('option');
                    optTo.value = idx;
                    optTo.textContent = week;
                    weekToSelect.appendChild(optTo);
                }});

                weekFromSelect.value = 0;
                weekToSelect.value = wsData.weeks.length - 1;

                window.weeklySalesInitialized_{self.chart_id} = true;
            }}
        }}

        function selectAllStores_{self.chart_id}() {{
            const select = document.getElementById('{self.chart_id}_stores');
            Array.from(select.options).forEach(o => o.selected = true);
            update{self.chart_id}();
        }}

        function clearStores_{self.chart_id}() {{
            const select = document.getElementById('{self.chart_id}_stores');
            Array.from(select.options).forEach(o => o.selected = false);
            update{self.chart_id}();
        }}

        // Переключатель видов
        function toggleView_{self.chart_id}(view) {{
            const chartDiv = document.getElementById('{self.chart_id}');
            const tableDiv = document.getElementById('{self.chart_id}_table');
            const promptDiv = document.getElementById('{self.chart_id}_prompt');
            const wrapper = chartDiv.closest('.chart-wrapper');
            const buttons = wrapper.querySelectorAll('.view-btn');

            buttons.forEach(btn => btn.classList.remove('active'));

            if (view === 'chart') {{
                chartDiv.style.display = 'block';
                tableDiv.style.display = 'none';
                if (promptDiv) promptDiv.style.display = 'none';
                buttons[0].classList.add('active');
            }} else if (view === 'table') {{
                chartDiv.style.display = 'none';
                tableDiv.style.display = 'block';
                if (promptDiv) promptDiv.style.display = 'none';
                buttons[1].classList.add('active');
                generateTable_{self.chart_id}();
            }} else if (view === 'prompt') {{
                chartDiv.style.display = 'none';
                tableDiv.style.display = 'none';
                if (promptDiv) promptDiv.style.display = 'block';
                buttons[2].classList.add('active');
            }}
        }}

        window.tableSortState_{self.chart_id} = {{ column: null, direction: 'desc' }};
        window.tableData_{self.chart_id} = [];

        function generateTable_{self.chart_id}() {{
            const tableData = window.tableData_{self.chart_id} || [];
            if (!tableData.length) {{
                document.getElementById('{self.chart_id}_table').innerHTML = '<p style="padding: 20px;">Нет данных</p>';
                return;
            }}

            const sortState = window.tableSortState_{self.chart_id};
            const sortedData = [...tableData];

            if (sortState.column) {{
                sortedData.sort((a, b) => {{
                    let valA = a[sortState.column];
                    let valB = b[sortState.column];
                    if (typeof valA === 'number' && typeof valB === 'number') {{
                        return sortState.direction === 'asc' ? valA - valB : valB - valA;
                    }}
                    const cmp = naturalSort_{self.chart_id}(valA, valB);
                    return sortState.direction === 'asc' ? cmp : -cmp;
                }});
            }}

            const columns = Object.keys(tableData[0]);
            let html = '<div class="table-scroll-wrapper"><table class="chart-table">';

            html += '<thead><tr>' + columns.map((c, idx) => {{
                const isActive = sortState.column === c;
                const arrow = isActive ? (sortState.direction === 'asc' ? ' ↑' : ' ↓') : '';
                const style = 'cursor: pointer;' + (isActive ? ' background: #e3f2fd;' : '');
                return `<th style="${{style}}" onclick="sortTable_{self.chart_id}('${{c}}')">${{c}}${{arrow}}</th>`;
            }}).join('') + '</tr></thead>';

            html += '<tbody>';
            sortedData.forEach(row => {{
                html += '<tr>' + columns.map(c => {{
                    const val = row[c];
                    if (typeof val === 'number') {{
                        return '<td>' + val.toLocaleString('ru-RU', {{maximumFractionDigits: 1}}) + '</td>';
                    }}
                    return '<td>' + (val || '-') + '</td>';
                }}).join('') + '</tr>';
            }});
            html += '</tbody></table></div>';

            document.getElementById('{self.chart_id}_table').innerHTML = html;
        }}

        function sortTable_{self.chart_id}(column) {{
            const sortState = window.tableSortState_{self.chart_id};
            if (sortState.column === column) {{
                sortState.direction = sortState.direction === 'asc' ? 'desc' : 'asc';
            }} else {{
                sortState.column = column;
                sortState.direction = 'desc';
            }}
            generateTable_{self.chart_id}();
        }}

        // Главная функция обновления графика
        function update{self.chart_id}() {{
            const chartDiv = document.getElementById('{self.chart_id}');
            if (!chartDiv) return;

            const wsData = window.weeklySalesData;
            if (!wsData) {{
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Загрузите данные в window.weeklySalesData</p>';
                return;
            }}

            initSelectors_{self.chart_id}();

            const metric = document.getElementById('{self.chart_id}_metric')?.value || 'revenue';
            const weekFrom = parseInt(document.getElementById('{self.chart_id}_week_from')?.value) || 0;
            const weekTo = parseInt(document.getElementById('{self.chart_id}_week_to')?.value) || wsData.weeks.length - 1;
            const showMean = document.getElementById('{self.chart_id}_showMean')?.checked ?? true;
            const showMedian = document.getElementById('{self.chart_id}_showMedian')?.checked ?? false;
            const showCorridor = document.getElementById('{self.chart_id}_showCorridor')?.checked ?? false;
            const showTrend = document.getElementById('{self.chart_id}_showTrend')?.checked ?? false;
            const showLabels = document.getElementById('{self.chart_id}_showLabels')?.checked ?? false;

            const storesSelect = document.getElementById('{self.chart_id}_stores');
            const selectedIndices = Array.from(storesSelect.selectedOptions).map(o => parseInt(o.value));

            if (selectedIndices.length === 0) {{
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Выберите магазины</p>';
                return;
            }}

            // Рассчитываем метрики
            const metrics = calculateDerivedMetrics_{self.chart_id}(wsData.data);
            const metricData = metrics[metric];

            const metricLabels = {{
                'revenue': 'Выручка',
                'growth_pct': 'Рост к пред. неделе (%)',
                'growth_index': 'Индекс роста (%)',
                'cumulative': 'Кумулятивная сумма',
                'moving_avg': 'Скользящее среднее (4 нед)'
            }};
            const metricLabel = metricLabels[metric] || metric;

            // Диапазон недель
            const weekIndices = [];
            for (let i = weekFrom; i <= weekTo; i++) weekIndices.push(i);
            const xValues = weekIndices.map(i => i + 1); // 1-based
            const weekLabels = weekIndices.map(i => wsData.weeks[i]);

            const traces = [];
            const annotations = [];
            const tableData = [];

            // Коридор min-max
            if (showCorridor) {{
                const stats = getAggregateStats_{self.chart_id}(metricData, selectedIndices);
                const minVals = weekIndices.map(i => stats.min[i]);
                const maxVals = weekIndices.map(i => stats.max[i]);

                traces.push({{
                    x: xValues.concat([...xValues].reverse()),
                    y: maxVals.concat([...minVals].reverse()),
                    fill: 'toself',
                    fillcolor: 'rgba(128, 128, 128, 0.15)',
                    line: {{ color: 'rgba(128, 128, 128, 0)' }},
                    name: 'Коридор min-max',
                    hoverinfo: 'skip',
                    showlegend: true
                }});
            }}

            // Линии магазинов
            selectedIndices.forEach((storeIdx, i) => {{
                const storeName = wsData.stores[storeIdx];
                const yValues = weekIndices.map(j => metricData[storeIdx]?.[j]);
                const color = storeColors_{self.chart_id}[i % storeColors_{self.chart_id}.length];

                traces.push({{
                    x: xValues,
                    y: yValues,
                    mode: 'lines+markers',
                    name: storeName,
                    line: {{ color: color, width: 2 }},
                    marker: {{ size: 6 }},
                    hovertemplate: `<b>${{storeName}}</b><br>Неделя: %{{x}}<br>${{metricLabel}}: %{{y:,.0f}}<extra></extra>`
                }});

                // Тренд
                if (showTrend) {{
                    const validPoints = [];
                    yValues.forEach((y, j) => {{
                        if (y !== null && !isNaN(y)) {{
                            validPoints.push({{ x: xValues[j], y: y }});
                        }}
                    }});

                    if (validPoints.length >= 2) {{
                        const xArr = validPoints.map(p => p.x);
                        const yArr = validPoints.map(p => p.y);
                        const reg = linearRegression_{self.chart_id}(xArr, yArr);

                        if (reg) {{
                            const trendY = xArr.map(x => reg.slope * x + reg.intercept);
                            traces.push({{
                                x: xArr,
                                y: trendY,
                                mode: 'lines',
                                name: `${{storeName}} (тренд)`,
                                line: {{ color: color, width: 1, dash: 'dot' }},
                                showlegend: false,
                                hovertemplate: `<b>${{storeName}} - Тренд</b><br>R²: ${{reg.r2.toFixed(2)}}<extra></extra>`
                            }});
                        }}
                    }}
                }}

                // Подписи значений
                if (showLabels) {{
                    yValues.forEach((y, j) => {{
                        if (y !== null && !isNaN(y)) {{
                            annotations.push({{
                                x: xValues[j],
                                y: y,
                                text: Math.round(y).toLocaleString('ru-RU'),
                                showarrow: false,
                                font: {{ size: 8, color: color }},
                                yshift: 10
                            }});
                        }}
                    }});
                }}

                // Данные для таблицы
                const revenue = wsData.data[storeIdx];
                const validRevenue = revenue.filter(v => v !== null);
                const firstVal = validRevenue[0] || 0;
                const lastVal = validRevenue[validRevenue.length - 1] || 0;

                tableData.push({{
                    'Магазин': storeName,
                    'Недель': validRevenue.length,
                    'Выручка (1 нед)': firstVal,
                    'Выручка (посл.)': lastVal,
                    'Рост (%)': firstVal > 0 ? Math.round((lastVal / firstVal - 1) * 100) : 0,
                    'Всего': validRevenue.reduce((a, b) => a + b, 0)
                }});
            }});

            // Средняя линия
            if (showMean) {{
                const stats = getAggregateStats_{self.chart_id}(metricData, selectedIndices);
                const meanVals = weekIndices.map(i => stats.mean[i]);

                traces.push({{
                    x: xValues,
                    y: meanVals,
                    mode: 'lines',
                    name: 'Средняя',
                    line: {{ color: '#000000', width: 3, dash: 'dash' }},
                    hovertemplate: `<b>Средняя</b><br>Неделя: %{{x}}<br>${{metricLabel}}: %{{y:,.0f}}<extra></extra>`
                }});
            }}

            // Медиана
            if (showMedian) {{
                const stats = getAggregateStats_{self.chart_id}(metricData, selectedIndices);
                const medianVals = weekIndices.map(i => stats.median[i]);

                traces.push({{
                    x: xValues,
                    y: medianVals,
                    mode: 'lines',
                    name: 'Медиана',
                    line: {{ color: '#E91E63', width: 2, dash: 'dot' }},
                    hovertemplate: `<b>Медиана</b><br>Неделя: %{{x}}<br>${{metricLabel}}: %{{y:,.0f}}<extra></extra>`
                }});
            }}

            window.tableData_{self.chart_id} = tableData;

            const layout = {{
                title: {{
                    text: `Динамика продаж по неделям: ${{metricLabel}}`,
                    font: {{ size: 16 }}
                }},
                xaxis: {{
                    title: 'Неделя работы',
                    dtick: xValues.length <= 24 ? 1 : Math.ceil(xValues.length / 12),
                    gridcolor: '#e9ecef'
                }},
                yaxis: {{
                    title: metricLabel,
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                margin: {{ l: 80, r: 180, t: 60, b: 60 }},
                showlegend: true,
                legend: {{
                    x: 1.02,
                    y: 1,
                    xanchor: 'left',
                    font: {{ size: 10 }}
                }},
                hovermode: 'x unified',
                annotations: annotations
            }};

            const config = {{
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['lasso2d', 'select2d']
            }};

            Plotly.react('{self.chart_id}', traces, layout, config);

            // Обновляем таблицу если открыта
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none') {{
                generateTable_{self.chart_id}();
            }}
        }}

        if (!window.chartUpdateFunctions) {{
            window.chartUpdateFunctions = {{}};
        }}
        window.chartUpdateFunctions['{self.chart_id}'] = update{self.chart_id};

        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(function() {{
                update{self.chart_id}();
            }}, 100);
        }});
        """
