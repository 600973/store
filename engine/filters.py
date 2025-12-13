# PROJECT_ROOT: engine/filters.py
"""
Глобальные фильтры дашборда
"""
import pandas as pd
from .data_processor import get_unique_values


class GlobalFilters:
    """
    Глобальные фильтры для дашборда с config-driven подходом
    """

    def __init__(self, df: pd.DataFrame, filter_config: dict = None):
        """
        Args:
            df: DataFrame с данными для построения списков фильтров
            filter_config: Конфигурация фильтров в формате:
                {
                    'Магазин': {'type': 'multiselect', 'label': 'Магазин'},
                    'Товар': {'type': 'multiselect', 'label': 'Товар'},
                    'Тип': {'type': 'multiselect', 'label': 'Тип товара'}
                }
        """
        self.df = df
        self.filter_config = filter_config or {}
        self.status_columns = [col for col in df.columns if 'статус' in col.lower()]

        # Подготовка значений для каждого фильтра из конфига
        self.filter_values = {}
        for column, config in self.filter_config.items():
            if column in df.columns:
                self.filter_values[column] = get_unique_values(df, column)

    def _get_active_df(self) -> pd.DataFrame:
        """
        Вернуть подмножество с сотрудниками без статуса «Увольнение».
        """
        if not self.status_columns:
            return self.df

        mask = pd.Series(True, index=self.df.index)
        for col in self.status_columns:
            mask &= ~self.df[col].astype(str).str.contains('увольн', case=False, na=False)
        return self.df[mask]

    def _generate_filter_html(self, column: str, config: dict, options_html: str, count: int) -> str:
        """
        Генерирует HTML блок для одного фильтра

        Args:
            column: Название колонки
            config: Конфигурация фильтра
            options_html: HTML со списком опций
            count: Количество уникальных значений

        Returns:
            HTML строка блока фильтра
        """
        # Генерируем ID фильтра (убираем пробелы)
        filter_id = 'filter' + column.replace(' ', '')
        label = config.get('label', column)

        return f'''
                <div class="filter-group" data-filter-key="{column}">
                    <div class="filter-group-header">
                        <label for="{filter_id}">{label} ({count})</label>
                        <div style="display: flex; gap: 4px;">
                            <button type="button"
                                    class="toggle-search-btn"
                                    onclick="toggleFilterSearch('{filter_id}')">
                                🔍
                            </button>
                            <button type="button"
                                    class="toggle-selected-btn"
                                    onclick="toggleSelectedValues('{filter_id}')">
                                👁
                            </button>
                            <button type="button"
                                    class="filter-reset-btn"
                                    data-filter-reset="{column}">
                                ⟳
                            </button>
                        </div>
                    </div>
                    <div id="{filter_id}_search" class="filter-search-container">
                        <input type="text"
                               class="filter-search-input"
                               placeholder="Поиск..."
                               oninput="filterSelectOptions('{filter_id}', this.value)">
                        <button type="button"
                                class="filter-search-clear"
                                onclick="clearFilterSearch('{filter_id}')">×</button>
                    </div>
                    <select id="{filter_id}" multiple size="5">
                        <option value="">Все</option>
                        {options_html}
                    </select>
                    <div id="{filter_id}_selected" class="selected-values-container"></div>
                </div>'''

    def get_html(self) -> str:
        """
        Генерирует HTML для панели фильтров (выдвижная панель справа)

        Returns:
            HTML строка
        """
        active_df = self._get_active_df()

        # Генерируем HTML для опций каждого фильтра
        filter_options_html = {}
        filter_counts = {}

        for column, config in self.filter_config.items():
            if column in active_df.columns:
                counts = active_df[column].value_counts().to_dict()
                values = self.filter_values.get(column, [])
                filter_options_html[column] = ''.join([
                    f'<option value="{v}">{v}      ({counts.get(v, 0)})</option>'
                    for v in values
                ])
                filter_counts[column] = len(values)
            else:
                filter_options_html[column] = ''
                filter_counts[column] = 0

        # Генерируем HTML блоки для всех фильтров из конфига
        filters_html = ''
        for column, config in self.filter_config.items():
            options = filter_options_html.get(column, '')
            count = filter_counts.get(column, 0)
            filters_html += self._generate_filter_html(column, config, options, count)

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
                        <button type="button"
                                class="global-detail-btn"
                                data-level="year"
                                onclick="setGlobalDetailLevel('year')">
                            Год
                        </button>
                        <button type="button"
                                class="global-detail-btn"
                                data-level="month"
                                onclick="setGlobalDetailLevel('month')">
                            Месяц
                        </button>
                        <button type="button"
                                class="global-detail-btn"
                                data-level="week"
                                onclick="setGlobalDetailLevel('week')">
                            Неделя
                        </button>
                        <button type="button"
                                class="global-detail-btn active"
                                data-level="day"
                                onclick="setGlobalDetailLevel('day')">
                            День
                        </button>
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

                    <!-- Пресеты диапазонов дат -->
                    <div class="date-presets">
                        <!-- Оперативные периоды -->
                        <div class="date-presets-row">
                            <span class="date-presets-label">Оперативные:</span>

                            <button type="button"
                                    class="date-preset-btn"
                                    data-date-preset="today"
                                    onclick="setDateRangePreset('today')">
                                Сегодня
                            </button>

                            <button type="button"
                                    class="date-preset-btn"
                                    data-date-preset="last_7_days"
                                    onclick="setDateRangePreset('last_7_days')">
                                7 дней
                            </button>

                            <button type="button"
                                    class="date-preset-btn"
                                    data-date-preset="last_30_days"
                                    onclick="setDateRangePreset('last_30_days')">
                                30 дней
                            </button>
                        </div>

                        <!-- Аналитические периоды -->
                        <div class="date-presets-row">
                            <span class="date-presets-label">Аналитические:</span>

                            <button type="button"
                                    class="date-preset-btn"
                                    data-date-preset="this_month"
                                    onclick="setDateRangePreset('this_month')">
                                Этот месяц
                            </button>

                            <button type="button"
                                    class="date-preset-btn"
                                    data-date-preset="prev_month"
                                    onclick="setDateRangePreset('prev_month')">
                                Прошлый месяц
                            </button>

                            <button type="button"
                                    class="date-preset-btn"
                                    data-date-preset="this_year"
                                    onclick="setDateRangePreset('this_year')">
                                Этот год
                            </button>

                            <button type="button"
                                    class="date-preset-btn"
                                    data-date-preset="prev_year"
                                    onclick="setDateRangePreset('prev_year')">
                                Прошлый год
                            </button>
                        </div>
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

                    <div style="margin-top: 10px; padding-left: 4px;">
                        <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 11px; color: #9ca3af;">
                            <input type="checkbox" id="showFilterCounts" checked style="cursor: pointer; width: 14px; height: 14px;">
                            <span>Показывать количество</span>
                        </label>
                    </div>
                </div>

                <!-- Динамические фильтры из конфига -->
                <div class="filters-grid">
                    {filters_html}
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
        # Генерируем JavaScript объект с конфигурацией фильтров
        filter_config_js = '{'
        for column, config in self.filter_config.items():
            filter_config_js += f'"{column}": {{"type": "{config["type"]}", "label": "{config["label"]}"}}, '
        filter_config_js = filter_config_js.rstrip(', ') + '}'

        return f'''
        // ============================================================================
        // ГЛОБАЛЬНЫЕ ФИЛЬТРЫ
        // ============================================================================

        let filteredData = [];
        let combinedData = [];

        // Конфигурация фильтров
        const filterConfig = {filter_config_js};

        /**
         * Переключение видимости панели глобальных фильтров
         */
        function toggleGlobalFilters() {{
            const panel = document.getElementById('global-filters-panel');
            if (panel) {{
                panel.classList.toggle('open');
            }}
        }}

        /**
         * Получить выбранные значения из multi-select
         */
        function getSelectedValues(selectId) {{
            const select = document.getElementById(selectId);
            if (!select) return [];
            return Array.from(select.selectedOptions)
                .map(opt => opt.value)
                .filter(v => v !== "");
        }}

        /**
         * Сброс ЗНАЧЕНИЙ одного фильтра по ключу
         */
        function resetSingleFilter(key) {{
            let selectId = null;

            // Специальный случай для даты
            if (key === 'date') {{
                const from = document.getElementById('startDate');
                const to   = document.getElementById('endDate');
                if (from) from.value = '';
                if (to)   to.value = '';
                return;
            }}

            // Для всех остальных фильтров используем конфиг
            if (filterConfig[key]) {{
                selectId = 'filter' + key.replace(/\\s/g, '');
                const el = document.getElementById(selectId);
                if (el) {{
                    [...el.options].forEach(o => o.selected = false);
                }}
            }}

            // Обновляем контейнер с выбранными значениями, если он открыт
            if (selectId) {{
                updateSelectedValuesContainer(selectId);
            }}
        }}

        /**
         * Применить глобальные фильтры
         */
        function applyFilters() {{
            // Получить выбранные значения для каждого фильтра из конфига
            const filters = {{}};
            for (const [column, config] of Object.entries(filterConfig)) {{
                const filterId = 'filter' + column.replace(/\\s/g, '');
                const select = document.getElementById(filterId);
                if (select) {{
                    filters[column] = Array.from(select.selectedOptions)
                        .map(opt => opt.value)
                        .filter(v => v !== '');
                }}
            }}

            // Получить фильтры по датам
            const startDateStr = document.getElementById('startDate')?.value || '';
            const endDateStr = document.getElementById('endDate')?.value || '';

            const startDate = startDateStr ? new Date(startDateStr) : null;
            const endDate = endDateStr ? new Date(endDateStr) : null;

            // Фильтрация данных
            filteredData = rawData.filter(row => {{
                // Применить все фильтры из конфига
                for (const [column, values] of Object.entries(filters)) {{
                    if (values.length > 0) {{
                        const rowValue = String(row[column]);
                        if (!values.includes(rowValue)) {{
                            return false;
                        }}
                    }}
                }}

                // Фильтр по датам
                if (startDate) {{
                    // Если уволен до startDate - исключаем
                    if (row.dateFired && row.dateFired < startDate) {{
                        return false;
                    }}
                }}

                if (endDate) {{
                    // Если принят после endDate - исключаем
                    if (row.dateHired && row.dateHired > endDate) {{
                        return false;
                    }}
                }}

                return true;
            }});

            console.log('🔍 Отфильтровано записей:', filteredData.length);

            // Обновление счетчика на кнопке применить
            updateApplyButtonText();

            // Обновление контекста для AI-анализа
            if (typeof updateAnalysisContext === 'function') {{
                const activeFilters = {{}};

                // Добавляем активные фильтры из конфига
                for (const [column, values] of Object.entries(filters)) {{
                    if (values.length > 0) {{
                        activeFilters[column] = values;
                    }}
                }}

                // Добавляем период если выбран
                if (startDate || endDate) {{
                    activeFilters['Период'] = (startDate && endDate)
                        ? {{from: startDate.toISOString().split('T')[0], to: endDate.toISOString().split('T')[0]}}
                        : (startDate
                            ? {{from: startDate.toISOString().split('T')[0], to: 'н/д'}}
                            : {{from: 'н/д', to: endDate.toISOString().split('T')[0]}});
                }}

                updateAnalysisContext(filteredData, activeFilters);
            }}

            // Пересчёт комбинированных данных
            calculateCombinedDataJS(startDate, endDate, globalDetailLevel);

            // Обновление графиков
            updateAllCharts();
        }}

        /**
         * Обновить текст кнопки применить с количеством записей
         */
        function updateApplyButtonText() {{
            const btnText = document.getElementById('apply-button-text');
            if (!btnText) return;

            const count = filteredData ? filteredData.length : 0;
            btnText.textContent = `Применить (${{count}})`;
        }}

        /**
         * Сбросить все фильтры (кнопка в шапке и внизу панели)
         */
        function resetFilters() {{
            // пробегаемся по всем кнопкам сброса и чистим значения
            document.querySelectorAll('.filter-reset-btn')
                .forEach(btn => {{
                    const key = btn.dataset.filterReset;
                    if (key) {{
                        resetSingleFilter(key);
                    }}
                }});

            applyFilters();
        }}

        /**
         * Делегирование кликов по кнопкам "сбросить конкретный фильтр"
         */
        document.addEventListener('click', function (e) {{
            const btn = e.target.closest('.filter-reset-btn');
            if (!btn) return;

            const key = btn.dataset.filterReset;
            if (!key) return;

            resetSingleFilter(key);
            applyFilters();
        }});

        /**
         * Сортировка выбранных опций наверх и обновление счетчика
         */
        document.addEventListener('change', function (e) {{
            const select = e.target;
            if (!select.matches('select[multiple]')) return;

            const selected = [];
            const unselected = [];

            Array.from(select.options).forEach(opt => {{
                if (opt.value === "") {{
                    return;
                }}
                if (opt.selected) {{
                    selected.push(opt);
                }} else {{
                    unselected.push(opt);
                }}
            }});

            const allOption = select.querySelector('option[value=""]');
            select.innerHTML = '';
            if (allOption) select.appendChild(allOption);
            selected.forEach(opt => select.appendChild(opt));
            unselected.forEach(opt => select.appendChild(opt));

            select.scrollTop = 0;

            updateApplyButtonPreview();
            updateSelectedValuesContainer(select.id);
        }});

        /**
         * Переключение отображения выбранных значений
         */
        function toggleSelectedValues(selectId) {{
            const container = document.getElementById(selectId + '_selected');
            const btn = event.target;

            if (!container) return;

            container.classList.toggle('visible');
            btn.classList.toggle('active');

            if (container.classList.contains('visible')) {{
                updateSelectedValuesContainer(selectId);
            }}
        }}

        /**
         * Переключение строки поиска
         */
        function toggleFilterSearch(selectId) {{
            const searchContainer = document.getElementById(selectId + '_search');
            const searchBtn = event.target;

            if (!searchContainer) return;

            searchContainer.classList.toggle('visible');
            searchBtn.classList.toggle('active');

            if (searchContainer.classList.contains('visible')) {{
                // Фокус на поле ввода
                const input = searchContainer.querySelector('input');
                if (input) {{
                    setTimeout(() => input.focus(), 100);
                }}
            }} else {{
                // Очищаем поиск при закрытии
                const input = searchContainer.querySelector('input');
                if (input) {{
                    input.value = '';
                    filterSelectOptions(selectId, '');
                }}
            }}
        }}

        /**
         * Фильтрация опций в select по тексту поиска
         */
        function filterSelectOptions(selectId, searchText) {{
            const select = document.getElementById(selectId);
            const searchContainer = document.getElementById(selectId + '_search');

            if (!select) return;

            // Управляем отображением крестика
            if (searchContainer) {{
                if (searchText.trim() !== '') {{
                    searchContainer.classList.add('has-text');
                }} else {{
                    searchContainer.classList.remove('has-text');
                }}
            }}

            const searchLower = searchText.toLowerCase().trim();

            Array.from(select.options).forEach(option => {{
                if (option.value === '') {{
                    // Опция "Все" всегда видна
                    option.style.display = '';
                    return;
                }}

                const optionText = option.text.toLowerCase();

                if (searchLower === '' || optionText.includes(searchLower)) {{
                    option.style.display = '';
                }} else {{
                    option.style.display = 'none';
                }}
            }});
        }}

        /**
         * Очистка поиска
         */
        function clearFilterSearch(selectId) {{
            const searchContainer = document.getElementById(selectId + '_search');
            if (!searchContainer) return;

            const input = searchContainer.querySelector('input');
            if (input) {{
                input.value = '';
                filterSelectOptions(selectId, '');
                input.focus();
            }}
        }}

        /**
         * Обновление контейнера выбранных значений
         */
        function updateSelectedValuesContainer(selectId) {{
            const select = document.getElementById(selectId);
            const container = document.getElementById(selectId + '_selected');

            if (!select || !container) return;
            if (!container.classList.contains('visible')) return;

            container.innerHTML = '';

            const selectedOptions = Array.from(select.selectedOptions).filter(opt => opt.value !== "");

            if (selectedOptions.length === 0) {{
                container.innerHTML = '<span style="color: #9ca3af; font-size: 12px; padding: 4px;">Ничего не выбрано</span>';
                return;
            }}

            selectedOptions.forEach(opt => {{
                const chip = document.createElement('div');
                chip.className = 'selected-value-chip';

                const text = document.createElement('span');
                text.textContent = opt.text.trim().split('(')[0].trim(); // Убираем счетчик

                const removeBtn = document.createElement('button');
                removeBtn.className = 'selected-value-remove';
                removeBtn.textContent = '×';
                removeBtn.onclick = (e) => {{
                    e.preventDefault();
                    e.stopPropagation();

                    // Снимаем выбор с option
                    opt.selected = false;

                    // Пересортируем список
                    const selected = [];
                    const unselected = [];

                    Array.from(select.options).forEach(option => {{
                        if (option.value === "") return;
                        if (option.selected) {{
                            selected.push(option);
                        }} else {{
                            unselected.push(option);
                        }}
                    }});

                    const allOption = select.querySelector('option[value=""]');
                    select.innerHTML = '';
                    if (allOption) select.appendChild(allOption);
                    selected.forEach(option => select.appendChild(option));
                    unselected.forEach(option => select.appendChild(option));

                    // Обновляем контейнер и счетчик
                    updateSelectedValuesContainer(selectId);
                    updateApplyButtonPreview();

                    // Обновляем состояние кнопок сброса
                    if (typeof updateResetButtons === 'function') {{
                        updateResetButtons();
                    }}
                }};

                chip.appendChild(text);
                chip.appendChild(removeBtn);
                container.appendChild(chip);
            }});
        }}

        /**
         * Обновление счетчика при изменении дат
         */
        document.addEventListener('change', function (e) {{
            if (e.target.id === 'startDate' || e.target.id === 'endDate') {{
                updateApplyButtonPreview();
            }}
        }});

        /**
         * Предварительный расчет для кнопки "Применить"
         */
        function updateApplyButtonPreview() {{
            // Получить выбранные значения для каждого фильтра из конфига
            const filters = {{}};
            for (const [column, config] of Object.entries(filterConfig)) {{
                const filterId = 'filter' + column.replace(/\\s/g, '');
                const select = document.getElementById(filterId);
                if (select) {{
                    filters[column] = Array.from(select.selectedOptions)
                        .map(opt => opt.value)
                        .filter(v => v !== '');
                }}
            }}

            const startDateStr = document.getElementById('startDate')?.value || '';
            const endDateStr = document.getElementById('endDate')?.value || '';

            const startDate = startDateStr ? new Date(startDateStr) : null;
            const endDate = endDateStr ? new Date(endDateStr) : null;

            const previewData = rawData.filter(row => {{
                // Применить все фильтры из конфига
                for (const [column, values] of Object.entries(filters)) {{
                    if (values.length > 0) {{
                        const rowValue = String(row[column]);
                        if (!values.includes(rowValue)) {{
                            return false;
                        }}
                    }}
                }}

                if (startDate) {{
                    if (row.dateFired && row.dateFired < startDate) {{
                        return false;
                    }}
                }}

                if (endDate) {{
                    if (row.dateHired && row.dateHired > endDate) {{
                        return false;
                    }}
                }}

                return true;
            }});

            const btnText = document.getElementById('apply-button-text');
            if (btnText) {{
                btnText.textContent = `Применить (${{previewData.length}})`;
            }}
        }}

        // ============================================================================
        // РАСЧЁТЫ (АНАЛОГИ PYTHON ФУНКЦИЙ)
        // ============================================================================

        /**
         * Подсчёт сотрудников на дату
         */
        function countEmployeesJS(data, checkDate) {{
            return data.filter(row => {{
                const status = (row['Статус'] || row['Статус сотрудника'] || row.status || '').toString().toLowerCase();
                if (status.includes('увольн')) return false;
                if (!row.dateHired) return false;
                if (row.dateHired > checkDate) return false;
                if (row.dateFired && row.dateFired <= checkDate) return false;
                return true;
            }}).length;
        }}

        /**
         * Расчёт комбинированных данных с детализацией
         */
        function calculateCombinedDataJS(startDate, endDate, detailLevel = 'month') {{
            if (!filteredData || filteredData.length === 0) {{
                combinedData = [];
                return;
            }}

            const dates = filteredData.map(r => r.dateHired).filter(d => d);
            if (dates.length === 0) {{
                combinedData = [];
                return;
            }}

            let minDate = startDate || new Date(Math.min(...dates));
            let maxDate = endDate || new Date();

            const periods = [];
            let current = new Date(minDate);

            // Генерация периодов по уровню детализации
            if (detailLevel === 'year') {{
                current = new Date(current.getFullYear(), 0, 1);
                while (current <= maxDate) {{
                    periods.push(new Date(current));
                    current.setFullYear(current.getFullYear() + 1);
                }}
            }} else if (detailLevel === 'month') {{
                current = new Date(current.getFullYear(), current.getMonth(), 1);
                while (current <= maxDate) {{
                    periods.push(new Date(current));
                    current.setMonth(current.getMonth() + 1);
                }}
            }} else if (detailLevel === 'week') {{
                const day = current.getDay();
                const diff = current.getDate() - day + (day === 0 ? -6 : 1);
                current = new Date(current.setDate(diff));
                current.setHours(0, 0, 0, 0);
                while (current <= maxDate) {{
                    periods.push(new Date(current));
                    current.setDate(current.getDate() + 7);
                }}
            }} else if (detailLevel === 'day') {{
                current.setHours(0, 0, 0, 0);
                while (current <= maxDate) {{
                    periods.push(new Date(current));
                    current.setDate(current.getDate() + 1);
                }}
            }}

            // Расчёт данных для каждого периода
            combinedData = periods.map(period => {{
                let periodEnd;

                if (detailLevel === 'year') {{
                    periodEnd = new Date(period.getFullYear(), 11, 31, 23, 59, 59);
                }} else if (detailLevel === 'month') {{
                    periodEnd = new Date(period.getFullYear(), period.getMonth() + 1, 0, 23, 59, 59);
                }} else if (detailLevel === 'week') {{
                    periodEnd = new Date(period);
                    periodEnd.setDate(periodEnd.getDate() + 6);
                    periodEnd.setHours(23, 59, 59);
                }} else {{
                    periodEnd = new Date(period);
                    periodEnd.setHours(23, 59, 59);
                }}

                const headcount = countEmployeesJS(filteredData, period);
                const dismissals = filteredData.filter(row =>
                    row.dateFired && row.dateFired >= period && row.dateFired <= periodEnd
                ).length;
                const hired = filteredData.filter(row =>
                    row.dateHired && row.dateHired >= period && row.dateHired <= periodEnd
                ).length;

                const turnoverRate = headcount > 0 ? (dismissals / headcount * 100) : 0;
                const hiredRate = headcount > 0 ? (hired / headcount * 100) : 0;

                return {{
                    date: period,
                    headcount: headcount,
                    dismissals: dismissals,
                    hired: hired,
                    turnoverRate: turnoverRate,
                    hiredRate: hiredRate
                }};
            }});

            console.log('📊 Комбинированные данные (' + detailLevel + '):', combinedData.length);
        }}
        '''
