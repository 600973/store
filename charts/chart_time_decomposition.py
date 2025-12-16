# PROJECT_ROOT: charts/chart_time_decomposition.py
from charts.base_chart import BaseChart


class ChartTimeDecomposition(BaseChart):
    """Декомпозиция временных рядов (тренд + сезонность + остатки)"""

    def __init__(self, chart_id='chart_time_decomposition', **kwargs):
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)
        super().__init__(chart_id=chart_id, **kwargs)

    def _generate_chart_selectors_html(self) -> str:
        """Генерирует селекторы для выбора магазина, метрики, товара/типа и локальный фильтр дат"""
        return f'''
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef; flex-wrap: wrap; align-items: center;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Магазин:</label>
                <select id="{self.chart_id}_store" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Метрика:</label>
                <select id="{self.chart_id}_metric" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="Сумма в чеке" selected>Сумма в чеке</option>
                    <option value="Число чеков">Число чеков</option>
                    <option value="Количество в чеке">Количество в чеке</option>
                    <option value="Наценка продажи в чеке">Наценка продажи в чеке</option>
                    <option value="revenue_per_m2">Выручка на м²</option>
                    <option value="profit_per_m2">Прибыль на м²</option>
                    <option value="margin">Маржинальность (%)</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Тип товара:</label>
                <select id="{self.chart_id}_product_type" onchange="onTypeChange_{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="all" selected>Все</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Товар:</label>
                <select id="{self.chart_id}_product" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white; max-width: 180px;">
                    <option value="all" selected>Все</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">Режим:</label>
                <select id="{self.chart_id}_mode" onchange="update{self.chart_id}()" style="padding: 6px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px; background: white;">
                    <option value="absolute" selected>Абсолютные</option>
                    <option value="percent">% вклада</option>
                </select>
            </div>
            <div class="selector-group" style="display: flex; align-items: center;">
                <button onclick="toggleDecompositionInfo()" style="
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
        <div class="chart-selectors" style="display: flex; gap: 20px; margin-bottom: 12px; padding: 10px; background: #fff8e1; border-radius: 8px; border: 1px solid #ffe082; flex-wrap: wrap; align-items: center;">
            <div class="selector-group" style="display: flex; align-items: center; gap: 8px;">
                <label style="font-weight: 500; font-size: 13px; color: #495057;">📅 Локальный период:</label>
                <input type="date" id="{self.chart_id}_date_from" onchange="update{self.chart_id}()" style="padding: 5px 10px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px;">
                <span style="color: #495057;">—</span>
                <input type="date" id="{self.chart_id}_date_to" onchange="update{self.chart_id}()" style="padding: 5px 10px; border: 1px solid #ced4da; border-radius: 6px; font-size: 13px;">
                <button onclick="resetLocalDates_{self.chart_id}()" style="
                    background: #e9ecef;
                    color: #495057;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    padding: 5px 10px;
                    font-size: 12px;
                    cursor: pointer;
                " title="Сбросить на весь период">↺</button>
            </div>
            <div style="font-size: 11px; color: #666;">
                <span id="{self.chart_id}_date_info"></span>
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

            <!-- Модальное окно с объяснением декомпозиции (динамическое содержимое) -->
            <div id="decomposition-modal" style="
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
                    max-width: 800px;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                    margin: 20px auto;
                    position: relative;
                ">
                    <div style="
                        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
                        color: white;
                        padding: 20px 25px;
                        border-radius: 15px 15px 0 0;
                        font-size: 20px;
                        font-weight: 600;
                        position: relative;
                    ">
                        📊 Декомпозиция временных рядов
                        <span onclick="toggleDecompositionInfo()" style="
                            position: absolute;
                            top: 15px;
                            right: 20px;
                            font-size: 32px;
                            cursor: pointer;
                            line-height: 1;
                        ">&times;</span>
                    </div>
                    <div id="decomposition-modal-content" style="padding: 25px; line-height: 1.7;">
                        <!-- Динамическое содержимое будет вставлено через JavaScript -->
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
        // Глобальное хранилище данных декомпозиции для модального окна
        window.{self.chart_id}_decompositionData = null;

        /**
         * Переключение модального окна с объяснением декомпозиции
         */
        function toggleDecompositionInfo() {{
            const modal = document.getElementById('decomposition-modal');
            if (modal.style.display === 'none' || modal.style.display === '') {{
                // Генерируем содержимое с реальными данными
                generateDecompositionModalContent_{self.chart_id}();
                modal.style.display = 'flex';
                modal.style.alignItems = 'center';
                modal.style.justifyContent = 'center';
            }} else {{
                modal.style.display = 'none';
            }}
        }}

        /**
         * Форматирование числа для отображения
         */
        function formatNum(num, decimals = 0) {{
            if (num === null || num === undefined || isNaN(num)) return '—';
            if (Math.abs(num) >= 1000000) {{
                return (num / 1000000).toFixed(1) + ' млн';
            }} else if (Math.abs(num) >= 1000) {{
                return (num / 1000).toFixed(1) + ' тыс';
            }}
            return num.toFixed(decimals);
        }}

        /**
         * Генерация динамического содержимого модального окна
         */
        function generateDecompositionModalContent_{self.chart_id}() {{
            const contentDiv = document.getElementById('decomposition-modal-content');
            const d = window.{self.chart_id}_decompositionData;

            if (!d) {{
                contentDiv.innerHTML = '<p style="color: #666;">Нет данных для отображения. Выберите магазин и метрику.</p>';
                return;
            }}

            // Получаем min/max для тренда (без null)
            const validTrend = d.trend.filter(v => v !== null);
            const trendMin = validTrend.length ? Math.min(...validTrend) : 0;
            const trendMax = validTrend.length ? Math.max(...validTrend) : 0;
            const trendMean = validTrend.length ? validTrend.reduce((a,b) => a+b, 0) / validTrend.length : 0;

            // Получаем min/max для остатков
            const validResidual = d.residual.filter(v => v !== null);
            const residualMin = validResidual.length ? Math.min(...validResidual) : 0;
            const residualMax = validResidual.length ? Math.max(...validResidual) : 0;
            const residualMean = validResidual.length ? validResidual.reduce((a,b) => a+b, 0) / validResidual.length : 0;

            // Сезонность - min/max
            const seasonalMin = Math.min(...d.seasonal);
            const seasonalMax = Math.max(...d.seasonal);

            // Определяем цвет R²
            let r2Color = '#C73E1D';  // красный < 50%
            let r2Text = 'слабая модель, много случайных факторов';
            if (d.r2 >= 80) {{
                r2Color = '#28a745';
                r2Text = 'отличная модель, данные хорошо предсказуемы';
            }} else if (d.r2 >= 50) {{
                r2Color = '#F18F01';
                r2Text = 'хорошая модель, есть сезонность и/или тренд';
            }}

            contentDiv.innerHTML = `
                <div style="background: linear-gradient(135deg, #e8f5e9 0%, #e3f2fd 100%); border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 2px solid #2E86AB;">
                    <h3 style="color: #2E86AB; font-size: 16px; margin: 0 0 12px 0;">📍 Текущие данные: ${{d.store}} | ${{d.metric}}</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">
                        <div style="background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #2E86AB;">
                            <div style="font-size: 11px; color: #666;">Период</div>
                            <div style="font-size: 14px; font-weight: 600; color: #333;">${{d.periods[0]}} — ${{d.periods[d.periods.length-1]}}</div>
                            <div style="font-size: 11px; color: #888;">${{d.periods.length}} мес.</div>
                        </div>
                        <div style="background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #A23B72;">
                            <div style="font-size: 11px; color: #666;">Тренд</div>
                            <div style="font-size: 14px; font-weight: 600; color: #A23B72;">${{formatNum(trendMin)}} → ${{formatNum(trendMax)}}</div>
                            <div style="font-size: 11px; color: #888;">Δ ${{formatNum(trendMax - trendMin)}} за период</div>
                        </div>
                        <div style="background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #F18F01;">
                            <div style="font-size: 11px; color: #666;">Сезонность</div>
                            <div style="font-size: 14px; font-weight: 600; color: #F18F01;">±${{formatNum(Math.max(Math.abs(seasonalMin), Math.abs(seasonalMax)))}}</div>
                            <div style="font-size: 11px; color: #888;">от ${{formatNum(seasonalMin)}} до +${{formatNum(seasonalMax)}}</div>
                        </div>
                        <div style="background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #C73E1D;">
                            <div style="font-size: 11px; color: #666;">Остатки</div>
                            <div style="font-size: 14px; font-weight: 600; color: #C73E1D;">±${{formatNum(Math.max(Math.abs(residualMin), Math.abs(residualMax)))}}</div>
                            <div style="font-size: 11px; color: #888;">от ${{formatNum(residualMin)}} до +${{formatNum(residualMax)}}</div>
                        </div>
                    </div>
                </div>

                <div style="background: #f0f7ff; border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 2px solid ${{r2Color}};">
                    <h3 style="color: ${{r2Color}}; font-size: 16px; margin: 0 0 10px 0;">🎯 Точность модели (R²): ${{d.r2}}%</h3>
                    <p style="margin: 0; color: #4a5568; font-size: 13px;">${{r2Text}}</p>
                    <div style="margin-top: 10px; background: white; border-radius: 6px; padding: 10px;">
                        <div style="display: flex; height: 24px; border-radius: 4px; overflow: hidden; font-size: 11px;">
                            <div style="width: ${{d.pctTrend}}%; background: #A23B72; color: white; display: flex; align-items: center; justify-content: center;">
                                ${{d.pctTrend > 5 ? 'Тренд ' + d.pctTrend + '%' : ''}}
                            </div>
                            <div style="width: ${{d.pctSeasonal}}%; background: #F18F01; color: white; display: flex; align-items: center; justify-content: center;">
                                ${{d.pctSeasonal > 5 ? 'Сезон. ' + d.pctSeasonal + '%' : ''}}
                            </div>
                            <div style="width: ${{d.pctResidual}}%; background: #C73E1D; color: white; display: flex; align-items: center; justify-content: center;">
                                ${{d.pctResidual > 5 ? 'Остатки ' + d.pctResidual + '%' : ''}}
                            </div>
                        </div>
                    </div>
                </div>

                <h3 style="color: #28a745; font-size: 16px; margin-top: 20px;">📊 Расчёт % вклада для ${{d.store}}</h3>

                <div style="background: #e8f5e9; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745;">
                    <p style="margin: 0 0 10px 0; color: #333; font-weight: 600;">Реальные данные декомпозиции:</p>
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px;">
                        <tr style="background: #c8e6c9;">
                            <th style="padding: 8px; text-align: left; border: 1px solid #a5d6a7;">Компонента</th>
                            <th style="padding: 8px; text-align: left; border: 1px solid #a5d6a7;">Диапазон</th>
                            <th style="padding: 8px; text-align: right; border: 1px solid #a5d6a7;">Дисперсия</th>
                            <th style="padding: 8px; text-align: right; border: 1px solid #a5d6a7;">% вклада</th>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #a5d6a7; color: #A23B72; font-weight: 600;">Тренд</td>
                            <td style="padding: 8px; border: 1px solid #a5d6a7;">${{formatNum(trendMin)}} → ${{formatNum(trendMax)}}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7;">${{formatNum(d.varTrend)}}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7; font-weight: 600;">${{d.pctTrend}}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #a5d6a7; color: #F18F01; font-weight: 600;">Сезонность</td>
                            <td style="padding: 8px; border: 1px solid #a5d6a7;">±${{formatNum(Math.max(Math.abs(seasonalMin), Math.abs(seasonalMax)))}}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7;">${{formatNum(d.varSeasonal)}}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7; font-weight: 600;">${{d.pctSeasonal}}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #a5d6a7; color: #C73E1D; font-weight: 600;">Остатки</td>
                            <td style="padding: 8px; border: 1px solid #a5d6a7;">±${{formatNum(Math.max(Math.abs(residualMin), Math.abs(residualMax)))}}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7;">${{formatNum(d.varResidual)}}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7; font-weight: 600;">${{d.pctResidual}}%</td>
                        </tr>
                        <tr style="background: #c8e6c9; font-weight: 600;">
                            <td style="padding: 8px; border: 1px solid #a5d6a7;">Сумма</td>
                            <td style="padding: 8px; border: 1px solid #a5d6a7;"></td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7;">${{formatNum(d.totalVar)}}</td>
                            <td style="padding: 8px; text-align: right; border: 1px solid #a5d6a7;">100%</td>
                        </tr>
                    </table>

                    <p style="margin: 15px 0 5px 0; color: #333; font-weight: 600;">Как считаются проценты:</p>
                    <ul style="margin: 5px 0; padding-left: 20px; color: #4a5568; font-size: 13px; font-family: monospace;">
                        <li>% Тренда = ${{formatNum(d.varTrend)}} / ${{formatNum(d.totalVar)}} × 100 = <strong>${{d.pctTrend}}%</strong></li>
                        <li>% Сезонности = ${{formatNum(d.varSeasonal)}} / ${{formatNum(d.totalVar)}} × 100 = <strong>${{d.pctSeasonal}}%</strong></li>
                        <li>% Остатков = ${{formatNum(d.varResidual)}} / ${{formatNum(d.totalVar)}} × 100 = <strong>${{d.pctResidual}}%</strong></li>
                    </ul>
                </div>

                <div style="background: #fff3e0; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #ff9800;">
                    <p style="margin: 0 0 10px 0; color: #333; font-weight: 600;">⚠️ Почему % вклада ≠ % от суммы?</p>
                    <p style="margin: 5px 0; color: #4a5568; font-size: 13px;">
                        <strong>Дисперсия</strong> измеряет разброс (изменчивость), а не величину.
                        Тренд может быть большим по абсолютному значению (${{formatNum(trendMean)}}), но <em>стабильным</em> —
                        меняется всего на ${{formatNum((trendMax - trendMin) / d.periods.length, 1)}} в месяц.
                    </p>
                    <p style="margin: 10px 0 0 0; color: #4a5568; font-size: 13px;">
                        Остатки малы по величине (±${{formatNum(Math.max(Math.abs(residualMin), Math.abs(residualMax)))}}),
                        но <em>скачут каждый месяц</em> → создают основную изменчивость (${{d.pctResidual}}%).
                    </p>
                    <p style="margin: 10px 0 0 0; color: #333; font-size: 13px; font-style: italic;">
                        Проценты отвечают на вопрос: <strong>«Почему значения каждый месяц разные?»</strong>
                    </p>
                </div>

                <h3 style="color: #2E86AB; font-size: 16px; margin-top: 25px;">🎯 Что это такое?</h3>
                <p style="margin: 10px 0; color: #4a5568;">
                    Декомпозиция временного ряда — разложение данных на <strong>три составляющие</strong>:
                </p>
                <ul style="margin: 10px 0; padding-left: 25px; color: #4a5568;">
                    <li><strong>Тренд</strong> — долгосрочное направление (скользящее среднее за 12 мес.)</li>
                    <li><strong>Сезонность</strong> — повторяющиеся паттерны по месяцам</li>
                    <li><strong>Остатки</strong> — случайные колебания, не объяснённые моделью</li>
                </ul>
                <div style="background: #e3f2fd; border-radius: 8px; padding: 12px; margin: 15px 0; border-left: 4px solid #2E86AB;">
                    <p style="margin: 0; color: #333; font-family: monospace; font-size: 13px;">
                        <strong>Формула:</strong> Исходные данные = Тренд + Сезонность + Остатки
                    </p>
                </div>

                <h3 style="color: #17a2b8; font-size: 16px; margin-top: 25px;">📝 Что такое дисперсия?</h3>
                <div style="background: #d1ecf1; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #17a2b8;">
                    <p style="margin: 0 0 10px 0; color: #4a5568;">
                        <strong>Дисперсия</strong> = среднее от (значение − среднее)²
                    </p>
                    <p style="margin: 5px 0; color: #4a5568; font-size: 13px;">
                        Чем сильнее значения «скачут» вокруг среднего — тем выше дисперсия.
                    </p>
                    <p style="margin: 10px 0 0 0; color: #333; font-size: 13px;">
                        <strong>Пример:</strong> Ряд [100, 101, 99, 100] имеет дисперсию ≈1 (стабилен),<br>
                        а ряд [50, 150, 30, 170] имеет дисперсию ≈3000 (сильно скачет).
                    </p>
                </div>

                <h3 style="color: #495057; font-size: 16px; margin-top: 25px;">⚙️ Важные особенности</h3>
                <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0;">
                    <ul style="margin: 0; padding-left: 20px; color: #4a5568; font-size: 13px;">
                        <li>Для полноценной декомпозиции нужно <strong>≥24 месяца</strong> данных</li>
                        <li>При 12 месяцах тренд будет пустым (недостаточно данных для скользящего среднего)</li>
                        <li>Локальный фильтр дат работает независимо от глобального фильтра дашборда</li>
                        <li><strong>R² > 80%</strong> — данные хорошо предсказуемы, <strong>R² < 50%</strong> — много случайных факторов</li>
                    </ul>
                </div>
            `;
        }}

        // Глобальные переменные для хранения диапазона дат из данных
        window.{self.chart_id}_dateRange = null;
        window.{self.chart_id}_initialized = false;

        /**
         * Сброс локальных дат на весь доступный период
         */
        function resetLocalDates_{self.chart_id}() {{
            const range = window.{self.chart_id}_dateRange;
            if (range) {{
                document.getElementById('{self.chart_id}_date_from').value = range.min;
                document.getElementById('{self.chart_id}_date_to').value = range.max;
                update{self.chart_id}();
            }}
        }}

        /**
         * Обновление списка товаров в зависимости от выбранного типа
         */
        function updateProductList_{self.chart_id}() {{
            const data = window.rawData;
            const typeSelect = document.getElementById('{self.chart_id}_product_type');
            const productSelect = document.getElementById('{self.chart_id}_product');

            if (!typeSelect || !productSelect) return;

            const selectedType = typeSelect.value;
            const currentProduct = productSelect.value;

            // Фильтруем товары по выбранному типу
            let filteredData = data;
            if (selectedType !== 'all') {{
                filteredData = data.filter(r => r['Тип'] === selectedType);
            }}

            // Получаем уникальные товары
            const products = [...new Set(filteredData.map(r => r['Товар']).filter(v => v))].sort();

            // Очищаем и заполняем список
            productSelect.innerHTML = '<option value="all" selected>Все</option>';
            products.forEach(product => {{
                const option = document.createElement('option');
                option.value = product;
                option.textContent = product;
                productSelect.appendChild(option);
            }});

            // Если текущий товар есть в новом списке — оставляем его выбранным
            if (currentProduct !== 'all' && products.includes(currentProduct)) {{
                productSelect.value = currentProduct;
            }}
        }}

        /**
         * Обработчик изменения типа товара
         */
        function onTypeChange_{self.chart_id}() {{
            updateProductList_{self.chart_id}();
            update{self.chart_id}();
        }}

        /**
         * Инициализация списков магазинов и типов
         */
        function initSelectors_{self.chart_id}() {{
            const data = window.rawData; // Используем rawData для полного диапазона

            // Заполняем список магазинов
            const storeSelect = document.getElementById('{self.chart_id}_store');
            if (storeSelect && !storeSelect.options.length) {{
                const stores = [...new Set(data.map(r => r['Магазин']).filter(v => v))].sort((a, b) => {{
                    const numA = parseInt(a.match(/\\d+/)) || 0;
                    const numB = parseInt(b.match(/\\d+/)) || 0;
                    return numA - numB;
                }});
                stores.forEach(store => {{
                    const option = document.createElement('option');
                    option.value = store;
                    option.textContent = store;
                    storeSelect.appendChild(option);
                }});
            }}

            // Заполняем список типов товаров
            const typeSelect = document.getElementById('{self.chart_id}_product_type');
            if (typeSelect && typeSelect.options.length <= 1) {{
                const types = [...new Set(data.map(r => r['Тип']).filter(v => v))].sort();
                types.forEach(type => {{
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type;
                    typeSelect.appendChild(option);
                }});
            }}

            // Обновляем список товаров при инициализации
            updateProductList_{self.chart_id}();

            // Определяем диапазон дат из данных (rawData - весь датасет)
            if (!window.{self.chart_id}_dateRange) {{
                let minDate = null;
                let maxDate = null;

                data.forEach(row => {{
                    const dateStr = row['Дата'];
                    if (!dateStr) return;

                    const parts = dateStr.split('.');
                    if (parts.length !== 3) return;

                    const day = parseInt(parts[0]);
                    const month = parseInt(parts[1]);
                    const year = parseInt(parts[2]);

                    // Формат для input[type=date]: YYYY-MM-DD
                    const isoDate = `${{year}}-${{String(month).padStart(2, '0')}}-${{String(day).padStart(2, '0')}}`;

                    if (!minDate || isoDate < minDate) minDate = isoDate;
                    if (!maxDate || isoDate > maxDate) maxDate = isoDate;
                }});

                if (minDate && maxDate) {{
                    window.{self.chart_id}_dateRange = {{ min: minDate, max: maxDate }};

                    // Устанавливаем начальные значения
                    document.getElementById('{self.chart_id}_date_from').value = minDate;
                    document.getElementById('{self.chart_id}_date_to').value = maxDate;

                    // Обновляем информацию
                    const fromParts = minDate.split('-');
                    const toParts = maxDate.split('-');
                    document.getElementById('{self.chart_id}_date_info').textContent =
                        `Доступный диапазон: ${{fromParts[2]}}.${{fromParts[1]}}.${{fromParts[0]}} — ${{toParts[2]}}.${{toParts[1]}}.${{toParts[0]}}`;
                }}
            }}
        }}

        // Простая декомпозиция временных рядов
        function simpleDecompose(values, period = 12) {{
            const n = values.length;

            // 1. Тренд (скользящее среднее)
            const trend = [];
            const halfPeriod = Math.floor(period / 2);

            for (let i = 0; i < n; i++) {{
                if (i < halfPeriod || i >= n - halfPeriod) {{
                    trend.push(null);
                }} else {{
                    let sum = 0;
                    for (let j = i - halfPeriod; j <= i + halfPeriod; j++) {{
                        sum += values[j] || 0;
                    }}
                    trend.push(sum / period);
                }}
            }}

            // 2. Детрендированные данные
            const detrended = values.map((v, i) => trend[i] !== null ? v - trend[i] : null);

            // 3. Сезонность (средние по месяцам)
            const seasonalAverages = new Array(period).fill(0);
            const seasonalCounts = new Array(period).fill(0);

            detrended.forEach((val, i) => {{
                if (val !== null) {{
                    const monthIndex = i % period;
                    seasonalAverages[monthIndex] += val;
                    seasonalCounts[monthIndex]++;
                }}
            }});

            for (let i = 0; i < period; i++) {{
                if (seasonalCounts[i] > 0) {{
                    seasonalAverages[i] /= seasonalCounts[i];
                }}
            }}

            // Центрируем сезонность
            const seasonalMean = seasonalAverages.reduce((a, b) => a + b, 0) / period;
            const seasonal = values.map((_, i) => seasonalAverages[i % period] - seasonalMean);

            // 4. Остатки
            const residual = values.map((v, i) => {{
                if (trend[i] !== null) {{
                    return v - trend[i] - seasonal[i];
                }}
                return null;
            }});

            return {{ trend, seasonal, residual }};
        }}

        function update{self.chart_id}() {{
            // Инициализация селекторов при первом вызове
            if (!window.{self.chart_id}_initialized) {{
                initSelectors_{self.chart_id}();
                window.{self.chart_id}_initialized = true;
            }}

            // Используем rawData и фильтруем локально
            const data = window.rawData;

            const storeSelect = document.getElementById('{self.chart_id}_store');
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const typeSelect = document.getElementById('{self.chart_id}_product_type');
            const productSelect = document.getElementById('{self.chart_id}_product');
            const dateFromInput = document.getElementById('{self.chart_id}_date_from');
            const dateToInput = document.getElementById('{self.chart_id}_date_to');

            const modeSelect = document.getElementById('{self.chart_id}_mode');

            const selectedStore = storeSelect.value;
            const selectedMetric = metricSelect.value;
            const selectedType = typeSelect.value;
            const selectedProduct = productSelect.value;
            const selectedMode = modeSelect ? modeSelect.value : 'absolute';
            const dateFrom = dateFromInput.value; // YYYY-MM-DD
            const dateTo = dateToInput.value;

            if (!selectedStore) return;

            // Фильтруем данные по магазину, типу, товару и локальным датам
            const storeData = data.filter(row => {{
                // Фильтр по магазину
                if (row['Магазин'] !== selectedStore) return false;

                // Фильтр по типу товара
                if (selectedType !== 'all' && row['Тип'] !== selectedType) return false;

                // Фильтр по товару
                if (selectedProduct !== 'all' && row['Товар'] !== selectedProduct) return false;

                // Фильтр по локальным датам
                if (dateFrom || dateTo) {{
                    const dateStr = row['Дата'];
                    if (!dateStr) return false;

                    const parts = dateStr.split('.');
                    if (parts.length !== 3) return false;

                    const day = parseInt(parts[0]);
                    const month = parseInt(parts[1]);
                    const year = parseInt(parts[2]);
                    const isoDate = `${{year}}-${{String(month).padStart(2, '0')}}-${{String(day).padStart(2, '0')}}`;

                    if (dateFrom && isoDate < dateFrom) return false;
                    if (dateTo && isoDate > dateTo) return false;
                }}

                return true;
            }});

            // Группировка по месяцам
            const monthlyData = {{}};

            storeData.forEach(row => {{
                const dateStr = row['Дата'];
                if (!dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);
                const periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;

                if (!monthlyData[periodKey]) {{
                    monthlyData[periodKey] = {{
                        revenue: 0,
                        profit: 0,
                        checks: 0,
                        quantity: 0,
                        area: parseFloat(row['Торговая площадь магазина']) || 0
                    }};
                }}

                monthlyData[periodKey].revenue += parseFloat(row['Сумма в чеке']) || 0;
                monthlyData[periodKey].profit += parseFloat(row['Наценка продажи в чеке']) || 0;
                // Используем хелпер для корректного подсчёта чеков (группировка по магазину)
                monthlyData[periodKey].checks += getChecksValue(row, 'Магазин');
                monthlyData[periodKey].quantity += parseFloat(row['Количество в чеке']) || 0;
            }});

            // Сортируем по датам
            const periods = Object.keys(monthlyData).sort((a, b) => {{
                const [d1, m1, y1] = a.split('.');
                const [d2, m2, y2] = b.split('.');
                return (parseInt(y1) * 12 + parseInt(m1)) - (parseInt(y2) * 12 + parseInt(m2));
            }});

            // Вычисляем метрику
            const values = periods.map(p => {{
                const d = monthlyData[p];
                switch (selectedMetric) {{
                    case 'Сумма в чеке': return d.revenue;
                    case 'Число чеков': return d.checks;
                    case 'Количество в чеке': return d.quantity;
                    case 'Наценка продажи в чеке': return d.profit;
                    case 'revenue_per_m2': return d.area > 0 ? d.revenue / d.area : 0;
                    case 'profit_per_m2': return d.area > 0 ? d.profit / d.area : 0;
                    case 'margin': return d.revenue > 0 ? (d.profit / d.revenue) * 100 : 0;
                    default: return d.revenue;
                }}
            }});

            // Декомпозиция
            const {{ trend, seasonal, residual }} = simpleDecompose(values, 12);

            // Расчёт процентного вклада каждой компоненты (через дисперсию)
            function calcVariance(arr) {{
                const validVals = arr.filter(v => v !== null);
                if (validVals.length === 0) return 0;
                const mean = validVals.reduce((a, b) => a + b, 0) / validVals.length;
                return validVals.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / validVals.length;
            }}

            const varOriginal = calcVariance(values);
            const varTrend = calcVariance(trend);
            const varSeasonal = calcVariance(seasonal);
            const varResidual = calcVariance(residual);

            // Сумма дисперсий компонент (для нормировки)
            const totalVar = varTrend + varSeasonal + varResidual;

            const pctTrend = totalVar > 0 ? (varTrend / totalVar * 100).toFixed(1) : 0;
            const pctSeasonal = totalVar > 0 ? (varSeasonal / totalVar * 100).toFixed(1) : 0;
            const pctResidual = totalVar > 0 ? (varResidual / totalVar * 100).toFixed(1) : 0;

            // R² - доля объяснённой дисперсии (тренд + сезонность)
            const r2 = totalVar > 0 ? ((varTrend + varSeasonal) / totalVar * 100).toFixed(1) : 0;

            const metricNames = {{
                'Сумма в чеке': 'Сумма в чеке',
                'Число чеков': 'Число чеков',
                'Количество в чеке': 'Количество в чеке',
                'Наценка продажи в чеке': 'Наценка продажи в чеке',
                'revenue_per_m2': 'Выручка на м²',
                'profit_per_m2': 'Прибыль на м²',
                'margin': 'Маржинальность (%)'
            }};

            const metricName = metricNames[selectedMetric] || selectedMetric;

            // Сохраняем данные для модального окна
            window.{self.chart_id}_decompositionData = {{
                store: selectedStore,
                metric: metricName,
                periods: periods,
                values: values,
                trend: trend,
                seasonal: seasonal,
                residual: residual,
                varTrend: varTrend,
                varSeasonal: varSeasonal,
                varResidual: varResidual,
                totalVar: totalVar,
                pctTrend: parseFloat(pctTrend),
                pctSeasonal: parseFloat(pctSeasonal),
                pctResidual: parseFloat(pctResidual),
                r2: parseFloat(r2)
            }};

            // Добавляем информацию о фильтрах в заголовок
            let titleSuffix = '';
            if (selectedType !== 'all') titleSuffix += ` | ${{selectedType}}`;
            if (selectedProduct !== 'all') titleSuffix += ` | ${{selectedProduct}}`;

            // Заголовок с R² в режиме процентов
            let chartTitle = `Декомпозиция: ${{metricName}} - ${{selectedStore}}${{titleSuffix}}`;
            if (selectedMode === 'percent') {{
                chartTitle += ` | Точность модели (R²): ${{r2}}%`;
            }}

            // Подготовка данных в зависимости от режима
            let yValues, yTrend, ySeasonal, yResidual;
            let yAxisTitles;

            if (selectedMode === 'percent') {{
                // В режиме процентов показываем вклад в дисперсию
                yValues = values;
                yTrend = trend;
                ySeasonal = seasonal;
                yResidual = residual;
                yAxisTitles = {{
                    y1: 'Исходные',
                    y2: `Тренд (${{pctTrend}}%)`,
                    y3: `Сезонность (${{pctSeasonal}}%)`,
                    y4: `Остатки (${{pctResidual}}%)`
                }};
            }} else {{
                yValues = values;
                yTrend = trend;
                ySeasonal = seasonal;
                yResidual = residual;
                yAxisTitles = {{
                    y1: 'Исходные',
                    y2: 'Тренд',
                    y3: 'Сезонность',
                    y4: 'Остатки'
                }};
            }}

            // 4 субплота - скрываем подписи X на первых 3
            const trace1 = {{
                x: periods,
                y: yValues,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Исходные данные',
                line: {{ color: '#2E86AB', width: 2 }},
                marker: {{ size: 6 }},
                xaxis: 'x1',
                yaxis: 'y1'
            }};

            const trace2 = {{
                x: periods,
                y: yTrend,
                type: 'scatter',
                mode: 'lines',
                name: 'Тренд',
                line: {{ color: '#A23B72', width: 3 }},
                xaxis: 'x2',
                yaxis: 'y2'
            }};

            const trace3 = {{
                x: periods,
                y: ySeasonal,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Сезонность',
                line: {{ color: '#F18F01', width: 2 }},
                marker: {{ size: 5 }},
                fill: 'tozeroy',
                xaxis: 'x3',
                yaxis: 'y3'
            }};

            const trace4 = {{
                x: periods,
                y: yResidual,
                type: 'scatter',
                mode: 'markers',
                name: 'Остатки',
                marker: {{ color: '#C73E1D', size: 5 }},
                xaxis: 'x4',
                yaxis: 'y4'
            }};

            const layout = {{
                title: chartTitle,
                grid: {{ rows: 4, columns: 1, pattern: 'independent', roworder: 'top to bottom' }},
                height: 750,
                showlegend: false,
                margin: {{ t: 50, b: 60, l: 80, r: 30 }},
                // Первые 3 графика без подписей X
                xaxis: {{
                    type: 'category',
                    showticklabels: false,
                    showgrid: true,
                    gridcolor: '#eee'
                }},
                xaxis2: {{
                    type: 'category',
                    showticklabels: false,
                    showgrid: true,
                    gridcolor: '#eee'
                }},
                xaxis3: {{
                    type: 'category',
                    showticklabels: false,
                    showgrid: true,
                    gridcolor: '#eee'
                }},
                // Только нижний график с подписями
                xaxis4: {{
                    title: 'Период',
                    type: 'category',
                    showticklabels: true,
                    tickangle: -45,
                    tickfont: {{ size: 10 }},
                    showgrid: true,
                    gridcolor: '#eee'
                }},
                yaxis: {{ title: yAxisTitles.y1, titlefont: {{ size: 12 }} }},
                yaxis2: {{ title: yAxisTitles.y2, titlefont: {{ size: 12 }} }},
                yaxis3: {{ title: yAxisTitles.y3, titlefont: {{ size: 12 }} }},
                yaxis4: {{ title: yAxisTitles.y4, titlefont: {{ size: 12 }} }}
            }};

            Plotly.newPlot('{self.chart_id}', [trace1, trace2, trace3, trace4], layout, {{responsive: true}});

            // Обновляем таблицу если открыта
            const tableDiv = document.getElementById('{self.chart_id}_table');
            if (tableDiv && tableDiv.style.display !== 'none') {{
                generateTable_{self.chart_id}();
            }}
        }}

        function getTableData_{self.chart_id}() {{
            const data = window.rawData;
            const storeSelect = document.getElementById('{self.chart_id}_store');
            const metricSelect = document.getElementById('{self.chart_id}_metric');
            const typeSelect = document.getElementById('{self.chart_id}_product_type');
            const productSelect = document.getElementById('{self.chart_id}_product');
            const dateFromInput = document.getElementById('{self.chart_id}_date_from');
            const dateToInput = document.getElementById('{self.chart_id}_date_to');

            const selectedStore = storeSelect.value;
            const selectedMetric = metricSelect.value;
            const selectedType = typeSelect.value;
            const selectedProduct = productSelect.value;
            const dateFrom = dateFromInput.value;
            const dateTo = dateToInput.value;

            if (!selectedStore) return [];

            const storeData = data.filter(row => {{
                if (row['Магазин'] !== selectedStore) return false;
                if (selectedType !== 'all' && row['Тип'] !== selectedType) return false;
                if (selectedProduct !== 'all' && row['Товар'] !== selectedProduct) return false;

                if (dateFrom || dateTo) {{
                    const dateStr = row['Дата'];
                    if (!dateStr) return false;

                    const parts = dateStr.split('.');
                    if (parts.length !== 3) return false;

                    const day = parseInt(parts[0]);
                    const month = parseInt(parts[1]);
                    const year = parseInt(parts[2]);
                    const isoDate = `${{year}}-${{String(month).padStart(2, '0')}}-${{String(day).padStart(2, '0')}}`;

                    if (dateFrom && isoDate < dateFrom) return false;
                    if (dateTo && isoDate > dateTo) return false;
                }}

                return true;
            }});

            const monthlyData = {{}};

            storeData.forEach(row => {{
                const dateStr = row['Дата'];
                if (!dateStr) return;

                const parts = dateStr.split('.');
                if (parts.length !== 3) return;

                const month = parseInt(parts[1]);
                const year = parseInt(parts[2]);
                const periodKey = `01.${{String(month).padStart(2, '0')}}.${{year}}`;

                if (!monthlyData[periodKey]) {{
                    monthlyData[periodKey] = {{
                        revenue: 0,
                        profit: 0,
                        checks: 0,
                        quantity: 0,
                        area: parseFloat(row['Торговая площадь магазина']) || 0
                    }};
                }}

                monthlyData[periodKey].revenue += parseFloat(row['Сумма в чеке']) || 0;
                monthlyData[periodKey].profit += parseFloat(row['Наценка продажи в чеке']) || 0;
                // Используем хелпер для корректного подсчёта чеков (группировка по магазину)
                monthlyData[periodKey].checks += getChecksValue(row, 'Магазин');
                monthlyData[periodKey].quantity += parseFloat(row['Количество в чеке']) || 0;
            }});

            const periods = Object.keys(monthlyData).sort((a, b) => {{
                const [d1, m1, y1] = a.split('.');
                const [d2, m2, y2] = b.split('.');
                return (parseInt(y1) * 12 + parseInt(m1)) - (parseInt(y2) * 12 + parseInt(m2));
            }});

            const values = periods.map(p => {{
                const d = monthlyData[p];
                switch (selectedMetric) {{
                    case 'Сумма в чеке': return d.revenue;
                    case 'Число чеков': return d.checks;
                    case 'Количество в чеке': return d.quantity;
                    case 'Наценка продажи в чеке': return d.profit;
                    case 'revenue_per_m2': return d.area > 0 ? d.revenue / d.area : 0;
                    case 'profit_per_m2': return d.area > 0 ? d.profit / d.area : 0;
                    case 'margin': return d.revenue > 0 ? (d.profit / d.revenue) * 100 : 0;
                    default: return d.revenue;
                }}
            }});

            const {{ trend, seasonal, residual }} = simpleDecompose(values, 12);

            return periods.map((period, i) => ({{
                'Период': period,
                'Значение': Math.round(values[i] * 100) / 100,
                'Тренд': trend[i] !== null ? Math.round(trend[i] * 100) / 100 : null,
                'Сезонность': Math.round(seasonal[i] * 100) / 100,
                'Остатки': residual[i] !== null ? Math.round(residual[i] * 100) / 100 : null
            }}));
        }}
        """
