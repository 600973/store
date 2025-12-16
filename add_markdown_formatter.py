#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Скрипт для добавления функции форматирования Markdown и замены .textContent на .innerHTML"""

import re

# Читаем файл
with open('store_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Добавляем функцию formatMarkdown после updateMetricDelta
markdown_function = '''
        // ============================================================================
        // MARKDOWN ФОРМАТИРОВАНИЕ
        // ============================================================================

        function formatMarkdown(text) {
            if (!text) return '';

            let html = text;

            // Заголовки
            html = html.replace(/^### (.*$)/gim, '<h3 style="margin: 10px 0 8px 0; font-size: 14px;">$1</h3>');
            html = html.replace(/^## (.*$)/gim, '<h2 style="margin: 12px 0 10px 0; font-size: 16px;">$1</h2>');
            html = html.replace(/^# (.*$)/gim, '<h1 style="margin: 14px 0 12px 0; font-size: 18px;">$1</h1>');

            // Жирный текст (экранируем звездочки правильно)
            html = html.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');

            // Курсив (одна звездочка, но не две подряд)
            html = html.replace(/(?<!\\*)\\*(?!\\*)(.+?)\\*(?!\\*)/g, '<em>$1</em>');

            // Списки
            html = html.replace(/^[\\*\\-] (.+)$/gim, '<li>$1</li>');
            html = html.replace(/((?:<li>.*?<\\/li>\\s*)+)/gims, '<ul style="margin: 8px 0; padding-left: 20px;">$1</ul>');

            // Переносы строк
            html = html.replace(/\\n\\n/g, '<br><br>');
            html = html.replace(/\\n/g, '<br>');

            return html;
        }
'''

# Находим позицию после updateMetricDelta
pattern = r'(function updateMetricDelta\(elementId, current, previous\) \{[^}]+\})\s*\n'
match = re.search(pattern, content, re.DOTALL)

if match:
    insert_pos = match.end()
    content = content[:insert_pos] + '\n' + markdown_function + content[insert_pos:]
    print("[OK] Funktsiya formatMarkdown dobavlena")
else:
    print("[ERROR] Ne naydena funktsiya updateMetricDelta")

# 2. Заменяем все .textContent = data.response на .innerHTML = formatMarkdown(data.response)
# Используем двойные кавычки вместо одинарных
count1 = len(re.findall(r"\.querySelector\(\'\.llm-result-text\'\)\.textContent = data\.response;", content))
content = re.sub(
    r"\.querySelector\(\'\.llm-result-text\'\)\.textContent = data\.response;",
    r".querySelector('.llm-result-text').innerHTML = formatMarkdown(data.response);",
    content
)
print(f"[OK] Zameneno {count1} vyzovov .textContent na .innerHTML (Ollama)")

# 3. Заменяем для LM Studio
count2 = len(re.findall(r"\.querySelector\(\'\.llm-result-text\'\)\.textContent = data\.choices\[0\]\.message\.content;", content))
content = re.sub(
    r"\.querySelector\(\'\.llm-result-text\'\)\.textContent = data\.choices\[0\]\.message\.content;",
    r".querySelector('.llm-result-text').innerHTML = formatMarkdown(data.choices[0].message.content);",
    content
)
print(f"[OK] Zameneno {count2} vyzovov .textContent na .innerHTML (LM Studio)")

# Сохраняем
with open('store_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Fayl sokhranyen")
print("\nGotovo! Teper' otvety LLM budut formatirovat'sya s Markdown")
