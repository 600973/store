# PROJECT_ROOT: context_builder.py
"""
Построение контекста для AI-анализа графиков
Поддерживает 3 уровня контекста:
1. Общий контекст компании
2. Активные фильтры
3. Ключевые метрики дашборда
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional


class AnalysisContext:
    """Формирование многоуровневого контекста для AI-анализа"""
    
    def __init__(self, df_full: pd.DataFrame, context_config: Optional[Dict[str, bool]] = None):
        """
        Args:
            df_full: Полный датафрейм (без фильтров)
            context_config: Конфигурация уровней контекста
                {
                    'company_context': True,
                    'filters_context': True,
                    'dashboard_metrics': True
                }
        """
        self.df_full = df_full
        self.df_filtered = df_full  # По умолчанию = полный датафрейм
        self.active_filters = {}
        self.dashboard_metrics = {}
        
        # Конфигурация по умолчанию: все включено
        self.config = {
            'company_context': True,
            'filters_context': True,
            'dashboard_metrics': True
        }
        
        if context_config:
            self.config.update(context_config)
    
    def update_filtered_data(self, df_filtered: pd.DataFrame, active_filters: Dict[str, Any]):
        """
        Обновить отфильтрованные данные и информацию о фильтрах
        Вызывается при изменении глобальных фильтров
        """
        self.df_filtered = df_filtered
        self.active_filters = active_filters
    
    def set_dashboard_metrics(self, metrics: Dict[str, Any]):
        """
        Сохранить ключевые метрики с других графиков
        
        Args:
            metrics: Словарь с метриками, например:
                {
                    'headcount_current': 1234,
                    'headcount_trend': '+5.2%',
                    'turnover_rate': 12.3,
                    'top_problem_departments': ['Отдел А', 'Отдел Б', 'Отдел В'],
                    'critical_months': ['Март 2024', 'Июнь 2024'],
                    'critical_tenure': '3-6 месяцев'
                }
        """
        self.dashboard_metrics = metrics
    
    def build_context(self, chart_name: str = "", chart_specific_config: Optional[Dict[str, bool]] = None) -> str:
        """
        Собрать полный контекст для конкретного графика
        
        Args:
            chart_name: Название графика для заголовка
            chart_specific_config: Переопределение конфига для конкретного графика
                Если None - используется общий конфиг
        
        Returns:
            Строка с контекстом
        """
        # Используем специфичный конфиг или общий
        config = self.config.copy()
        if chart_specific_config:
            config.update(chart_specific_config)
        
        context_parts = []
        
        # Уровень 1: Общий контекст компании
        if config.get('company_context', True):
            company_ctx = self._build_company_context()
            if company_ctx:
                context_parts.append(company_ctx)
        
        # Уровень 2: Активные фильтры
        if config.get('filters_context', True):
            filters_ctx = self._build_filters_context()
            if filters_ctx:
                context_parts.append(filters_ctx)
        
        # Уровень 3: Метрики дашборда
        if config.get('dashboard_metrics', True) and self.dashboard_metrics:
            metrics_ctx = self._build_dashboard_metrics()
            if metrics_ctx:
                context_parts.append(metrics_ctx)
        
        # Если есть хоть один уровень контекста, добавляем разделитель
        if context_parts:
            context_parts.append("---")
        
        # Заголовок для данных графика
        if chart_name:
            context_parts.append(f"📈 ДАННЫЕ ТЕКУЩЕГО ГРАФИКА ({chart_name}):")
        
        return "\n\n".join(context_parts)
    
    def _build_company_context(self) -> str:
        """Построить контекст уровня 1: Общая информация о компании"""
        if self.df_full.empty:
            return ""
        
        # Текущая численность (последняя дата или на момент "сейчас")
        active_employees = self.df_full[self.df_full['Дата увольнения'].isna()]
        current_headcount = len(active_employees)
        
        # Период данных
        hire_dates = self.df_full['Дата приема'].dropna()
        dismissal_dates = self.df_full['Дата увольнения'].dropna()
        
        if not hire_dates.empty:
            date_from = hire_dates.min().strftime('%d.%m.%Y')
            date_to = datetime.now().strftime('%d.%m.%Y')
        else:
            date_from = date_to = "Н/Д"
        
        # Общая текучесть за весь период
        total_hired = len(self.df_full[self.df_full['Дата приема'].notna()])
        total_dismissed = len(dismissal_dates)
        
        turnover_rate = 0
        if current_headcount > 0:
            # Упрощенная формула: (уволенные / средняя численность) * 100
            avg_headcount = (current_headcount + total_dismissed) / 2
            if avg_headcount > 0:
                turnover_rate = round((total_dismissed / avg_headcount) * 100, 1)
        
        # Средний возраст
        avg_age = ""
        if 'Дата рождения' in self.df_full.columns:
            ages = active_employees.apply(
                lambda row: (datetime.now() - row['Дата рождения']).days / 365.25 
                if pd.notna(row['Дата рождения']) else None,
                axis=1
            ).dropna()
            if not ages.empty:
                avg_age = f"{round(ages.mean(), 1)} лет"
        
        # Средний стаж
        avg_tenure = ""
        if 'Дата приема' in self.df_full.columns:
            tenures = active_employees.apply(
                lambda row: (datetime.now() - row['Дата приема']).days / 30.44 
                if pd.notna(row['Дата приема']) else None,
                axis=1
            ).dropna()
            if not tenures.empty:
                avg_tenure_months = round(tenures.mean(), 1)
                avg_tenure = f"{avg_tenure_months} месяцев"
        
        context = f"""🏢 ОБЩИЙ КОНТЕКСТ КОМПАНИИ:
