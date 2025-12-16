# PROJECT_ROOT: charts/chart_regression_analysis.py
"""
Метод 2: Регрессионный анализ выручки от площади
- Scatter plot с точками магазинов
- Линейная регрессия (зелёная пунктирная)
- Квадратичная регрессия (красная сплошная)
- Вертикальная линия = Оптимум (точка максимума квадратичной функции)
"""
from charts.base_chart import BaseChart


class ChartRegressionAnalysis(BaseChart):
    """
    Метод 2: Регрессионный анализ
    - X = Площадь (м²)
    - Y = Выбранная метрика (Выручка, Прибыль, Выручка/м², Прибыль/м²)
    - Линейная и квадратичная регрессия
    - Оптимум = точка максимума параболы
    """

    def __init__(self, chart_id='chart_regression_analysis', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        # Опции для селекторов (одинаковые для Ось Y, Цвет, Размер)
        self.metric_options = [
            ('revenuePerM2', 'Выручка/м²'),
            ('profitPerM2', 'Прибыль/м²'),
            ('revenue', 'Общая выручка'),
            ('profit', 'Общая прибыль'),
            ('area', 'Площадь')
        ]
        # Для размера добавляем опцию "Одинаковый"
        self.size_options = self.metric_options + [('fixed', 'Одинаковый')]
        self.top_options = [3, 5, 10, 'all']

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерация HTML для селекторов графика"""
        # Ось X: по умолчанию Площадь
        x_axis_html = ''.join([
            f'<option value="{val}"{" selected" if val == "area" else ""}>{label}</option>'
            for val, label in self.metric_options
        ])
        # Ось Y: по умолчанию Выручка/м²
        y_axis_html = ''.join([
            f'<option value="{val}"{" selected" if val == "revenuePerM2" else ""}>{label}</option>'
            for val, label in self.metric_options
        ])
        # Цвет: по умолчанию Прибыль/м²
        color_html = ''.join([
            f'<option value="{val}"{" selected" if val == "profitPerM2" else ""}>{label}</option>'
            for val, label in self.metric_options
        ])
        # Размер: по умолчанию Общая выручка
        size_html = ''.join([
            f'<option value="{val}"{" selected" if val == "revenue" else ""}>{label}</option>'
            for val, label in self.size_options
        ])
        top_html = ''.join([
            f'<option value="{t}"{"" if t != 5 else " selected"}>{"Все" if t == "all" else f"Топ {t}"}</option>'
            for t in self.top_options
        ])

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Ось X:</label>
                <select id="{self.chart_id}_xaxis" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {x_axis_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Ось Y:</label>
                <select id="{self.chart_id}_yaxis" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {y_axis_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Цвет:</label>
                <select id="{self.chart_id}_color" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {color_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Размер:</label>
                <select id="{self.chart_id}_size" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {size_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Оптимум:</label>
                <select id="{self.chart_id}_top" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {top_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Регрессия:</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showLinear" checked onchange="update{self.chart_id}()"> Линейная</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showQuadratic" checked onchange="update{self.chart_id}()"> Квадратичная</label>
            </div>
        </div>
        '''

    def _generate_detail_selector_html(self) -> str:
        """Этот график не использует детализацию по времени"""
        return ''

    def _generate_table_js(self) -> str:
        """Переопределяем - вся логика таблицы уже в get_js_code()"""
        return ''

    def get_html_container(self) -> str:
        """Переопределяем для упрощённого контейнера без детализации"""
        css = self._merge_css_styles()
        style_str = '; '.join([f'{k}: {v}' for k, v in css.items()])

        view_switcher_html = self._generate_view_switcher_html()
        llm_comment_html = self._generate_llm_comment_html()
        chart_selectors_html = self._generate_chart_selectors_html()

        return f'''
        <div class="chart-wrapper" style="{style_str}">
            {view_switcher_html}
            {chart_selectors_html}

            <!-- ОТВЕТ LLM -->
            <div id="{self.chart_id}_llm_result" class="llm-result" style="display: none;">
                <div class="llm-result-controls">
                    <button class="llm-result-toggle" onclick="this.closest('.llm-result').querySelector('.llm-result-text').classList.toggle('collapsed'); this.textContent = this.textContent === '−' ? '+' : '−'">−</button>
                    <button class="llm-result-close" onclick="document.getElementById('{self.chart_id}_llm_result').style.display='none'">x</button>
                </div>
                <div class="llm-result-text {self.ai_view_mode}" style="--max-lines: {self.ai_max_lines};"></div>
            </div>
            <div id="{self.chart_id}_llm_loading" class="llm-loading" style="display: none;">Генерация ответа...</div>

            <div id="{self.chart_id}" style="width: 100%; height: 450px;"></div>
            <div id="{self.chart_id}_table" class="chart-table-container" style="width: 100%; display: none;"></div>
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
        /**
         * Переключение вида График/Таблица
         */
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
                loadPrompt_{self.chart_id}();
            }}
        }}

        // Состояние сортировки таблицы
        window.tableSortState_{self.chart_id} = {{ column: null, direction: 'desc' }};

        /**
         * Генерация таблицы с сортировкой
         */
        function generateTable_{self.chart_id}() {{
            const tableData = getTableData_{self.chart_id}();
            if (!tableData || tableData.length === 0) {{
                document.getElementById('{self.chart_id}_table').innerHTML = '<p style="padding: 20px;">Нет данных</p>';
                return;
            }}

            // Отделяем данные магазинов от результатов регрессии
            const storeRows = tableData.filter(row => !row['Магазин'].startsWith('---') && !row['Магазин'].startsWith('R²') && !row['Магазин'].startsWith('Оптимум'));
            const resultRows = tableData.filter(row => row['Магазин'].startsWith('---') || row['Магазин'].startsWith('R²') || row['Магазин'].startsWith('Оптимум'));

            // Применяем сортировку к данным магазинов
            const sortState = window.tableSortState_{self.chart_id};
            if (sortState.column) {{
                storeRows.sort((a, b) => {{
                    let valA = a[sortState.column];
                    let valB = b[sortState.column];

                    // Числовая сортировка
                    if (typeof valA === 'number' && typeof valB === 'number') {{
                        return sortState.direction === 'asc' ? valA - valB : valB - valA;
                    }}
                    // Натуральная сортировка для строк (Магазин 1, 2, ... 10, 11)
                    const cmp = window.naturalCompare ? window.naturalCompare(valA, valB) : String(valA || '').localeCompare(String(valB || ''), 'ru');
                    return sortState.direction === 'asc' ? cmp : -cmp;
                }});
            }}

            const columns = Object.keys(tableData[0]);
            let html = '<div class="table-scroll-wrapper"><table class="chart-table">';

            // Заголовки с возможностью сортировки
            html += '<thead><tr>' + columns.map((c, idx) => {{
                const isActive = sortState.column === c;
                const arrow = isActive ? (sortState.direction === 'asc' ? ' ↑' : ' ↓') : '';
                const style = 'cursor: pointer; user-select: none;' + (isActive ? ' background: #e3f2fd;' : '');
                return `<th style="${{style}}" data-col-idx="${{idx}}" class="sortable-header-{self.chart_id}">${{c}}${{arrow}}</th>`;
            }}).join('') + '</tr></thead>';

            // Сохраняем колонки для обработчика клика
            window.tableColumns_{self.chart_id} = columns;

            html += '<tbody>';
            // Сначала отсортированные данные магазинов
            storeRows.forEach(row => {{
                html += '<tr>' + columns.map(c => {{
                    const val = row[c];
                    return '<td>' + (typeof val === 'number' ? val.toLocaleString('ru-RU') : val) + '</td>';
                }}).join('') + '</tr>';
            }});
            // Потом результаты регрессии (без сортировки)
            resultRows.forEach(row => {{
                html += '<tr style="background: #f0f0f0; font-style: italic;">' + columns.map(c => {{
                    const val = row[c];
                    return '<td>' + (typeof val === 'number' ? val.toLocaleString('ru-RU') : val) + '</td>';
                }}).join('') + '</tr>';
            }});
            html += '</tbody></table></div>';

            document.getElementById('{self.chart_id}_table').innerHTML = html;
        }}

        /**
         * Сортировка таблицы по колонке
         */
        function sortTable_{self.chart_id}(column) {{
            const sortState = window.tableSortState_{self.chart_id};
            if (sortState.column === column) {{
                // Переключаем направление
                sortState.direction = sortState.direction === 'asc' ? 'desc' : 'asc';
            }} else {{
                // Новая колонка - по умолчанию по убыванию (максимум сначала)
                sortState.column = column;
                sortState.direction = 'desc';
            }}
            generateTable_{self.chart_id}();
        }}

        // Делегирование событий для сортировки (обходим проблему со спецсимволами в названиях колонок)
        // Используем document для делегирования, так как таблица перезаписывается при каждом generateTable
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

        /**
         * Агрегация данных по магазинам
         */
        function aggregateStoreData_{self.chart_id}(data) {{
            const storeMap = {{}};

            data.forEach(row => {{
                const store = row['Магазин'];
                const area = parseFloat(row['Торговая площадь магазина']) || 0;
                const revenue = parseFloat(row['Сумма в чеке']) || 0;
                const profit = parseFloat(row['Наценка продажи в чеке']) || 0;

                if (!storeMap[store]) {{
                    storeMap[store] = {{
                        store: store,
                        area: area,
                        revenue: 0,
                        profit: 0
                    }};
                }}
                storeMap[store].revenue += revenue;
                storeMap[store].profit += profit;
            }});

            const result = Object.values(storeMap).map(s => {{
                const revenuePerM2 = s.area > 0 ? Math.round(s.revenue / s.area) : 0;
                const profitPerM2 = s.area > 0 ? Math.round(s.profit / s.area) : 0;
                return {{
                    store: s.store,
                    area: s.area,
                    revenue: s.revenue,
                    profit: s.profit,
                    revenuePerM2: revenuePerM2,
                    profitPerM2: profitPerM2
                }};
            }});

            // Сортируем по площади для регрессии
            result.sort((a, b) => a.area - b.area);
            return result;
        }}

        /**
         * Линейная регрессия (метод наименьших квадратов)
         */
        function linearRegression(x, y) {{
            const n = x.length;
            let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;

            for (let i = 0; i < n; i++) {{
                sumX += x[i];
                sumY += y[i];
                sumXY += x[i] * y[i];
                sumX2 += x[i] * x[i];
            }}

            const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
            const intercept = (sumY - slope * sumX) / n;

            // R² расчёт
            const yMean = sumY / n;
            let ssRes = 0, ssTot = 0;
            for (let i = 0; i < n; i++) {{
                const yPred = slope * x[i] + intercept;
                ssRes += (y[i] - yPred) ** 2;
                ssTot += (y[i] - yMean) ** 2;
            }}
            const r2 = 1 - ssRes / ssTot;

            return {{ slope, intercept, r2 }};
        }}

        /**
         * Квадратичная регрессия (y = a + bx + cx²)
         */
        function quadraticRegression(x, y) {{
            const n = x.length;

            // Матричный метод для полинома 2-й степени
            let sumX = 0, sumX2 = 0, sumX3 = 0, sumX4 = 0;
            let sumY = 0, sumXY = 0, sumX2Y = 0;

            for (let i = 0; i < n; i++) {{
                const xi = x[i];
                const yi = y[i];
                sumX += xi;
                sumX2 += xi * xi;
                sumX3 += xi * xi * xi;
                sumX4 += xi * xi * xi * xi;
                sumY += yi;
                sumXY += xi * yi;
                sumX2Y += xi * xi * yi;
            }}

            // Решение системы 3x3
            const det = n * (sumX2 * sumX4 - sumX3 * sumX3) - sumX * (sumX * sumX4 - sumX3 * sumX2) + sumX2 * (sumX * sumX3 - sumX2 * sumX2);

            if (Math.abs(det) < 1e-10) {{
                return {{ a: 0, b: 0, c: 0, r2: 0, optimal: null }};
            }}

            const a = (sumY * (sumX2 * sumX4 - sumX3 * sumX3) - sumX * (sumXY * sumX4 - sumX2Y * sumX3) + sumX2 * (sumXY * sumX3 - sumX2Y * sumX2)) / det;
            const b = (n * (sumXY * sumX4 - sumX2Y * sumX3) - sumY * (sumX * sumX4 - sumX3 * sumX2) + sumX2 * (sumX * sumX2Y - sumXY * sumX2)) / det;
            const c = (n * (sumX2 * sumX2Y - sumX3 * sumXY) - sumX * (sumX * sumX2Y - sumXY * sumX2) + sumY * (sumX * sumX3 - sumX2 * sumX2)) / det;

            // R² расчёт
            const yMean = sumY / n;
            let ssRes = 0, ssTot = 0;
            for (let i = 0; i < n; i++) {{
                const yPred = a + b * x[i] + c * x[i] * x[i];
                ssRes += (y[i] - yPred) ** 2;
                ssTot += (y[i] - yMean) ** 2;
            }}
            const r2 = 1 - ssRes / ssTot;

            // Оптимум (вершина параболы): x = -b / (2c)
            let optimal = null;
            if (c < 0) {{
                optimal = -b / (2 * c);
            }}

            return {{ a, b, c, r2, optimal }};
        }}

        // Маппинг меток
        const metricLabels_{self.chart_id} = {{
            'revenue': 'Выручка (руб)',
            'profit': 'Прибыль (руб)',
            'revenuePerM2': 'Выручка/м² (руб)',
            'profitPerM2': 'Прибыль/м² (руб)',
            'area': 'Площадь (м²)',
            'fixed': 'Одинаковый'
        }};

        /**
         * Обновление графика
         */
        function update{self.chart_id}() {{
            const chartDiv = document.getElementById('{self.chart_id}');
            if (!chartDiv) return;

            // Проверяем видимость
            const tabContent = chartDiv.closest('.tab-content');
            const isVisible = tabContent && tabContent.classList.contains('active');
            if (!isVisible) {{
                window.chartsNeedUpdate = window.chartsNeedUpdate || {{}};
                window.chartsNeedUpdate['{self.chart_id}'] = true;
                return;
            }}

            const data = window.filteredData || window.rawData;
            const storeData = aggregateStoreData_{self.chart_id}(data);

            if (storeData.length < 3) {{
                Plotly.purge('{self.chart_id}');
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Недостаточно данных для регрессии (нужно минимум 3 магазина)</p>';
                return;
            }}

            // Читаем параметры из селекторов
            const xAxisMetric = document.getElementById('{self.chart_id}_xaxis')?.value || 'area';
            const yAxisMetric = document.getElementById('{self.chart_id}_yaxis')?.value || 'revenuePerM2';
            const colorMetric = document.getElementById('{self.chart_id}_color')?.value || 'profitPerM2';
            const sizeMetric = document.getElementById('{self.chart_id}_size')?.value || 'revenue';
            const topN = document.getElementById('{self.chart_id}_top')?.value || '5';
            const showLinear = document.getElementById('{self.chart_id}_showLinear')?.checked ?? true;
            const showQuadratic = document.getElementById('{self.chart_id}_showQuadratic')?.checked ?? true;

            // Сохраняем для таблицы
            window.regressionData_{self.chart_id} = storeData;

            // Данные для регрессии
            const x = storeData.map(s => s[xAxisMetric]);
            const y = storeData.map(s => s[yAxisMetric]);

            // Цвет и размер точек
            const colors = storeData.map(s => s[colorMetric]);
            let sizes;
            if (sizeMetric === 'fixed') {{
                sizes = storeData.map(() => 12);
            }} else {{
                const sizeValues = storeData.map(s => s[sizeMetric]);
                const sizeMin = Math.min(...sizeValues);
                const sizeMax = Math.max(...sizeValues);
                const sizeRange = sizeMax - sizeMin || 1;
                sizes = sizeValues.map(v => 8 + ((v - sizeMin) / sizeRange) * 25);
            }}

            // Регрессии
            const linear = linearRegression(x, y);
            const quadratic = quadraticRegression(x, y);

            // Сохраняем результаты регрессии
            window.regressionResults_{self.chart_id} = {{ linear, quadratic }};

            // Расчёт оптимума по ТОП-N (среднее значение X для топ магазинов по Y)
            const sortedByY = [...storeData].sort((a, b) => b[yAxisMetric] - a[yAxisMetric]);
            const topStores = topN === 'all' ? sortedByY : sortedByY.slice(0, parseInt(topN));
            const optimalX = topStores.reduce((sum, s) => sum + s[xAxisMetric], 0) / topStores.length;

            const traces = [];

            // Кастомная красно-зелёная шкала
            const redGreenScale = [
                [0, 'rgb(215, 48, 39)'],
                [0.5, 'rgb(255, 255, 191)'],
                [1, 'rgb(26, 152, 80)']
            ];

            const xAxisLabel = metricLabels_{self.chart_id}[xAxisMetric] || xAxisMetric;
            const yAxisLabel = metricLabels_{self.chart_id}[yAxisMetric] || yAxisMetric;
            const colorLabel = metricLabels_{self.chart_id}[colorMetric] || colorMetric;

            // Точки магазинов
            traces.push({{
                x: x,
                y: y,
                mode: 'markers',
                type: 'scatter',
                showlegend: false,
                marker: {{
                    size: sizes,
                    sizemode: 'diameter',
                    color: colors,
                    colorscale: redGreenScale,
                    showscale: true,
                    colorbar: {{
                        title: colorLabel,
                        tickformat: ',.0f'
                    }}
                }},
                hovertext: storeData.map(s =>
                    `<b>${{s.store}}</b><br>` +
                    `Площадь: ${{s.area.toLocaleString('ru-RU')}} м²<br>` +
                    `Выручка/м²: ${{s.revenuePerM2.toLocaleString('ru-RU')}} руб<br>` +
                    `Прибыль/м²: ${{s.profitPerM2.toLocaleString('ru-RU')}} руб<br>` +
                    `Общая выручка: ${{Math.round(s.revenue).toLocaleString('ru-RU')}} руб<br>` +
                    `Общая прибыль: ${{Math.round(s.profit).toLocaleString('ru-RU')}} руб`
                ),
                hoverinfo: 'text'
            }});

            // Генерация точек для линий регрессии
            const xMin = Math.min(...x);
            const xMax = Math.max(...x);
            const xLine = [];
            for (let i = xMin; i <= xMax; i += (xMax - xMin) / 50) {{
                xLine.push(i);
            }}

            // Линейная регрессия
            if (showLinear) {{
                traces.push({{
                    x: xLine,
                    y: xLine.map(xi => linear.intercept + linear.slope * xi),
                    mode: 'lines',
                    name: `Линейная (R²=${{linear.r2.toFixed(2)}})`,
                    line: {{
                        dash: 'dash',
                        color: 'green',
                        width: 2
                    }}
                }});
            }}

            // Квадратичная регрессия
            if (showQuadratic) {{
                traces.push({{
                    x: xLine,
                    y: xLine.map(xi => quadratic.a + quadratic.b * xi + quadratic.c * xi * xi),
                    mode: 'lines',
                    name: `Квадратичная (R²=${{quadratic.r2.toFixed(2)}})`,
                    line: {{
                        color: 'red',
                        width: 3
                    }}
                }});
            }}

            const layout = {{
                title: {{
                    text: `Метод 2: Регрессионный анализ (${{yAxisLabel.split(' ')[0]}} от ${{xAxisLabel.split(' ')[0]}})`,
                    font: {{ size: 16 }}
                }},
                xaxis: {{
                    title: xAxisLabel,
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                yaxis: {{
                    title: yAxisLabel,
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                margin: {{ l: 80, r: 120, t: 60, b: 60 }},
                hovermode: 'closest',
                showlegend: true,
                legend: {{
                    x: 1,
                    y: 1,
                    xanchor: 'right'
                }},
                shapes: [],
                annotations: []
            }};

            // Вертикальная линия оптимума по ТОП-N (синяя)
            const topLabel = topN === 'all' ? 'всех' : `ТОП-${{topN}}`;
            layout.shapes.push({{
                type: 'line',
                x0: optimalX,
                x1: optimalX,
                y0: 0,
                y1: 1,
                yref: 'paper',
                line: {{
                    color: 'blue',
                    width: 2,
                    dash: 'dash'
                }}
            }});
            layout.annotations.push({{
                x: optimalX,
                y: 0.95,
                yref: 'paper',
                text: `Оптимум (${{topLabel}}): ${{Math.round(optimalX).toLocaleString('ru-RU')}}`,
                showarrow: false,
                font: {{
                    color: 'blue',
                    size: 11
                }},
                yanchor: 'top',
                xanchor: optimalX < (xMin + xMax) / 2 ? 'left' : 'right'
            }});

            // Вертикальная линия оптимума по регрессии (оранжевая)
            if (showQuadratic && quadratic.optimal && quadratic.optimal > xMin && quadratic.optimal < xMax) {{
                layout.shapes.push({{
                    type: 'line',
                    x0: quadratic.optimal,
                    x1: quadratic.optimal,
                    y0: 0,
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'orange',
                        width: 2,
                        dash: 'dot'
                    }}
                }});
                layout.annotations.push({{
                    x: quadratic.optimal,
                    y: 0.85,
                    yref: 'paper',
                    text: `Регрессия: ${{Math.round(quadratic.optimal).toLocaleString('ru-RU')}}`,
                    showarrow: false,
                    font: {{
                        color: 'orange',
                        size: 11
                    }},
                    yanchor: 'top',
                    xanchor: quadratic.optimal < (xMin + xMax) / 2 ? 'left' : 'right'
                }});
            }}

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

        /**
         * Данные для таблицы
         */
        function getTableData_{self.chart_id}() {{
            const storeData = window.regressionData_{self.chart_id} || [];
            const results = window.regressionResults_{self.chart_id} || {{}};

            const tableData = storeData.map(s => ({{
                'Магазин': s.store,
                'Площадь (м²)': s.area,
                'Выручка': Math.round(s.revenue),
                'Прибыль': Math.round(s.profit),
                'Выручка/м²': s.revenuePerM2,
                'Прибыль/м²': s.profitPerM2
            }}));

            // Добавляем строку с результатами регрессии
            if (results.linear && results.quadratic) {{
                tableData.push({{
                    'Магазин': '--- Результаты ---',
                    'Площадь (м²)': '',
                    'Выручка': '',
                    'Прибыль': '',
                    'Выручка/м²': '',
                    'Прибыль/м²': ''
                }});
                tableData.push({{
                    'Магазин': 'R² линейная',
                    'Площадь (м²)': results.linear.r2.toFixed(3),
                    'Выручка': '',
                    'Прибыль': '',
                    'Выручка/м²': '',
                    'Прибыль/м²': ''
                }});
                tableData.push({{
                    'Магазин': 'R² квадратичная',
                    'Площадь (м²)': results.quadratic.r2.toFixed(3),
                    'Выручка': '',
                    'Прибыль': '',
                    'Выручка/м²': '',
                    'Прибыль/м²': ''
                }});
                if (results.quadratic.optimal) {{
                    tableData.push({{
                        'Магазин': 'Оптимум (м²)',
                        'Площадь (м²)': Math.round(results.quadratic.optimal),
                        'Выручка': '',
                        'Прибыль': '',
                        'Выручка/м²': '',
                        'Прибыль/м²': ''
                    }});
                }}
            }}

            return tableData;
        }}

        // ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ПРОМПТАМИ ==========

        function loadPrompt_{self.chart_id}() {{
            fetch('prompts.json')
                .then(response => response.json())
                .then(prompts => {{
                    const promptText = prompts['{self.chart_id}'] || 'Промпт не найден для этого графика';
                    document.getElementById('{self.chart_id}_prompt_text').value = promptText;
                }})
                .catch(error => {{
                    console.error('Ошибка загрузки промпта:', error);
                    document.getElementById('{self.chart_id}_prompt_text').value = 'Ошибка загрузки промпта';
                }});
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
                    document.getElementById('{self.chart_id}_llm_result').querySelector('.llm-result-text').textContent = data.response;
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
                    document.getElementById('{self.chart_id}_llm_result').querySelector('.llm-result-text').textContent = data.choices[0].message.content;
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

        // Регистрация
        if (!window.chartUpdateFunctions) {{
            window.chartUpdateFunctions = {{}};
        }}
        window.chartUpdateFunctions['{self.chart_id}'] = update{self.chart_id};

        // Первоначальная отрисовка
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
