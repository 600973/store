# PROJECT_ROOT: charts/chart_store_cards.py
"""
Карточки обзора магазинов с ключевыми метриками
"""
from charts.base_chart import BaseChart


class ChartStoreCards(BaseChart):
    """
    Карточки магазинов с метриками и статусом эффективности
    """

    def __init__(self, chart_id: str = 'chart_store_cards', **kwargs):
        # Локальные фильтры для карточек
        local_filters = {
            'sort_by': {
                'type': 'select',
                'label': 'Сортировка',
                'options': [
                    {'value': 'revenue_desc', 'label': 'По выручке (↓)'},
                    {'value': 'revenue_asc', 'label': 'По выручке (↑)'},
                    {'value': 'revenue_per_m2_desc', 'label': 'По выручке/м² (↓)'},
                    {'value': 'revenue_per_m2_asc', 'label': 'По выручке/м² (↑)'},
                    {'value': 'checks_desc', 'label': 'По числу чеков (↓)'},
                    {'value': 'checks_asc', 'label': 'По числу чеков (↑)'},
                    {'value': 'name_asc', 'label': 'По названию (А-Я)'},
                ],
                'default': 'revenue_per_m2_desc'
            },
            'optimal_area_method': {
                'type': 'select',
                'label': 'Метод расчета оптимальной площади',
                'options': [
                    {'value': 'method1', 'label': 'Метод 1: Выручка/м²'},
                    {'value': 'method2', 'label': 'Метод 2: Нелинейная регрессия'},
                ],
                'default': 'method1'
            },
            'efficiency_revenue_per_m2': {
                'type': 'checkbox',
                'label': 'Выручка/м²',
                'default': True
            },
            'efficiency_checks': {
                'type': 'checkbox',
                'label': 'Число чеков',
                'default': True
            },
            'efficiency_profit': {
                'type': 'checkbox',
                'label': 'Прибыль',
                'default': False
            },
            'efficiency_revenue': {
                'type': 'checkbox',
                'label': 'Выручка',
                'default': False
            },
            'efficiency_profit_per_m2': {
                'type': 'checkbox',
                'label': 'Прибыль/м²',
                'default': False
            },
            'efficiency_margin': {
                'type': 'checkbox',
                'label': 'Маржинальность',
                'default': False
            }
        }

        super().__init__(
            chart_id=chart_id,
            local_filters=local_filters,
            llm_comment="""
            Карточки магазинов с ключевыми метриками эффективности.
            Каждая карточка показывает: название, площадь, выручку, выручку/м²,
            число чеков, средний чек, прибыль, тренды, сравнения с АППГ,
            статус эффективности, топ товары и рекомендуемую площадь.
            """,
            show_table=False,
            show_prompt=True,
            **kwargs
        )

    def generate_html(self) -> str:
        """Генерация HTML для карточек магазинов"""

        # HTML контейнер для карточек
        html = f'''
        <div class="store-cards-container">
            <!-- Панель управления -->
            <div class="chart-panel">
                <div class="panel-row">
                    <div class="panel-group">
                        <label class="panel-label">Сортировка:</label>
                        <select id="{self.chart_id}_sort_by" onchange="update{self.chart_id}()" class="panel-select">
                            <option value="revenue">Выручка</option>
                            <option value="revenue_per_m2" selected>Выручка/м²</option>
                            <option value="checks">Число чеков</option>
                            <option value="name">Название</option>
                        </select>
                    </div>

                    <div class="panel-group">
                        <label class="panel-label">Порядок:</label>
                        <select id="{self.chart_id}_sort_order" onchange="update{self.chart_id}()" class="panel-select">
                            <option value="desc" selected>По убыванию</option>
                            <option value="asc">По возрастанию</option>
                        </select>
                    </div>

                    <div class="panel-group">
                        <label class="panel-label">Оптимальная площадь:</label>
                        <select id="{self.chart_id}_optimal_area_method" onchange="update{self.chart_id}()" class="panel-select">
                            <option value="method1" selected>Метод 1: Выручка/м²</option>
                            <option value="method2">Метод 2: Нелинейная регрессия</option>
                        </select>
                    </div>

                    <button onclick="showStoreCardsMethodology_{self.chart_id}()" class="panel-info-btn" title="Описание метрик">❓</button>
                </div>

                <div class="panel-row">
                    <div class="panel-group">
                        <label class="panel-label">Критерии эффективности:</label>
                        <div class="panel-checkboxes">
                            <label class="panel-checkbox-label"><input type="checkbox" id="{self.chart_id}_efficiency_revenue_per_m2" checked onchange="update{self.chart_id}()"> Выручка/м²</label>
                            <label class="panel-checkbox-label"><input type="checkbox" id="{self.chart_id}_efficiency_checks" checked onchange="update{self.chart_id}()"> Число чеков</label>
                            <label class="panel-checkbox-label"><input type="checkbox" id="{self.chart_id}_efficiency_profit" onchange="update{self.chart_id}()"> Прибыль</label>
                            <label class="panel-checkbox-label"><input type="checkbox" id="{self.chart_id}_efficiency_revenue" onchange="update{self.chart_id}()"> Выручка</label>
                            <label class="panel-checkbox-label"><input type="checkbox" id="{self.chart_id}_efficiency_profit_per_m2" onchange="update{self.chart_id}()"> Прибыль/м²</label>
                            <label class="panel-checkbox-label"><input type="checkbox" id="{self.chart_id}_efficiency_margin" onchange="update{self.chart_id}()"> Маржинальность</label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Контейнер для карточек -->
            <div id="{self.chart_id}_cards" class="cards-grid">
                <!-- Карточки будут добавлены через JS -->
            </div>
        </div>

        <!-- Модальное окно с описанием методики -->
        <div id="store-cards-methodology-modal" class="modal">
            <div class="modal-content">
                <span class="modal-close" onclick="closeStoreCardsMethodology_{self.chart_id}()">&times;</span>
                <h2>📊 Описание метрик карточек магазинов</h2>
                <div class="modal-body">
                    <h3>Основные показатели</h3>
                    <ul>
                        <li><strong>Выручка</strong> — общая сумма продаж за выбранный период (₽)</li>
                        <li><strong>Выручка/м²</strong> — эффективность использования торговой площади (₽/м²)<br>
                            <em>Формула: Выручка / Торговая площадь</em></li>
                        <li><strong>Число чеков</strong> — количество транзакций (объем трафика)</li>
                        <li><strong>Средний чек</strong> — средняя сумма одной покупки (₽)<br>
                            <em>Формула: Выручка / Число чеков</em></li>
                        <li><strong>Прибыль</strong> — финансовый результат (₽)<br>
                            <em>Формула: Выручка - Себестоимость</em></li>
                        <li><strong>Прибыль/м²</strong> — эффективность площади по прибыли (₽/м²)<br>
                            <em>Формула: Прибыль / Торговая площадь</em></li>
                        <li><strong>Маржинальность</strong> — доля прибыли в выручке (%)<br>
                            <em>Формула: (Прибыль / Выручка) × 100%</em></li>
                    </ul>

                    <h3>Статус эффективности</h3>
                    <p>Магазин оценивается по выбранным критериям. За каждый критерий выше медианы начисляется 1 балл:</p>
                    <ul>
                        <li><strong>Эффективный</strong> (🟢) — набрано >= 2 баллов (большинство показателей выше медианы)</li>
                        <li><strong>Неэффективный</strong> (🔴) — набрано < 2 баллов</li>
                    </ul>
                    <p><em>Пример: если выбраны "Выручка/м²" и "Число чеков", и оба показателя выше медианы — магазин получает 2 балла = Эффективный</em></p>

                    <h3>Динамика (спарклайны)</h3>
                    <p>Мини-графики показывают тренд показателя за последние 12 месяцев</p>

                    <h3>Сравнения</h3>
                    <ul>
                        <li><strong>vs АППГ (выручка)</strong> — сравнение выручки с аналогичным периодом прошлого года (%)<br>
                            <em>Формула: (Выручка текущего года - Выручка прошлого года) / Выручка прошлого года × 100%</em></li>
                        <li><strong>vs медиана (выр/м²)</strong> — отклонение выручки/м² магазина от медианы по сети (%)<br>
                            <em>Формула: (Выручка/м² магазина - Медиана выручки/м²) / Медиана × 100%</em><br>
                            <em>Медиана — центральное значение среди всех магазинов (устойчива к выбросам)</em></li>
                    </ul>

                    <h3>Оптимальная площадь</h3>
                    <ul>
                        <li><strong>Метод 1: Выручка/м²</strong> — площадь, обеспечивающая максимальную выручку на м²</li>
                        <li><strong>Метод 2: Нелинейная регрессия</strong> — площадь из регрессионной модели зависимости выручки от площади</li>
                    </ul>
                </div>
            </div>
        </div>
        '''

        return html

    def generate_js(self) -> str:
        """Генерация JavaScript для карточек"""

        js = f'''
        // ============================================================================
        // КАРТОЧКИ МАГАЗИНОВ
        // ============================================================================

        let currentStoreForModal = null;

        // Вспомогательные функции форматирования
        function formatNumber_{self.chart_id}(num) {{
            if (!num && num !== 0) return '0';
            return Math.round(num).toLocaleString('ru-RU');
        }}

        function formatCurrency_{self.chart_id}(num) {{
            if (!num && num !== 0) return '0 ₽';
            return Math.round(num).toLocaleString('ru-RU') + ' ₽';
        }}

        function formatCurrencyShort_{self.chart_id}(num) {{
            if (!num && num !== 0) return '0 ₽';
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'М ₽';
            if (num >= 1000) return (num / 1000).toFixed(0) + 'К ₽';
            return Math.round(num).toLocaleString('ru-RU') + ' ₽';
        }}

        function formatPercent_{self.chart_id}(num) {{
            if (!num && num !== 0) return '0%';
            const sign = num > 0 ? '+' : '';
            return sign + num.toFixed(1) + '%';
        }}

        // Алиас для совместимости с базовым классом
        function updateChart_{self.chart_id.replace('chart_', '')}() {{
            update{self.chart_id}();
        }}

        function update{self.chart_id}() {{
            if (!window.filteredData || window.filteredData.length === 0) {{
                console.warn('Нет данных для отображения карточек');
                document.getElementById('{self.chart_id}_cards').innerHTML = '<p style="text-align: center; padding: 40px; color: #6c757d;">Нет данных для отображения</p>';
                return;
            }}

            const sortBy = document.getElementById('{self.chart_id}_sort_by')?.value || 'revenue_per_m2';
            const sortOrder = document.getElementById('{self.chart_id}_sort_order')?.value || 'desc';
            const optimalAreaMethod = document.getElementById('{self.chart_id}_optimal_area_method')?.value || 'method1';

            // Собираем выбранные критерии эффективности
            const efficiencyCriteria = [];
            if (document.getElementById('{self.chart_id}_efficiency_revenue_per_m2')?.checked) efficiencyCriteria.push('revenue_per_m2');
            if (document.getElementById('{self.chart_id}_efficiency_checks')?.checked) efficiencyCriteria.push('checks');
            if (document.getElementById('{self.chart_id}_efficiency_profit')?.checked) efficiencyCriteria.push('profit');
            if (document.getElementById('{self.chart_id}_efficiency_revenue')?.checked) efficiencyCriteria.push('revenue');
            if (document.getElementById('{self.chart_id}_efficiency_profit_per_m2')?.checked) efficiencyCriteria.push('profit_per_m2');
            if (document.getElementById('{self.chart_id}_efficiency_margin')?.checked) efficiencyCriteria.push('margin');

            // Если ни один критерий не выбран, используем по умолчанию
            if (efficiencyCriteria.length === 0) {{
                efficiencyCriteria.push('revenue_per_m2', 'checks');
            }}

            console.log('Обновление карточек магазинов:', {{
                данных: window.filteredData.length,
                критерии: efficiencyCriteria,
                сортировка: sortBy
            }});

            // Агрегируем данные по магазинам
            const storeData = aggregateStoreData_{self.chart_id}(window.filteredData, efficiencyCriteria, optimalAreaMethod);
            console.log('✅ Агрегировано магазинов:', storeData.length);

            // Сортируем
            const sortedStores = sortStores_{self.chart_id}(storeData, sortBy, sortOrder);
            console.log('✅ Отсортировано:', sortedStores.length, 'первый магазин:', sortedStores[0]?.name);

            // Рендерим карточки
            renderStoreCards_{self.chart_id}(sortedStores, '{self.chart_id}_cards');
            console.log('✅ Карточки отрендерены в контейнер:', '{self.chart_id}_cards');
        }}

        function aggregateStoreData_{self.chart_id}(data, efficiencyCriteria, optimalAreaMethod) {{
            if (!data || data.length === 0) return [];

            const stores = {{}};

            // Группируем по магазинам
            data.forEach(row => {{
                const storeName = row['Магазин'];
                if (!stores[storeName]) {{
                    stores[storeName] = {{
                        name: storeName,
                        area: row['Торговая площадь магазина'] || 0,
                        revenue: 0,
                        checks: 0,
                        profit: 0,
                        revenueByYear: {{}},
                        checksByYear: {{}},
                        profitByYear: {{}},
                        monthlyRevenue: {{}},
                        monthlyChecks: {{}},
                        products: {{}},
                        productTypes: {{}}
                    }};
                }}

                const store = stores[storeName];
                const year = row['Год'];
                const revenue = row['Сумма в чеке'] || 0;
                // Используем хелпер для корректного подсчёта чеков (группировка по магазину)
                const checks = getChecksValue(row, 'Магазин');
                const profit = row['Наценка продажи в чеке'] || 0;

                store.revenue += revenue;
                store.checks += checks;
                store.profit += profit;

                // Разделяем текущий и прошлый год для сравнения АППГ
                if (!store.revenueByYear[year]) store.revenueByYear[year] = 0;
                if (!store.checksByYear[year]) store.checksByYear[year] = 0;
                if (!store.profitByYear[year]) store.profitByYear[year] = 0;

                store.revenueByYear[year] += revenue;
                store.checksByYear[year] += checks;
                store.profitByYear[year] += profit;

                // Помесячная динамика
                const monthKey = `${{year}}-${{String(row['Месяц']).padStart(2, '0')}}`;
                if (!store.monthlyRevenue[monthKey]) store.monthlyRevenue[monthKey] = 0;
                if (!store.monthlyChecks[monthKey]) store.monthlyChecks[monthKey] = 0;
                store.monthlyRevenue[monthKey] += revenue;
                store.monthlyChecks[monthKey] += checks;

                // Топ товары
                const product = row['Товар'];
                const productType = row['Тип'];
                if (!store.products[product]) store.products[product] = 0;
                if (!store.productTypes[productType]) store.productTypes[productType] = 0;
                store.products[product] += row['Сумма в чеке'] || 0;
                store.productTypes[productType] += row['Сумма в чеке'] || 0;
            }});

            // Вычисляем дополнительные метрики
            const storeList = Object.values(stores).map(store => {{
                store.revenue_per_m2 = store.area > 0 ? store.revenue / store.area : 0;
                store.avg_check = store.checks > 0 ? store.revenue / store.checks : 0;
                store.profit_per_m2 = store.area > 0 ? store.profit / store.area : 0;
                store.margin = store.revenue > 0 ? (store.profit / store.revenue) * 100 : 0;

                // Топ товар и тип
                store.topProduct = Object.entries(store.products).sort((a, b) => b[1] - a[1])[0]?.[0] || '—';
                store.topProductType = Object.entries(store.productTypes).sort((a, b) => b[1] - a[1])[0]?.[0] || '—';

                // Спарклайны (последние 12 месяцев)
                const monthKeys = Object.keys(store.monthlyRevenue).sort().slice(-12);
                store.sparklineRevenue = monthKeys.map(k => store.monthlyRevenue[k]);
                store.sparklineChecks = monthKeys.map(k => store.monthlyChecks[k]);

                // Расчет АППГ будет выполнен после агрегации всех магазинов

                return store;
            }});

            // Расчет АППГ: оба года из уже отфильтрованных данных
            const yearsInFiltered = new Set();
            data.forEach(row => {{
                const year = row['Год'];
                if (year) yearsInFiltered.add(parseInt(year));
            }});
            const currentYear = Math.max(...yearsInFiltered);
            const previousYear = currentYear - 1;

            console.log('АППГ расчет:', {{
                currentYear,
                previousYear,
                магазинов: storeList.length
            }});

            // Вычисляем медианы для критериев эффективности
            const medians = calculateMedians_{self.chart_id}(storeList);

            // Добавляем сравнения
            storeList.forEach(store => {{
                // vs АППГ: используем данные из store.revenueByYear (уже отфильтрованные)
                const currentRev = store.revenueByYear[currentYear] || 0;
                const prevRev = store.revenueByYear[previousYear] || 0;

                // Формула: (текущий / прошлый - 1) * 100%
                store.vsAAPG = prevRev > 0 ? ((currentRev / prevRev - 1) * 100) : 0;

                console.log(`${{store.name}}: 2025=${{currentRev}}, 2024=${{prevRev}}, %=${{store.vsAAPG.toFixed(1)}}`);

                // vs медиана
                store.vsMedian = medians.revenue_per_m2 > 0
                    ? ((store.revenue_per_m2 - medians.revenue_per_m2) / medians.revenue_per_m2) * 100
                    : 0;
            }});

            // Определяем статус эффективности
            storeList.forEach(store => {{
                let score = 0;
                efficiencyCriteria.forEach(criterion => {{
                    if (store[criterion] >= medians[criterion]) score++;
                }});

                const threshold = Math.min(2, efficiencyCriteria.length);
                store.isEfficient = score >= threshold;
                store.efficiencyScore = score;
                store.efficiencyTotal = efficiencyCriteria.length;
            }});

            // Добавляем оптимальную площадь (пока заглушка)
            storeList.forEach(store => {{
                if (optimalAreaMethod === 'method1') {{
                    store.optimalArea = store.area * 1.1; // Заглушка
                }} else {{
                    store.optimalArea = store.area * 0.9; // Заглушка
                }}
            }});

            return storeList;
        }}

        function calculateMedians_{self.chart_id}(stores) {{
            const medians = {{}};
            const metrics = ['revenue', 'revenue_per_m2', 'checks', 'profit', 'profit_per_m2', 'margin'];

            metrics.forEach(metric => {{
                const values = stores.map(s => s[metric]).filter(v => v > 0).sort((a, b) => a - b);
                const mid = Math.floor(values.length / 2);
                medians[metric] = values.length % 2 === 0
                    ? (values[mid - 1] + values[mid]) / 2
                    : values[mid];
            }});

            return medians;
        }}

        function naturalSort_{self.chart_id}(a, b) {{
            // Натуральная сортировка: Магазин 1, Магазин 2, ..., Магазин 10
            const regex = /(\\d+)|(\\D+)/g;
            const aParts = a.match(regex);
            const bParts = b.match(regex);

            for (let i = 0; i < Math.min(aParts.length, bParts.length); i++) {{
                const aPart = aParts[i];
                const bPart = bParts[i];

                const aNum = parseInt(aPart);
                const bNum = parseInt(bPart);

                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    if (aNum !== bNum) return aNum - bNum;
                }} else {{
                    const cmp = aPart.localeCompare(bPart);
                    if (cmp !== 0) return cmp;
                }}
            }}

            return aParts.length - bParts.length;
        }}

        function sortStores_{self.chart_id}(stores, sortBy, sortOrder) {{
            const sorted = [...stores];
            const isAsc = sortOrder === 'asc';

            switch(sortBy) {{
                case 'revenue':
                    return sorted.sort((a, b) => isAsc ? a.revenue - b.revenue : b.revenue - a.revenue);
                case 'revenue_per_m2':
                    return sorted.sort((a, b) => isAsc ? a.revenue_per_m2 - b.revenue_per_m2 : b.revenue_per_m2 - a.revenue_per_m2);
                case 'checks':
                    return sorted.sort((a, b) => isAsc ? a.checks - b.checks : b.checks - a.checks);
                case 'name':
                    const result = sorted.sort((a, b) => naturalSort_{self.chart_id}(a.name, b.name));
                    return isAsc ? result : result.reverse();
                default:
                    return sorted;
            }}
        }}

        function renderStoreCards_{self.chart_id}(stores, containerId) {{
            const container = document.getElementById(containerId);
            if (!container) return;

            container.innerHTML = stores.map(store => createStoreCard_{self.chart_id}(store)).join('');
        }}

        function createStoreCard_{self.chart_id}(store) {{
            const statusIcon = store.isEfficient ? '✓' : '✗';
            const statusClass = store.isEfficient ? 'status-good' : 'status-bad';

            // Определяем цвет и стрелку для оптимальной площади
            let optimalArrow = '';
            let optimalClass = '';
            if (store.optimalArea < store.area) {{
                optimalArrow = '↓';
                optimalClass = 'optimal-down';
            }} else if (store.optimalArea > store.area) {{
                optimalArrow = '↑';
                optimalClass = 'optimal-up';
            }}

            return `
                <div class="store-card">
                    <div class="store-name">
                        <span class="store-status ${{statusClass}}">${{statusIcon}}</span>
                        ${{store.name}}
                    </div>
                    <div class="store-metrics">
                        <div class="store-metric">
                            <div class="metric-value-main">${{formatNumber_{self.chart_id}(store.area)}}</div>
                            <div class="metric-label-main">Площадь, м²</div>
                            <div class="metric-optimal ${{optimalClass}}">${{optimalArrow}} ${{formatNumber_{self.chart_id}(store.optimalArea)}}</div>
                        </div>
                        <div class="store-metric">
                            <div class="metric-value-main">${{formatCurrencyShort_{self.chart_id}(store.revenue)}}</div>
                            <div class="metric-label-main">Выручка</div>
                            ${{createSparklineSVG_{self.chart_id}(store.sparklineRevenue)}}
                        </div>
                        <div class="store-metric">
                            <div class="metric-value-main">${{formatCurrency_{self.chart_id}(store.revenue_per_m2)}}</div>
                            <div class="metric-label-main">Выручка/м²</div>
                        </div>
                        <div class="store-metric">
                            <div class="metric-value-main">${{formatNumber_{self.chart_id}(store.checks)}}</div>
                            <div class="metric-label-main">Число чеков</div>
                            ${{createSparklineSVG_{self.chart_id}(store.sparklineChecks)}}
                        </div>
                        <div class="store-metric">
                            <div class="metric-value-main">${{formatCurrency_{self.chart_id}(store.avg_check)}}</div>
                            <div class="metric-label-main">Средний чек</div>
                        </div>
                        <div class="store-metric">
                            <div class="metric-value-main">${{formatCurrencyShort_{self.chart_id}(store.profit)}}</div>
                            <div class="metric-label-main">Прибыль</div>
                        </div>
                        <div class="store-metric">
                            <div class="metric-value-main ${{store.vsAAPG >= 0 ? 'metric-positive' : 'metric-negative'}}">${{formatPercent_{self.chart_id}(store.vsAAPG)}}</div>
                            <div class="metric-label-main">vs АППГ (выручка)</div>
                        </div>
                        <div class="store-metric">
                            <div class="metric-value-main ${{store.vsMedian >= 0 ? 'metric-positive' : 'metric-negative'}}">${{formatPercent_{self.chart_id}(store.vsMedian)}}</div>
                            <div class="metric-label-main">vs медиана (выр/м²)</div>
                        </div>
                    </div>
                </div>
            `;
        }}

        function createSparklineSVG_{self.chart_id}(data) {{
            if (!data || data.length === 0) return '';

            const width = 120;
            const height = 15;
            const max = Math.max(...data);
            const min = Math.min(...data);
            const range = max - min || 1;

            const points = data.map((val, i) => {{
                const x = (i / (data.length - 1)) * width;
                const y = height - ((val - min) / range) * height;
                return `${{x}},${{y}}`;
            }}).join(' ');

            return `<svg width="${{width}}" height="${{height}}" class="sparkline" viewBox="0 0 ${{width}} ${{height}}" preserveAspectRatio="none">
                <polyline points="${{points}}" fill="none" stroke="#667eea" stroke-width="1.5"/>
            </svg>`;
        }}

        function showStoreCardsMethodology_{self.chart_id}() {{
            document.getElementById('store-cards-methodology-modal').classList.add('active');
        }}

        function closeStoreCardsMethodology_{self.chart_id}() {{
            document.getElementById('store-cards-methodology-modal').classList.remove('active');
        }}
        '''

        return js

    def get_html_container(self) -> str:
        """Переопределяем контейнер для кастомного HTML"""
        css = self._merge_css_styles()
        style_str = '; '.join([f'{k}: {v}' for k, v in css.items()])

        view_switcher_html = self._generate_view_switcher_html()
        llm_comment_html = self._generate_llm_comment_html()

        # Вставляем наш кастомный HTML внутрь контейнера
        custom_html = self.generate_html()

        return f'''
        <div class="chart-wrapper" style="{style_str}">
            {view_switcher_html}

            <!-- ОТВЕТ LLM -->
            <div id="{self.chart_id}_llm_result" class="llm-result" style="display: none;">
                <div class="llm-result-controls">
                    <button class="llm-result-toggle" onclick="this.closest('.llm-result').querySelector('.llm-result-text').classList.toggle('collapsed'); this.textContent = this.textContent === '−' ? '+' : '−'">−</button>
                    <button class="llm-result-close" onclick="document.getElementById('{self.chart_id}_llm_result').style.display='none'">✕</button>
                </div>
                <div class="llm-result-text {self.ai_view_mode}" style="--max-lines: {self.ai_max_lines};"></div>
            </div>
            <div id="{self.chart_id}_llm_loading" class="llm-loading" style="display: none;">⳩ Генерация ответа...</div>

            <!-- Кастомный HTML карточек -->
            <div id="{self.chart_id}" style="width: 100%; min-height: 400px;">
                {custom_html}
            </div>

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
                <textarea id="{self.chart_id}_prompt_text" placeholder="Введите вопрос по графику..."></textarea>
                <div class="prompt-buttons">
                    <button onclick="analyzeChart('{self.chart_id}')">Отправить</button>
                </div>
            </div>
        </div>
        '''

    def get_js_code(self) -> str:
        """Возвращает JavaScript код (переопределение базового метода)"""
        return self.generate_js()

    def get_html_code(self) -> str:
        """Возвращает HTML код (переопределение базового метода)"""
        return self.generate_html()

    def get_css_styles(self) -> str:
        """Возвращает CSS код (переопределение базового метода)"""
        return self.generate_css()

    def generate_css(self) -> str:
        """Генерация CSS для карточек"""

        css = '''
        /* === КАРТОЧКИ МАГАЗИНОВ === */
        .store-cards-container {
            padding: 10px 0;
        }

        .panel-row {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }

        .panel-row:last-child {
            margin-bottom: 0;
        }

        .panel-group {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .panel-label {
            font-weight: 600;
            font-size: 12px;
            color: #495057;
        }

        .panel-select {
            padding: 4px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 12px;
            background: white;
        }

        .panel-checkboxes {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .panel-checkbox-label {
            font-weight: normal;
            font-size: 11px;
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            color: #495057;
        }

        .panel-info-btn {
            background: #f8f9fa;
            color: #495057;
            border: 1px solid #ced4da;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .panel-info-btn:hover {
            background: #e9ecef;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }

        .store-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            color: #1f2937;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }

        .store-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .store-name {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .store-status {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            font-size: 12px;
            font-weight: bold;
        }

        .store-status.status-good {
            background: rgba(76, 175, 80, 0.9);
            color: white;
        }

        .store-status.status-bad {
            background: rgba(244, 67, 54, 0.9);
            color: white;
        }

        .store-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }

        .store-metric {
            text-align: center;
        }

        .metric-value-main {
            font-size: 18px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 4px;
        }

        .metric-value-main.metric-positive {
            color: #22c55e;
        }

        .metric-value-main.metric-negative {
            color: #ef4444;
        }

        .metric-label-main {
            font-size: 10px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-optimal {
            font-size: 13px;
            font-weight: 600;
            margin-top: 4px;
        }

        .metric-optimal.optimal-down {
            color: #ef4444;
        }

        .metric-optimal.optimal-up {
            color: #22c55e;
        }

        .sparkline {
            margin-top: 4px;
        }

        @media (max-width: 1200px) {
            .cards-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 768px) {
            .cards-grid {
                grid-template-columns: 1fr;
            }
        }
        '''

        return css
