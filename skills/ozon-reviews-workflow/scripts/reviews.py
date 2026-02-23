#!/usr/bin/env python3
"""
Ozon Reviews Client
Получение и управление отзывами покупателей
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


def get_reviews(
    limit: int = 20,
    sort_dir: str = "DESC",
    sku: Optional[int] = None,
    rating_min: Optional[int] = None,
    rating_max: Optional[int] = None,
    status: Optional[str] = None
) -> List[Dict]:
    """Получить список отзывов"""
    payload = {"limit": max(20, min(limit, 100)), "sort_dir": sort_dir}
    if sku:
        payload["sku"] = sku
    
    r = requests.post(
        f"{BASE_URL}/v1/review/list",
        headers=get_headers(),
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    
    reviews = r.json().get("reviews", [])
    
    # Фильтрация на клиенте
    if rating_min is not None:
        reviews = [r for r in reviews if r.get("rating", 0) >= rating_min]
    if rating_max is not None:
        reviews = [r for r in reviews if r.get("rating", 5) <= rating_max]
    if status:
        reviews = [r for r in reviews if r.get("status") == status]
    
    return reviews


def get_comments(review_id: str, limit: int = 20) -> List[Dict]:
    """Получить комментарии к отзыву"""
    r = requests.post(
        f"{BASE_URL}/v1/review/comment/list",
        headers=get_headers(),
        json={"review_id": review_id, "limit": max(20, min(limit, 100))},
        timeout=30
    )
    r.raise_for_status()
    return r.json().get("comments", [])


def reply_to_review(review_id: str, text: str) -> Dict:
    """Ответить на отзыв"""
    r = requests.post(
        f"{BASE_URL}/v1/review/comment/create",
        headers=get_headers(),
        json={"review_id": review_id, "text": text},
        timeout=30
    )
    r.raise_for_status()
    return r.json()


def main():
    load_env()
    
    parser = argparse.ArgumentParser(description="Ozon Reviews Client")
    parser.add_argument("--limit", type=int, default=20, help="Limit (20-100)")
    parser.add_argument("--sort-dir", default="DESC", choices=["ASC", "DESC"], help="Sort direction")
    parser.add_argument("--sku", type=int, help="Filter by SKU")
    parser.add_argument("--rating-min", type=int, help="Min rating (1-5)")
    parser.add_argument("--rating-max", type=int, help="Max rating (1-5)")
    parser.add_argument("--status", choices=["UNPROCESSED", "PROCESSED"], help="Filter by status")
    parser.add_argument("--comments-for", help="Get comments for review ID")
    parser.add_argument("--reply-to", help="Reply to review ID")
    parser.add_argument("--reply-text", help="Reply text")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        if args.comments_for:
            # Get comments
            comments = get_comments(args.comments_for, args.limit)
            if args.json:
                print(json.dumps({"comments": comments}, ensure_ascii=False, indent=2))
            else:
                print(f"Comments for review {args.comments_for}:")
                for c in comments:
                    author = "Seller" if c.get("is_owner") else "Customer"
                    print(f"  [{author}] {c.get('text', '')}")
                    
        elif args.reply_to:
            # Reply to review
            if not args.reply_text:
                print("Error: --reply-text required")
                sys.exit(1)
            result = reply_to_review(args.reply_to, args.reply_text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
        else:
            # Get reviews
            reviews = get_reviews(
                limit=args.limit,
                sort_dir=args.sort_dir,
                sku=args.sku,
                rating_min=args.rating_min,
                rating_max=args.rating_max,
                status=args.status
            )
            
            if args.json:
                print(json.dumps({"reviews": reviews}, ensure_ascii=False, indent=2))
            else:
                print(f"Found {len(reviews)} reviews:")
                for r in reviews:
                    status_icon = "✓" if r.get("status") == "PROCESSED" else "○"
                    print(f"\n{status_icon} [{r.get('rating')}★] {r.get('published_at', '')[:10]}")
                    print(f"   SKU: {r.get('sku')}")
                    print(f"   ID: {r.get('id')}")
                    text = r.get('text', '') or "(no text)"
                    print(f"   {text[:150]}{'...' if len(text) > 150 else ''}")
                    if r.get('comments_amount', 0) > 0:
                        print(f"   Comments: {r['comments_amount']}")
                    if r.get('photos_amount', 0) > 0:
                        print(f"   Photos: {r['photos_amount']}")
                        
    except requests.exceptions.HTTPError as e:
        print(json.dumps({"error": f"API error: {e.response.status_code} - {e.response.text}"}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
