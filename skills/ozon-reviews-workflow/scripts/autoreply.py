#!/usr/bin/env python3
"""
Ozon 5-Star Auto-Reply v2
Автоматические ответы на 5-звёздочные отзывы
- Без текста
- С фото (и текстом)
Сортировка: от новых к старым (DESC)
"""

import json
import os
import sys
import time
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests

BASE_URL = "https://api-seller.ozon.ru"

# Шаблоны для отзывов без фото
TEMPLATES_TEXT = [
    "Здравствуйте! Благодарим за высокую оценку 🙏 Рады, что товар вам понравился!",
    "Добрый день! Спасибо за 5 звёзд ⭐ Мы ценим ваш выбор и будем рады видеть вас снова!",
    "Здравствуйте! Большое спасибо за отзыв ❤️ Если будут вопросы — всегда на связи!",
    "Спасибо за доверие! ⭐⭐⭐⭐⭐",
    "Приветствуем! 🎉 Спасибо за тёплый приём товара! Это лучшая награда для нас 💙",
    "Благодарим за оценку! Для нас важно, чтобы вы оставались довольны качеством 🌟",
    "Спасибо за 5 звёзд! Рады быть частью вашего выбора. Рекомендуйте нас друзьям 🤗",
]

# Шаблоны для отзывов с фото
TEMPLATES_PHOTOS = [
    "Здравствуйте! Спасибо за ваши фотографии 📸 Они помогают другим покупателям с выбором!",
    "Благодарим за отзыв и фотографии! ❤️ Ваши снимки — лучшая рекомендация 🌟",
    "Спасибо за 5 звёзд и фото! 🙏 Рады видеть товар в ваших руках 📷",
    "Приветствуем! Спасибо за красивые фотографии 🎉 Они делают выбор проще для всех 💙",
    "Благодарим за высокую оценку и фото! 📸 Ваш опыт важен для нас и других покупателей ✨",
]


def load_env():
    """Загружает .env из разных мест"""
    paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
    ]
    for env_path in paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "=" in line:
                        k, v = line.strip().split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"\''))
            break


def get_headers():
    """Возвращает заголовки для API"""
    client_id = os.environ.get("OZON_CLIENT_ID")
    api_key = os.environ.get("OZON_API_KEY")
    if not client_id or not api_key:
        print(json.dumps({"error": "Missing OZON_CLIENT_ID or OZON_API_KEY"}, ensure_ascii=False))
        sys.exit(1)
    return {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }


