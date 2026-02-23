#!/usr/bin/env python3
"""
Ozon Reviews AI Generator
Экспортирует отзывы и генерирует AI-ответы через OpenClaw
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict

WORKSPACE = Path("/home/firstvds/.openclaw/workspace")
SKILL_DIR = WORKSPACE / "skills" / "ozon-reviews-workflow"
OUTPUT_DIR = WORKSPACE / "tmp_files" / "ozon-reviews-workflow"

# Создаем директорию если не существует
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_env():
    """Загружает .env"""
    env_path = WORKSPACE / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    k, v = line.strip().split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"""'))

def get_reviews_from_api(limit: int = 50, rating_min: int = 4, rating_max: int = 5) -> List[Dict]:
    """Получает отзывы из Ozon API"""
    import requests
    
    load_env()
    
    headers = {
        "Client-Id": os.environ.get("OZON_CLIENT_ID"),
        "Api-Key": os.environ.get("OZON_API_KEY"),
        "Content-Type": "application/json"
    }
    
    r = requests.post(
        "https://api-seller.ozon.ru/v1/review/list",
        headers=headers,
        json={"limit": max(20, min(limit, 100)), "sort_dir": "DESC"},
        timeout=30
    )
    r.raise_for_status()
    
    reviews = r.json().get("reviews", [])
    
    # Фильтр: 4-5★ + UNPROCESSED + с текстом
    filtered = [
        r for r in reviews
        if r.get("status") == "UNPROCESSED"
        and rating_min <= r.get("rating", 0) <= rating_max
        and r.get("text", "").strip()
    ]
    
    return filtered

def load_company_policy() -> str:
    """Загружает правила компании"""
    policy_path = SKILL_DIR / "references" / "company-policy.md"
    if policy_path.exists():
        with open(policy_path) as f:
            return f.read()
    return ""

def generate_ai_reviews_file(reviews: List[Dict]) -> str:
    """Создает файл для AI-обработки"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"ai_reviews_4_5_{timestamp}.json"
    filepath = OUTPUT_DIR / filename
    
    # Добавляем поле для AI-ответа
    for review in reviews:
        review["ai_reply"] = ""
    
    with open(filepath, "w") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    
    return str(filepath)

def create_prompt_for_ai(reviews_file: str, policy: str) -> str:
    """Создает промпт для AI"""
    with open(reviews_file) as f:
        reviews = json.load(f)
    
    if not reviews:
        return ""
    
    prompt = f"""Сгенерируй персонализированные ответы на отзывы Ozon.

## ⚠️ КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА КОМПАНИИ:
{policy}

## Отзывы для обработки:
"""
    
    for i, review in enumerate(reviews, 1):
        prompt += f"""
{i}. ID: {review['id']}
   Рейтинг: {review['rating']}★
   Текст: {review['text']}
   SKU: {review.get('sku', 'N/A')}
"""
    
    prompt += f"""

## Требования к ответам:
1. Каждый ответ должен быть уникальным и персонализированным
2. Учитывай содержание отзыва (упоминание конкретных продуктов, эмоции)
3. Используй эмодзи уместно
4. **СТРОГО** соблюдай правила компании - никаких возвратов/компенсаций
5. Если проблема с упаковкой/доставкой - направляй в Ozon
6. Если товар не подошел - предлагай консультацию по применению
7. Тон: вежливый, профессиональный, сочувствующий

## Формат ответа:
Верни JSON массив с полем "ai_reply" для каждого отзыва:
```json
[
  {{"id": "...", "ai_reply": "..."}},
  ...
]
```

Файл с отзывами: {reviews_file}
Сохрани результат в файл с суффиксом "_replied.json"
"""
    
    return prompt

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Export Ozon reviews for AI processing")
    parser.add_argument("--limit", type=int, default=20, help="Max reviews to export")
    parser.add_argument("--dry-run", action="store_true", help="Only export, don't process")
    
    args = parser.parse_args()
    
    print("=== Ozon Reviews AI Generator ===\n")
    
    # 1. Получаем отзывы
    print("Fetching reviews from Ozon API...")
    reviews = get_reviews_from_api(limit=args.limit)
    
    if not reviews:
        print("No unprocessed 4-5★ reviews with text found.")
        return
    
    print(f"Found {len(reviews)} reviews to process\n")
    
    # 2. Создаем файл
    reviews_file = generate_ai_reviews_file(reviews)
    print(f"✓ Exported to: {reviews_file}")
    
    # 3. Загружаем политику
    policy = load_company_policy()
    
    # 4. Создаем промпт
    prompt = create_prompt_for_ai(reviews_file, policy)
    
    # 5. Сохраняем промпт
    prompt_file = OUTPUT_DIR / f"ai_prompt_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(prompt_file, "w") as f:
        f.write(prompt)
    
    print(f"✓ Prompt saved to: {prompt_file}")
    
    if args.dry_run:
        print("\n[DRY RUN] Reviews exported. AI processing skipped.")
        print(f"\nTo process with AI, send the prompt to OpenClaw.")
        return
    
    # 6. Выводим инструкцию
    print("\n" + "="*60)
    print("СЛЕДУЮЩИЙ ШАГ:")
    print("="*60)
    print(f"\n1. Отправь файл AI для генерации ответов:")
    print(f"   {reviews_file}")
    print(f"\n2. Или используй промпт:")
    print(f"   {prompt_file}")
    print(f"\n3. После получения ответов - импортируй:")
    print(f"   python3 {SKILL_DIR}/scripts/ai_reply.py --import-file [файл]_replied.json")

if __name__ == "__main__":
    main()
