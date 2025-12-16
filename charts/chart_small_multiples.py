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
            <div class="selector-group" style="display: flex; align-items: center; gap: 6px;">
                <label style="display: flex; align-items: center; gap: 6px; font-weight: 500; font-size: 13px; color: #495057; cursor: pointer;">
                    <input type="checkbox" id="{self.chart_id}_compare_yoy" onchange="update{self.chart_id}()" style="width: 16px; height: 16px; cursor: pointer;" checked>
                    vs прошлый год
                </label>
            </div>
            <div class="selector-group" style="display: flex; align-items: center;">
                <button onclick="toggleSmallMultiplesInfo()" style="
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

            <!-- Модальное окно с объяснением -->
            <div id="small-multiples-modal" style="
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
                    max-width: 650px;
                    max-height: 85vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                    margin: 30px auto;
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
                        📊 Показатели шпалеры
                        <span onclick="toggleSmallMultiplesInfo()" style="
                            position: absolute;
                            top: 15px;
                            right: 20px;
                            font-size: 32px;
                            cursor: pointer;
                            line-height: 1;
                        ">&times;</span>
                    </div>
                    <div style="padding: 25px; line-height: 1.6;">
                        <h3 style="color: #667eea; font-size: 16px; margin-top: 0;">📈 Тренд (%)</h3>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Что это:</strong> Процент изменения показателя за весь период относительно среднего значения.</p>

                        <p style="margin: 10px 0; color: #4a5568;"><strong>Как считается (линейная регрессия):</strong></p>
                        <ol style="margin: 10px 0; padding-left: 25px; color: #4a5568;">
                            <li>По точкам строится линия тренда методом наименьших квадратов</li>
                            <li>Вычисляется угловой коэффициент (slope) — насколько растёт/падает значение за 1 период</li>
                            <li>Формула: <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 4px;">Тренд = (slope × N) / avg × 100%</code></li>
                        </ol>

                        <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea;">
                            <p style="margin: 0 0 10px 0; color: #333; font-weight: 600;">📝 Пример расчёта:</p>
                            <p style="margin: 5px 0; color: #4a5568;">Данные за 4 месяца: <strong>100, 120, 140, 160</strong></p>
                            <p style="margin: 5px 0; color: #4a5568;">• Среднее (avg) = (100+120+140+160) / 4 = <strong>130</strong></p>
                            <p style="margin: 5px 0; color: #4a5568;">• Угол наклона (slope) = <strong>20</strong> (каждый месяц +20)</p>
                            <p style="margin: 5px 0; color: #4a5568;">• Тренд = (20 × 4) / 130 × 100% = <strong style="color: #28a745;">+61.5%</strong></p>
                            <p style="margin: 10px 0 0 0; color: #666; font-size: 13px;">Интерпретация: за 4 месяца показатель вырос на 61.5% относительно среднего уровня</p>
                        </div>

                        <p style="margin: 10px 0; color: #4a5568;"><strong>Цвета:</strong> <span style="color: #28a745; font-weight: 600;">Зелёный (+)</span> — рост, <span style="color: #dc3545; font-weight: 600;">Красный (−)</span> — падение</p>

                        <h3 style="color: #667eea; font-size: 16px; margin-top: 20px;">💰 Сумма (натуральное выражение)</h3>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Что это:</strong> Общая сумма выбранной метрики за весь период.</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Как считается:</strong> Простое суммирование всех значений метрики по всем периодам.</p>

                        <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea;">
                            <p style="margin: 0 0 10px 0; color: #333; font-weight: 600;">📝 Пример:</p>
                            <p style="margin: 5px 0; color: #4a5568;">Данные: 100, 120, 140, 160</p>
                            <p style="margin: 5px 0; color: #4a5568;">Сумма = 100 + 120 + 140 + 160 = <strong>520</strong> (отображается как <strong>520</strong> или <strong>0.5К</strong>)</p>
                        </div>

                        <p style="margin: 10px 0; color: #4a5568;"><strong>Формат отображения:</strong></p>
                        <ul style="margin: 10px 0; padding-left: 25px; color: #4a5568;">
                            <li><strong>К</strong> — тысячи (1К = 1 000, 15К = 15 000)</li>
                            <li><strong>М</strong> — миллионы (1М = 1 000 000, 1.5М = 1 500 000)</li>
                        </ul>

                        <h3 style="color: #667eea; font-size: 16px; margin-top: 20px;">🔀 Режимы сортировки</h3>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>По сумме:</strong> Графики упорядочены по общей сумме (от большего к меньшему). В заголовке — сумма в скобках.</p>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>По тренду:</strong> Графики упорядочены по тренду (от роста к падению). В заголовке — % тренда, на графике — пунктирная линия тренда.</p>

                        <h3 style="color: #667eea; font-size: 16px; margin-top: 20px;">📅 Сравнение с прошлым годом (YoY)</h3>
                        <p style="margin: 10px 0; color: #4a5568;"><strong>Что это:</strong> Мини-гистограмма под каждым графиком, показывающая изменение относительно того же месяца прошлого года.</p>

                        <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea;">
                            <p style="margin: 0 0 10px 0; color: #333; font-weight: 600;">📝 Как читать:</p>
                            <p style="margin: 5px 0; color: #4a5568;">
                                <span style="display: inline-block; width: 12px; height: 12px; background: #28a745; margin-right: 6px; vertical-align: middle;"></span>
                                <strong>Зелёный столбик вверх</strong> — рост относительно того же месяца прошлого года
                            </p>
                            <p style="margin: 5px 0; color: #4a5568;">
                                <span style="display: inline-block; width: 12px; height: 12px; background: #dc3545; margin-right: 6px; vertical-align: middle;"></span>
                                <strong>Красный столбик вниз</strong> — падение относительно прошлого года
                            </p>
                            <p style="margin: 10px 0 0 0; color: #666; font-size: 13px;">
                                Высота столбика пропорциональна % изменения. Наведите для точного значения.
                            </p>
                        </div>

                        <p style="margin: 10px 0; color: #4a5568;"><strong>Примечание:</strong> Работает только в режиме детализации "По месяцам". При отсутствии данных за прошлый год столбик будет отсутствовать.</p>
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
        /**
         * Переключение модального окна с объяснением показателей
         */
        function toggleSmallMultiplesInfo() {{
            const modal = document.getElementById('small-multiples-modal');
            if (modal.style.display === 'none' || modal.style.display === '') {{
                modal.style.display = 'flex';
                modal.style.alignItems = 'center';
                modal.style.justifyContent = 'center';
            }} else {{
                modal.style.display = 'none';
            }}
        }}

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
            const compareYoyCheckbox = document.getElementById('{self.chart_id}_compare_yoy');

            const groupByField = groupBySelect ? groupBySelect.value : 'Магазин';
            const metricField = metricSelect ? metricSelect.value : 'Сумма в чеке';
            const topValue = topSelect ? topSelect.value : '20';
            const sortMode = sortSelect ? sortSelect.value : 'sum';
            const showYoyCompare = compareYoyCheckbox ? compareYoyCheckbox.checked : false;

            // Агрегация: группа -> период -> сумма
            const groupData = {{}};
            const groupTotals = {{}};

            data.forEach(row => {{
                const group = row[groupByField];
                const year = parseInt(row['Год']);
                const monthName = row['Месяц'];
                const month = monthNameToNum_{self.chart_id}[monthName] || 1;
                // Для метрики "Число чеков" используем хелпер с учётом группировки
                const value = metricField === 'Число чеков'
                    ? getChecksValue(row, groupByField)
                    : (parseFloat(row[metricField]) || 0);

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
            const yoyBarHeightPx = showYoyCompare ? 70 : 0;  // высота мини-гистограммы YoY (увеличена)

            // Общая высота
            const totalHeight = topPaddingPx + rows * (plotHeightPx + yoyBarHeightPx) + (rows - 1) * gapPx + 40;

            // Переводим в доли для domain
            const horizontalSpacing = 0.05;
            const topPadding = topPaddingPx / totalHeight;
            const verticalGap = gapPx / totalHeight;
            const plotHeight = plotHeightPx / totalHeight;
            const yoyBarHeight = yoyBarHeightPx / totalHeight;

            // Расчёт YoY изменений для каждой группы (месяц текущего года vs тот же месяц прошлого года)
            // Берём данные за прошлый год из rawData, даже если они не в фильтре
            const groupYoyChanges = {{}};
            if (showYoyCompare && level === 'month') {{
                // Агрегируем данные за прошлый год из rawData (не filteredData!)
                const rawDataForYoy = window.rawData || [];
                const prevYearData = {{}};  // group -> period -> value

                // Определяем год из текущих отфильтрованных данных
                const yearsInFiltered = new Set();
                periods.forEach(p => {{
                    const [d, m, y] = p.split('.');
                    yearsInFiltered.add(parseInt(y));
                }});
                const currentYear = Math.max(...yearsInFiltered);
                const prevYear = currentYear - 1;

                // Агрегируем данные за прошлый год из rawData
                rawDataForYoy.forEach(row => {{
                    const group = row[groupByField];
                    const year = parseInt(row['Год']);
                    const monthName = row['Месяц'];
                    const month = monthNameToNum_{self.chart_id}[monthName] || 1;
                    // Для метрики "Число чеков" используем хелпер с учётом группировки
                    const value = metricField === 'Число чеков'
                        ? getChecksValue(row, groupByField)
                        : (parseFloat(row[metricField]) || 0);

                    if (!group || year !== prevYear) return;

                    const periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;

                    if (!prevYearData[group]) prevYearData[group] = {{}};
                    if (!prevYearData[group][periodKey]) prevYearData[group][periodKey] = 0;
                    prevYearData[group][periodKey] += value;
                }});

                // Теперь считаем YoY изменения
                groups.forEach(group => {{
                    const yoyChanges = [];

                    // Проходим по периодам текущего года
                    periods.forEach(period => {{
                        const [d, m, y] = period.split('.');
                        const year = parseInt(y);

                        if (year === currentYear) {{
                            const prevYearPeriod = `01.${{m}}.${{prevYear}}`;
                            const currentVal = groupData[group][period] || 0;
                            const prevVal = (prevYearData[group] && prevYearData[group][prevYearPeriod]) || 0;

                            if (prevVal > 0 && currentVal > 0) {{
                                const change = ((currentVal - prevVal) / prevVal) * 100;
                                yoyChanges.push({{ period, month: m, change, currentVal, prevVal, prevYearPeriod }});
                            }} else if (currentVal > 0 && prevVal === 0) {{
                                // Нет данных за прошлый год
                                yoyChanges.push({{ period, month: m, change: null, currentVal, prevVal: 0, prevYearPeriod }});
                            }} else {{
                                yoyChanges.push({{ period, month: m, change: null, currentVal: 0, prevVal: 0, prevYearPeriod }});
                            }}
                        }}
                    }});
                    groupYoyChanges[group] = yoyChanges;
                }});
            }}

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

            // Счётчик для осей (включая YoY)
            let axisCounter = 0;

            groups.forEach((group, idx) => {{
                const rowNum = Math.floor(idx / cols);
                const colNum = idx % cols;

                // Domain для X оси (слева направо)
                const xStart = colNum * (plotWidth + horizontalSpacing);
                const xEnd = xStart + plotWidth;

                // Domain для Y оси (снизу вверх, поэтому инвертируем row)
                // topPadding резервирует место для основного заголовка
                const cellHeight = plotHeight + yoyBarHeight;
                const yEnd = 1 - topPadding - rowNum * (cellHeight + verticalGap);
                const yStart = yEnd - plotHeight;

                // YoY bar domain (под основным графиком)
                const yoyYEnd = yStart;
                const yoyYStart = yoyYEnd - yoyBarHeight;

                axisCounter++;
                const xKey = axisCounter === 1 ? 'xaxis' : `xaxis${{axisCounter}}`;
                const yKey = axisCounter === 1 ? 'yaxis' : `yaxis${{axisCounter}}`;
                const xRef = axisCounter === 1 ? 'x' : `x${{axisCounter}}`;
                const yRef = axisCounter === 1 ? 'y' : `y${{axisCounter}}`;

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
                    showticklabels: !showYoyCompare,  // Скрываем подписи если включено YoY
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

                // Мини-гистограмма YoY (если включена)
                if (showYoyCompare && level === 'month' && groupYoyChanges[group] && groupYoyChanges[group].length > 0) {{
                    axisCounter++;
                    const yoyXKey = `xaxis${{axisCounter}}`;
                    const yoyYKey = `yaxis${{axisCounter}}`;
                    const yoyXRef = `x${{axisCounter}}`;
                    const yoyYRef = `y${{axisCounter}}`;

                    const yoyData = groupYoyChanges[group];

                    // Фильтруем только валидные изменения (не null)
                    const validChanges = yoyData.filter(d => d.change !== null).map(d => d.change);
                    const maxAbsChange = validChanges.length > 0
                        ? Math.max(...validChanges.map(c => Math.abs(c)))
                        : 50;
                    const yoyRange = Math.max(maxAbsChange * 1.2, 10);  // минимум 10%

                    // Столбцы: зелёные вверх (рост), красные вниз (падение)
                    // Положительные значения
                    traces.push({{
                        x: yoyData.map(d => d.period),  // Формат 01.MM.YYYY
                        y: yoyData.map(d => d.change !== null && d.change > 0 ? Math.min(d.change, 200) : 0),
                        type: 'bar',
                        marker: {{ color: '#28a745', opacity: 0.85 }},
                        xaxis: yoyXRef,
                        yaxis: yoyYRef,
                        hovertemplate: yoyData.map(d =>
                            d.change !== null && d.change > 0
                                ? `<b>${{group}}</b><br>${{d.period}} vs ${{d.prevYearPeriod}}<br>YoY: <b>+${{d.change.toFixed(1)}}%</b><extra></extra>`
                                : ''
                        ),
                        showlegend: false
                    }});

                    // Отрицательные значения
                    traces.push({{
                        x: yoyData.map(d => d.period),  // Формат 01.MM.YYYY
                        y: yoyData.map(d => d.change !== null && d.change < 0 ? Math.max(d.change, -200) : 0),
                        type: 'bar',
                        marker: {{ color: '#dc3545', opacity: 0.85 }},
                        xaxis: yoyXRef,
                        yaxis: yoyYRef,
                        hovertemplate: yoyData.map(d =>
                            d.change !== null && d.change < 0
                                ? `<b>${{group}}</b><br>${{d.period}} vs ${{d.prevYearPeriod}}<br>YoY: <b>${{d.change.toFixed(1)}}%</b><extra></extra>`
                                : ''
                        ),
                        showlegend: false
                    }});

                    layout[yoyXKey] = {{
                        domain: [xStart, xEnd],
                        showticklabels: true,
                        tickfont: {{ size: 7, color: '#666' }},
                        tickangle: -45,
                        showgrid: false,
                        type: 'category',
                        anchor: yoyYRef,
                        side: 'bottom'
                    }};

                    layout[yoyYKey] = {{
                        domain: [yoyYStart, yoyYEnd],
                        range: [-yoyRange, yoyRange],
                        showticklabels: true,
                        tickfont: {{ size: 7, color: '#666' }},
                        tickformat: '+.0f',
                        ticksuffix: '%',
                        nticks: 3,
                        showgrid: true,
                        gridcolor: '#eee',
                        zeroline: true,
                        zerolinecolor: '#999',
                        zerolinewidth: 1,
                        anchor: yoyXRef,
                        side: 'left'
                    }};
                }}

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
