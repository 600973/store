#!/usr/bin/env python3
# PROJECT_ROOT: tree_generator_enhanced.py
# -*- coding: utf-8 -*-
"""
Генератор структуры проекта с расширенной аналитикой
Создает текстовое представление структуры директорий с метриками и флажками

# Автоматически сохранится рядом со скриптом
python tree_generator.py .

# Только вывод в консоль
python tree_generator.py . --console

# Указать свой путь
python tree_generator.py . --output=/path/to/file.txt

# С форматом markdown и метриками
python tree_generator.py . --format=markdown --sizes
"""

import os
import sys
import json
import fnmatch
import re
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Set, Dict, Optional, Union
import argparse

# ===============================================
# НАСТРОЙКИ (легко изменяемые)
# ===============================================

# Файлы и папки для исключения (паттерны)
DEFAULT_IGNORE_PATTERNS = {
    # Системные папки
    '.git', '.svn', '.hg', '__pycache__', '.pytest_cache', '.coverage',
    'node_modules', '.npm', 'bower_components', 'rag_env_new', 'archive',
    'docs', 'documentation', 'to do', 'tests',
    
    # Виртуальные окружения
    'venv', '.venv', 'env', '.env', 'virtualenv', '.virtualenv',
    
    # IDE папки
    '.idea', '.vscode', '.eclipse', '.sublime-project', '.sublime-workspace',
    
    # Временные и сборочные папки
    'build', 'dist', 'target', 'out', 'tmp', 'temp', 'logs', 'log',
    '*.egg-info', '.tox',
    
    # Файлы
    '*.pyc', '*.pyo', '*.pyd', '*.log', '*.tmp', '*.cache',
    '.DS_Store', 'Thumbs.db', '*.swp', '*.swo', '*~',
}

# Форматы вывода
OUTPUT_FORMATS = ['tree', 'list', 'json', 'markdown']

# Чувствительные файлы (для флажка безопасности)
SENSITIVE_PATTERNS = [
    '*.key', '*.pem', '*.p12', '*.pfx', '*.cer', '*.crt',
    '.env', '.env.*', '*secret*', '*password*', '*token*',
    'credentials*', 'auth*', '*.sqlite', '*.db'
]

# ===============================================
# ОСНОВНЫЕ КЛАССЫ
# ===============================================

