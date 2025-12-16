# PROJECT_ROOT: charts/chart_marginal_analysis.py
"""
Метод 3: Маржинальный анализ (Предельная эффективность)
- Верхний субграфик: Выручка от площади
- Нижний субграфик: Предельная выручка (∂Revenue/∂Area)
- Оптимум = точка пика предельной выручки
"""
from charts.base_chart import BaseChart


class ChartMarginalAnalysis(BaseChart):
    """
    Метод 3: Маржинальный анализ
    - Два субграфика (subplots)
    - Верхний: Выручка от площади (линия + маркеры)
    - Нижний: Предельная выручка (точки + скользящее среднее)
    - Вертикальная линия = Оптимум (пик предельной выручки)
    """

    def __init__(self, chart_id='chart_marginal_analysis', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        # Опции для метрики анализа
        self.metric_options = [
            ('revenue', 'Выручка'),
            ('profit', 'Прибыль'),
            ('revenuePerM2', 'Выручка/м²'),
            ('profitPerM2', 'Прибыль/м²')
        ]

        # Окно скользящего среднего
        self.ma_options = [2, 3, 5, 7]

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерация HTML для селекторов графика"""
        # Чекбоксы для метрик
        metric_checkboxes = ''.join([
            f'<label style="font-size: 13px; display: flex; align-items: center; gap: 4px;">'
            f'<input type="checkbox" id="{self.chart_id}_metric_{val}" {"checked" if val == "revenue" else ""} onchange="update{self.chart_id}()"> {label}</label>'
            for val, label in self.metric_options
        ])

        # Окно MA
        ma_html = ''.join([
            f'<option value="{ma}"{" selected" if ma == 3 else ""}>MA-{ma}</option>'
            for ma in self.ma_options
        ])

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 12px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрики:</label>
                {metric_checkboxes}
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Регрессия:</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_regLinear" checked onchange="update{self.chart_id}()"> Линейная</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_regQuadratic" onchange="update{self.chart_id}()"> Квадратичная</label>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Сглаживание:</label>
                <select id="{self.chart_id}_ma" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {ma_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showFact" checked onchange="update{self.chart_id}()"> Факт</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showTrend" checked onchange="update{self.chart_id}()"> Тренд</label>
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

            <div id="{self.chart_id}" style="width: 100%; height: 550px;"></div>
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

            // Отделяем данные магазинов от итогов
            const storeRows = tableData.filter(row => !row['Магазин'].startsWith('---') && !row['Магазин'].startsWith('Пик'));
            const resultRows = tableData.filter(row => row['Магазин'].startsWith('---') || row['Магазин'].startsWith('Пик'));

            // Применяем сортировку к данным магазинов
            const sortState = window.tableSortState_{self.chart_id};
            if (sortState.column) {{
                storeRows.sort((a, b) => {{
                    let valA = a[sortState.column];
                    let valB = b[sortState.column];

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

            html += '<thead><tr>' + columns.map((c, idx) => {{
                const isActive = sortState.column === c;
                const arrow = isActive ? (sortState.direction === 'asc' ? ' ↑' : ' ↓') : '';
                const style = 'cursor: pointer; user-select: none;' + (isActive ? ' background: #e3f2fd;' : '');
                return `<th style="${{style}}" data-col-idx="${{idx}}" class="sortable-header-{self.chart_id}">${{c}}${{arrow}}</th>`;
            }}).join('') + '</tr></thead>';

            window.tableColumns_{self.chart_id} = columns;

            html += '<tbody>';
            storeRows.forEach(row => {{
                html += '<tr>' + columns.map(c => {{
                    const val = row[c];
                    return '<td>' + (typeof val === 'number' ? val.toLocaleString('ru-RU') : val) + '</td>';
                }}).join('') + '</tr>';
            }});
            resultRows.forEach(row => {{
                html += '<tr style="background: #f0f0f0; font-style: italic;">' + columns.map(c => {{
                    const val = row[c];
                    return '<td>' + (typeof val === 'number' ? val.toLocaleString('ru-RU') : val) + '</td>';
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

            // Сортируем по площади для маржинального анализа
            result.sort((a, b) => a.area - b.area);
            return result;
        }}

        /**
         * Расчёт предельных значений и скользящего среднего
         * Возвращает массив с полями marginal и marginalMA для конкретной метрики
         */
        function calculateMarginalData_{self.chart_id}(storeData, metric, maWindow) {{
            // Создаём глубокую копию данных, чтобы не перезаписывать
            const result = storeData.map(d => ({{ ...d }}));

            for (let i = 0; i < result.length; i++) {{
                let deltaArea = null;
                let deltaMetric = null;
                let marginal = null;

                if (i > 0) {{
                    const prev = result[i - 1];
                    const current = result[i];
                    deltaArea = current.area - prev.area;
                    deltaMetric = current[metric] - prev[metric];
                    marginal = deltaArea !== 0 ? deltaMetric / deltaArea : null;
                }}

                result[i].deltaArea = deltaArea;
                result[i].deltaMetric = deltaMetric;
                result[i].marginal = marginal;
            }}

            // Расчёт скользящего среднего
            for (let i = 0; i < result.length; i++) {{
                const start = Math.max(0, i - maWindow + 1);
                const windowData = result.slice(start, i + 1).filter(d => d.marginal !== null && isFinite(d.marginal));

                if (windowData.length > 0) {{
                    const sum = windowData.reduce((acc, d) => acc + d.marginal, 0);
                    result[i].marginalMA = sum / windowData.length;
                }} else {{
                    result[i].marginalMA = null;
                }}
            }}

            return result;
        }}

        // Маппинг меток и цветов
        const metricLabels_{self.chart_id} = {{
            'revenue': 'Выручка',
            'profit': 'Прибыль',
            'revenuePerM2': 'Выручка/м²',
            'profitPerM2': 'Прибыль/м²'
        }};

        const metricColors_{self.chart_id} = {{
            'revenue': '#1f77b4',
            'profit': '#ff7f0e',
            'revenuePerM2': '#2ca02c',
            'profitPerM2': '#d62728'
        }};

        /**
         * Получение выбранных метрик
         */
        function getSelectedMetrics_{self.chart_id}() {{
            const metrics = ['revenue', 'profit', 'revenuePerM2', 'profitPerM2'];
            return metrics.filter(m => {{
                const cb = document.getElementById('{self.chart_id}_metric_' + m);
                return cb && cb.checked;
            }});
        }}

        /**
         * Обновление графика
         */
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

            const data = window.filteredData || window.rawData;
            const storeData = aggregateStoreData_{self.chart_id}(data);

            if (storeData.length < 3) {{
                Plotly.purge('{self.chart_id}');
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Недостаточно данных для анализа (нужно минимум 3 магазина)</p>';
                return;
            }}

            // Читаем параметры из селекторов
            const selectedMetrics = getSelectedMetrics_{self.chart_id}();
            const maWindow = parseInt(document.getElementById('{self.chart_id}_ma')?.value) || 3;
            const showFact = document.getElementById('{self.chart_id}_showFact')?.checked ?? true;
            const showTrend = document.getElementById('{self.chart_id}_showTrend')?.checked ?? true;

            if (selectedMetrics.length === 0) {{
                Plotly.purge('{self.chart_id}');
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Выберите хотя бы одну метрику</p>';
                return;
            }}

            // Расчёт маржинальных данных для каждой метрики
            const allMarginalData = {{}};
            const allResults = {{}};

            selectedMetrics.forEach(metric => {{
                const marginalData = calculateMarginalData_{self.chart_id}(storeData, metric, maWindow);
                allMarginalData[metric] = marginalData;

                // Находим точку пика для каждой метрики
                let peakIdx = 0;
                let maxMarginalMA = -Infinity;
                marginalData.forEach((d, idx) => {{
                    if (d.marginalMA !== null && isFinite(d.marginalMA) && d.marginalMA > maxMarginalMA) {{
                        maxMarginalMA = d.marginalMA;
                        peakIdx = idx;
                    }}
                }});
                allResults[metric] = {{
                    optimalArea: marginalData[peakIdx]?.area || 0,
                    maxMarginalMA: maxMarginalMA
                }};
            }});

            // Сохраняем для таблицы (первая выбранная метрика как основная)
            const primaryMetric = selectedMetrics[0];
            window.marginalData_{self.chart_id} = allMarginalData[primaryMetric];
            window.marginalResult_{self.chart_id} = allResults[primaryMetric];
            window.allMarginalData_{self.chart_id} = allMarginalData;
            window.allResults_{self.chart_id} = allResults;
            window.selectedMetrics_{self.chart_id} = selectedMetrics;

            // Создаём subplots
            const traces = [];
            const shapes = [];
            const annotations = [];

            // Если метрик > 1, создаём отдельные оси Y для корреляционного анализа
            const useMultipleYAxes = selectedMetrics.length > 1;
            const numMetrics = selectedMetrics.length;

            // Рассчитываем отступы для дополнительных осей Y
            const rightMargin = numMetrics > 1 ? 50 + (numMetrics - 1) * 60 : 50;
            const xDomainEnd = numMetrics > 1 ? 1 - (numMetrics - 1) * 0.08 : 1;

            // Функция расчёта линейной регрессии и R²
            function calcLinearRegression(xArr, yArr) {{
                const n = xArr.length;
                if (n < 2) return {{ slope: 0, intercept: 0, r2: 0 }};

                const sumX = xArr.reduce((a, b) => a + b, 0);
                const sumY = yArr.reduce((a, b) => a + b, 0);
                const sumXY = xArr.reduce((acc, x, i) => acc + x * yArr[i], 0);
                const sumX2 = xArr.reduce((acc, x) => acc + x * x, 0);

                const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
                const intercept = (sumY - slope * sumX) / n;

                // R² (коэффициент детерминации)
                const meanY = sumY / n;
                const ssTotal = yArr.reduce((acc, y) => acc + Math.pow(y - meanY, 2), 0);
                const ssResidual = yArr.reduce((acc, y, i) => acc + Math.pow(y - (slope * xArr[i] + intercept), 2), 0);
                const r2 = ssTotal > 0 ? 1 - (ssResidual / ssTotal) : 0;

                return {{ slope, intercept, r2, predict: (x) => slope * x + intercept }};
            }}

            // Функция расчёта квадратичной (полиномиальной степени 2) регрессии
            function calcQuadraticRegression(xArr, yArr) {{
                const n = xArr.length;
                if (n < 3) return {{ a: 0, b: 0, c: 0, r2: 0, predict: () => 0 }};

                // Суммы для нормальных уравнений
                let sumX = 0, sumX2 = 0, sumX3 = 0, sumX4 = 0;
                let sumY = 0, sumXY = 0, sumX2Y = 0;

                for (let i = 0; i < n; i++) {{
                    const x = xArr[i], y = yArr[i];
                    const x2 = x * x, x3 = x2 * x, x4 = x3 * x;
                    sumX += x; sumX2 += x2; sumX3 += x3; sumX4 += x4;
                    sumY += y; sumXY += x * y; sumX2Y += x2 * y;
                }}

                // Решение системы 3x3 методом Крамера
                // | n     sumX   sumX2  | | c |   | sumY   |
                // | sumX  sumX2  sumX3  | | b | = | sumXY  |
                // | sumX2 sumX3  sumX4  | | a |   | sumX2Y |

                const D = n * (sumX2 * sumX4 - sumX3 * sumX3)
                        - sumX * (sumX * sumX4 - sumX3 * sumX2)
                        + sumX2 * (sumX * sumX3 - sumX2 * sumX2);

                if (Math.abs(D) < 1e-10) return {{ a: 0, b: 0, c: 0, r2: 0, predict: () => 0 }};

                const Dc = sumY * (sumX2 * sumX4 - sumX3 * sumX3)
                         - sumX * (sumXY * sumX4 - sumX3 * sumX2Y)
                         + sumX2 * (sumXY * sumX3 - sumX2 * sumX2Y);

                const Db = n * (sumXY * sumX4 - sumX3 * sumX2Y)
                         - sumY * (sumX * sumX4 - sumX3 * sumX2)
                         + sumX2 * (sumX * sumX2Y - sumXY * sumX2);

                const Da = n * (sumX2 * sumX2Y - sumXY * sumX3)
                         - sumX * (sumX * sumX2Y - sumXY * sumX2)
                         + sumY * (sumX * sumX3 - sumX2 * sumX2);

                const c = Dc / D;  // свободный член
                const b = Db / D;  // коэффициент при x
                const a = Da / D;  // коэффициент при x²

                // R²
                const meanY = sumY / n;
                let ssTotal = 0, ssResidual = 0;
                for (let i = 0; i < n; i++) {{
                    const predicted = a * xArr[i] * xArr[i] + b * xArr[i] + c;
                    ssTotal += Math.pow(yArr[i] - meanY, 2);
                    ssResidual += Math.pow(yArr[i] - predicted, 2);
                }}
                const r2 = ssTotal > 0 ? 1 - (ssResidual / ssTotal) : 0;

                return {{ a, b, c, r2, predict: (x) => a * x * x + b * x + c }};
            }}

            // Сохраняем R² для каждой метрики
            const correlationResults = {{}};

            // Читаем настройки регрессии
            const showLinear = document.getElementById('{self.chart_id}_regLinear')?.checked ?? true;
            const showQuadratic = document.getElementById('{self.chart_id}_regQuadratic')?.checked ?? false;

            // Верхний график: Метрика от площади для каждой выбранной метрики
            // Оси: y для первой метрики, y6, y7, y8 для остальных (чтобы не пересекаться с нижним графиком)
            selectedMetrics.forEach((metric, idx) => {{
                const marginalData = allMarginalData[metric];
                const metricLabel = metricLabels_{self.chart_id}[metric];
                const color = metricColors_{self.chart_id}[metric];

                // Для верхнего графика: y, y6, y7, y8
                const yAxisName = idx === 0 ? 'y' : 'y' + (6 + idx - 1);

                const xValues = marginalData.map(d => d.area);
                const yValues = marginalData.map(d => d[metric]);

                // Расчёт регрессий
                const linearReg = calcLinearRegression(xValues, yValues);
                const quadReg = calcQuadraticRegression(xValues, yValues);
                correlationResults[metric] = {{ linear: linearReg, quadratic: quadReg }};

                // Точки (факт)
                traces.push({{
                    x: xValues,
                    y: yValues,
                    mode: 'markers',
                    name: metricLabel,
                    marker: {{ size: 10, color: color }},
                    xaxis: 'x',
                    yaxis: yAxisName,
                    hovertemplate: '<b>%{{text}}</b><br>Площадь: %{{x}} м²<br>' + metricLabel + ': %{{y:,.0f}}<extra></extra>',
                    text: marginalData.map(d => d.store)
                }});

                const minX = Math.min(...xValues);
                const maxX = Math.max(...xValues);

                // Линейная регрессия
                if (showLinear) {{
                    traces.push({{
                        x: [minX, maxX],
                        y: [linearReg.predict(minX), linearReg.predict(maxX)],
                        mode: 'lines',
                        name: `${{metricLabel}} линейн. (R²=${{linearReg.r2.toFixed(2)}})`,
                        line: {{ color: color, width: 2, dash: 'dash' }},
                        xaxis: 'x',
                        yaxis: yAxisName,
                        hoverinfo: 'skip'
                    }});
                }}

                // Квадратичная регрессия (парабола - нужно больше точек)
                if (showQuadratic) {{
                    const curveX = [];
                    const curveY = [];
                    const steps = 50;
                    for (let i = 0; i <= steps; i++) {{
                        const x = minX + (maxX - minX) * i / steps;
                        curveX.push(x);
                        curveY.push(quadReg.predict(x));
                    }}
                    traces.push({{
                        x: curveX,
                        y: curveY,
                        mode: 'lines',
                        name: `${{metricLabel}} квадр. (R²=${{quadReg.r2.toFixed(2)}})`,
                        line: {{ color: color, width: 2, dash: 'dot' }},
                        xaxis: 'x',
                        yaxis: yAxisName,
                        hoverinfo: 'skip'
                    }});
                }}

                // Аннотации R² на верхнем графике
                let annotationText = `<b>${{metricLabel}}</b>:`;
                if (showLinear) annotationText += ` лин.R²=${{linearReg.r2.toFixed(3)}}`;
                if (showQuadratic) annotationText += ` квадр.R²=${{quadReg.r2.toFixed(3)}}`;

                annotations.push({{
                    x: 0.02 + idx * 0.28,
                    y: 0.98,
                    xref: 'paper',
                    yref: 'y domain',
                    text: annotationText,
                    showarrow: false,
                    font: {{ color: color, size: 11 }},
                    bgcolor: 'rgba(255,255,255,0.8)',
                    borderpad: 4,
                    yanchor: 'top',
                    xanchor: 'left'
                }});
            }});

            // Сохраняем для таблицы
            window.correlationResults_{self.chart_id} = correlationResults;

            // Нижний график: Предельная метрика для каждой выбранной метрики
            // Оси: y2, y3, y4, y5
            selectedMetrics.forEach((metric, idx) => {{
                // Для нижнего графика: y2, y3, y4, y5
                const yAxisNum = 2 + idx;
                const yAxisName = 'y' + yAxisNum;

                const marginalData = allMarginalData[metric];
                const result = allResults[metric];
                const metricLabel = metricLabels_{self.chart_id}[metric];
                const color = metricColors_{self.chart_id}[metric];

                if (showFact) {{
                    traces.push({{
                        x: marginalData.filter(d => d.marginal !== null && isFinite(d.marginal)).map(d => d.area),
                        y: marginalData.filter(d => d.marginal !== null && isFinite(d.marginal)).map(d => d.marginal),
                        mode: 'markers',
                        name: `∂${{metricLabel}} (факт)`,
                        marker: {{ color: color, size: 8, opacity: 0.6 }},
                        xaxis: 'x2',
                        yaxis: yAxisName,
                        showlegend: true
                    }});
                }}

                if (showTrend) {{
                    traces.push({{
                        x: marginalData.filter(d => d.marginalMA !== null).map(d => d.area),
                        y: marginalData.filter(d => d.marginalMA !== null).map(d => d.marginalMA),
                        mode: 'lines',
                        name: `∂${{metricLabel}} (MA-${{maWindow}})`,
                        line: {{ color: color, width: 3 }},
                        xaxis: 'x2',
                        yaxis: yAxisName
                    }});
                }}

                // Вертикальная линия оптимума для каждой метрики
                shapes.push({{
                    type: 'line',
                    x0: result.optimalArea,
                    x1: result.optimalArea,
                    y0: 0,
                    y1: 1,
                    yref: 'y2 domain',
                    xref: 'x2',
                    line: {{
                        color: color,
                        width: 2,
                        dash: 'dash'
                    }}
                }});

                // Аннотация оптимума
                const avgArea = (storeData[0].area + storeData[storeData.length-1].area) / 2;
                annotations.push({{
                    x: result.optimalArea,
                    y: 0.95 - idx * 0.08,
                    xref: 'x2',
                    yref: 'y2 domain',
                    text: `${{metricLabel}}: ${{Math.round(result.optimalArea).toLocaleString('ru-RU')}} м²`,
                    showarrow: false,
                    font: {{ color: color, size: 11 }},
                    yanchor: 'top',
                    xanchor: result.optimalArea < avgArea ? 'left' : 'right'
                }});
            }});

            // Заголовки графиков
            const metricTitles = selectedMetrics.map(m => metricLabels_{self.chart_id}[m]).join(', ');
            annotations.push({{
                x: 0.5,
                y: 1,
                xref: 'paper',
                yref: 'y domain',
                text: `Метрики от площади`,
                showarrow: false,
                font: {{ size: 13, color: '#495057' }},
                yanchor: 'bottom'
            }});
            annotations.push({{
                x: 0.5,
                y: 1,
                xref: 'paper',
                yref: 'y2 domain',
                text: `Предельные значения (∂Метрика/∂Площадь)`,
                showarrow: false,
                font: {{ size: 13, color: '#495057' }},
                yanchor: 'bottom'
            }});

            const layout = {{
                title: {{
                    text: `Метод 3: Маржинальный анализ (${{metricTitles}})`,
                    font: {{ size: 16 }}
                }},
                grid: {{
                    rows: 2,
                    columns: 1,
                    pattern: 'independent',
                    roworder: 'top to bottom'
                }},
                xaxis: {{
                    title: 'Площадь (м²)',
                    gridcolor: '#e9ecef',
                    domain: [0, xDomainEnd],
                    anchor: 'y'
                }},
                yaxis: {{
                    title: useMultipleYAxes ? metricLabels_{self.chart_id}[selectedMetrics[0]] : 'Значение',
                    titlefont: {{ color: metricColors_{self.chart_id}[selectedMetrics[0]] }},
                    tickfont: {{ color: metricColors_{self.chart_id}[selectedMetrics[0]] }},
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f',
                    domain: [0.55, 1],
                    anchor: 'x'
                }},
                xaxis2: {{
                    title: 'Площадь (м²)',
                    gridcolor: '#e9ecef',
                    domain: [0, xDomainEnd],
                    anchor: 'y2'
                }},
                yaxis2: {{
                    title: useMultipleYAxes ? '∂' + metricLabels_{self.chart_id}[selectedMetrics[0]] : 'Предельное значение',
                    titlefont: {{ color: metricColors_{self.chart_id}[selectedMetrics[0]] }},
                    tickfont: {{ color: metricColors_{self.chart_id}[selectedMetrics[0]] }},
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f',
                    domain: [0, 0.45],
                    anchor: 'x2'
                }},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                margin: {{ l: 80, r: rightMargin, t: 60, b: 60 }},
                hovermode: 'closest',
                showlegend: true,
                legend: {{
                    x: 1.02,
                    y: 1,
                    xanchor: 'left'
                }},
                shapes: shapes,
                annotations: annotations
            }};

            // Добавляем дополнительные оси Y для второй и последующих метрик
            if (useMultipleYAxes) {{
                selectedMetrics.slice(1).forEach((metric, idx) => {{
                    const color = metricColors_{self.chart_id}[metric];
                    const metricLabel = metricLabels_{self.chart_id}[metric];
                    const position = xDomainEnd + 0.02 + idx * 0.08;

                    // Оси для верхнего графика (y6, y7, y8)
                    const topYAxisNum = 6 + idx;
                    layout['yaxis' + topYAxisNum] = {{
                        title: metricLabel,
                        titlefont: {{ color: color }},
                        tickfont: {{ color: color }},
                        tickformat: ',.0f',
                        anchor: 'free',
                        overlaying: 'y',
                        side: 'right',
                        position: position,
                        showgrid: false
                    }};

                    // Оси для нижнего графика (y3, y4, y5)
                    const bottomYAxisNum = 3 + idx;
                    layout['yaxis' + bottomYAxisNum] = {{
                        title: '∂' + metricLabel,
                        titlefont: {{ color: color }},
                        tickfont: {{ color: color }},
                        tickformat: ',.0f',
                        anchor: 'free',
                        overlaying: 'y2',
                        side: 'right',
                        position: position,
                        showgrid: false
                    }};
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
            const marginalData = window.marginalData_{self.chart_id} || [];
            const result = window.marginalResult_{self.chart_id} || {{}};

            const tableData = marginalData.map(d => ({{
                'Магазин': d.store,
                'Площадь (м²)': d.area,
                'Выручка': Math.round(d.revenue),
                'Прибыль': Math.round(d.profit),
                'Δ Площадь': d.deltaArea !== null ? Math.round(d.deltaArea) : '-',
                'Δ Выручка': d.deltaMetric !== null ? Math.round(d.deltaMetric) : '-',
                'Предельная выручка': d.marginal !== null && isFinite(d.marginal) ? Math.round(d.marginal) : '-',
                'MA': d.marginalMA !== null ? Math.round(d.marginalMA) : '-'
            }}));

            // Добавляем итоговую строку
            if (result.optimalArea) {{
                tableData.push({{
                    'Магазин': '--- Результат ---',
                    'Площадь (м²)': '',
                    'Выручка': '',
                    'Прибыль': '',
                    'Δ Площадь': '',
                    'Δ Выручка': '',
                    'Предельная выручка': '',
                    'MA': ''
                }});
                tableData.push({{
                    'Магазин': 'Пик предельной выручки',
                    'Площадь (м²)': Math.round(result.optimalArea),
                    'Выручка': '',
                    'Прибыль': '',
                    'Δ Площадь': '',
                    'Δ Выручка': '',
                    'Предельная выручка': Math.round(result.maxMarginalMA),
                    'MA': ''
                }});
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