def get_5star_reviews(limit: int = 100, include_with_text: bool = False) -> List[Dict]:
    """
    Получает 5★ отзывы для авто-ответа
    - Без текста (любые)
    - С фото (даже с текстом)
    Сортировка: от новых к старым (DESC)
    """
    payload = {
        "limit": max(20, min(limit, 100)),
        "sort_dir": "DESC"  # От новых к старым
    }
    
    r = requests.post(
        f"{BASE_URL}/v1/review/list",
        headers=get_headers(),
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    
    reviews = r.json().get("reviews", [])
    
    filtered = []
    for review in reviews:
        # Только 5★ и UNPROCESSED
        if review.get("rating") != 5 or review.get("status") != "UNPROCESSED":
            continue
        
        has_photos = review.get("photos_amount", 0) > 0
        has_text = bool(review.get("text", "").strip())
        
        # Логика:
        # 1) 5★ + UNPROCESSED + без текста + без фото → шаблоны
        # 2) 5★ + UNPROCESSED + без текста + с фото → шаблоны (с фото)
        # 3) 5★ с текстом → AI (ai_reply.py)
        # Важно: если есть текст — пропускаем (пусть AI обрабатывает)
        if not has_text:
            filtered.append(review)
    
    return filtered


def get_template(review: Dict) -> str:
    """Выбирает шаблон в зависимости от наличия фото"""
    has_photos = review.get("photos_amount", 0) > 0
    if has_photos:
        return random.choice(TEMPLATES_PHOTOS)
    return random.choice(TEMPLATES_TEXT)


def reply_to_review(review_id: str, text: str) -> Dict:
    """Отправляет ответ на отзыв"""
    r = requests.post(
        f"{BASE_URL}/v1/review/comment/create",
        headers=get_headers(),
        json={"review_id": review_id, "text": text},
        timeout=30
    )
    r.raise_for_status()
    return r.json()


def change_status(review_ids: List[str], status: str = "PROCESSED") -> Dict:
    """Обновляет статус отзывов ⚠️ ОБЯЗАТЕЛЬНО"""
    r = requests.post(
        f"{BASE_URL}/v1/review/change-status",
        headers=get_headers(),
        json={"review_ids": review_ids, "status": status},
        timeout=30
    )
    r.raise_for_status()
    return r.json()


def save_log(log_data: Dict):
    """Сохраняет лог в JSON"""
    # Директория для логов
    log_dir = Path("/home/firstvds/.openclaw/workspace/tmp_files/ozon-reviews-workflow")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "autoreply_log.json"
    
    logs = []
    if log_file.exists():
        try:
            with open(log_file) as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.append(log_data)
    
    with open(log_file, "w") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def main():
    load_env()
    
    parser = argparse.ArgumentParser(description="Ozon 5-Star Auto-Reply v2")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Test mode - don't actually send replies")
    parser.add_argument("--limit", type=int, default=100,
                        help="Max reviews to process (default: 100)")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Delay between requests in seconds (default: 1.5)")
    parser.add_argument("--no-status-update", action="store_true",
                        help="Skip status update to PROCESSED (not recommended)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"=== Ozon 5-Star Auto-Reply v2 [{mode}] ===\n")
    print("Sorting: Newest first (DESC)")
    print("Including: 5★ without text OR with photos\n")
    
    try:
        # Get reviews
        print("Fetching 5★ reviews...")
        reviews = get_5star_reviews(limit=args.limit)
        
        # Statistics
        with_photos = sum(1 for r in reviews if r.get("photos_amount", 0) > 0)
        without_photos = len(reviews) - with_photos
        with_text = sum(1 for r in reviews if r.get("text", "").strip())
        
        print(f"Found {len(reviews)} reviews to reply:")
        print(f"  📸 With photos: {with_photos}")
        print(f"  📄 Without photos: {without_photos}")
        print(f"  📝 With text: {with_text}, Without text: {len(reviews) - with_text}\n")
        
        if not reviews:
            print("No reviews to process. Exiting.")
            return
        
        if args.dry_run:
            print("[DRY RUN] Would reply to:")
            for i, review in enumerate(reviews[:15], 1):
                template = get_template(review)
                has_photos = review.get("photos_amount", 0) > 0
                has_text = bool(review.get("text", "").strip())
                
                photo_badge = " 📸" if has_photos else ""
                text_badge = " 📝" if has_text else ""
                
                print(f"\n{i}. Review {review['id'][:20]}... (SKU: {review['sku']}){photo_badge}{text_badge}")
                if has_photos:
                    print(f"   Photos: {review['photos_amount']}")
                if has_text:
                    text = review.get('text', '')
                    print(f"   Text: {text[:70]}{'...' if len(text) > 70 else ''}")
                print(f"   Template: {template[:60]}...")
            
            if len(reviews) > 15:
                print(f"\n... and {len(reviews) - 15} more")
            
            print(f"\n[DRY RUN] Total: {len(reviews)} reviews")
            print(f"[DRY RUN] Status update: {'skipped' if args.no_status_update else 'would update to PROCESSED'}")
            return
        
        # Process reviews
        results = []
        success_count = 0
        error_count = 0
        replied_ids = []
        
        for i, review in enumerate(reviews, 1):
            review_id = review["id"]
            sku = review["sku"]
            template = get_template(review)
            has_photos = review.get("photos_amount", 0) > 0
            
            photo_badge = " 📸" if has_photos else ""
            
            print(f"[{i}/{len(reviews)}] Replying to review {review_id[:20]}... (SKU: {sku}){photo_badge}")
            if has_photos:
                print(f"  Photos: {review['photos_amount']}")
            print(f"  Template: {template[:50]}...")
            
            try:
                result = reply_to_review(review_id, template)
                comment_id = result.get("comment_id", "unknown")
                print(f"  ✓ Sent! Comment ID: {comment_id[:20]}...")
                
                results.append({
                    "review_id": review_id,
                    "sku": sku,
                    "has_photos": has_photos,
                    "photos_amount": review.get("photos_amount", 0),
                    "has_text": bool(review.get("text", "").strip()),
                    "template_used": template,
                    "comment_id": comment_id,
                    "status": "success"
                })
                replied_ids.append(review_id)
                success_count += 1
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                results.append({
                    "review_id": review_id,
                    "sku": sku,
                    "has_photos": has_photos,
                    "photos_amount": review.get("photos_amount", 0),
                    "has_text": bool(review.get("text", "").strip()),
                    "template_used": template,
                    "error": str(e),
                    "status": "error"
                })
                error_count += 1
            
            # Delay between requests
            if i < len(reviews):
                time.sleep(args.delay)
        
        # Update status to PROCESSED ⚠️ ОБЯЗАТЕЛЬНО
        if replied_ids and not args.no_status_update:
            print(f"\n{'='*50}")
            print(f"Updating status to PROCESSED for {len(replied_ids)} reviews...")
            try:
                change_status(replied_ids, "PROCESSED")
                print(f"✓ Status updated!")
            except Exception as e:
                print(f"✗ Status update error: {e}")
                print(f"⚠️  Run: python3 ../../ozon-reviews/scripts/mark_processed.py")
        
        # Summary
        print(f"\n{'='*50}")
        print(f"Done! Processed {len(reviews)} reviews")
        print(f"  ✓ Success: {success_count}")
        print(f"  ✗ Errors: {error_count}")
        print(f"  📸 With photos: {with_photos}")
        print(f"  📄 Without photos: {without_photos}")
        
        if not args.no_status_update and replied_ids:
            print(f"  ✓ Status updated to PROCESSED")
        
        # Save log
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": "dry_run" if args.dry_run else "live",
            "total_found": len(reviews),
            "replied": success_count,
            "errors": error_count,
            "with_photos": with_photos,
            "without_photos": without_photos,
            "status_updated": not args.no_status_update and len(replied_ids) > 0,
            "reviews": results
        }
        save_log(log_data)
        print(f"\nLog saved to autoreply_log.json")
        
        if args.json:
            print(json.dumps(log_data, ensure_ascii=False, indent=2))
        
    except requests.exceptions.HTTPError as e:
        print(f"Error: API error {e.response.status_code} - {e.response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
