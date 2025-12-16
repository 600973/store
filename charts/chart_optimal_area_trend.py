# PROJECT_ROOT: charts/chart_optimal_area_trend.py
from charts.base_chart import BaseChart


class ChartOptimalAreaTrend(BaseChart):
    """Тренд оптимальной площади во времени - сетка графиков по магазинам (small multiples)"""

    def __init__(self, chart_id='chart_optimal_area_trend', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)
        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерирует селекторы для выбора параметров"""
        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Базовая метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="revenue" selected>Выручка</option>
                    <option value="profit">Прибыль</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Топ:</label>
                <select id="{self.chart_id}_top" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="4">4</option>
                    <option value="8" selected>8</option>
                    <option value="12">12</option>
                    <option value="16">16</option>
                    <option value="20">20</option>
                    <option value="all">Все</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Сортировка:</label>
                <select id="{self.chart_id}_sort" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="less_efficient" selected>Менее эффективные</option>
                    <option value="more_efficient">Более эффективные</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center;">
                <button onclick="toggleOptimalAreaInfo_{self.chart_id}()" style="
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

            <!-- Модальное окно с объяснением -->
            <div id="{self.chart_id}_modal" style="
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 10000;
            " onclick="if(event.target === this) toggleOptimalAreaInfo_{self.chart_id}()">
                <div style="
                    position: relative;
                    background: white;
                    margin: 3% auto;
                    max-width: 850px;
                    max-height: 90vh;
                    overflow-y: auto;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                ">
                    <div style="
                        background: linear-gradient(135deg, #2E86AB 0%, #F18F01 100%);
                        color: white;
                        padding: 20px 25px;
                        font-size: 18px;
                        font-weight: 600;
                        border-radius: 12px 12px 0 0;
                        position: relative;
                    ">
                        📐 Тренд оптимальной площади (шпалера)
                        <span onclick="toggleOptimalAreaInfo_{self.chart_id}()" style="
                            position: absolute;
                            top: 15px;
                            right: 20px;
                            font-size: 32px;
                            cursor: pointer;
                            line-height: 1;
                        ">&times;</span>
                    </div>
                    <div style="padding: 25px; line-height: 1.7;">
                        <h3 style="color: #2E86AB; font-size: 16px; margin-top: 0;">🎯 Что показывает этот график?</h3>
                        <p style="margin: 10px 0; color: #4a5568;">
                            Сетка графиков сравнивает <strong>фактическую площадь</strong> каждого магазина (синяя линия)
                            с <strong>оптимальной</strong> (оранжевая пунктирная) — той, которая соответствовала бы
                            медианной эффективности по сети.
                        </p>

                        <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #2E86AB;">
                            <p style="margin: 0 0 10px 0; color: #333; font-weight: 600;">📐 Формула расчёта:</p>
                            <p style="margin: 0; color: #333; font-family: monospace; font-size: 14px; background: white; padding: 10px; border-radius: 4px;">
                                Оптимальная площадь = Выручка (или прибыль) магазина / Медианная эффективность сети
                            </p>
                        </div>

                        <h3 style="color: #28a745; font-size: 16px; margin-top: 25px;">📊 Пример расчёта</h3>
                        <div style="background: #e8f5e9; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745;">
                            <p style="margin: 0 0 10px 0; color: #333;">Допустим, за месяц:</p>
                            <ul style="margin: 5px 0; padding-left: 20px; color: #4a5568; font-size: 13px;">
                                <li>Выручка магазина: <strong>500 000 ₽</strong></li>
                                <li>Фактическая площадь: <strong>100 м²</strong></li>
                                <li>Эффективность магазина: 500 000 / 100 = <strong>5 000 ₽/м²</strong></li>
                                <li>Медианная эффективность по сети: <strong>4 000 ₽/м²</strong></li>
                                <li>Оптимальная площадь = 500 000 / 4 000 = <strong>125 м²</strong></li>
                            </ul>
                            <p style="margin: 10px 0 0 0; color: #28a745; font-weight: 600;">
                                ✅ Оптимальная (125 м²) > Фактической (100 м²) → Магазин работает эффективнее медианы!
                            </p>
                        </div>

                        <h3 style="color: #17a2b8; font-size: 16px; margin-top: 25px;">📝 Что такое медианная эффективность?</h3>
                        <div style="background: #d1ecf1; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #17a2b8;">
                            <p style="margin: 0 0 10px 0; color: #4a5568;">
                                <strong>Медиана</strong> — значение, которое делит все магазины пополам:
                                половина работает эффективнее, половина — хуже.
                            </p>
                            <p style="margin: 10px 0 0 0; color: #333; font-size: 13px;">
                                <strong>Почему медиана, а не среднее?</strong><br>
                                Медиана устойчива к выбросам. Если один магазин показывает аномально высокую эффективность,
                                это не искажает бенчмарк для остальных.
                            </p>
                        </div>

                        <h3 style="color: #495057; font-size: 16px; margin-top: 25px;">🔍 Как интерпретировать?</h3>
                        <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                                <tr style="background: #e9ecef;">
                                    <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Ситуация</th>
                                    <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Что это значит</th>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; color: #28a745; font-weight: 600;">
                                        Оранжевая выше синей
                                    </td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">
                                        Магазин работает <strong>лучше медианы</strong>. Генерирует больше выручки на м².
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; color: #C73E1D; font-weight: 600;">
                                        Оранжевая ниже синей
                                    </td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">
                                        Площадь используется <strong>менее эффективно</strong>. Возможно, стоит оптимизировать.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; color: #6c757d; font-weight: 600;">
                                        Линии близки
                                    </td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">
                                        Магазин работает примерно на уровне медианы по сети.
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <h3 style="color: #667eea; font-size: 16px; margin-top: 25px;">🔀 Режимы сортировки</h3>
                        <p style="margin: 10px 0; color: #4a5568;">
                            <strong>Менее эффективные:</strong> Сначала магазины, где фактическая площадь больше всего превышает оптимальную
                            (наибольший потенциал оптимизации).
                        </p>
                        <p style="margin: 10px 0; color: #4a5568;">
                            <strong>Более эффективные:</strong> Сначала магазины, где оптимальная площадь больше всего превышает фактическую
                            (лучшие по эффективности).
                        </p>

                        <h3 style="color: #F18F01; font-size: 16px; margin-top: 25px;">📈 Показатели в заголовке</h3>
                        <div style="background: #fff3e0; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #F18F01;">
                            <p style="margin: 0 0 10px 0; color: #333;">
                                <strong>Δ +15 м²</strong> — фактическая площадь на 15 м² больше оптимальной (неэффективно)
                            </p>
                            <p style="margin: 0; color: #333;">
                                <strong>Δ -20 м²</strong> — фактическая площадь на 20 м² меньше оптимальной (эффективно!)
                            </p>
                        </div>

                        <div style="background: #fff3e0; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #ff9800;">
                            <p style="margin: 0; color: #333; font-weight: 600;">⚠️ Важно учитывать:</p>
                            <ul style="margin: 10px 0 0 0; padding-left: 20px; color: #4a5568; font-size: 13px;">
                                <li>Локация магазина (трафик, конкуренция)</li>
                                <li>Ассортимент и ценовой сегмент</li>
                                <li>Сезонность и временные факторы</li>
                                <li>Возраст магазина (новые могут ещё не выйти на плановые показатели)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

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
        // Хранилище данных для таблицы
        window.{self.chart_id}_tableData = null;

        /**
         * Переключение модального окна с объяснением
         */
        function toggleOptimalAreaInfo_{self.chart_id}() {{
            const modal = document.getElementById('{self.chart_id}_modal');
            if (modal.style.display === 'none' || modal.style.display === '') {{
                modal.style.display = 'flex';
                modal.style.alignItems = 'center';
                modal.style.justifyContent = 'center';
            }} else {{
                modal.style.display = 'none';
            }}
        }}

        function update{self.chart_id}() {{
            const data = window.filteredData || window.rawData;
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const topSelect = document.getElementById('{self.chart_id}_top');
            const sortSelect = document.getElementById('{self.chart_id}_sort');

            const selectedMetric = metricSelect ? metricSelect.value : 'revenue';
            const topValue = topSelect ? topSelect.value : '8';
            const sortMode = sortSelect ? sortSelect.value : 'less_efficient';

            // Группировка по месяцам для всех магазинов
            const allStoresMonthlyData = {{}};

            data.forEach(row => {{
                const store = row['Магазин'];
                const dateStr = row['Дата'];
                if (!store || !dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);
                const periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;

                if (!allStoresMonthlyData[periodKey]) {{
                    allStoresMonthlyData[periodKey] = {{}};
                }}

                if (!allStoresMonthlyData[periodKey][store]) {{
                    allStoresMonthlyData[periodKey][store] = {{
                        revenue: 0,
                        profit: 0,
                        area: parseFloat(row['Торговая площадь магазина']) || 0
                    }};
                }}

                allStoresMonthlyData[periodKey][store].revenue += parseFloat(row['Сумма в чеке']) || 0;
                allStoresMonthlyData[periodKey][store].profit += parseFloat(row['Наценка продажи в чеке']) || 0;
            }});

            // Сортируем периоды
            const periods = Object.keys(allStoresMonthlyData).sort((a, b) => {{
                const [d1, m1, y1] = a.split('.');
                const [d2, m2, y2] = b.split('.');
                return (parseInt(y1) * 12 + parseInt(m1)) - (parseInt(y2) * 12 + parseInt(m2));
            }});

            // Получаем список всех магазинов
            const allStores = new Set();
            Object.values(allStoresMonthlyData).forEach(storesInPeriod => {{
                Object.keys(storesInPeriod).forEach(store => allStores.add(store));
            }});

            // Для каждого магазина рассчитываем данные
            const storeResults = {{}};

            [...allStores].forEach(store => {{
                const actualAreas = [];
                const optimalAreas = [];
                let totalDiff = 0;
                let validPeriods = 0;

                periods.forEach(period => {{
                    const storesInPeriod = allStoresMonthlyData[period];

                    // Вычисляем эффективность для всех магазинов в этом периоде
                    const efficiencies = [];
                    Object.values(storesInPeriod).forEach(d => {{
                        if (d.area > 0) {{
                            const metric = selectedMetric === 'revenue' ? d.revenue : d.profit;
                            efficiencies.push(metric / d.area);
                        }}
                    }});

                    // Медиана
                    if (efficiencies.length === 0) {{
                        actualAreas.push(0);
                        optimalAreas.push(0);
                        return;
                    }}

                    const sorted = efficiencies.slice().sort((a, b) => a - b);
                    const mid = Math.floor(sorted.length / 2);
                    const medianEff = sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];

                    // Данные магазина
                    const storeData = storesInPeriod[store];
                    if (!storeData || storeData.area === 0) {{
                        actualAreas.push(0);
                        optimalAreas.push(0);
                        return;
                    }}

                    const actualArea = storeData.area;
                    const storeMetric = selectedMetric === 'revenue' ? storeData.revenue : storeData.profit;
                    const optimalArea = medianEff > 0 ? storeMetric / medianEff : 0;

                    actualAreas.push(actualArea);
                    optimalAreas.push(optimalArea);

                    if (actualArea > 0 && optimalArea > 0) {{
                        totalDiff += (actualArea - optimalArea);
                        validPeriods++;
                    }}
                }});

                const avgDiff = validPeriods > 0 ? totalDiff / validPeriods : 0;

                storeResults[store] = {{
                    actualAreas,
                    optimalAreas,
                    avgDiff,  // положительное = неэффективно, отрицательное = эффективно
                    avgActual: actualAreas.filter(v => v > 0).reduce((a, b) => a + b, 0) / (actualAreas.filter(v => v > 0).length || 1),
                    avgOptimal: optimalAreas.filter(v => v > 0).reduce((a, b) => a + b, 0) / (optimalAreas.filter(v => v > 0).length || 1)
                }};
            }});

            // Сортировка магазинов
            let sortedStores;
            if (sortMode === 'less_efficient') {{
                // Сначала те, где фактическая > оптимальной (большой положительный diff)
                sortedStores = Object.keys(storeResults).sort((a, b) => storeResults[b].avgDiff - storeResults[a].avgDiff);
            }} else {{
                // Сначала те, где оптимальная > фактической (большой отрицательный diff)
                sortedStores = Object.keys(storeResults).sort((a, b) => storeResults[a].avgDiff - storeResults[b].avgDiff);
            }}

            // Фильтр по топу
            if (topValue !== 'all') {{
                sortedStores = sortedStores.slice(0, parseInt(topValue));
            }}

            // Расчёт сетки
            const count = sortedStores.length;
            let cols = 4;
            if (count <= 4) cols = 2;
            else if (count <= 8) cols = 4;
            else cols = 4;
            const rows = Math.ceil(count / cols);

            // Фиксированные отступы
            const gapPx = 70;
            const topPaddingPx = 50;
            const plotHeightPx = 160;
            const totalHeight = topPaddingPx + rows * plotHeightPx + (rows - 1) * gapPx + 40;

            const horizontalSpacing = 0.05;
            const topPadding = topPaddingPx / totalHeight;
            const verticalGap = gapPx / totalHeight;
            const plotHeight = plotHeightPx / totalHeight;
            const plotWidth = (1 - horizontalSpacing * (cols - 1)) / cols;

            const traces = [];
            const annotations = [];

            const metricLabel = selectedMetric === 'revenue' ? 'выручки' : 'прибыли';

            const layout = {{
                title: {{
                    text: `Тренд оптимальной площади (на основе ${{metricLabel}}) — ${{sortMode === 'less_efficient' ? 'менее эффективные' : 'более эффективные'}}`,
                    font: {{ size: 16 }},
                    y: 0.99
                }},
                height: totalHeight,
                showlegend: false,
                margin: {{ t: 40, b: 30, l: 50, r: 20 }}
            }};

            sortedStores.forEach((store, idx) => {{
                const rowNum = Math.floor(idx / cols);
                const colNum = idx % cols;

                const xStart = colNum * (plotWidth + horizontalSpacing);
                const xEnd = xStart + plotWidth;
                const yEnd = 1 - topPadding - rowNum * (plotHeight + verticalGap);
                const yStart = yEnd - plotHeight;

                const xKey = idx === 0 ? 'xaxis' : `xaxis${{idx + 1}}`;
                const yKey = idx === 0 ? 'yaxis' : `yaxis${{idx + 1}}`;
                const xRef = idx === 0 ? 'x' : `x${{idx + 1}}`;
                const yRef = idx === 0 ? 'y' : `y${{idx + 1}}`;

                const result = storeResults[store];

                // Фактическая площадь (синяя)
                traces.push({{
                    x: periods,
                    y: result.actualAreas,
                    type: 'scatter',
                    mode: 'lines',
                    name: `${{store}} факт`,
                    line: {{ width: 2, color: '#2E86AB' }},
                    xaxis: xRef,
                    yaxis: yRef,
                    hovertemplate: `<b>${{store}}</b><br>%{{x}}<br>Факт: %{{y:.1f}} м²<extra></extra>`
                }});

                // Оптимальная площадь (оранжевая пунктирная)
                traces.push({{
                    x: periods,
                    y: result.optimalAreas,
                    type: 'scatter',
                    mode: 'lines',
                    name: `${{store}} оптим`,
                    line: {{ width: 2, color: '#F18F01', dash: 'dash' }},
                    xaxis: xRef,
                    yaxis: yRef,
                    hovertemplate: `<b>${{store}}</b><br>%{{x}}<br>Оптим: %{{y:.1f}} м²<extra></extra>`
                }});

                // Y range для subplot
                const allY = [...result.actualAreas, ...result.optimalAreas].filter(v => v > 0);
                const yMin = allY.length > 0 ? Math.min(...allY) * 0.9 : 0;
                const yMax = allY.length > 0 ? Math.max(...allY) * 1.1 : 100;

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
                    range: [yMin, yMax],
                    showticklabels: true,
                    tickfont: {{ size: 8 }},
                    showgrid: true,
                    gridcolor: '#eee',
                    anchor: xRef
                }};

                // Заголовок
                const titleX = (xStart + xEnd) / 2;
                const titleY = yEnd + 0.005;

                const diff = result.avgDiff;
                const diffColor = diff > 0 ? '#C73E1D' : '#28a745';
                const diffSign = diff > 0 ? '+' : '';
                const diffLabel = `<span style="color:${{diffColor}}">Δ ${{diffSign}}${{diff.toFixed(1)}} м²</span>`;

                annotations.push({{
                    text: `<b>${{store}}</b> ${{diffLabel}}`,
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

            // Сохраняем данные для таблицы
            window.{self.chart_id}_tableData = {{
                stores: sortedStores,
                periods: periods,
                storeResults: storeResults,
                metric: selectedMetric
            }};

            Plotly.newPlot('{self.chart_id}', traces, layout, {{responsive: true}});

            // Обновляем таблицу если открыта
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none') {{
                generateTable_{self.chart_id}();
            }}
        }}

        function getTableData_{self.chart_id}() {{
            const td = window.{self.chart_id}_tableData;
            if (!td) return [];

            const tableData = [];
            td.stores.forEach(store => {{
                const result = td.storeResults[store];
                const row = {{
                    'Магазин': store,
                    'Факт. площадь (ср.)': Math.round(result.avgActual * 10) / 10,
                    'Оптим. площадь (ср.)': Math.round(result.avgOptimal * 10) / 10,
                    'Разница (ср.)': Math.round(result.avgDiff * 10) / 10
                }};

                // Добавляем данные по периодам
                td.periods.forEach((period, i) => {{
                    row[`Факт ${{period}}`] = Math.round(result.actualAreas[i] * 10) / 10;
                    row[`Оптим ${{period}}`] = Math.round(result.optimalAreas[i] * 10) / 10;
                }});

                tableData.push(row);
            }});

            return tableData;
        }}
        """
