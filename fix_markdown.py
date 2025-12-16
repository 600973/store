#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Простой скрипт для добавления Markdown форматирования"""

# Читаем файл
with open('store_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Функция для форматирования Markdown
js_function = """
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

            // Списки
            html = html.replace(/^[\*\-] (.+)$/gim, '<li>$1</li>');
            html = html.replace(/<li>/g, '<ul style="margin:5px 0;padding-left:20px"><li>').replace(/<\/li>(?!<li>)/g, '</li></ul>');

            // Переводы строк
            html = html.replace(/\n\n/g, '<br><br>');
            html = html.replace(/\n/g, '<br>');

            return html;
        }
"""

# Находим место после updateMetricDelta и вставляем
search_text = """        function updateMetricDelta(elementId, current, previous) {
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

if search_text in content:
    content = content.replace(search_text, search_text + '\n' + js_function)
    print("[OK] Funktsiya formatMarkdown dobavlena")
else:
    print("[ERROR] Ne naydena funktsiya updateMetricDelta")

# Заменяем .textContent на .innerHTML с formatMarkdown
content = content.replace(
    ".querySelector('.llm-result-text').textContent = data.response;",
    ".querySelector('.llm-result-text').innerHTML = formatMarkdown(data.response);"
)
content = content.replace(
    ".querySelector('.llm-result-text').textContent = data.choices[0].message.content;",
    ".querySelector('.llm-result-text').innerHTML = formatMarkdown(data.choices[0].message.content);"
)

print("[OK] Zameneny .textContent na .innerHTML")

# Сохраняем
with open('store_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Gotovo!")
