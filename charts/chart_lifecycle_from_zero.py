# PROJECT_ROOT: charts/chart_lifecycle_from_zero.py
"""
График жизненного цикла магазинов с нулевой точки
- Ось X = номер месяца работы магазина (0 = первый месяц с продажами)
- Каждый магазин начинает с точки 0, независимо от даты открытия
- Позволяет сравнивать магазины на одинаковых этапах жизненного цикла
"""
from charts.base_chart import BaseChart


class ChartLifecycleFromZero(BaseChart):
    """
    Жизненный цикл магазинов - динамика с первого месяца работы
    """

    def __init__(self, chart_id='chart_lifecycle_from_zero', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        self.metric_options = [
            'Сумма в чеке',
            'Наценка продажи в чеке',
            'Число чеков',
            'Количество в чеке'
        ]

        self.mode_options = [
            ('absolute', 'Абсолютные значения'),
            ('percent', '% от предыдущего месяца')
        ]

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        metric_html = ''.join([
            f'<option value="{m}"{" selected" if m == "Сумма в чеке" else ""}>{m}</option>'
            for m in self.metric_options
        ])

        mode_html = ''.join([
            f'<option value="{val}"{" selected" if val == "absolute" else ""}>{label}</option>'
            for val, label in self.mode_options
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
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Режим:</label>
                <select id="{self.chart_id}_mode" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {mode_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Магазины:</label>
                <select id="{self.chart_id}_stores" multiple onchange="update{self.chart_id}()" style="padding: 4px 8px; border: 1px solid #ced4da; border-radius: 6px; font-size: 12px; background: white; min-width: 150px; max-width: 300px; height: 60px;">
                </select>
                <button onclick="clearStores_{self.chart_id}()" style="padding: 4px 8px; font-size: 11px; border: 1px solid #ced4da; border-radius: 4px; background: #fff; cursor: pointer;">Сброс</button>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showAvg" checked onchange="update{self.chart_id}()"> Средняя</label>
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

        // Natural sort для правильной сортировки "Магазин 1", "Магазин 2", ..., "Магазин 10"
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

        function generateTable_{self.chart_id}() {{
            const tableData = window.lifecycleTableData_{self.chart_id} || [];
            if (!tableData || tableData.length === 0) {{
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
                    // Используем natural sort для строк (правильная сортировка Магазин 1, 2, ..., 10)
                    const cmp = naturalSort_{self.chart_id}(valA, valB);
                    return sortState.direction === 'asc' ? cmp : -cmp;
                }});
            }}

            const columns = Object.keys(tableData[0]);
            let html = '<div class="table-scroll-wrapper"><table class="chart-table">';

            html += '<thead><tr>' + columns.map((c, idx) => {{
                const isActive = sortState.column === c;
                const arrow = isActive ? (sortState.direction === 'asc' ? ' ↑' : ' ↓') : '';
                const style = 'cursor: pointer; user-select: none;' + (isActive ? ' background: #e3f2fd;' : '');
                return `<th style="${{style}}" data-col-idx="${{idx}}" class="sortable-header-{self.chart_id}">${{c}}${{arrow}}</th>`;
            }}).join('') + '</tr></thead>';

            window.tableColumns_{self.chart_id} = columns;

            html += '<tbody>';
            sortedData.forEach(row => {{
                html += '<tr>' + columns.map(c => {{
                    const val = row[c];
                    return '<td>' + (typeof val === 'number' ? val.toLocaleString('ru-RU') : (val || '-')) + '</td>';
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

        document.addEventListener('click', function(e) {{
            const th = e.target.closest('.sortable-header-{self.chart_id}');
            if (th) {{
                const colIdx = parseInt(th.dataset.colIdx);
                const columns = window.tableColumns_{self.chart_id};
                if (columns && columns[colIdx] !== undefined) {{
                    sortTable_{self.chart_id}(columns[colIdx]);
                }}
            }}
        }});

        const monthNameToNum_{self.chart_id} = {{
            'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4,
            'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
            'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12
        }};

        // Флаг первой загрузки селектора магазинов
        window.storesInitialized_{self.chart_id} = false;

        // Локальный фильтр магазинов
        function updateStoreSelector_{self.chart_id}(stores) {{
            const select = document.getElementById('{self.chart_id}_stores');
            if (!select) return;

            const currentSelected = Array.from(select.selectedOptions).map(o => o.value);
            select.innerHTML = '';

            // Используем natural sort для правильной сортировки: Магазин 1, 2, ..., 10
            stores.sort(naturalSort_{self.chart_id}).forEach(store => {{
                const option = document.createElement('option');
                option.value = store;
                option.textContent = store;
                // При первой загрузке - ничего не выбрано, потом сохраняем выбор пользователя
                if (window.storesInitialized_{self.chart_id}) {{
                    option.selected = currentSelected.includes(store);
                }} else {{
                    option.selected = false;
                }}
                select.appendChild(option);
            }});

            window.storesInitialized_{self.chart_id} = true;
        }}

        function getSelectedStores_{self.chart_id}() {{
            const select = document.getElementById('{self.chart_id}_stores');
            if (!select) return [];
            // Возвращаем только выбранные магазины (пустой массив если ничего не выбрано)
            return Array.from(select.selectedOptions).map(o => o.value);
        }}

        function selectAllStores_{self.chart_id}() {{
            const select = document.getElementById('{self.chart_id}_stores');
            if (!select) return;
            Array.from(select.options).forEach(o => o.selected = true);
            update{self.chart_id}();
        }}

        function clearStores_{self.chart_id}() {{
            const select = document.getElementById('{self.chart_id}_stores');
            if (!select) return;
            Array.from(select.options).forEach(o => o.selected = false);
            update{self.chart_id}();
        }}

        const storeColors_{self.chart_id} = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'
        ];

        /**
         * Построение данных жизненного цикла с нулевой точки
         * Ось X = номер месяца работы магазина (0 = первый месяц с продажами)
         * Каждый магазин начинает с точки 0, разная длина линий
         */
        function buildLifecycleData_{self.chart_id}(data, metricField) {{
            // Группируем данные по магазину и периоду
            const storeMonthly = {{}};

            data.forEach(row => {{
                const store = row['Магазин'];
                const year = parseInt(row['Год']) || 0;
                const monthName = row['Месяц'];
                const month = monthNameToNum_{self.chart_id}[monthName] || 0;
                const metricValue = parseFloat(row[metricField]) || 0;

                if (!store || year === 0 || month === 0) return;

                if (!storeMonthly[store]) {{
                    storeMonthly[store] = {{}};
                }}

                const periodKey = year * 12 + month;
                if (!storeMonthly[store][periodKey]) {{
                    storeMonthly[store][periodKey] = {{
                        year: year,
                        month: month,
                        value: 0
                    }};
                }}

                storeMonthly[store][periodKey].value += metricValue;
            }});

            // Для каждого магазина: находим первый месяц с продажами и строим lifecycle
            const storeLifecycles = {{}};
            let maxMonthsWorking = 0;

            Object.entries(storeMonthly).forEach(([store, periods]) => {{
                // Сортируем периоды
                const sortedKeys = Object.keys(periods).map(k => parseInt(k)).sort((a, b) => a - b);

                // Находим первый месяц с ненулевым значением метрики
                let firstPeriodIdx = 0;
                for (let i = 0; i < sortedKeys.length; i++) {{
                    if (periods[sortedKeys[i]].value > 0) {{
                        firstPeriodIdx = i;
                        break;
                    }}
                }}

                // Строим lifecycle начиная с первого месяца работы
                const lifecycle = [];
                for (let i = firstPeriodIdx; i < sortedKeys.length; i++) {{
                    const periodKey = sortedKeys[i];
                    const p = periods[periodKey];
                    const monthFromStart = i - firstPeriodIdx; // 0, 1, 2, ...

                    lifecycle.push({{
                        monthFromStart: monthFromStart,
                        calendarLabel: `${{String(p.month).padStart(2, '0')}}.${{p.year}}`,
                        value: Math.round(p.value)
                    }});
                }}

                if (lifecycle.length > 0) {{
                    storeLifecycles[store] = lifecycle;
                    maxMonthsWorking = Math.max(maxMonthsWorking, lifecycle.length);
                }}
            }});

            return {{
                stores: storeLifecycles,
                maxMonthsWorking: maxMonthsWorking
            }};
        }}

        function update{self.chart_id}() {{
            const chartDiv = document.getElementById('{self.chart_id}');
            if (!chartDiv) return;

            const tabContent = chartDiv.closest('.tab-content');
            const isVisible = tabContent && tabContent.classList.contains('active');
            if (!isVisible) {{
                window.chartsNeedUpdate = window.chartsNeedUpdate || {{}};
                window.chartsNeedUpdate['{self.chart_id}'] = true;
                return;
            }}

            const metricField = document.getElementById('{self.chart_id}_metric')?.value || 'Сумма в чеке';
            const mode = document.getElementById('{self.chart_id}_mode')?.value || 'absolute';
            const showAvg = document.getElementById('{self.chart_id}_showAvg')?.checked ?? true;

            const data = window.filteredData || window.rawData;
            const result = buildLifecycleData_{self.chart_id}(data, metricField);
            const lifecycleData = result.stores;
            const maxMonthsWorking = result.maxMonthsWorking;

            const allStores = Object.keys(lifecycleData);
            if (allStores.length === 0 || maxMonthsWorking === 0) {{
                Plotly.purge('{self.chart_id}');
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Нет данных для отображения</p>';
                return;
            }}

            // Обновляем локальный селектор магазинов
            updateStoreSelector_{self.chart_id}(allStores);

            // Получаем выбранные магазины
            const selectedStores = getSelectedStores_{self.chart_id}();
            const stores = allStores.filter(s => selectedStores.includes(s));

            if (stores.length === 0) {{
                Plotly.purge('{self.chart_id}');
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Выберите магазины для отображения</p>';
                return;
            }}

            const isPercent = mode === 'percent';

            const traces = [];
            const tableData = [];

            // Данные для расчёта средней по номеру месяца работы
            const avgByMonthFromStart = {{}};

            stores.forEach((store, idx) => {{
                const lc = lifecycleData[store];

                const xValues = [];
                const yValues = [];
                const textLabels = [];

                lc.forEach((d, i) => {{
                    const monthNum = d.monthFromStart;
                    xValues.push(monthNum);
                    textLabels.push(d.calendarLabel);

                    let yVal;
                    if (isPercent) {{
                        // % от предыдущего месяца (для первого месяца = 0%)
                        if (i === 0) {{
                            yVal = 0;
                        }} else {{
                            const prevValue = lc[i - 1].value;
                            yVal = prevValue > 0 ? Math.round(((d.value - prevValue) / prevValue) * 100) : 0;
                        }}
                    }} else {{
                        yVal = d.value;
                    }}
                    yValues.push(yVal);

                    // Для средней - группируем по номеру месяца работы
                    if (!avgByMonthFromStart[monthNum]) {{
                        avgByMonthFromStart[monthNum] = {{ sum: 0, count: 0, sumPercent: 0 }};
                    }}
                    avgByMonthFromStart[monthNum].sum += d.value;
                    avgByMonthFromStart[monthNum].count++;
                    avgByMonthFromStart[monthNum].sumPercent += yVal;
                }});

                // Линия магазина
                traces.push({{
                    x: xValues,
                    y: yValues,
                    text: textLabels,
                    mode: 'lines+markers',
                    name: store,
                    line: {{
                        color: storeColors_{self.chart_id}[idx % storeColors_{self.chart_id}.length],
                        width: 1.5
                    }},
                    marker: {{
                        size: 4
                    }},
                    hovertemplate: `<b>${{store}}</b><br>Месяц работы: %{{x}}<br>Дата: %{{text}}<br>${{metricField}}: %{{y:,.0f}}${{isPercent ? '%' : ''}}<extra></extra>`
                }});

                // Для таблицы
                const firstVal = lc[0]?.value || 0;
                const lastVal = lc[lc.length - 1]?.value || 0;
                const firstDate = lc[0]?.calendarLabel || '-';

                tableData.push({{
                    'Магазин': store,
                    'Открытие': firstDate,
                    'Месяцев работы': lc.length,
                    [`${{metricField}} (1 мес)`]: firstVal,
                    [`${{metricField}} (посл.)`]: lastVal,
                    'Рост %': firstVal > 0 ? Math.round((lastVal / firstVal - 1) * 100) : 0
                }});
            }});

            // Средняя линия - по номеру месяца работы
            if (showAvg) {{
                const avgX = [];
                const avgY = [];

                Object.keys(avgByMonthFromStart)
                    .map(k => parseInt(k))
                    .sort((a, b) => a - b)
                    .forEach(monthNum => {{
                        const m = avgByMonthFromStart[monthNum];
                        avgX.push(monthNum);
                        if (isPercent) {{
                            avgY.push(m.count > 0 ? Math.round(m.sumPercent / m.count) : 0);
                        }} else {{
                            avgY.push(m.count > 0 ? Math.round(m.sum / m.count) : 0);
                        }}
                    }});

                traces.push({{
                    x: avgX,
                    y: avgY,
                    mode: 'lines',
                    name: 'Средняя',
                    line: {{
                        color: '#000',
                        width: 3,
                        dash: 'dash'
                    }},
                    hovertemplate: `<b>Средняя</b><br>Месяц работы: %{{x}}<br>${{metricField}}: %{{y:,.0f}}${{isPercent ? '%' : ''}}<extra></extra>`
                }});
            }}

            window.lifecycleTableData_{self.chart_id} = tableData;

            const yAxisTitle = isPercent ? `${{metricField}} (% от пред. месяца)` : metricField;

            // Находим максимальное кол-во месяцев среди выбранных магазинов
            let maxMonths = 0;
            stores.forEach(store => {{
                maxMonths = Math.max(maxMonths, lifecycleData[store].length);
            }});

            const layout = {{
                title: {{
                    text: `Жизненный цикл магазинов (макс. ${{maxMonths}} мес.)`,
                    font: {{ size: 16 }}
                }},
                xaxis: {{
                    title: 'Месяц работы',
                    dtick: maxMonths > 24 ? Math.ceil(maxMonths / 12) : 1,
                    gridcolor: '#e9ecef',
                    zeroline: true
                }},
                yaxis: {{
                    title: yAxisTitle,
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                margin: {{ l: 80, r: 50, t: 60, b: 60 }},
                showlegend: true,
                legend: {{
                    x: 1.02,
                    y: 1,
                    xanchor: 'left',
                    font: {{ size: 10 }}
                }},
                hovermode: 'closest'
            }};

            const config = {{
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['lasso2d', 'select2d']
            }};

            Plotly.react('{self.chart_id}', traces, layout, config);
        }}

        if (!window.chartUpdateFunctions) {{
            window.chartUpdateFunctions = {{}};
        }}
        window.chartUpdateFunctions['{self.chart_id}'] = update{self.chart_id};

        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(function() {{
                const chartDiv = document.getElementById('{self.chart_id}');
                if (chartDiv) {{
                    const tabContent = chartDiv.closest('.tab-content');
                    if (tabContent && tabContent.classList.contains('active')) {{
                        update{self.chart_id}();
                    }} else {{
                        window.chartsNeedUpdate = window.chartsNeedUpdate || {{}};
                        window.chartsNeedUpdate['{self.chart_id}'] = true;
                    }}
                }}
            }}, 100);
        }});
        """
