# PROJECT_ROOT: charts/chart_small_multiples.py
from charts.base_chart import BaseChart


class ChartSmallMultiples(BaseChart):
    """Шпалера (small multiples) - сетка мини-графиков"""

    def __init__(self, chart_id='chart_small_multiples', available_detail_levels=None,
                 metric_options=None, group_by_options=None, **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        self.available_detail_levels = available_detail_levels or ['year', 'month']
        self.metric_options = metric_options or [
            'Сумма в чеке', 'Число чеков', 'Количество в чеке', 'Наценка продажи в чеке'
        ]
        self.group_by_options = group_by_options or ['Магазин', 'Товар', 'Тип']

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        metric_options_html = ''.join([
            f'<option value="{m}">{m}</option>' for m in self.metric_options
        ])
        group_options_html = ''.join([
            f'<option value="{g}">{g}</option>' for g in self.group_by_options
        ])

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
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Топ:</label>
                <select id="{self.chart_id}_top" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="4">4</option>
                    <option value="8">8</option>
                    <option value="12">12</option>
                    <option value="16">16</option>
                    <option value="20" selected>20</option>
                    <option value="all">Все</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Сортировка:</label>
                <select id="{self.chart_id}_sort" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="sum" selected>По сумме</option>
                    <option value="trend">По тренду</option>
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

        window.smallMultiplesData_{self.chart_id} = null;

        // Функция расчёта тренда (линейная регрессия)
        // Возвращает объект: {{ percent: %, trendLine: [y0, y1, ...] }}
        function calcTrend_{self.chart_id}(values) {{
            const n = values.length;
            if (n < 2) return {{ percent: 0, trendLine: values.slice() }};

            let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
            for (let i = 0; i < n; i++) {{
                sumX += i;
                sumY += values[i];
                sumXY += i * values[i];
                sumX2 += i * i;
            }}

            const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
            const intercept = (sumY - slope * sumX) / n;
            const avgY = sumY / n;

            // Линия тренда
            const trendLine = [];
            for (let i = 0; i < n; i++) {{
                trendLine.push(slope * i + intercept);
            }}

            // % изменения за период относительно среднего
            const percent = avgY > 0 ? (slope * n / avgY) * 100 : 0;

            return {{ percent, trendLine }};
        }}

        // Форматирование числа (1200000 -> 1.2М)
        function formatNumber_{self.chart_id}(num) {{
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'М';
            if (num >= 1000) return (num / 1000).toFixed(0) + 'К';
            return num.toFixed(0);
        }}

        function update{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const level = getDetailLevel_{self.chart_id}();

            const groupBySelect = document.getElementById('{self.chart_id}_groupby');
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const topSelect = document.getElementById('{self.chart_id}_top');
            const sortSelect = document.getElementById('{self.chart_id}_sort');

            const groupByField = groupBySelect ? groupBySelect.value : 'Магазин';
            const metricField = metricSelect ? metricSelect.value : 'Сумма в чеке';
            const topValue = topSelect ? topSelect.value : '20';
            const sortMode = sortSelect ? sortSelect.value : 'sum';

            // Агрегация: группа -> период -> сумма
            const groupData = {{}};
            const groupTotals = {{}};

            data.forEach(row => {{
                const group = row[groupByField];
                const year = parseInt(row['Год']);
                const monthName = row['Месяц'];
                const month = monthNameToNum_{self.chart_id}[monthName] || 1;
                const value = parseFloat(row[metricField]) || 0;

                if (!group || !year) return;

                let periodKey;
                if (level === 'year') {{
                    periodKey = `${{year}}`;
                }} else {{
                    periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;
                }}

                if (!groupData[group]) {{
                    groupData[group] = {{}};
                    groupTotals[group] = 0;
                }}
                if (!groupData[group][periodKey]) groupData[group][periodKey] = 0;
                groupData[group][periodKey] += value;
                groupTotals[group] += value;
            }});

            // Все периоды для расчёта тренда
            const allPeriods = new Set();
            Object.values(groupData).forEach(periods => {{
                Object.keys(periods).forEach(p => allPeriods.add(p));
            }});
            const sortedPeriods = [...allPeriods].sort((a, b) => {{
                if (level === 'year') return parseInt(a) - parseInt(b);
                // Формат: 01.MM.YYYY
                const [d1, m1, y1] = a.split('.');
                const [d2, m2, y2] = b.split('.');
                return (parseInt(y1) * 12 + parseInt(m1)) - (parseInt(y2) * 12 + parseInt(m2));
            }});

            // Расчёт тренда для каждой группы
            const groupTrends = {{}};
            Object.keys(groupData).forEach(group => {{
                const values = sortedPeriods.map(p => groupData[group][p] || 0);
                groupTrends[group] = calcTrend_{self.chart_id}(values);
            }});

            // Сортировка групп
            let groups;
            if (sortMode === 'trend') {{
                groups = Object.keys(groupData).sort((a, b) => groupTrends[b].percent - groupTrends[a].percent);
            }} else {{
                groups = Object.keys(groupData).sort((a, b) => groupTotals[b] - groupTotals[a]);
            }}

            // Фильтр по топу
            if (topValue !== 'all') {{
                groups = groups.slice(0, parseInt(topValue));
            }}

            // Используем уже отсортированные периоды
            const periods = sortedPeriods;

            // Расчёт сетки
            const count = groups.length;
            let cols = 4;
            if (count <= 4) cols = 2;
            else if (count <= 8) cols = 4;
            else cols = 4;
            const rows = Math.ceil(count / cols);

            // Индивидуальные Y min/max для каждой группы
            const groupYRanges = {{}};
            groups.forEach(g => {{
                let gMax = 0;
                let gMin = Infinity;
                periods.forEach(p => {{
                    const v = groupData[g][p] || 0;
                    if (v > gMax) gMax = v;
                    if (v > 0 && v < gMin) gMin = v;
                }});
                // Отступ 10% от диапазона
                const padding = (gMax - gMin) * 0.1;
                groupYRanges[g] = {{
                    min: Math.max(0, gMin - padding),
                    max: gMax + padding
                }};
            }});

            // Фиксированные отступы в пикселях
            const gapPx = 70;  // отступ между рядами (подписи X + заголовок)
            const topPaddingPx = 50;  // отступ сверху для заголовка
            const plotHeightPx = 160;  // высота каждого графика

            // Общая высота
            const totalHeight = topPaddingPx + rows * plotHeightPx + (rows - 1) * gapPx + 40;

            // Переводим в доли для domain
            const horizontalSpacing = 0.05;
            const topPadding = topPaddingPx / totalHeight;
            const verticalGap = gapPx / totalHeight;
            const plotHeight = plotHeightPx / totalHeight;

            // Создаём subplots с domain для каждой оси
            const traces = [];
            const annotations = [];

            // Расчёт domain для каждого subplot
            const plotWidth = (1 - horizontalSpacing * (cols - 1)) / cols;

            // Layout с subplots
            const layout = {{
                title: {{
                    text: `${{metricField}} по ${{groupByField}} (Топ ${{topValue === 'all' ? 'все' : topValue}})`,
                    font: {{ size: 16 }},
                    y: 0.99
                }},
                height: totalHeight,
                showlegend: false,
                margin: {{ t: 40, b: 30, l: 50, r: 20 }}
            }};

            groups.forEach((group, idx) => {{
                const rowNum = Math.floor(idx / cols);
                const colNum = idx % cols;

                // Domain для X оси (слева направо)
                const xStart = colNum * (plotWidth + horizontalSpacing);
                const xEnd = xStart + plotWidth;

                // Domain для Y оси (снизу вверх, поэтому инвертируем row)
                // topPadding резервирует место для основного заголовка
                const yEnd = 1 - topPadding - rowNum * (plotHeight + verticalGap);
                const yStart = yEnd - plotHeight;

                const xKey = idx === 0 ? 'xaxis' : `xaxis${{idx + 1}}`;
                const yKey = idx === 0 ? 'yaxis' : `yaxis${{idx + 1}}`;
                const xRef = idx === 0 ? 'x' : `x${{idx + 1}}`;
                const yRef = idx === 0 ? 'y' : `y${{idx + 1}}`;

                // Основная линия данных
                traces.push({{
                    x: periods,
                    y: periods.map(p => groupData[group][p] || 0),
                    type: 'scatter',
                    mode: 'lines',
                    name: group,
                    line: {{ width: 1.5, color: '#667eea' }},
                    xaxis: xRef,
                    yaxis: yRef,
                    hovertemplate: `<b>${{group}}</b><br>%{{x}}<br>${{metricField}}: %{{y:,.0f}}<extra></extra>`
                }});

                // Линия тренда (пунктир) - только в режиме сортировки по тренду
                if (sortMode === 'trend') {{
                    traces.push({{
                        x: periods,
                        y: groupTrends[group].trendLine,
                        type: 'scatter',
                        mode: 'lines',
                        name: `${{group}} тренд`,
                        line: {{ width: 1, color: '#999', dash: 'dash' }},
                        xaxis: xRef,
                        yaxis: yRef,
                        hoverinfo: 'skip',
                        showlegend: false
                    }});
                }}

                layout[xKey] = {{
                    domain: [xStart, xEnd],
                    showticklabels: true,
                    tickangle: -45,
                    tickfont: {{ size: 8 }},
                    showgrid: true,
                    gridcolor: '#eee',
                    type: 'category',
                    anchor: yRef
                }};

                layout[yKey] = {{
                    domain: [yStart, yEnd],
                    range: [groupYRanges[group].min, groupYRanges[group].max],
                    showticklabels: true,
                    tickfont: {{ size: 8 }},
                    showgrid: true,
                    gridcolor: '#eee',
                    anchor: xRef
                }};

                // Заголовок сверху каждого subplot
                const titleX = (xStart + xEnd) / 2;
                const titleY = yEnd + 0.005;

                // Формируем метрику для заголовка
                let metricLabel;
                const trendPercent = groupTrends[group].percent;
                const total = groupTotals[group];

                if (sortMode === 'trend') {{
                    const trendColor = trendPercent >= 0 ? '#28a745' : '#dc3545';
                    const trendSign = trendPercent >= 0 ? '+' : '';
                    metricLabel = `<span style="color:${{trendColor}}">${{trendSign}}${{trendPercent.toFixed(1)}}%</span>`;
                }} else {{
                    metricLabel = `(${{formatNumber_{self.chart_id}(total)}})`;
                }}

                annotations.push({{
                    text: `<b>${{group}}</b> ${{metricLabel}}`,
                    x: titleX,
                    y: titleY,
                    xref: 'paper',
                    yref: 'paper',
                    showarrow: false,
                    font: {{ size: 11, color: '#333' }},
                    xanchor: 'center',
                    yanchor: 'bottom'
                }});
            }});

            layout.annotations = annotations;

            // Сохраняем для таблицы
            window.smallMultiplesData_{self.chart_id} = {{
                groups: groups,
                periods: periods,
                groupData: groupData,
                metricField: metricField,
                groupByField: groupByField
            }};

            Plotly.newPlot('{self.chart_id}', traces, layout, {{responsive: true}});

            // Обновляем таблицу если открыта
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none') {{
                generateTable_{self.chart_id}();
            }}
        }}

        function getTableData_{self.chart_id}() {{
            const sd = window.smallMultiplesData_{self.chart_id};
            if (!sd) return [];

            const tableData = [];
            sd.groups.forEach(group => {{
                const row = {{}};
                row[sd.groupByField] = group;
                sd.periods.forEach(period => {{
                    row[period] = Math.round(sd.groupData[group][period] || 0);
                }});
                tableData.push(row);
            }});

            return tableData;
        }}
        """
