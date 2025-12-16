# PROJECT_ROOT: charts/chart_dea_analysis.py
"""
DEA (Data Envelopment Analysis) - Метод оболочечного анализа данных
- Расчет границы эффективности (efficiency frontier)
- Балл эффективности для каждого магазина (0-100%)
- Идентификация эталонных магазинов
- Потенциал улучшения для неэффективных магазинов
"""
from charts.base_chart import BaseChart


class ChartDEAAnalysis(BaseChart):
    """
    DEA Analysis - Граница эффективности
    - Scatter plot с convex hull границей эффективности
    - Балл эффективности (0-100%) для каждого магазина
    - Ranking по эффективности
    - Таблица с рекомендациями по улучшению
    """

    def __init__(self, chart_id='chart_dea_analysis', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        # Метрики для outputs
        self.output_metrics = [
            ('revenue', 'Выручка'),
            ('profit', 'Прибыль'),
            ('ebitda', 'EBITDA')
        ]

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерация HTML для селекторов графика"""
        output_html = ''.join([
            f'<option value="{val}"{" selected" if val == "revenue" else ""}>{label}</option>'
            for val, label in self.output_metrics
        ])

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">
                    Output метрика:
                    <span style="
                        display: inline-block;
                        width: 16px;
                        height: 16px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border-radius: 50%;
                        text-align: center;
                        line-height: 16px;
                        font-size: 11px;
                        font-weight: bold;
                        cursor: help;
                        margin-left: 4px;
                    " title="Этот список влияет только на отображение метрики по оси Y для визуального анализа.&#10;&#10;⚠️ Важно: Расчёт эффективности (% Efficiency) всегда использует ВСЕ 3 метрики:&#10;• Revenue (40%)&#10;• Profit (35%)&#10;• EBITDA (25%)&#10;&#10;Выбор метрики здесь НЕ влияет на расчёт эффективности!">?</span>
                </label>
                <select id="{self.chart_id}_output" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {output_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showLabels" onchange="update{self.chart_id}()"> Подписи магазинов</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showFrontier" checked onchange="update{self.chart_id}()"> Граница эффективности</label>
            </div>
            <div class="selector-group" style="display: flex; align-items: center;">
                <button onclick="toggleDEAMetricsInfo()" style="
                    background: #f8f9fa;
                    color: #495057;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 14px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                " onmouseover="this.style.background='#e9ecef'" onmouseout="this.style.background='#f8f9fa'">
                    ❓
                </button>
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
                    <button class="llm-result-close" onclick="document.getElementById('{self.chart_id}_llm_result').style.display='none'">✕</button>
                </div>
                <div class="llm-result-text {self.ai_view_mode}" style="--max-lines: {self.ai_max_lines};"></div>
            </div>
            <div id="{self.chart_id}_llm_loading" class="llm-loading" style="display: none;">⳩ Генерация ответа...</div>

            <!-- Модальное окно с объяснением -->
            <div id="dea-metrics-modal" style="
                display: none;
                position: fixed;
                z-index: 2000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.6);
            ">
                <div style="
                    background: white;
                    border-radius: 15px;
                    max-width: 600px;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                    margin: 50px auto;
                    position: relative;
                ">
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px 25px;
                        border-radius: 15px 15px 0 0;
                        font-size: 20px;
                        font-weight: 600;
                        position: relative;
                    ">
                        📊 Метрики DEA анализа
                        <span onclick="toggleDEAMetricsInfo()" style="
                            position: absolute;
                            top: 15px;
                            right: 20px;
                            font-size: 32px;
                            cursor: pointer;
                            line-height: 1;
                        ">&times;</span>
                    </div>
                    <div style="padding: 25px; line-height: 1.6;">
                        <h3 style="color: #667eea; font-size: 16px; margin-top: 0;">📈 Revenue (Выручка) — 40%</h3>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Что это:</strong> Общий доход от продаж товаров/услуг без учета расходов.</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Как считается:</strong> Сумма всех продаж = Цена × Количество проданных товаров</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Вес 40%:</strong> Самый важный показатель, т.к. отражает масштаб бизнеса магазина</p>

                        <h3 style="color: #667eea; font-size: 16px; margin-top: 20px;">💰 Profit (Прибыль/Наценка) — 35%</h3>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Что это:</strong> Разница между выручкой и себестоимостью товаров.</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Как считается:</strong> Profit = Revenue - Себестоимость товаров</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Вес 35%:</strong> Показывает реальную прибыльность продаж</p>

                        <h3 style="color: #667eea; font-size: 16px; margin-top: 20px;">📊 EBITDA — 25%</h3>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Что это:</strong> Прибыль до вычета процентов, налогов и амортизации (Earnings Before Interest, Taxes, Depreciation, Amortization)</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Как считается:</strong> EBITDA = Profit - Операционные расходы (аренда, зарплата, и т.д.)</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Вес 25%:</strong> Показывает операционную эффективность магазина</p>

                        <h3 style="color: #667eea; font-size: 16px; margin-top: 20px;">🎯 Как используется в DEA</h3>
                        <p style="margin: 10px 0; color: #4a5568;">DEA анализ оценивает эффективность каждого магазина по <strong>комбинации всех трех метрик</strong>:</p>
                        <ul style="margin: 10px 0; padding-left: 25px;">
                            <li>Магазин получает 100% (эталонный), если имеет лучшее соотношение этих показателей к площади</li>
                            <li>Остальные магазины оцениваются относительно эталонных</li>
                            <li>Чем ближе к 100%, тем эффективнее магазин использует свою площадь</li>
                        </ul>
                    </div>
                </div>
            </div>

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
                    <button class="btn-prompt-action btn-send" onclick="sendPrompt_{self.chart_id}()">🚀 Отправить в LLM</button>
                    <button class="btn-prompt-action btn-save" onclick="savePrompt_{self.chart_id}()">💾 Сохранить промпт</button>
                    <button class="btn-prompt-action btn-reset" onclick="resetPrompt_{self.chart_id}()">🔄 Сбросить</button>
                </div>
                <div id="{self.chart_id}_save_status" class="save-status" style="display: none;"></div>
            </div>
            {llm_comment_html}
        </div>
        '''

    def get_js_code(self):
        return f"""
        /**
         * Переключение модального окна с метриками DEA
         */
        function toggleDEAMetricsInfo() {{
            const modal = document.getElementById('dea-metrics-modal');
            if (modal.style.display === 'none' || modal.style.display === '') {{
                modal.style.display = 'flex';
                modal.style.alignItems = 'center';
                modal.style.justifyContent = 'center';
            }} else {{
                modal.style.display = 'none';
            }}
        }}

        // Закрытие при клике вне модального окна
        window.addEventListener('click', function(event) {{
            const modal = document.getElementById('dea-metrics-modal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }});

        /**
         * Переключение вида График/Таблица/Промпт
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
        window.tableSortState_{self.chart_id} = {{ column: 'Композитный балл', direction: 'desc' }};

        /**
         * Генерация таблицы с сортировкой
         */
        function generateTable_{self.chart_id}() {{
            const tableData = window.deaTableData_{self.chart_id} || [];
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
                    const cmp = window.naturalCompare ? window.naturalCompare(valA, valB) : String(valA || '').localeCompare(String(valB || ''), 'ru');
                    return sortState.direction === 'asc' ? cmp : -cmp;
                }});
            }}

            const columns = ['Ранг', 'Магазин', 'Площадь', 'Выручка/м²', 'Прибыль/м²', 'EBITDA/м²',
                           'Балл (Revenue)', 'Балл (Profit)', 'Балл (EBITDA)', 'Композитный балл',
                           'Статус', 'Потенциал', 'Эталон'];
            let html = '<div class="table-scroll-wrapper"><table class="chart-table">';

            html += '<thead><tr>' + columns.map((c, idx) => {{
                const isActive = sortState.column === c;
                const arrow = isActive ? (sortState.direction === 'asc' ? ' ↑' : ' ↓') : '';
                const style = 'cursor: pointer; user-select: none; white-space: nowrap;' + (isActive ? ' background: #e3f2fd;' : '');
                return `<th style="${{style}}" data-col-idx="${{idx}}" class="sortable-header-{self.chart_id}">${{c}}${{arrow}}</th>`;
            }}).join('') + '</tr></thead>';

            window.tableColumns_{self.chart_id} = columns;

            html += '<tbody>';
            sortedData.forEach((row, idx) => {{
                const isEfficient = row['Статус'] === '★ Эталонный';
                const rowStyle = isEfficient ? 'background: #d4edda; font-weight: 500;' : '';
                html += `<tr style="${{rowStyle}}">` + columns.map(c => {{
                    let val = row[c];
                    let cellContent;

                    if (c === 'Композитный балл') {{
                        // Парсим значение без знака %
                        const numVal = typeof val === 'string' ? parseFloat(val) : val;
                        const color = numVal >= 95 ? '#28a745' : numVal >= 70 ? '#ffc107' : '#dc3545';
                        cellContent = `<span style="color: ${{color}}; font-weight: 700;">${{val}}</span>`;
                    }} else if (c.startsWith('Балл (')) {{
                        // Балл по отдельной метрике
                        const numVal = typeof val === 'string' ? parseFloat(val) : val;
                        const color = numVal >= 90 ? '#28a745' : numVal >= 60 ? '#ffc107' : '#fd7e14';
                        cellContent = `<span style="color: ${{color}}; font-weight: 500; font-size: 11px;">${{val}}</span>`;
                    }} else if (c === 'Статус' && isEfficient) {{
                        cellContent = `<span style="color: #28a745;">${{val}}</span>`;
                    }} else {{
                        cellContent = typeof val === 'number' ? val.toLocaleString('ru-RU') : (val || '-');
                    }}

                    return '<td>' + cellContent + '</td>';
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
                // По умолчанию: сортировка по убыванию для всех балльных колонок и ранга
                const descColumns = ['Композитный балл', 'Балл (Revenue)', 'Балл (Profit)', 'Балл (EBITDA)', 'Ранг'];
                sortState.direction = descColumns.includes(column) ? 'desc' : 'asc';
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
                const cost = parseFloat(row['Себестоимость продажи в чеке']) || 0;

                if (!storeMap[store]) {{
                    storeMap[store] = {{
                        store: store,
                        area: area,
                        revenue: 0,
                        profit: 0,
                        cost: 0
                    }};
                }}
                storeMap[store].revenue += revenue;
                storeMap[store].profit += profit;
                storeMap[store].cost += cost;
            }});

            return Object.values(storeMap).map(s => {{
                // EBITDA = Прибыль (так как у нас нет данных по амортизации)
                const ebitda = s.profit;
                return {{
                    store: s.store,
                    area: s.area,
                    revenue: s.revenue,
                    profit: s.profit,
                    ebitda: ebitda,
                    // Выходы на м²
                    revenuePerM2: s.area > 0 ? s.revenue / s.area : 0,
                    profitPerM2: s.area > 0 ? s.profit / s.area : 0,
                    ebitdaPerM2: s.area > 0 ? ebitda / s.area : 0
                }};
            }}).filter(s => s.area > 0);
        }}

        /**
         * Построение выпуклой оболочки (Convex Hull) - алгоритм Грэхема
         */
        function convexHull_{self.chart_id}(points) {{
            if (points.length < 3) return points;

            // Сортируем точки по x, затем по y
            const sorted = [...points].sort((a, b) => {{
                if (a.x === b.x) return a.y - b.y;
                return a.x - b.x;
            }});

            // Функция для определения поворота (cross product)
            const cross = (o, a, b) => {{
                return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
            }};

            // Строим нижнюю половину
            const lower = [];
            for (let i = 0; i < sorted.length; i++) {{
                while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], sorted[i]) <= 0) {{
                    lower.pop();
                }}
                lower.push(sorted[i]);
            }}

            // Строим верхнюю половину
            const upper = [];
            for (let i = sorted.length - 1; i >= 0; i--) {{
                while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], sorted[i]) <= 0) {{
                    upper.pop();
                }}
                upper.push(sorted[i]);
            }}

            // Убираем последние точки (дубликаты)
            lower.pop();
            upper.pop();

            return lower.concat(upper);
        }}

        /**
         * Расчет DEA efficiency score многокритериальным методом
         * Для CCR модели с одним входом (площадь) и тремя выходами (revenue, profit, ebitda на м²)
         */
        function calculateDEA_{self.chart_id}(storeData, outputMetric) {{
            // Многокритериальный DEA: учитываем все три метрики одновременно
            // 1. Нормализуем каждую метрику (0-1) для корректного сравнения
            const metrics = ['revenue', 'profit', 'ebitda'];
            const normalized = {{}};

            metrics.forEach(metric => {{
                const values = storeData.map(s => s[metric + 'PerM2']);
                const maxVal = Math.max(...values);
                const minVal = Math.min(...values);
                const range = maxVal - minVal;

                normalized[metric] = storeData.map(s => {{
                    if (range === 0) return 1;
                    return (s[metric + 'PerM2'] - minVal) / range;
                }});
            }});

            // 2. Рассчитываем композитный балл эффективности
            // Веса: revenue=40%, profit=35%, ebitda=25%
            const weights = {{
                revenue: 0.40,
                profit: 0.35,
                ebitda: 0.25
            }};

            const deaResults = storeData.map((s, idx) => {{
                // Композитный балл = взвешенная сумма нормализованных метрик
                const compositeScore =
                    normalized.revenue[idx] * weights.revenue +
                    normalized.profit[idx] * weights.profit +
                    normalized.ebitda[idx] * weights.ebitda;

                // Переводим в проценты (0-100%)
                const score = compositeScore * 100;

                return {{
                    store: s.store,
                    area: s.area,
                    output: s[outputMetric],
                    outputPerM2: s[outputMetric + 'PerM2'],
                    // Детализация по метрикам
                    revenuePerM2: s.revenuePerM2,
                    profitPerM2: s.profitPerM2,
                    ebitdaPerM2: s.ebitdaPerM2,
                    // Нормализованные значения
                    revenueNorm: normalized.revenue[idx] * 100,
                    profitNorm: normalized.profit[idx] * 100,
                    ebitdaNorm: normalized.ebitda[idx] * 100,
                    // Итоговый балл
                    efficiencyScore: Math.round(score * 10) / 10,
                    // Более мягкий критерий: >= 95% вместо 99.9%
                    isEfficient: score >= 95.0,
                    potentialImprovement: Math.round((100 - score) * 10) / 10
                }};
            }});

            // Сортируем по баллу эффективности
            deaResults.sort((a, b) => b.efficiencyScore - a.efficiencyScore);

            // Добавляем ранг
            deaResults.forEach((s, idx) => {{
                s.rank = idx + 1;
            }});

            return deaResults;
        }}

        /**
         * Поиск ближайшего эталонного магазина для неэффективного
         */
        function findBenchmark_{self.chart_id}(store, efficientStores) {{
            if (efficientStores.length === 0) return null;

            // Находим эталон с наиболее близкой площадью
            let minDiff = Infinity;
            let benchmark = efficientStores[0];

            efficientStores.forEach(eff => {{
                const diff = Math.abs(eff.area - store.area);
                if (diff < minDiff) {{
                    minDiff = diff;
                    benchmark = eff;
                }}
            }});

            return benchmark;
        }}

        const outputLabels_{self.chart_id} = {{
            'revenue': 'Выручка',
            'profit': 'Прибыль',
            'ebitda': 'EBITDA'
        }};

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
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Недостаточно данных для DEA анализа (нужно минимум 3 магазина)</p>';
                return;
            }}

            // Параметры
            const outputMetric = document.getElementById('{self.chart_id}_output')?.value || 'revenue';
            const showLabels = document.getElementById('{self.chart_id}_showLabels')?.checked ?? false;
            const showFrontier = document.getElementById('{self.chart_id}_showFrontier')?.checked ?? true;

            const outputLabel = outputLabels_{self.chart_id}[outputMetric];

            // Рассчитываем DEA scores
            const deaResults = calculateDEA_{self.chart_id}(storeData, outputMetric);

            // Разделяем на эффективные и неэффективные
            const efficientStores = deaResults.filter(s => s.isEfficient);
            const inefficientStores = deaResults.filter(s => !s.isEfficient);

            // Подготовка данных для таблицы с детализацией по метрикам
            const tableData = deaResults.map(s => {{
                const benchmark = s.isEfficient ? '-' : findBenchmark_{self.chart_id}(s, efficientStores);
                return {{
                    'Ранг': s.rank,
                    'Магазин': s.store,
                    'Площадь': Math.round(s.area),
                    'Выручка/м²': Math.round(s.revenuePerM2),
                    'Прибыль/м²': Math.round(s.profitPerM2),
                    'EBITDA/м²': Math.round(s.ebitdaPerM2),
                    'Балл (Revenue)': Math.round(s.revenueNorm) + '%',
                    'Балл (Profit)': Math.round(s.profitNorm) + '%',
                    'Балл (EBITDA)': Math.round(s.ebitdaNorm) + '%',
                    'Композитный балл': s.efficiencyScore + '%',
                    'Статус': s.isEfficient ? '★ Эталонный' : 'Неэффективный',
                    'Потенциал': s.potentialImprovement + '%',
                    'Эталон': benchmark ? benchmark.store : '-'
                }};
            }});
            window.deaTableData_{self.chart_id} = tableData;

            // Подготовка данных для графика
            const traces = [];

            // 1. Неэффективные магазины
            if (inefficientStores.length > 0) {{
                traces.push({{
                    type: 'scatter',
                    mode: showLabels ? 'markers+text' : 'markers',
                    name: 'Неэффективные',
                    x: inefficientStores.map(s => s.area),
                    y: inefficientStores.map(s => s.outputPerM2),
                    text: inefficientStores.map(s => s.store),
                    customdata: inefficientStores.map(s => [
                        s.efficiencyScore,
                        Math.round(s.revenuePerM2),
                        Math.round(s.profitPerM2),
                        Math.round(s.ebitdaPerM2)
                    ]),
                    textposition: 'top center',
                    textfont: {{ size: 9 }},
                    marker: {{
                        size: 10,
                        color: inefficientStores.map(s => s.efficiencyScore),
                        colorscale: [
                            [0, '#dc3545'],
                            [0.5, '#ffc107'],
                            [1, '#fd7e14']
                        ],
                        colorbar: {{
                            title: 'Композитный<br>балл',
                            titleside: 'right',
                            ticksuffix: '%',
                            x: 1.15
                        }},
                        line: {{ width: 1, color: 'white' }}
                    }},
                    hovertemplate: '<b>%{{text}}</b><br>' +
                                   'Площадь: %{{x:.0f}} м²<br>' +
                                   'Выручка/м²: %{{customdata[1]:,.0f}}<br>' +
                                   'Прибыль/м²: %{{customdata[2]:,.0f}}<br>' +
                                   'EBITDA/м²: %{{customdata[3]:,.0f}}<br>' +
                                   '<b>Композитный балл: %{{customdata[0]:.1f}}%</b><br>' +
                                   '<extra></extra>'
                }});
            }}

            // 2. Эффективные магазины (на границе)
            if (efficientStores.length > 0) {{
                traces.push({{
                    type: 'scatter',
                    mode: showLabels ? 'markers+text' : 'markers',
                    name: 'Эталонные (≥95%)',
                    x: efficientStores.map(s => s.area),
                    y: efficientStores.map(s => s.outputPerM2),
                    text: efficientStores.map(s => s.store),
                    customdata: efficientStores.map(s => [
                        s.efficiencyScore,
                        Math.round(s.revenuePerM2),
                        Math.round(s.profitPerM2),
                        Math.round(s.ebitdaPerM2)
                    ]),
                    textposition: 'top center',
                    textfont: {{ size: 9, color: '#28a745' }},
                    marker: {{
                        size: 14,
                        color: '#28a745',
                        symbol: 'star',
                        line: {{ width: 2, color: 'white' }}
                    }},
                    hovertemplate: '<b>%{{text}}</b> ★<br>' +
                                   'Площадь: %{{x:.0f}} м²<br>' +
                                   'Выручка/м²: %{{customdata[1]:,.0f}}<br>' +
                                   'Прибыль/м²: %{{customdata[2]:,.0f}}<br>' +
                                   'EBITDA/м²: %{{customdata[3]:,.0f}}<br>' +
                                   '<b>Композитный балл: %{{customdata[0]:.1f}}%</b><br>' +
                                   '<b>ЭТАЛОННЫЙ МАГАЗИН</b><extra></extra>'
                }});
            }}

            // 3. Граница эффективности (convex hull)
            if (showFrontier && efficientStores.length >= 3) {{
                const frontierPoints = efficientStores.map(s => ({{
                    x: s.area,
                    y: s.outputPerM2,
                    store: s.store
                }}));

                const hull = convexHull_{self.chart_id}(frontierPoints);

                // Замыкаем контур
                const hullX = hull.map(p => p.x);
                const hullY = hull.map(p => p.y);
                hullX.push(hull[0].x);
                hullY.push(hull[0].y);

                traces.push({{
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Граница эффективности',
                    x: hullX,
                    y: hullY,
                    line: {{
                        color: '#28a745',
                        width: 2,
                        dash: 'dot'
                    }},
                    hoverinfo: 'skip',
                    showlegend: true
                }});
            }}

            // Статистика
            const avgScore = Math.round(deaResults.reduce((sum, s) => sum + s.efficiencyScore, 0) / deaResults.length * 10) / 10;
            const efficientCount = efficientStores.length;
            const totalCount = deaResults.length;

            const layout = {{
                title: {{
                    text: `DEA Многокритериальный анализ (Revenue 40% + Profit 35% + EBITDA 25%)`,
                    font: {{ size: 16 }}
                }},
                xaxis: {{
                    title: 'Площадь магазина (м²)',
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                yaxis: {{
                    title: outputLabel + ' на м² (руб)',
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                margin: {{ l: 80, r: 150, t: 120, b: 60 }},
                showlegend: true,
                legend: {{
                    x: 0.5,
                    y: -0.25,
                    xanchor: 'center',
                    yanchor: 'top',
                    orientation: 'h',
                    bgcolor: 'rgba(255,255,255,0.9)',
                    bordercolor: '#dee2e6',
                    borderwidth: 1
                }},
                annotations: [
                    {{
                        x: 0.5,
                        y: 1.08,
                        xref: 'paper',
                        yref: 'paper',
                        text: `Эталонных: <b>${{efficientCount}}</b> из ${{totalCount}} | Средний балл: <b>${{avgScore}}%</b>`,
                        showarrow: false,
                        font: {{ size: 13, color: '#495057' }},
                        bgcolor: 'rgba(255,255,255,0.9)',
                        borderpad: 6
                    }}
                ]
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

        /**
         * Получение данных таблицы для промпта
         */
        function getTableData_{self.chart_id}() {{
            return window.deaTableData_{self.chart_id} || [];
        }}

        // ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ПРОМПТАМИ ==========

        function loadPrompt_{self.chart_id}() {{
            let promptText = (typeof promptTemplates !== 'undefined' && promptTemplates['{self.chart_id}'])
                ? promptTemplates['{self.chart_id}']
                : 'Промпт не найден для этого графика';

            const rowsLimit = document.getElementById('{self.chart_id}_rows_limit')?.value || '50';
            let tableData = typeof getTableData_{self.chart_id} === 'function' ? getTableData_{self.chart_id}() : [];
            if (rowsLimit !== 'all') {{
                tableData = tableData.slice(0, parseInt(rowsLimit));
            }}

            const dataStr = JSON.stringify(tableData, null, 2);
            const contextStr = typeof buildLLMContext === 'function' ? buildLLMContext('{self.chart_id}') : '';

            promptText = promptText
                .replace('{{{{context}}}}', contextStr)
                .replace('{{{{data}}}}', dataStr);

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
