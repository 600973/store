#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Финальное исправление Markdown форматирования"""

# Читаем файл
with open('store_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Удаляем старую сломанную функцию formatMarkdown
import re
pattern = r'// ={70,}\s+// MARKDOWN ФОРМАТИРОВАНИЕ.*?function formatMarkdown\(text\) \{.*?\n\s+\}'
content = re.sub(pattern, '', content, flags=re.DOTALL)
print("[OK] Udalena starayafunktsiya")

# Правильная функция - используем raw string
correct_function = r"""
        // ============================================================================
        // MARKDOWN ФОРМАТИРОВАНИЕ
        // ============================================================================

        function formatMarkdown(text) {
            if (!text) return '';
            let html = text;

            // Жирный текст **text**
            html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

            // Курсив *text*
            html = html.replace(/\*([^\*]+?)\*/g, '<em>$1</em>');

            // Заголовки
            html = html.replace(/^### (.+)$/gim, '<h3 style="margin:10px 0 5px 0;font-size:14px">$1</h3>');
            html = html.replace(/^## (.+)$/gim, '<h2 style="margin:12px 0 6px 0;font-size:16px">$1</h2>');
            html = html.replace(/^# (.+)$/gim, '<h1 style="margin:14px 0 7px 0;font-size:18px">$1</h1>');

            // Списки - упрощенный вариант
            html = html.replace(/^[\*\-] (.+)$/gim, '<li style="margin-left:20px">$1</li>');

            // Переводы строк
            html = html.replace(/\n\n/g, '<br><br>');
            html = html.replace(/\n/g, '<br>');

            return html;
        }
"""

# Находим и вставляем после updateMetricDelta
search = """        function updateMetricDelta(elementId, current, previous) {
            const el = document.getElementById(elementId);
            if (!el) return;
            if (!previous || previous === 0 || current === null) {
                el.textContent = '—';
                el.className = 'metric-delta neutral';
                return;
            }
            const delta = ((current - previous) / previous) * 100;
            const sign = delta >= 0 ? '↑' : '↓';
            el.textContent = `${sign} ${Math.abs(delta).toFixed(1).replace('.', ',')}%`;
            el.className = `metric-delta ${delta >= 0 ? 'positive' : 'negative'}`;
        }"""

if search in content:
    content = content.replace(search, search + '\n' + correct_function)
    print("[OK] Dobavlena novaya funktsiya formatMarkdown")
else:
    print("[ERROR] Ne naydena funktsiya updateMetricDelta")

# Сохраняем
with open('store_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Gotovo!")
