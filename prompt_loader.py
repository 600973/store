# PROJECT_ROOT: prompt_loader.py
import json
import os


def load_prompts():
    """Загрузка промптов из JSON"""
    prompts_file = 'prompts.json'

    if os.path.exists(prompts_file):
        with open(prompts_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {}


def get_prompts_js():
    """Генерация JS объекта с промптами"""
    prompts = load_prompts()
    return json.dumps(prompts, ensure_ascii=False)