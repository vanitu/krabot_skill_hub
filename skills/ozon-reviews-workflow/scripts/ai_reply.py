#!/usr/bin/env python3
"""
Ozon Reviews AI - Smart Replies
AI-генерация ответов на отзывы с учётом контекста
"""

import json
import os
import sys
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional

BASE_URL = "https://api-seller.ozon.ru"


def load_env():
    """Загружает .env"""
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
    """Возвращает заголовки Ozon API"""
    client_id = os.environ.get("OZON_CLIENT_ID")
    api_key = os.environ.get("OZON_API_KEY")
    if not client_id or not api_key:
        print("Error: Missing OZON_CLIENT_ID or OZON_API_KEY")
        sys.exit(1)
    return {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }


def get_reviews(
    limit: int = 20,
    status: Optional[str] = "UNPROCESSED",
    rating_min: Optional[int] = None,
    rating_max: Optional[int] = None
) -> List[Dict]:
    """Получает отзывы из Ozon"""
    payload = {
        "limit": max(20, min(limit, 100)),
        "sort_dir": "DESC"
    }
    
    r = requests.post(
        f"{BASE_URL}/v1/review/list",
        headers=get_headers(),
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    
    reviews = r.json().get("reviews", [])
    
    # Фильтрация по статусу (если указан)
    if status is not None:
        filtered = [r for r in reviews if r.get("status") == status]
    else:
        filtered = reviews
    
    if rating_min is not None:
        filtered = [r for r in filtered if r.get("rating", 0) >= rating_min]
    if rating_max is not None:
        filtered = [r for r in filtered if r.get("rating", 5) <= rating_max]
    
    # ВАЖНО: AI обрабатывает ТОЛЬКО отзывы с текстом
    # (без текста идут в autoreply.py)
    filtered = [r for r in filtered if bool(r.get("text", "").strip())]
    
    return filtered


def generate_ai_reply(review: Dict, mode: str = "auto") -> str:
    """
    Генерирует AI-ответ на отзыв
    Для демо использует шаблоны, в продакшене — OpenAI API
    """
    rating = review.get("rating", 5)
    text = review.get("text", "")
    has_photos = review.get("photos_amount", 0) > 0
    
    # Промпт для AI (в демо — шаблоны)
    if rating >= 5:
        if has_photos:
            return f"Здравствуйте! Благодарим за прекрасный отзыв и фотографии 📸 Рады, что товар оправдал ожидания! Ваши снимки помогут другим покупателям с выбором. Ждём вас снова! ⭐"
        else:
            return f"Здравствуйте! Спасибо за высокую оценку и доверие 🙏 Мы рады, что товар вам понравился! Будем ждать вас снова ⭐"
    
    elif rating == 4:
        return f"Добрый день! Благодарим за отзыв и оценку 🌟 Рады, что покупка вам подошла! Если будут вопросы — всегда на связи. Ждём снова!"
    
    elif rating == 3:
        return f"Здравствуйте! Спасибо за честный отзыв 🙏 Нам важно ваше мнение. Если есть конкретные пожелания по улучшению — напишите нам, постараемся сделать лучше!"
    
    else:  # 1-2 stars
        if text and ("брак" in text.lower() or "плох" in text.lower() or "не подош" in text.lower()):
            return f"Здравствуйте! Приносим искренние извинения за неприятный опыт 😔 Это не соответствует нашим стандартам. Пожалуйста, напишите нам в личные сообщения — мы обязательно решим вопрос: заменим товар или оформим возврат. Спасибо за ваше терпение 🙏"
        else:
            return f"Здравствуйте! Сожалеем, что товар не оправдал ожиданий 🙏 Пожалуйста, свяжитесь с нами — мы постараемся найти решение: подберём альтернативу или поможем с возвратом. Ваше мнение важно для нас!"


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


def change_status(review_ids: List[str]) -> Dict:
    """Обновляет статус на PROCESSED"""
    print(f"  DEBUG: Updating status for {len(review_ids)} reviews...")
    r = requests.post(
        f"{BASE_URL}/v1/review/change-status",
        headers=get_headers(),
        json={"review_ids": review_ids, "status": "PROCESSED"},
        timeout=30
    )
    print(f"  DEBUG: Status API response: {r.status_code}")
    if r.status_code != 200:
        print(f"  DEBUG: Response body: {r.text[:200]}")
    r.raise_for_status()
    return r.json()


def main():
    load_env()
    
    parser = argparse.ArgumentParser(
        description="Ozon Reviews AI - Smart Replies for 4-5★ reviews WITH TEXT"
    )
    parser.add_argument("--review-id", help="Reply to specific review ID")
    parser.add_argument("--all", action="store_true", help="Process all matching reviews")
    parser.add_argument("--limit", type=int, default=20, help="Max reviews to process")
    parser.add_argument("--rating-min", type=int, help="Min rating (1-5)")
    parser.add_argument("--rating-max", type=int, help="Max rating (1-5)")
    parser.add_argument("--dry-run", action="store_true", help="Show replies without sending")
    parser.add_argument("--confirm", action="store_true", help="Confirm each reply before sending")
    parser.add_argument("--no-status-update", action="store_true", help="Skip status update")
    
    args = parser.parse_args()
    
    print("=== Ozon Reviews AI ===\n")
    
    try:
        if args.review_id:
            # Single review mode
            print(f"Fetching review {args.review_id}...")
            # Get review details (no status filter for specific ID lookup)
            reviews = get_reviews(limit=100, status=None)
            review = next((r for r in reviews if r["id"] == args.review_id), None)
            
            if not review:
                print(f"Review {args.review_id} not found")
                sys.exit(1)
            
            target_reviews = [review]
        else:
            # Batch mode
            print(f"Fetching reviews (rating: {args.rating_min or 'any'}-{args.rating_max or 'any'})...")
            target_reviews = get_reviews(
                limit=args.limit,
                rating_min=args.rating_min,
                rating_max=args.rating_max
            )
        
        if not target_reviews:
            print("No reviews found matching criteria.")
            return
        
        print(f"\nFound {len(target_reviews)} reviews\n")
        
        # Generate AI replies
        replies = []
        for review in target_reviews:
            reply_text = generate_ai_reply(review)
            replies.append({
                "review": review,
                "reply": reply_text
            })
        
        # Show previews
        print("=" * 60)
        for i, item in enumerate(replies, 1):
            review = item["review"]
            reply = item["reply"]
            
            print(f"\n{i}. Review {review['id'][:20]}... [{review['rating']}★]")
            if review.get('text'):
                print(f"   Original: {review['text'][:70]}...")
            print(f"   AI Reply: {reply}")
        
        print("\n" + "=" * 60)
        
        if args.dry_run:
            print(f"\n[DRY RUN] Would reply to {len(replies)} reviews")
            return
        
        # Confirm
        if args.confirm:
            print(f"\nReply to {len(replies)} reviews? (y/N): ", end='', flush=True)
            response = input().strip().lower()
            if response != 'y':
                print("Cancelled.")
                return
        
        # Send replies
        print(f"\nSending {len(replies)} AI-generated replies...\n")
        success_count = 0
        replied_ids = []
        
        for i, item in enumerate(replies, 1):
            review = item["review"]
            reply_text = item["reply"]
            
            print(f"[{i}/{len(replies)}] {review['id'][:20]}... [{review['rating']}★]")
            
            try:
                result = reply_to_review(review["id"], reply_text)
                print(f"  ✓ Sent! Comment ID: {result.get('comment_id', 'unknown')[:20]}...")
                success_count += 1
                replied_ids.append(review["id"])
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        # Update status
        status_updated = False
        if replied_ids and not args.no_status_update:
            print(f"\nUpdating status to PROCESSED for {len(replied_ids)} reviews...")
            try:
                result = change_status(replied_ids)
                print(f"✓ Status updated successfully! API response: {result}")
                status_updated = True
            except Exception as e:
                print(f"✗ Status update error: {e}")
                print(f"  ⚠️  WARNING: {len(replied_ids)} reviews replied but status not updated!")
                print(f"  Run manually: python3 {__file__} --update-status-only")
        
        # Save log
        log_data = {
            "timestamp": str(Path.cwd() / "autoreply_log.json"),
            "mode": "live",
            "total_processed": len(replies),
            "replied": success_count,
            "status_updated": status_updated,
            "replied_ids": replied_ids
        }
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Done! Replied to {success_count}/{len(replies)} reviews")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
