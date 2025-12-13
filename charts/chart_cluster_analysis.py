# PROJECT_ROOT: charts/chart_cluster_analysis.py
"""
Метод 4: Кластеризация по размеру + Бенчмаркинг
- Box-plot по кластерам (Малые, Средние, Крупные)
- Отметки лидеров в каждом кластере
- Статистика по кластерам
"""
from charts.base_chart import BaseChart


class ChartClusterAnalysis(BaseChart):
    """
    Метод 4: Кластеризация + Бенчмаркинг
    - Box-plot эффективности по размерным кластерам
    - Аннотации лидеров (★)
    - Таблица с характеристиками кластеров
    """

    def __init__(self, chart_id='chart_cluster_analysis', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)

        # Метрика для анализа
        self.metric_options = [
            ('revenuePerM2', 'Выручка/м²'),
            ('profitPerM2', 'Прибыль/м²')
        ]

        # Количество кластеров
        self.cluster_options = [2, 3, 4]

        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерация HTML для селекторов графика"""
        metric_html = ''.join([
            f'<option value="{val}"{" selected" if val == "revenuePerM2" else ""}>{label}</option>'
            for val, label in self.metric_options
        ])

        cluster_html = ''.join([
            f'<option value="{n}"{" selected" if n == 3 else ""}>{n} кластера</option>'
            for n in self.cluster_options
        ])

        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {metric_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Кластеры:</label>
                <select id="{self.chart_id}_clusters" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    {cluster_html}
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showPoints" checked onchange="update{self.chart_id}()"> Точки</label>
                <label style="font-size: 13px;"><input type="checkbox" id="{self.chart_id}_showLeaders" checked onchange="update{self.chart_id}()"> Лидеры</label>
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

            <div id="{self.chart_id}" style="width: 100%; height: 500px;"></div>
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
         * Генерация таблицы с сортировкой - все магазины
         */
        function generateTable_{self.chart_id}() {{
            const allStoresData = window.allStoresTableData_{self.chart_id} || [];
            if (!allStoresData || allStoresData.length === 0) {{
                document.getElementById('{self.chart_id}_table').innerHTML = '<p style="padding: 20px;">Нет данных</p>';
                return;
            }}

            const sortState = window.tableSortState_{self.chart_id};
            const sortedData = [...allStoresData];

            if (sortState.column) {{
                sortedData.sort((a, b) => {{
                    let valA = a[sortState.column];
                    let valB = b[sortState.column];
                    if (typeof valA === 'number' && typeof valB === 'number') {{
                        return sortState.direction === 'asc' ? valA - valB : valB - valA;
                    }}
                    valA = String(valA || '');
                    valB = String(valB || '');
                    return sortState.direction === 'asc' ? valA.localeCompare(valB, 'ru') : valB.localeCompare(valA, 'ru');
                }});
            }}

            const columns = ['Магазин', 'Площадь', 'Выручка/м²', 'Прибыль/м²', 'Кластер', 'Статус'];
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
                const isLeader = row['Статус'] === '★ Лидер';
                const rowStyle = isLeader ? 'background: #fff3cd; font-weight: 500;' : '';
                html += `<tr style="${{rowStyle}}">` + columns.map(c => {{
                    const val = row[c];
                    let cellContent = typeof val === 'number' ? val.toLocaleString('ru-RU') : (val || '-');
                    if (c === 'Статус' && isLeader) {{
                        cellContent = `<span style="color: #d4a106;">${{cellContent}}</span>`;
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

            return Object.values(storeMap).map(s => {{
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
            }}).filter(s => s.area > 0);
        }}

        /**
         * Разбиение на кластеры по квантилям площади
         */
        function assignClusters_{self.chart_id}(storeData, numClusters) {{
            const sorted = [...storeData].sort((a, b) => a.area - b.area);
            const n = sorted.length;

            const clusterNames = numClusters === 2
                ? ['Малые', 'Крупные']
                : numClusters === 3
                    ? ['Малые', 'Средние', 'Крупные']
                    : ['Малые', 'Средние', 'Крупные', 'Очень крупные'];

            const clusterSize = Math.ceil(n / numClusters);

            sorted.forEach((store, idx) => {{
                const clusterIdx = Math.min(Math.floor(idx / clusterSize), numClusters - 1);
                store.cluster = clusterNames[clusterIdx];
            }});

            return sorted;
        }}

        /**
         * Расчёт статистики по кластерам
         */
        function calculateClusterStats_{self.chart_id}(storeData, metric) {{
            const clusters = {{}};

            storeData.forEach(store => {{
                if (!clusters[store.cluster]) {{
                    clusters[store.cluster] = {{
                        stores: [],
                        areas: [],
                        metrics: []
                    }};
                }}
                clusters[store.cluster].stores.push(store);
                clusters[store.cluster].areas.push(store.area);
                clusters[store.cluster].metrics.push(store[metric]);
            }});

            const stats = [];
            for (const [clusterName, data] of Object.entries(clusters)) {{
                const areas = data.areas;
                const metrics = data.metrics;

                // Находим лидера по метрике
                let leaderIdx = 0;
                let maxMetric = metrics[0];
                metrics.forEach((m, idx) => {{
                    if (m > maxMetric) {{
                        maxMetric = m;
                        leaderIdx = idx;
                    }}
                }});

                stats.push({{
                    cluster: clusterName,
                    count: data.stores.length,
                    minArea: Math.min(...areas),
                    maxArea: Math.max(...areas),
                    avgArea: Math.round(areas.reduce((a, b) => a + b, 0) / areas.length),
                    avgRevenuePerM2: Math.round(data.stores.reduce((s, st) => s + st.revenuePerM2, 0) / data.stores.length),
                    avgProfitPerM2: Math.round(data.stores.reduce((s, st) => s + st.profitPerM2, 0) / data.stores.length),
                    leader: data.stores[leaderIdx],
                    stores: data.stores,
                    metrics: metrics
                }});
            }}

            // Сортируем по средней площади
            stats.sort((a, b) => a.avgArea - b.avgArea);

            return stats;
        }}

        const clusterColors_{self.chart_id} = {{
            'Малые': '#2ecc71',
            'Средние': '#9b59b6',
            'Крупные': '#e74c3c',
            'Очень крупные': '#3498db'
        }};

        const metricLabels_{self.chart_id} = {{
            'revenuePerM2': 'Выручка/м²',
            'profitPerM2': 'Прибыль/м²'
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
                chartDiv.innerHTML = '<p style="padding: 40px; text-align: center;">Недостаточно данных для кластеризации (нужно минимум 3 магазина)</p>';
                return;
            }}

            // Параметры
            const metric = document.getElementById('{self.chart_id}_metric')?.value || 'revenuePerM2';
            const numClusters = parseInt(document.getElementById('{self.chart_id}_clusters')?.value) || 3;
            const showPoints = document.getElementById('{self.chart_id}_showPoints')?.checked ?? true;
            const showLeaders = document.getElementById('{self.chart_id}_showLeaders')?.checked ?? true;

            const metricLabel = metricLabels_{self.chart_id}[metric];

            // Разбиваем на кластеры
            const clusteredData = assignClusters_{self.chart_id}(storeData, numClusters);
            const clusterStats = calculateClusterStats_{self.chart_id}(clusteredData, metric);

            // Сохраняем для таблицы - все магазины с отметкой лидеров
            const allStoresTable = [];
            clusterStats.forEach(cs => {{
                cs.stores.forEach(store => {{
                    const isLeader = store.store === cs.leader.store;
                    allStoresTable.push({{
                        'Магазин': store.store,
                        'Площадь': store.area,
                        'Выручка/м²': store.revenuePerM2,
                        'Прибыль/м²': store.profitPerM2,
                        'Кластер': cs.cluster,
                        'Статус': isLeader ? '★ Лидер' : ''
                    }});
                }});
            }});
            window.allStoresTableData_{self.chart_id} = allStoresTable;
            window.clusterStats_{self.chart_id} = clusterStats;

            const traces = [];
            const annotations = [];

            // Box-plot для каждого кластера
            clusterStats.forEach((cs, idx) => {{
                const color = clusterColors_{self.chart_id}[cs.cluster] || '#666';

                traces.push({{
                    type: 'box',
                    name: cs.cluster,
                    y: cs.metrics,
                    x: cs.stores.map(() => cs.cluster),
                    text: cs.stores.map(s => s.store),
                    boxpoints: showPoints ? 'all' : false,
                    jitter: 0.3,
                    pointpos: -1.5,
                    marker: {{
                        color: color,
                        size: 8,
                        opacity: 0.7
                    }},
                    line: {{ color: color }},
                    fillcolor: color.replace(')', ', 0.3)').replace('rgb', 'rgba'),
                    hovertemplate: '<b>%{{text}}</b><br>' + metricLabel + ': %{{y:,.0f}}<br>Кластер: %{{x}}<extra></extra>'
                }});

                // Аннотация лидера
                if (showLeaders) {{
                    annotations.push({{
                        x: cs.cluster,
                        y: cs.leader[metric],
                        text: `★ ${{cs.leader.area}} м²`,
                        showarrow: true,
                        arrowhead: 2,
                        arrowsize: 1,
                        arrowwidth: 2,
                        arrowcolor: color,
                        font: {{ size: 11, color: color }},
                        bgcolor: 'rgba(255,255,255,0.9)',
                        borderpad: 3
                    }});
                }}
            }});

            // Оптимальная площадь (среднее лидеров)
            const avgLeaderArea = Math.round(
                clusterStats.reduce((sum, cs) => sum + cs.leader.area, 0) / clusterStats.length
            );

            const layout = {{
                title: {{
                    text: `Метод 4: Кластеризация + Бенчмаркинг (${{metricLabel}})`,
                    font: {{ size: 16 }}
                }},
                xaxis: {{
                    title: 'Кластер',
                    type: 'category'
                }},
                yaxis: {{
                    title: metricLabel + ' (руб)',
                    gridcolor: '#e9ecef',
                    tickformat: ',.0f'
                }},
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white',
                margin: {{ l: 80, r: 50, t: 100, b: 60 }},
                showlegend: true,
                legend: {{
                    x: 1.02,
                    y: 1,
                    xanchor: 'left',
                    title: {{ text: 'Кластер' }}
                }},
                annotations: [
                    ...annotations,
                    {{
                        x: 0.5,
                        y: 1.06,
                        xref: 'paper',
                        yref: 'paper',
                        text: `Оптимум (средн. лидеров): <b>${{avgLeaderArea}} м²</b>`,
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
        }}

        /**
         * Получение данных таблицы для промпта
         */
        function getTableData_{self.chart_id}() {{
            return window.allStoresTableData_{self.chart_id} || [];
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
            const contextStr = window.analysisContext ? JSON.stringify(window.analysisContext, null, 2) : '';

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
