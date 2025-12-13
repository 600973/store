# PROJECT_ROOT: charts/chart_area_performance.py
"""
График: Анализ производительности магазинов на м²
Scatter plot: X=Площадь, Y=Выручка/м², size=Выручка, color=Прибыль/м²
"""
from charts.base_chart import BaseChart


class ChartAreaPerformance(BaseChart):
    """
    Метод 1: Анализ производительности на м²
    - Scatter plot с точками магазинов
    - X = Площадь (м²)
    - Y = Выручка на м² (руб)
    - Size = Общая выручка
    - Color = Прибыль на м² (цветовая шкала RdYlGn)
    - Вертикальная линия = Оптимальная площадь (среднее ТОП-N)
    """

    def __init__(self, chart_id='chart_area_performance', **kwargs):
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
        </div>
        '''

    def _generate_detail_selector_html(self) -> str:
        """Этот график не использует детализацию по времени"""
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
                    <div class="model-selector">
                        <label>Модель:</label>
                        <select id="{self.chart_id}_model" class="model-select">
                            <option value="qwen2.5:7b" selected>qwen2.5:7b</option>
                            <option value="qwen3:14b">qwen3:14b</option>
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
            }}
        }}

        /**
         * Генерация таблицы
         */
        function generateTable_{self.chart_id}() {{
            const tableData = getTableData_{self.chart_id}();
            if (!tableData || tableData.length === 0) {{
                document.getElementById('{self.chart_id}_table').innerHTML = '<p style="padding: 20px;">Нет данных</p>';
                return;
            }}

            const columns = Object.keys(tableData[0]);
            let html = '<div class="table-scroll-wrapper"><table class="chart-table">';
            html += '<thead><tr>' + columns.map(c => '<th>' + c + '</th>').join('') + '</tr></thead>';
            html += '<tbody>';
            tableData.forEach(row => {{
                html += '<tr>' + columns.map(c => {{
                    const val = row[c];
                    return '<td>' + (typeof val === 'number' ? val.toLocaleString('ru-RU') : val) + '</td>';
                }}).join('') + '</tr>';
            }});
            html += '</tbody></table></div>';

            document.getElementById('{self.chart_id}_table').innerHTML = html;
        }}

        /**
         * Агрегация данных по магазинам с расчётом метрик на м²
         */
        function aggregateStorePerformance(data) {{
            const storeMap = {{}};

            data.forEach(row => {{
                const store = row['Магазин'];
                const area = parseFloat(row['Торговая площадь магазина']) || 0;
                // Используем реальные названия колонок из Excel
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

            // Преобразуем в массив и рассчитываем метрики на м²
            const result = Object.values(storeMap).map(s => {{
                const revenuePerM2 = s.area > 0 ? Math.round(s.revenue / s.area) : 0;
                const profitPerM2 = s.area > 0 ? Math.round(s.profit / s.area) : 0;
                const storeId = s.store.match(/\\d+/) ? parseInt(s.store.match(/\\d+/)[0]) : 0;

                return {{
                    store: s.store,
                    storeId: storeId,
                    area: s.area,
                    revenue: s.revenue,
                    profit: s.profit,
                    revenuePerM2: revenuePerM2,
                    profitPerM2: profitPerM2
                }};
            }});

            // Сортируем по выручке на м² для определения ТОП-5
            result.sort((a, b) => b.revenuePerM2 - a.revenuePerM2);

            return result;
        }}

        // Маппинг значений селекторов на названия для отображения
        const metricLabels_{self.chart_id} = {{
            'revenuePerM2': 'Выручка/м²',
            'profitPerM2': 'Прибыль/м²',
            'revenue': 'Общая выручка',
            'profit': 'Общая прибыль',
            'area': 'Площадь',
            'fixed': 'Одинаковый'
        }};

        /**
         * Обновление графика
         */
        function update{self.chart_id}() {{
            const chartDiv = document.getElementById('{self.chart_id}');
            if (!chartDiv) return;

            // Проверяем, видим ли график (на активной вкладке)
            const tabContent = chartDiv.closest('.tab-content');
            const isVisible = tabContent && tabContent.classList.contains('active');

            // Если график скрыт - помечаем для отложенного обновления и выходим
            if (!isVisible) {{
                window.chartsNeedUpdate = window.chartsNeedUpdate || {{}};
                window.chartsNeedUpdate['{self.chart_id}'] = true;
                return;
            }}

            const data = window.filteredData || window.rawData;
            const storeData = aggregateStorePerformance(data);

            if (storeData.length === 0) {{
                Plotly.purge('{self.chart_id}');
                return;
            }}

            // Читаем значения селекторов
            const yAxisSelect = document.getElementById('{self.chart_id}_yaxis');
            const colorSelect = document.getElementById('{self.chart_id}_color');
            const sizeSelect = document.getElementById('{self.chart_id}_size');
            const topSelect = document.getElementById('{self.chart_id}_top');

            const yAxisMetric = yAxisSelect ? yAxisSelect.value : 'revenuePerM2';
            const colorMetric = colorSelect ? colorSelect.value : 'profitPerM2';
            const sizeMetric = sizeSelect ? sizeSelect.value : 'revenue';
            const topValue = topSelect ? topSelect.value : '5';

            // Сортируем по выбранной метрике Y для определения ТОП
            const sortedData = [...storeData].sort((a, b) => b[yAxisMetric] - a[yAxisMetric]);

            // Сохраняем для таблицы
            window.storePerformanceData_{self.chart_id} = sortedData;

            // Расчёт оптимальной площади (среднее ТОП-N)
            let optimalArea = 0;
            let topN = topValue === 'all' ? sortedData.length : parseInt(topValue);
            if (topN > 0 && sortedData.length > 0) {{
                const topStores = sortedData.slice(0, Math.min(topN, sortedData.length));
                optimalArea = Math.round(topStores.reduce((sum, s) => sum + s.area, 0) / topStores.length);
            }}

            // Данные для графика
            const x = storeData.map(s => s.area);
            const y = storeData.map(s => s[yAxisMetric]);

            // Размер точек
            let sizes;
            if (sizeMetric === 'fixed') {{
                sizes = storeData.map(() => 15);
            }} else {{
                const maxSize = Math.max(...storeData.map(s => s[sizeMetric]));
                sizes = storeData.map(s => maxSize > 0 ? Math.max(8, Math.sqrt(s[sizeMetric] / maxSize) * 40) : 15);
            }}

            // Цвет точек
            const colors = storeData.map(s => s[colorMetric]);

            const text = storeData.map(s => s.storeId.toString());
            const hoverText = storeData.map(s =>
                `<b>${{s.store}}</b><br>` +
                `Площадь: ${{s.area.toLocaleString('ru-RU')}} м²<br>` +
                `Выручка/м²: ${{s.revenuePerM2.toLocaleString('ru-RU')}} руб<br>` +
                `Прибыль/м²: ${{s.profitPerM2.toLocaleString('ru-RU')}} руб<br>` +
                `Общая выручка: ${{Math.round(s.revenue).toLocaleString('ru-RU')}} руб<br>` +
                `Общая прибыль: ${{Math.round(s.profit).toLocaleString('ru-RU')}} руб`
            );

            const yAxisLabel = metricLabels_{self.chart_id}[yAxisMetric] || yAxisMetric;
            const colorLabel = metricLabels_{self.chart_id}[colorMetric] || colorMetric;

            // Кастомная красно-зелёная шкала (без жёлтого)
            const redGreenScale = [
                [0, 'rgb(215, 48, 39)'],      // Красный (низкие значения)
                [0.5, 'rgb(255, 255, 191)'],  // Светло-жёлтый (середина)
                [1, 'rgb(26, 152, 80)']       // Зелёный (высокие значения)
            ];

            const trace = {{
                x: x,
                y: y,
                mode: 'markers+text',
                type: 'scatter',
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
                text: text,
                textposition: 'top center',
                textfont: {{
                    size: 10,
                    color: '#666'
                }},
                hovertext: hoverText,
                hoverinfo: 'text'
            }};

            const topLabel = topValue === 'all' ? 'всех' : `Топ-${{topValue}}`;
            const layout = {{
                title: {{
                    text: `Метод 1: ${{yAxisLabel}} vs Площадь (оптимум по ${{topLabel}})`,
                    font: {{ size: 16 }}
                }},
                xaxis: {{
                    title: 'Площадь (м²)',
                    gridcolor: '#e9ecef'
                }},
                yaxis: {{
                    title: yAxisLabel,
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                margin: {{ l: 80, r: 80, t: 60, b: 60 }},
                hovermode: 'closest',
                shapes: [{{
                    type: 'line',
                    x0: optimalArea,
                    x1: optimalArea,
                    y0: 0,
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'red',
                        width: 2,
                        dash: 'dash'
                    }}
                }}],
                annotations: [{{
                    x: optimalArea,
                    y: 1,
                    yref: 'paper',
                    text: `Оптимум: ${{optimalArea}} м²`,
                    showarrow: false,
                    font: {{
                        color: 'red',
                        size: 12
                    }},
                    yanchor: 'bottom'
                }}]
            }};

            const config = {{
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['lasso2d', 'select2d']
            }};

            Plotly.react('{self.chart_id}', [trace], layout, config);
        }}

        /**
         * Данные для таблицы
         */
        function getTableData_{self.chart_id}() {{
            const storeData = window.storePerformanceData_{self.chart_id} || [];

            return storeData.map(s => ({{
                'Магазин': s.store,
                'Площадь (м²)': s.area,
                'Выручка': Math.round(s.revenue),
                'Прибыль': Math.round(s.profit),
                'Выручка/м²': s.revenuePerM2,
                'Прибыль/м²': s.profitPerM2
            }}));
        }}

        // Регистрация в глобальном обновлении
        if (!window.chartUpdateFunctions) {{
            window.chartUpdateFunctions = {{}};
        }}
        window.chartUpdateFunctions['{self.chart_id}'] = update{self.chart_id};

        // Первоначальная отрисовка - только если график на активной вкладке
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(function() {{
                const chartDiv = document.getElementById('{self.chart_id}');
                if (chartDiv) {{
                    const tabContent = chartDiv.closest('.tab-content');
                    // Инициализируем только если на активной вкладке
                    if (tabContent && tabContent.classList.contains('active')) {{
                        update{self.chart_id}();
                    }} else {{
                        // Помечаем для отложенной инициализации
                        window.chartsNeedUpdate = window.chartsNeedUpdate || {{}};
                        window.chartsNeedUpdate['{self.chart_id}'] = true;
                    }}
                }}
            }}, 100);
        }});
        """