class ProjectStructureGenerator:
    """Генератор структуры проекта с расширенной аналитикой"""
    
    def __init__(self, root_path: str, ignore_patterns: Optional[Set[str]] = None):
        self.root_path = Path(root_path).resolve()
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
        self.stats = {
            'total_dirs': 0,
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'total_lines': 0,
            'empty_files': 0,
            'large_files': 0,
            'old_files': 0,
            'recent_files': 0,
            'todo_count': 0,
            'sensitive_files': 0,
            'executable_files': 0,
            'encoding_stats': {}
        }
        self.file_hashes = {}  # Для поиска дубликатов
        
    def should_ignore(self, path: Path) -> bool:
        """Проверяет, нужно ли игнорировать путь"""
        # Проверяем относительный путь от корня
        try:
            relative_path = path.relative_to(self.root_path)
        except ValueError:
            return True
            
        # Проверяем каждую часть пути
        for part in relative_path.parts:
            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True
                    
        # Проверяем полный относительный путь
        relative_str = str(relative_path)
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(relative_str, pattern):
                return True
                
        return False
        
    def _count_file_lines(self, path: Path) -> Optional[int]:
        """Подсчитывает количество строк в текстовом файле"""
        try:
            # errors='ignore' на случай странной кодировки
            with path.open('r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except (OSError, UnicodeDecodeError):
            return None
            
    def _detect_encoding(self, path: Path) -> str:
        """Определяет кодировку файла"""
        try:
            # Пробуем UTF-8
            with path.open('r', encoding='utf-8') as f:
                f.read(1024)
                return 'utf-8'
        except UnicodeDecodeError:
            try:
                # Пробуем cp1251
                with path.open('r', encoding='cp1251') as f:
                    f.read(1024)
                    return 'cp1251'
            except:
                return 'binary'
        except:
            return 'unknown'
            
    def _count_todos(self, path: Path) -> int:
        """Подсчитывает TODO/FIXME/HACK комментарии"""
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Ищем TODO, FIXME, HACK, XXX, NOTE, WARN
                pattern = r'(TODO|FIXME|HACK|XXX|NOTE|WARN|BUG)\s*[:|\s]'
                matches = re.findall(pattern, content, re.IGNORECASE)
                return len(matches)
        except:
            return 0
            
    def _get_file_hash(self, path: Path, max_size: int = 10 * 1024 * 1024) -> Optional[str]:
        """Вычисляет хеш файла (для файлов до 10MB)"""
        try:
            if path.stat().st_size > max_size:
                return None
            with path.open('rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
            
    def _is_executable(self, path: Path) -> bool:
        """Проверяет, является ли файл исполняемым"""
        try:
            # Для Unix-like систем
            return os.access(path, os.X_OK)
        except:
            return False
            
    def _is_sensitive(self, path: Path) -> bool:
        """Проверяет, содержит ли файл чувствительные данные"""
        name = path.name.lower()
        for pattern in SENSITIVE_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
        
    def _analyze_python_file(self, path: Path) -> Dict:
        """Анализирует Python файл на классы/функции"""
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Подсчет классов и функций
            class_count = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
            func_count = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
            
            # Поиск импортов
            import_count = len(re.findall(r'^(from\s+[\w.]+\s+)?import\s+', content, re.MULTILINE))
            
            return {
                'classes': class_count,
                'functions': func_count,
                'imports': import_count
            }
        except:
            return {}
            
    def collect_structure(self) -> Dict:
        """Собирает структуру проекта"""
        structure = {
            'name': self.root_path.name,
            'path': str(self.root_path),
            'type': 'directory',
            'children': [],
            'size': 0
        }
        
        self._collect_recursive(self.root_path, structure)
        return structure
        
    def _collect_recursive(self, current_path: Path, node: Dict):
        """Рекурсивно собирает структуру с расширенной аналитикой"""
        if not current_path.is_dir():
            return
            
        try:
            items = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return
            
        for item in items:
            if self.should_ignore(item):
                continue
                
            if item.is_dir():
                self.stats['total_dirs'] += 1
                child_node = {
                    'name': item.name,
                    'path': str(item),
                    'type': 'directory',
                    'children': [],
                    'size': 0
                }
                self._collect_recursive(item, child_node)
                node['children'].append(child_node)
                
            elif item.is_file():
                self.stats['total_files'] += 1
                
                try:
                    stat = item.stat()
                    file_size = stat.st_size
                    self.stats['total_size'] += file_size
                    
                    # Проверка на пустой файл
                    if file_size == 0:
                        self.stats['empty_files'] += 1
                        
                    # Проверка на большой файл
                    if file_size > 1024 * 1024:  # > 1MB
                        self.stats['large_files'] += 1
                        
                    # Проверка даты модификации
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    age = datetime.now() - mtime
                    
                    if age > timedelta(days=365):  # Старше года
                        self.stats['old_files'] += 1
                    elif age < timedelta(days=7):  # Изменен в последнюю неделю
                        self.stats['recent_files'] += 1
                        
                    # Статистика по типам файлов
                    ext = item.suffix.lower()
                    self.stats['file_types'][ext] = self.stats['file_types'].get(ext, 0) + 1
                    
                    # Подсчет строк
                    line_count = self._count_file_lines(item)
                    if line_count is not None:
                        self.stats['total_lines'] += line_count
                        
                    # Определение кодировки
                    encoding = self._detect_encoding(item)
                    self.stats['encoding_stats'][encoding] = self.stats['encoding_stats'].get(encoding, 0) + 1
                    
                    # Подсчет TODO
                    todo_count = self._count_todos(item)
                    self.stats['todo_count'] += todo_count
                    
                    # Хеш файла (для поиска дубликатов)
                    file_hash = self._get_file_hash(item)
                    if file_hash:
                        if file_hash in self.file_hashes:
                            duplicate_of = self.file_hashes[file_hash]
                        else:
                            self.file_hashes[file_hash] = str(item)
                            duplicate_of = None
                    else:
                        duplicate_of = None
                        
                    # Проверка на исполняемый файл
                    is_exec = self._is_executable(item)
                    if is_exec:
                        self.stats['executable_files'] += 1
                        
                    # Проверка на чувствительные данные
                    is_sensitive = self._is_sensitive(item)
                    if is_sensitive:
                        self.stats['sensitive_files'] += 1
                        
                    # Анализ Python файлов
                    py_analysis = {}
                    if ext == '.py':
                        py_analysis = self._analyze_python_file(item)
                        
                    child_node = {
                        'name': item.name,
                        'path': str(item),
                        'type': 'file',
                        'size': file_size,
                        'extension': ext,
                        'lines': line_count,
                        'mtime': mtime.isoformat(),
                        'age_days': age.days,
                        'encoding': encoding,
                        'todos': todo_count,
                        'duplicate_of': duplicate_of,
                        'is_executable': is_exec,
                        'is_sensitive': is_sensitive,
                        'py_analysis': py_analysis
                    }
                    node['children'].append(child_node)
                    
                except (OSError, PermissionError):
                    continue
                    
    def _get_file_flags(self, node: Dict) -> str:
        """
        Возвращает набор пиктограмм-флажков для файла:
        - 📏  много строк (>500)
        - 💾  большой файл (>1MB)
        - 🕰️  старый файл (>1 год)
        - ✨  недавно изменен (<7 дней)
        - 🧪  тестовый файл
        - ⚙️  конфигурационный файл
        - 📝  есть TODO/FIXME
        - 🔒  чувствительные данные
        - ⚡  исполняемый файл
        - 📦  пустой файл
        - 🔁  дубликат
        - 🐍  Python с классами/функциями
        """
        flags = []
        
        size = node.get('size') or 0
        lines = node.get('lines')
        name = node.get('name', '').lower()
        ext = node.get('extension', '').lower()
        age = node.get('age_days', 0)
        todos = node.get('todos', 0)
        is_exec = node.get('is_executable', False)
        is_sensitive = node.get('is_sensitive', False)
        duplicate = node.get('duplicate_of')
        py_analysis = node.get('py_analysis', {})
        
        # Приоритетные флажки (предупреждения)
        if is_sensitive:
            flags.append('🔒')
            
        if duplicate:
            flags.append('🔁')
            
        # Размерные метрики
        if size == 0:
            flags.append('📦')
        elif size > 1024 * 1024:  # > 1MB
            flags.append('💾')
            
        if isinstance(lines, int) and lines > 500:
            flags.append('📏')
            
        # Временные метрики
        if age > 365:
            flags.append('🕰️')
        elif age < 7:
            flags.append('✨')
            
        # Тип контента
        if 'test' in name or 'spec' in name:
            flags.append('🧪')
            
        if ext in {'.yml', '.yaml', '.ini', '.cfg', '.conf', '.env', '.json', '.toml', '.xml'}:
            flags.append('⚙️')
            
        if todos > 0:
            flags.append(f'📝{todos}')
            
        if is_exec:
            flags.append('⚡')
            
        # Python анализ
        if py_analysis:
            classes = py_analysis.get('classes', 0)
            funcs = py_analysis.get('functions', 0)
            if classes > 0 or funcs > 0:
                flags.append(f'🐍c{classes}f{funcs}')
                
        return ' '.join(flags) if flags else ''
        
    def _get_file_icon(self, extension: str) -> str:
        """Возвращает иконку для типа файла"""
        icon_map = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.jsx': '⚛️', '.tsx': '⚛️',
            '.html': '🌐', '.css': '🎨', '.scss': '🎨', '.sass': '🎨',
            '.json': '📋', '.xml': '📋', '.yml': '⚙️', '.yaml': '⚙️', '.toml': '⚙️',
            '.md': '📝', '.rst': '📝', '.txt': '📄', '.log': '📜',
            '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📊', '.xlsx': '📊',
            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.mp4': '🎥', '.mp3': '🎵', '.wav': '🎵',
            '.zip': '🗜️', '.tar': '🗜️', '.gz': '🗜️', '.rar': '🗜️',
            '.sql': '🗄️', '.db': '🗄️', '.sqlite': '🗄️',
            '.sh': '🔧', '.bash': '🔧', '.ps1': '🔧', '.bat': '🔧', '.cmd': '🔧',
            '.go': '🐹', '.rs': '🦀', '.java': '☕', '.c': '🔤', '.cpp': '🔤',
            '.php': '🐘', '.rb': '💎', '.swift': '🦉', '.kt': '🟪',
            '.vue': '💚', '.env': '🔐', '.gitignore': '📝', '.dockerfile': '🐳',
        }
        return icon_map.get(extension.lower(), '📄')
        
    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер файла"""
        if size_bytes == 0:
            return "0B"
        units = ['B', 'KB', 'MB', 'GB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        if unit_index == 0:
            return f"{int(size)}{units[unit_index]}"
        else:
            return f"{size:.1f}{units[unit_index]}"
            
    def generate_tree_format(self, structure: Dict, include_sizes: bool = False) -> str:
        """Генерирует ASCII дерево с расширенной информацией"""
        lines = []
        lines.append(f"📁 {structure['name']}/")
        
        def _generate_tree_recursive(node: Dict, prefix: str = "", is_last: bool = True):
            children = node.get('children', [])
            
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                
                # Символы для дерева
                if is_last_child:
                    current_prefix = "└── "
                    next_prefix = prefix + "    "
                else:
                    current_prefix = "├── "
                    next_prefix = prefix + "│   "
                    
                # Иконка для типа
                if child['type'] == 'directory':
                    icon = "📁"
                    name_suffix = "/"
                else:
                    icon = self._get_file_icon(child.get('extension', ''))
                    name_suffix = ""
                    
                # Дополнительная информация
                extra_info = ""
                if include_sizes and child['type'] == 'file':
                    parts = []
                    
                    # Размер
                    size_str = self._format_size(child.get('size', 0))
                    parts.append(size_str)
                    
                    # Количество строк
                    line_count = child.get('lines')
                    if isinstance(line_count, int):
                        parts.append(f"{line_count}L")
                        
                    # Кодировка (если не utf-8)
                    encoding = child.get('encoding', 'utf-8')
                    if encoding not in ['utf-8', 'unknown']:
                        parts.append(encoding)
                        
                    extra_info = f" [{', '.join(parts)}]"
                    
                    # Флажки
                    flags = self._get_file_flags(child)
                    if flags:
                        extra_info += f" {flags}"
                        
                line = f"{prefix}{current_prefix}{icon} {child['name']}{name_suffix}{extra_info}"
                lines.append(line)
                
                # Рекурсивно для папок
                if child['type'] == 'directory':
                    _generate_tree_recursive(child, next_prefix, is_last_child)
                    
        _generate_tree_recursive(structure)
        return '\n'.join(lines)
        
    def generate_list_format(self, structure: Dict, include_sizes: bool = False) -> str:
        """Генерирует простой список файлов"""
        lines = []
        
        def _generate_list_recursive(node: Dict, current_path: str = ""):
            for child in node.get('children', []):
                if child['type'] == 'directory':
                    dir_path = f"{current_path}/{child['name']}" if current_path else child['name']
                    lines.append(f"{dir_path}/")
                    _generate_list_recursive(child, dir_path)
                else:
                    file_path = f"{current_path}/{child['name']}" if current_path else child['name']
                    
                    if include_sizes:
                        parts = []
                        parts.append(self._format_size(child.get('size', 0)))
                        
                        line_count = child.get('lines')
                        if isinstance(line_count, int):
                            parts.append(f"{line_count} строк")
                            
                        flags = self._get_file_flags(child)
                        if flags:
                            parts.append(flags)
                            
                        size_info = " (" + ", ".join(parts) + ")"
                        lines.append(f"{file_path}{size_info}")
                    else:
                        lines.append(file_path)
                        
        _generate_list_recursive(structure)
        return '\n'.join(lines)
        
    def generate_json_format(self, structure: Dict) -> str:
        """Генерирует JSON представление"""
        return json.dumps(structure, indent=2, ensure_ascii=False, default=str)
        
    def generate_markdown_format(self, structure: Dict, include_sizes: bool = False) -> str:
        """Генерирует Markdown документ с полной аналитикой"""
        lines = []
        lines.append(f"# 📊 Структура проекта: {structure['name']}")
        lines.append("")
        lines.append(f"**Сгенерировано:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Основная статистика
        lines.append("## 📈 Основная статистика")
        lines.append("| Метрика | Значение |")
        lines.append("|---------|----------|")
        lines.append(f"| **Папок** | {self.stats['total_dirs']} |")
        lines.append(f"| **Файлов** | {self.stats['total_files']} |")
        lines.append(f"| **Общий размер** | {self._format_size(self.stats['total_size'])} |")
        lines.append(f"| **Всего строк кода** | {self.stats['total_lines']:,} |")
        lines.append(f"| **Средний размер файла** | {self._format_size(self.stats['total_size'] // max(self.stats['total_files'], 1))} |")
        lines.append("")
        
        # Дополнительная статистика
        lines.append("## 🎯 Особые метрики")
        lines.append("| Метрика | Количество | Описание |")
        lines.append("|---------|------------|----------|")
        lines.append(f"| 📦 Пустые файлы | {self.stats['empty_files']} | Файлы размером 0 байт |")
        lines.append(f"| 💾 Большие файлы | {self.stats['large_files']} | Файлы больше 1 MB |")
        lines.append(f"| 🕰️ Старые файлы | {self.stats['old_files']} | Не изменялись больше года |")
        lines.append(f"| ✨ Недавно измененные | {self.stats['recent_files']} | Изменены за последнюю неделю |")
        lines.append(f"| 📝 TODO/FIXME | {self.stats['todo_count']} | Найдено пометок в коде |")
        lines.append(f"| 🔒 Чувствительные файлы | {self.stats['sensitive_files']} | Возможные ключи/пароли |")
        lines.append(f"| ⚡ Исполняемые файлы | {self.stats['executable_files']} | Файлы с правами на выполнение |")
        lines.append("")
        
        # Типы файлов
        if self.stats['file_types']:
            lines.append("## 📋 Топ-10 типов файлов")
            lines.append("| Расширение | Количество | Процент |")
            lines.append("|------------|------------|---------|")
            sorted_types = sorted(self.stats['file_types'].items(), key=lambda x: x[1], reverse=True)
            total_files = self.stats['total_files']
            for ext, count in sorted_types[:10]:
                ext_name = ext if ext else "без расширения"
                icon = self._get_file_icon(ext)
                percent = (count / total_files * 100) if total_files > 0 else 0
                lines.append(f"| {icon} **{ext_name}** | {count} | {percent:.1f}% |")
            lines.append("")
            
        # Статистика по кодировкам
        if self.stats['encoding_stats']:
            lines.append("## 🔤 Кодировки файлов")
            lines.append("| Кодировка | Количество |")
            lines.append("|-----------|------------|")
            for encoding, count in sorted(self.stats['encoding_stats'].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {encoding} | {count} |")
            lines.append("")
            
        # Легенда флажков
        lines.append("## 🏷️ Легенда флажков")
        lines.append("")
        lines.append("| Флажок | Значение |")
        lines.append("|--------|----------|")
        lines.append("| 📏 | Файл с большим количеством строк (>500) |")
        lines.append("| 💾 | Большой файл (>1MB) |")
        lines.append("| 🕰️ | Старый файл (не изменялся >1 года) |")
        lines.append("| ✨ | Недавно изменен (<7 дней) |")
        lines.append("| 🧪 | Тестовый файл |")
        lines.append("| ⚙️ | Конфигурационный файл |")
        lines.append("| 📝N | Содержит N пометок TODO/FIXME |")
        lines.append("| 🔒 | Возможно содержит чувствительные данные |")
        lines.append("| ⚡ | Исполняемый файл |")
        lines.append("| 📦 | Пустой файл |")
        lines.append("| 🔁 | Дубликат другого файла |")
        lines.append("| 🐍cNfM | Python файл с N классами и M функциями |")
        lines.append("")
        
        # Структура дерева
        lines.append("## 🌳 Структура проекта")
        lines.append("")
        lines.append("```")
        lines.append(self.generate_tree_format(structure, include_sizes))
        lines.append("```")
        
        return '\n'.join(lines)

# ===============================================
# ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ
# ===============================================

class GitAwareGenerator(ProjectStructureGenerator):
    """Генератор с учетом Git репозитория"""
    
    def __init__(self, root_path: str, ignore_patterns: Optional[Set[str]] = None, only_tracked: bool = False):
        super().__init__(root_path, ignore_patterns)
        self.only_tracked = only_tracked
        self.tracked_files = self._get_tracked_files() if only_tracked else None
        
    def _get_tracked_files(self) -> Set[str]:
        """Получает список отслеживаемых Git файлов"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            tracked = set()
            for line in result.stdout.strip().split('\n'):
                if line:
                    tracked.add(str(self.root_path / line))
            return tracked
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            return set()
            
    def should_ignore(self, path: Path) -> bool:
        """Расширенная проверка с учетом Git"""
        # Базовая проверка
        if super().should_ignore(path):
            return True
            
        # Проверка Git отслеживания
        if self.only_tracked and self.tracked_files is not None:
            if path.is_file() and str(path) not in self.tracked_files:
                return True
                
        return False

# ===============================================
# УТИЛИТА ДЛЯ ОПРЕДЕЛЕНИЯ ПУТИ СКРИПТА
# ===============================================

def get_script_directory() -> Path:
    """Возвращает директорию, где находится скрипт"""
    return Path(__file__).parent.resolve()
    
def generate_default_output_path(format_type: str, project_name: str) -> Path:
    """Генерирует путь для сохранения вывода рядом со скриптом"""
    script_dir = get_script_directory()
    
    # Расширения для разных форматов
    extensions = {
        'tree': '.txt',
        'list': '.txt',
        'json': '.json',
        'markdown': '.md'
    }
    
    ext = extensions.get(format_type, '.txt')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Создаем имя файла: structure_projectname_timestamp.ext
    filename = f"structure_{project_name}_{timestamp}{ext}"
    
    return script_dir / filename

# ===============================================
# ГЛАВНАЯ ФУНКЦИЯ И CLI
# ===============================================

def main():
    """Главная функция с CLI интерфейсом"""
    parser = argparse.ArgumentParser(
        description='Генератор структуры проекта с расширенной аналитикой',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python tree_generator.py .                        # Генерация дерева, сохранение рядом со скриптом
  python tree_generator.py /path/to/project --format=json   # JSON формат
  python tree_generator.py . --output=structure.txt         # Сохранение в указанный файл  
  python tree_generator.py . --git-only                     # Только отслеживаемые Git файлы
  python tree_generator.py . --ignore="*.log,temp"          # Дополнительные исключения
  python tree_generator.py . --console                      # Вывод в консоль без сохранения
  python tree_generator.py . --sizes                        # С размерами и метриками
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Путь к проекту для анализа (по умолчанию: текущая папка)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=OUTPUT_FORMATS,
        default='tree',
        help='Формат вывода (по умолчанию: tree)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Файл для сохранения результата (по умолчанию: автоматически рядом со скриптом)'
    )
    
    parser.add_argument(
        '--console', '-c',
        action='store_true',
        help='Выводить только в консоль, не сохранять в файл'
    )
    
    parser.add_argument(
        '--sizes', '-s',
        action='store_true',
        help='Включить размеры файлов и расширенные метрики в вывод'
    )
    
    parser.add_argument(
        '--git-only', '-g',
        action='store_true',
        help='Показывать только файлы, отслеживаемые Git'
    )
    
    parser.add_argument(
        '--ignore', '-i',
        help='Дополнительные паттерны для исключения (через запятую)'
    )
    
    parser.add_argument(
        '--no-default-ignores',
        action='store_true',
        help='Не использовать стандартные исключения'
    )
    
    args = parser.parse_args()
    
    # Подготавливаем паттерны исключений
    ignore_patterns = set()
    if not args.no_default_ignores:
        ignore_patterns.update(DEFAULT_IGNORE_PATTERNS)
        
    if args.ignore:
        custom_patterns = [p.strip() for p in args.ignore.split(',')]
        ignore_patterns.update(custom_patterns)
        
    # Проверяем путь
    project_path = Path(args.path).resolve()
    if not project_path.exists():
        print(f"❌ Путь не существует: {project_path}")
        return 1
        
    if not project_path.is_dir():
        print(f"❌ Путь не является папкой: {project_path}")
        return 1
        
    # Создаем генератор
    if args.git_only:
        generator = GitAwareGenerator(str(project_path), ignore_patterns, only_tracked=True)
    else:
        generator = ProjectStructureGenerator(str(project_path), ignore_patterns)
        
    print(f"🔍 Анализ проекта: {project_path}")
    print(f"📊 Формат: {args.format}")
    if args.git_only:
        print("📝 Режим: только Git отслеживаемые файлы")
    print("-" * 50)
    
    # Собираем структуру
    structure = generator.collect_structure()
    
    # Генерируем вывод
    if args.format == 'tree':
        output = generator.generate_tree_format(structure, args.sizes)
    elif args.format == 'list':
        output = generator.generate_list_format(structure, args.sizes)
    elif args.format == 'json':
        output = generator.generate_json_format(structure)
    elif args.format == 'markdown':
        output = generator.generate_markdown_format(structure, args.sizes)
        
    # Добавляем заголовок для консольного вывода
    if args.format != 'json':
        header = f"\n📁 Структура проекта: {project_path.name}\n"
        header += f"📊 Папок: {generator.stats['total_dirs']}, "
        header += f"Файлов: {generator.stats['total_files']}, "
        header += f"Размер: {generator._format_size(generator.stats['total_size'])}\n"
        header += f"📝 Строк кода: {generator.stats['total_lines']:,}, "
        header += f"TODO: {generator.stats['todo_count']}, "
        header += f"🔒 Чувствительных: {generator.stats['sensitive_files']}\n"
        header += "=" * 60 + "\n"
        output_with_header = header + output
    else:
        output_with_header = output
        
    # Определяем, куда сохранять
    if args.console:
        # Только консоль
        print(output_with_header)
    else:
        # Определяем путь для сохранения
        if args.output:
            output_path = Path(args.output)
        else:
            # Автоматически рядом со скриптом
            output_path = generate_default_output_path(args.format, project_path.name)
            
        # Сохраняем файл
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_with_header)
                
            print(f"✅ Структура сохранена в: {output_path}")
            print(f"📁 Абсолютный путь: {output_path.resolve()}")
            
            # Также выводим в консоль
            print("\n" + output_with_header)
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении файла: {e}")
            print("\n📄 Вывод в консоль:")
            print(output_with_header)
            return 1
            
    return 0
    
if __name__ == "__main__":
    exit(main())
