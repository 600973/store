# PROJECT_ROOT: engine/filters.py
"""
Глобальные фильтры дашборда
"""
import pandas as pd
from .data_processor import get_unique_values


class GlobalFilters:
    """
    Глобальные фильтры для дашборда
    """

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame с данными для построения списков фильтров
        """
        self.df = df
        self.magazines = get_unique_values(df, 'Магазин')
        self.years = sorted(get_unique_values(df, 'Год')) if 'Год' in df.columns else []
        self.months = get_unique_values(df, 'Месяц') if 'Месяц' in df.columns else []
        self.product_types = get_unique_values(df, 'Тип') if 'Тип' in df.columns else []
        self.products = get_unique_values(df, 'Товар') if 'Товар' in df.columns else []

        # Площадь магазинов (min/max для фильтра)
        if 'Торговая площадь магазина' in df.columns:
            self.area_min = int(df['Торговая площадь магазина'].min())
            self.area_max = int(df['Торговая площадь магазина'].max())
        else:
            self.area_min = 0
            self.area_max = 0

        # Автоопределение доступных уровней детализации
        self.available_detail_levels = self._detect_detail_levels()

    def _detect_detail_levels(self) -> list:
        """
        Определить доступные уровни детализации на основе данных
        Returns: список уровней ['year', 'month'] или ['year', 'month', 'week', 'day']
        """
        if 'Дата' not in self.df.columns:
            return ['year', 'month']

        # Проверить, все ли даты имеют день = 01
        dates = pd.to_datetime(self.df['Дата'], format='%d.%m.%Y', errors='coerce')
        days = dates.dt.day.dropna()

        if len(days) == 0:
            return ['year', 'month']

        # Если все даты - первое число месяца
        if (days == 1).all():
            return ['year', 'month']

        # Иначе есть разные дни - добавить неделю и день
        return ['year', 'month', 'week', 'day']

    def _get_detail_buttons(self) -> str:
        """Генерация HTML кнопок детализации"""
        labels = {'year': 'Год', 'month': 'Месяц', 'week': 'Неделя', 'day': 'День'}
        buttons = []
        for level in self.available_detail_levels:
            active_class = ' active' if level == 'month' else ''
            buttons.append(
                f'''<button type="button"
                        class="global-detail-btn{active_class}"
                        data-level="{level}"
                        onclick="setGlobalDetailLevel('{level}')">
                    {labels[level]}
                </button>'''
            )
        return ''.join(buttons)

    def get_html(self) -> str:
        """
        Генерирует HTML для панели фильтров (выдвижная панель справа)

        Returns:
            HTML строка
        """
        magazine_counts = self.df['Магазин'].value_counts().to_dict()
        year_counts = self.df['Год'].value_counts().to_dict() if 'Год' in self.df.columns else {}
        month_counts = self.df['Месяц'].value_counts().to_dict() if 'Месяц' in self.df.columns else {}
        product_type_counts = self.df['Тип'].value_counts().to_dict() if 'Тип' in self.df.columns else {}
        product_counts = self.df['Товар'].value_counts().to_dict() if 'Товар' in self.df.columns else {}

        magazines_options = ''.join([
            f'<option value="{m}">{m}      ({magazine_counts.get(m, 0)})</option>'
            for m in self.magazines
        ])

        years_options = ''.join([
            f'<option value="{y}">{y}      ({year_counts.get(y, 0)})</option>'
            for y in self.years
        ])

        months_options = ''.join([
            f'<option value="{m}">{m}      ({month_counts.get(m, 0)})</option>'
            for m in self.months
        ])

        product_types_options = ''.join([
            f'<option value="{pt}">{pt}      ({product_type_counts.get(pt, 0)})</option>'
            for pt in self.product_types
        ])

        products_options = ''.join([
            f'<option value="{p}">{p}      ({product_counts.get(p, 0)})</option>'
            for p in self.products
        ])

        return f'''
        <!-- Кнопка открытия панели фильтров -->
        <button class="global-filters-toggle" onclick="toggleGlobalFilters()">
            Фильтры
        </button>

        <!-- Выдвижная панель справа -->
        <div id="global-filters-panel" class="global-filters-panel">
            <div class="global-filters-header">
                <!-- Закрыть панель -->
                <button type="button"
                        class="global-filters-close"
                        onclick="toggleGlobalFilters()">
                    ✕
                </button>
            </div>

            <div class="filters-panel">

                <!-- Глобальная детализация -->
                <div class="filter-group">
                    <div class="filter-group-header">
                        <label>Глобальная детализация</label>
                    </div>
                    <div class="global-detail-group">
                        {self._get_detail_buttons()}
                    </div>
                </div>

                <!-- Фильтр по датам (один блок, своя кнопка сброса) -->
                <div class="filter-group" data-filter-key="date">
                    <div class="filter-group-header">
                        <label>Период</label>
                        <button type="button"
                                class="filter-reset-btn"
                                data-filter-reset="date">
                            ⟳
                        </button>
                    </div>

                    <div class="date-filters">
                        <div class="filter-group-inner">
                            <label for="startDate">Дата начала</label>
                            <input type="date" id="startDate">
                        </div>
                        <div class="filter-group-inner">
                            <label for="endDate">Дата окончания</label>
                            <input type="date" id="endDate">
                        </div>
                    </div>
                </div>

                <!-- Фильтр по площади магазина -->
                <div class="filter-group" data-filter-key="area">
                    <div class="filter-group-header">
                        <label>Площадь магазина (м²)</label>
                        <button type="button"
                                class="filter-reset-btn"
                                data-filter-reset="area">
                            ⟳
                        </button>
                    </div>
                    <div class="area-filters" style="display: flex; gap: 10px;">
                        <div class="filter-group-inner" style="flex: 1;">
                            <label for="minArea">Мин.</label>
                            <input type="number"
                                   id="minArea"
                                   value="{self.area_min}"
                                   min="{self.area_min}"
                                   max="{self.area_max}"
                                   style="width: 100%; padding: 6px; border: 1px solid #d1d5db; border-radius: 4px;">
                        </div>
                        <div class="filter-group-inner" style="flex: 1;">
                            <label for="maxArea">Макс.</label>
                            <input type="number"
                                   id="maxArea"
                                   value="{self.area_max}"
                                   min="{self.area_min}"
                                   max="{self.area_max}"
                                   style="width: 100%; padding: 6px; border: 1px solid #d1d5db; border-radius: 4px;">
                        </div>
                    </div>
                </div>

                <!-- Фильтры по годам и месяцам -->
                <div class="filters-grid">
                    <div class="filter-group" data-filter-key="year">
                        <div class="filter-group-header">
                            <label for="filterYear">Год ({len(self.years)})</label>
                            <div style="display: flex; gap: 4px;">
                                <button type="button"
                                        class="toggle-search-btn"
                                        onclick="toggleFilterSearch('filterYear')">
                                    🔍
                                </button>
                                <button type="button"
                                        class="toggle-selected-btn"
                                        onclick="toggleSelectedValues('filterYear')">
                                    👁
                                </button>
                                <button type="button"
                                        class="filter-reset-btn"
                                        data-filter-reset="year">
                                    ⟳
                                </button>
                            </div>
                        </div>
                        <div id="filterYear_search" class="filter-search-container">
                            <input type="text"
                                   class="filter-search-input"
                                   placeholder="Поиск..."
                                   oninput="filterSelectOptions('filterYear', this.value)">
                            <button type="button"
                                    class="filter-search-clear"
                                    onclick="clearFilterSearch('filterYear')">×</button>
                        </div>
                        <select id="filterYear" multiple size="5">
                            <option value="">Все</option>
                            {years_options}
                        </select>
                        <div id="filterYear_selected" class="selected-values-container"></div>
                    </div>

                    <div class="filter-group" data-filter-key="month">
                        <div class="filter-group-header">
                            <label for="filterMonth">Месяц ({len(self.months)})</label>
                            <div style="display: flex; gap: 4px;">
                                <button type="button"
                                        class="toggle-search-btn"
                                        onclick="toggleFilterSearch('filterMonth')">
                                    🔍
                                </button>
                                <button type="button"
                                        class="toggle-selected-btn"
                                        onclick="toggleSelectedValues('filterMonth')">
                                    👁
                                </button>
                                <button type="button"
                                        class="filter-reset-btn"
                                        data-filter-reset="month">
                                    ⟳
                                </button>
                            </div>
                        </div>
                        <div id="filterMonth_search" class="filter-search-container">
                            <input type="text"
                                   class="filter-search-input"
                                   placeholder="Поиск..."
                                   oninput="filterSelectOptions('filterMonth', this.value)">
                            <button type="button"
                                    class="filter-search-clear"
                                    onclick="clearFilterSearch('filterMonth')">×</button>
                        </div>
                        <select id="filterMonth" multiple size="5">
                            <option value="">Все</option>
                            {months_options}
                        </select>
                        <div id="filterMonth_selected" class="selected-values-container"></div>
                    </div>
                </div>

                <!-- Фильтры по магазинам и типам товаров -->
                <div class="filters-grid">
                    <div class="filter-group" data-filter-key="magazine">
                        <div class="filter-group-header">
                            <label for="filterMagazine">Магазин ({len(self.magazines)})</label>
                            <div style="display: flex; gap: 4px;">
                                <button type="button"
                                        class="toggle-search-btn"
                                        onclick="toggleFilterSearch('filterMagazine')">
                                    🔍
                                </button>
                                <button type="button"
                                        class="toggle-selected-btn"
                                        onclick="toggleSelectedValues('filterMagazine')">
                                    👁
                                </button>
                                <button type="button"
                                        class="filter-reset-btn"
                                        data-filter-reset="magazine">
                                    ⟳
                                </button>
                            </div>
                        </div>
                        <div id="filterMagazine_search" class="filter-search-container">
                            <input type="text"
                                   class="filter-search-input"
                                   placeholder="Поиск..."
                                   oninput="filterSelectOptions('filterMagazine', this.value)">
                            <button type="button"
                                    class="filter-search-clear"
                                    onclick="clearFilterSearch('filterMagazine')">×</button>
                        </div>
                        <select id="filterMagazine" multiple size="5">
                            <option value="">Все</option>
                            {magazines_options}
                        </select>
                        <div id="filterMagazine_selected" class="selected-values-container"></div>
                    </div>

                    <div class="filter-group" data-filter-key="product_type">
                        <div class="filter-group-header">
                            <label for="filterProductType">Тип товара ({len(self.product_types)})</label>
                            <div style="display: flex; gap: 4px;">
                                <button type="button"
                                        class="toggle-search-btn"
                                        onclick="toggleFilterSearch('filterProductType')">
                                    🔍
                                </button>
                                <button type="button"
                                        class="toggle-selected-btn"
                                        onclick="toggleSelectedValues('filterProductType')">
                                    👁
                                </button>
                                <button type="button"
                                        class="filter-reset-btn"
                                        data-filter-reset="product_type">
                                    ⟳
                                </button>
                            </div>
                        </div>
                        <div id="filterProductType_search" class="filter-search-container">
                            <input type="text"
                                   class="filter-search-input"
                                   placeholder="Поиск..."
                                   oninput="filterSelectOptions('filterProductType', this.value)">
                            <button type="button"
                                    class="filter-search-clear"
                                    onclick="clearFilterSearch('filterProductType')">×</button>
                        </div>
                        <select id="filterProductType" multiple size="5">
                            <option value="">Все</option>
                            {product_types_options}
                        </select>
                        <div id="filterProductType_selected" class="selected-values-container"></div>
                    </div>
                </div>

                <!-- Фильтр по товарам -->
                <div class="filters-grid">
                    <div class="filter-group" data-filter-key="product">
                        <div class="filter-group-header">
                            <label for="filterProduct">Товар ({len(self.products)})</label>
                            <div style="display: flex; gap: 4px;">
                                <button type="button"
                                        class="toggle-search-btn"
                                        onclick="toggleFilterSearch('filterProduct')">
                                    🔍
                                </button>
                                <button type="button"
                                        class="toggle-selected-btn"
                                        onclick="toggleSelectedValues('filterProduct')">
                                    👁
                                </button>
                                <button type="button"
                                        class="filter-reset-btn"
                                        data-filter-reset="product">
                                    ⟳
                                </button>
                            </div>
                        </div>
                        <div id="filterProduct_search" class="filter-search-container">
                            <input type="text"
                                   class="filter-search-input"
                                   placeholder="Поиск..."
                                   oninput="filterSelectOptions('filterProduct', this.value)">
                            <button type="button"
                                    class="filter-search-clear"
                                    onclick="clearFilterSearch('filterProduct')">×</button>
                        </div>
                        <select id="filterProduct" multiple size="5">
                            <option value="">Все</option>
                            {products_options}
                        </select>
                        <div id="filterProduct_selected" class="selected-values-container"></div>
                    </div>
                </div>
            </div>

            <!-- Кнопки внизу панели -->
            <div class="filters-footer">
                <button type="button"
                        class="btn-apply"
                        onclick="applyFilters()">
                    <span id="apply-button-text">Применить</span>
                </button>
                <button type="button"
                        class="btn-reset"
                        onclick="resetFilters()">
                    Сбросить все
                </button>
            </div>
        </div>
        '''

    def get_js_code(self) -> str:
        """
        Генерирует JS код для работы фильтров

        Returns:
            JS код
        """
        return '''
        // ============================================================================
        // ГЛОБАЛЬНЫЕ ФИЛЬТРЫ
        // ============================================================================

        let filteredData = [];

        /**
         * Переключение видимости панели глобальных фильтров
         */
        function toggleGlobalFilters() {
            const panel = document.getElementById('global-filters-panel');
            const btn = document.querySelector('.global-filters-toggle');
            if (!panel) return;

            panel.classList.toggle('open');
            const isOpen = panel.classList.contains('open');

            if (btn) {
                btn.classList.toggle('hidden', isOpen);
            }

            document.body.classList.toggle('filters-open', isOpen);

            setTimeout(() => {
                try {
                    window.dispatchEvent(new Event('resize'));

                    if (window.Plotly) {
                        const activeTab = document.querySelector('.tab-content.active');
                        if (activeTab) {
                            activeTab.querySelectorAll('.plotly-graph-div')
                                .forEach(div => {
                                    try {
                                        Plotly.Plots.resize(div);
                                    } catch (e) {
                                        console.warn('Resize error for chart', e);
                                    }
                                });
                        }
                    }
                } catch (e) {
                    console.warn('Charts resize error', e);
                }
            }, 300);
        }

        /**
         * Получить выбранные значения из multi-select
         */
        function getSelectedValues(selectId) {
            const select = document.getElementById(selectId);
            if (!select) return [];
            return Array.from(select.selectedOptions)
                .map(opt => opt.value)
                .filter(v => v !== "");
        }

        /**
         * Сброс ЗНАЧЕНИЙ одного фильтра по ключу
         */
        function resetSingleFilter(key) {
            let selectId = null;

            switch (key) {
                case 'magazine': {
                    selectId = 'filterMagazine';
                    const el = document.getElementById(selectId);
                    if (el) {
                        [...el.options].forEach(o => o.selected = false);
                    }
                    break;
                }
                case 'year': {
                    selectId = 'filterYear';
                    const el = document.getElementById(selectId);
                    if (el) {
                        [...el.options].forEach(o => o.selected = false);
                    }
                    break;
                }
                case 'month': {
                    selectId = 'filterMonth';
                    const el = document.getElementById(selectId);
                    if (el) {
                        [...el.options].forEach(o => o.selected = false);
                    }
                    break;
                }
                case 'date': {
                    const from = document.getElementById('startDate');
                    const to   = document.getElementById('endDate');
                    if (from) from.value = '';
                    if (to)   to.value = '';
                    break;
                }
                case 'product_type': {
                    selectId = 'filterProductType';
                    const el = document.getElementById(selectId);
                    if (el) {
                        [...el.options].forEach(o => o.selected = false);
                    }
                    break;
                }
                case 'product': {
                    selectId = 'filterProduct';
                    const el = document.getElementById(selectId);
                    if (el) {
                        [...el.options].forEach(o => o.selected = false);
                    }
                    break;
                }
                case 'area': {
                    const minArea = document.getElementById('minArea');
                    const maxArea = document.getElementById('maxArea');
                    if (minArea) minArea.value = minArea.min;
                    if (maxArea) maxArea.value = maxArea.max;
                    break;
                }
            }

            if (selectId) {
                updateSelectedValuesContainer(selectId);
            }
        }

        /**
         * Парсинг даты из формата DD.MM.YYYY
         */
        function parseDate(dateStr) {
            if (!dateStr) return null;
            const parts = dateStr.split('.');
            if (parts.length === 3) {
                return new Date(parts[2], parts[1] - 1, parts[0]);
            }
            return null;
        }

        /**
         * Применить глобальные фильтры
         */
        function applyFilters() {
            const selectedMagazines = getSelectedValues('filterMagazine');
            const selectedYears = getSelectedValues('filterYear').map(y => parseInt(y));
            const selectedMonths = getSelectedValues('filterMonth');
            const selectedProductTypes = getSelectedValues('filterProductType');
            const selectedProducts = getSelectedValues('filterProduct');

            const startDateStr = document.getElementById('startDate')?.value || '';
            const endDateStr = document.getElementById('endDate')?.value || '';

            const startDate = startDateStr ? new Date(startDateStr + 'T00:00:00') : null;
            const endDate = endDateStr ? new Date(endDateStr + 'T23:59:59') : null;

            // Фильтр по площади
            const minAreaEl = document.getElementById('minArea');
            const maxAreaEl = document.getElementById('maxArea');
            const minArea = minAreaEl ? parseFloat(minAreaEl.value) : 0;
            const maxArea = maxAreaEl ? parseFloat(maxAreaEl.value) : Infinity;
            const areaFilterActive = minAreaEl && maxAreaEl &&
                (minAreaEl.value !== minAreaEl.min || maxAreaEl.value !== maxAreaEl.max);

            // Фильтрация данных
            window.filteredData = window.rawData.filter(row => {
                // Фильтр по площади магазина
                if (areaFilterActive) {
                    const area = parseFloat(row['Торговая площадь магазина']);
                    if (isNaN(area) || area < minArea || area > maxArea) {
                        return false;
                    }
                }

                // Фильтр по магазину
                if (selectedMagazines.length > 0) {
                    const magazineStr = String(row['Магазин']);
                    if (!selectedMagazines.includes(magazineStr)) {
                        return false;
                    }
                }

                // Фильтр по году
                if (selectedYears.length > 0) {
                    const year = parseInt(row['Год']);
                    if (!selectedYears.includes(year)) {
                        return false;
                    }
                }

                // Фильтр по месяцу
                if (selectedMonths.length > 0) {
                    if (!selectedMonths.includes(row['Месяц'])) {
                        return false;
                    }
                }

                // Фильтр по типу товара
                if (selectedProductTypes.length > 0) {
                    if (!selectedProductTypes.includes(row['Тип'])) {
                        return false;
                    }
                }

                // Фильтр по товару
                if (selectedProducts.length > 0) {
                    if (!selectedProducts.includes(row['Товар'])) {
                        return false;
                    }
                }

                // Фильтр по датам (используем столбец Дата)
                if (startDate || endDate) {
                    const rowDate = parseDate(row['Дата']);
                    if (!rowDate) return false;

                    if (startDate && rowDate < startDate) {
                        return false;
                    }
                    if (endDate && rowDate > endDate) {
                        return false;
                    }
                }

                return true;
            });

            console.log('🔍 Отфильтровано записей:', window.filteredData.length);

            updateApplyButtonText();
            updateAllCharts();

            // Обновить KPI метрики
            if (typeof updateMetricsUI === 'function') {
                updateMetricsUI();
            }

            // Обновить все открытые таблицы
            if (typeof updateAllVisibleTables === 'function') {
                updateAllVisibleTables();
            }
        }

        /**
         * Обновить текст кнопки применить с количеством записей
         */
        function updateApplyButtonText() {
            const btnText = document.getElementById('apply-button-text');
            if (!btnText) return;

            const count = window.filteredData ? window.filteredData.length : 0;
            btnText.textContent = `Применить (${count})`;
        }

        /**
         * Сбросить все фильтры
         */
        function resetFilters() {
            document.querySelectorAll('.filter-reset-btn')
                .forEach(btn => {
                    const key = btn.dataset.filterReset;
                    if (key) {
                        resetSingleFilter(key);
                    }
                });

            // Обновляем состояние кнопок сброса
            updateResetButtons();

            applyFilters();
        }

        /**
         * Делегирование кликов по кнопкам сброса
         */
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.filter-reset-btn');
            if (!btn) return;

            const key = btn.dataset.filterReset;
            if (!key) return;

            resetSingleFilter(key);
            updateResetButtons();
            applyFilters();
        });

        /**
         * Сортировка выбранных опций наверх и обновление счетчика
         */
        document.addEventListener('change', function (e) {
            const select = e.target;
            if (!select.matches('select[multiple]')) return;

            const selected = [];
            const unselected = [];

            Array.from(select.options).forEach(opt => {
                if (opt.value === "") {
                    return;
                }
                if (opt.selected) {
                    selected.push(opt);
                } else {
                    unselected.push(opt);
                }
            });

            const allOption = select.querySelector('option[value=""]');
            select.innerHTML = '';
            if (allOption) select.appendChild(allOption);
            selected.forEach(opt => select.appendChild(opt));
            unselected.forEach(opt => select.appendChild(opt));

            select.scrollTop = 0;

            updateApplyButtonPreview();
            updateSelectedValuesContainer(select.id);
        });

        /**
         * Переключение отображения выбранных значений
         */
        function toggleSelectedValues(selectId) {
            const container = document.getElementById(selectId + '_selected');
            const btn = event.target;

            if (!container) return;

            container.classList.toggle('visible');
            btn.classList.toggle('active');

            if (container.classList.contains('visible')) {
                updateSelectedValuesContainer(selectId);
            }
        }

        /**
         * Переключение строки поиска
         */
        function toggleFilterSearch(selectId) {
            const searchContainer = document.getElementById(selectId + '_search');
            const searchBtn = event.target;

            if (!searchContainer) return;

            searchContainer.classList.toggle('visible');
            searchBtn.classList.toggle('active');

            if (searchContainer.classList.contains('visible')) {
                const input = searchContainer.querySelector('input');
                if (input) {
                    setTimeout(() => input.focus(), 100);
                }
            } else {
                const input = searchContainer.querySelector('input');
                if (input) {
                    input.value = '';
                    filterSelectOptions(selectId, '');
                }
            }
        }

        /**
         * Фильтрация опций в select по тексту поиска
         */
        function filterSelectOptions(selectId, searchText) {
            const select = document.getElementById(selectId);
            const searchContainer = document.getElementById(selectId + '_search');

            if (!select) return;

            if (searchContainer) {
                if (searchText.trim() !== '') {
                    searchContainer.classList.add('has-text');
                } else {
                    searchContainer.classList.remove('has-text');
                }
            }

            const searchLower = searchText.toLowerCase().trim();

            Array.from(select.options).forEach(option => {
                if (option.value === '') {
                    option.style.display = '';
                    return;
                }

                const optionText = option.text.toLowerCase();

                if (searchLower === '' || optionText.includes(searchLower)) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });
        }

        /**
         * Очистка поиска
         */
        function clearFilterSearch(selectId) {
            const searchContainer = document.getElementById(selectId + '_search');
            if (!searchContainer) return;

            const input = searchContainer.querySelector('input');
            if (input) {
                input.value = '';
                filterSelectOptions(selectId, '');
                input.focus();
            }
        }

        /**
         * Обновление контейнера выбранных значений
         */
        function updateSelectedValuesContainer(selectId) {
            const select = document.getElementById(selectId);
            const container = document.getElementById(selectId + '_selected');

            if (!select || !container) return;
            if (!container.classList.contains('visible')) return;

            container.innerHTML = '';

            const selectedOptions = Array.from(select.selectedOptions).filter(opt => opt.value !== "");

            if (selectedOptions.length === 0) {
                container.innerHTML = '<span style="color: #9ca3af; font-size: 12px; padding: 4px;">Ничего не выбрано</span>';
                return;
            }

            selectedOptions.forEach(opt => {
                const chip = document.createElement('div');
                chip.className = 'selected-value-chip';

                const text = document.createElement('span');
                text.textContent = opt.text.trim().split('(')[0].trim();

                const removeBtn = document.createElement('button');
                removeBtn.className = 'selected-value-remove';
                removeBtn.textContent = '×';
                removeBtn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    opt.selected = false;

                    const selected = [];
                    const unselected = [];

                    Array.from(select.options).forEach(option => {
                        if (option.value === "") return;
                        if (option.selected) {
                            selected.push(option);
                        } else {
                            unselected.push(option);
                        }
                    });

                    const allOption = select.querySelector('option[value=""]');
                    select.innerHTML = '';
                    if (allOption) select.appendChild(allOption);
                    selected.forEach(option => select.appendChild(option));
                    unselected.forEach(option => select.appendChild(option));

                    updateSelectedValuesContainer(selectId);
                    updateApplyButtonPreview();
                    updateResetButtons();
                };

                chip.appendChild(text);
                chip.appendChild(removeBtn);
                container.appendChild(chip);
            });
        }

        /**
         * Обновление счетчика при изменении дат и площади
         */
        document.addEventListener('change', function (e) {
            if (e.target.id === 'startDate' || e.target.id === 'endDate' ||
                e.target.id === 'minArea' || e.target.id === 'maxArea') {
                updateApplyButtonPreview();
            }
        });

        /**
         * Предварительный расчет для кнопки "Применить"
         */
        function updateApplyButtonPreview() {
            const selectedMagazines = getSelectedValues('filterMagazine');
            const selectedYears = getSelectedValues('filterYear').map(y => parseInt(y));
            const selectedMonths = getSelectedValues('filterMonth');
            const selectedProductTypes = getSelectedValues('filterProductType');
            const selectedProducts = getSelectedValues('filterProduct');

            const startDateStr = document.getElementById('startDate')?.value || '';
            const endDateStr = document.getElementById('endDate')?.value || '';

            const startDate = startDateStr ? new Date(startDateStr + 'T00:00:00') : null;
            const endDate = endDateStr ? new Date(endDateStr + 'T23:59:59') : null;

            // Фильтр по площади
            const minAreaEl = document.getElementById('minArea');
            const maxAreaEl = document.getElementById('maxArea');
            const minArea = minAreaEl ? parseFloat(minAreaEl.value) : 0;
            const maxArea = maxAreaEl ? parseFloat(maxAreaEl.value) : Infinity;
            const areaFilterActive = minAreaEl && maxAreaEl &&
                (minAreaEl.value !== minAreaEl.min || maxAreaEl.value !== maxAreaEl.max);

            const previewData = window.rawData.filter(row => {
                // Фильтр по площади магазина
                if (areaFilterActive) {
                    const area = parseFloat(row['Торговая площадь магазина']);
                    if (isNaN(area) || area < minArea || area > maxArea) {
                        return false;
                    }
                }

                if (selectedMagazines.length > 0) {
                    const magazineStr = String(row['Магазин']);
                    if (!selectedMagazines.includes(magazineStr)) {
                        return false;
                    }
                }

                if (selectedYears.length > 0) {
                    const year = parseInt(row['Год']);
                    if (!selectedYears.includes(year)) {
                        return false;
                    }
                }

                if (selectedMonths.length > 0) {
                    if (!selectedMonths.includes(row['Месяц'])) {
                        return false;
                    }
                }

                if (selectedProductTypes.length > 0) {
                    if (!selectedProductTypes.includes(row['Тип'])) {
                        return false;
                    }
                }

                if (selectedProducts.length > 0) {
                    if (!selectedProducts.includes(row['Товар'])) {
                        return false;
                    }
                }

                if (startDate || endDate) {
                    const rowDate = parseDate(row['Дата']);
                    if (!rowDate) return false;

                    if (startDate && rowDate < startDate) {
                        return false;
                    }
                    if (endDate && rowDate > endDate) {
                        return false;
                    }
                }

                return true;
            });

            const btnText = document.getElementById('apply-button-text');
            if (btnText) {
                btnText.textContent = `Применить (${previewData.length})`;
            }
        }

        /**
         * Группировка данных по выбранному уровню детализации
         */
        function groupDataByDetailLevel(data, level) {
            const grouped = {};

            data.forEach(row => {
                const dateStr = row['Дата'];
                if (!dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const day = parseInt(parts[0]);
                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);
                const date = new Date(year, month - 1, day);

                let key;
                switch(level) {
                    case 'year':
                        key = `${year}`;
                        break;
                    case 'month':
                        key = `${String(month).padStart(2, '0')}.${year}`;
                        break;
                    case 'week':
                        const weekNum = getWeekNumber(date);
                        key = `Н${weekNum} ${year}`;
                        break;
                    case 'day':
                        key = dateStr;
                        break;
                    default:
                        key = dateStr;
                }

                if (!grouped[key]) {
                    grouped[key] = [];
                }
                grouped[key].push(row);
            });

            return grouped;
        }

        /**
         * Получить номер недели в году
         */
        function getWeekNumber(date) {
            const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
            const dayNum = d.getUTCDay() || 7;
            d.setUTCDate(d.getUTCDate() + 4 - dayNum);
            const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
            return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
        }

        // Экспорт функций для использования в графиках
        window.groupDataByDetailLevel = groupDataByDetailLevel;
        window.getWeekNumber = getWeekNumber;
        window.globalDetailLevel = window.globalDetailLevel || 'month';
        window.availableDetailLevels = window.availableDetailLevels || ['year', 'month'];
        '''