• Общая численность: {current_headcount} человек (на текущий момент)
• Текучесть за период: {turnover_rate}% (Уволено: {total_dismissed} / Принято: {total_hired})"""
        
        if avg_age:
            context += f"\n• Средний возраст сотрудников: {avg_age}"
        
        if avg_tenure:
            context += f"\n• Средний стаж: {avg_tenure}"
        
        context += f"\n• Период данных: с {date_from} по {date_to}"
        
        return context
    
    def _build_filters_context(self) -> str:
        """Построить контекст уровня 2: Активные фильтры"""
        if not self.active_filters:
            # Если фильтры не применены
            total_records = len(self.df_full)
            return f"""🔍 АКТИВНЫЕ ФИЛЬТРЫ:
• Фильтры: не применены (анализируются все данные)
→ Охват выборки: {total_records} записей (100% от всех данных)"""
        
        # Формируем список примененных фильтров
        filter_lines = []
        for key, value in self.active_filters.items():
            if value:  # Если фильтр не пустой
                if isinstance(value, list):
                    if len(value) == 0:
                        continue
                    elif len(value) <= 3:
                        filter_lines.append(f"• {key}: {', '.join(map(str, value))}")
                    else:
                        filter_lines.append(f"• {key}: {', '.join(map(str, value[:3]))}... (+{len(value)-3})")
                elif isinstance(value, dict) and 'from' in value and 'to' in value:
                    # Диапазон дат
                    filter_lines.append(f"• {key}: с {value['from']} по {value['to']}")
                else:
                    filter_lines.append(f"• {key}: {value}")
        
        if not filter_lines:
            filter_lines.append("• Фильтры: не применены (анализируются все данные)")
        
        # Процент охвата
        total_records = len(self.df_full)
        filtered_records = len(self.df_filtered)
        coverage_percent = round((filtered_records / total_records * 100), 1) if total_records > 0 else 0
        
        filters_str = "\n".join(filter_lines)
        
        return f"""🔍 АКТИВНЫЕ ФИЛЬТРЫ:
{filters_str}
→ Охват выборки: {filtered_records} записей из {total_records} общих ({coverage_percent}%)"""
    
    def _build_dashboard_metrics(self) -> str:
        """Построить контекст уровня 3: Ключевые метрики дашборда"""
        if not self.dashboard_metrics:
            return ""
        
        metrics_lines = []
        
        # Динамика численности
        if 'headcount_current' in self.dashboard_metrics:
            line = f"• Текущая численность: {self.dashboard_metrics['headcount_current']}"
            if 'headcount_trend' in self.dashboard_metrics:
                line += f" (тренд: {self.dashboard_metrics['headcount_trend']})"
            metrics_lines.append(line)
        
        # Текучесть
        if 'turnover_rate' in self.dashboard_metrics:
            metrics_lines.append(f"• Коэффициент текучести: {self.dashboard_metrics['turnover_rate']}%")
        
        # Проблемные подразделения
        if 'top_problem_departments' in self.dashboard_metrics:
            depts = self.dashboard_metrics['top_problem_departments']
            if depts:
                depts_str = ', '.join(depts[:3])
                metrics_lines.append(f"• Топ проблемных подразделений: {depts_str}")
        
        # Критические периоды
        if 'critical_months' in self.dashboard_metrics:
            months = self.dashboard_metrics['critical_months']
            if months:
                months_str = ', '.join(months[:3])
                metrics_lines.append(f"• Критические периоды увольнений: {months_str}")
        
        # Критический стаж
        if 'critical_tenure' in self.dashboard_metrics:
            metrics_lines.append(f"• Критический период стажа: {self.dashboard_metrics['critical_tenure']}")
        
        # Баланс найма/увольнений
        if 'balance' in self.dashboard_metrics:
            metrics_lines.append(f"• Баланс найма/увольнений: {self.dashboard_metrics['balance']}")
        
        if not metrics_lines:
            # Создаем пустую секцию, которая будет заполнена динамически в JS
            return """📊 КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ ДАШБОРДА:
• Рассчитываются динамически при применении фильтров"""
        
        metrics_str = "\n".join(metrics_lines)
        
        return f"""📊 КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ ДАШБОРДА:
{metrics_str}"""
    
    def get_context_for_js(self) -> str:
        """
        Получить контекст в формате для JS (для динамического обновления)
        Возвращает JSON-сериализуемый словарь
        """
        import json
        
        context_data = {
            'company': {},
            'filters': {},
            'metrics': {}
        }
        
        # Компания
        if self.config.get('company_context', True):
            active_employees = self.df_full[self.df_full['Дата увольнения'].isna()]
            context_data['company'] = {
                'headcount': len(active_employees),
                'total_dismissed': len(self.df_full[self.df_full['Дата увольнения'].notna()]),
                'total_hired': len(self.df_full[self.df_full['Дата приема'].notna()])
            }
        
        # Фильтры
        if self.config.get('filters_context', True):
            context_data['filters'] = {
                'active': self.active_filters,
                'coverage': {
                    'filtered': len(self.df_filtered),
                    'total': len(self.df_full),
                    'percent': round((len(self.df_filtered) / len(self.df_full) * 100), 1) if len(self.df_full) > 0 else 0
                }
            }
        
        # Метрики
        if self.config.get('dashboard_metrics', True):
            context_data['metrics'] = self.dashboard_metrics
        
        return json.dumps(context_data, ensure_ascii=False, default=str)

