#!/usr/bin/env python3
"""
Ozon Reviews - Mark processed with comments as PROCESSED
Обновляет статус отзывов, на которые уже есть ответ
"""
import json
import os
import sys
import argparse
import requests
from pathlib import Path
from typing import List, Dict

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


def get_reviews_with_comments_unprocessed(limit: int = 100) -> List[Dict]:
    """Получает UNPROCESSED отзывы с комментариями"""
    r = requests.post(
        f"{BASE_URL}/v1/review/list",
        headers=get_headers(),
        json={"limit": max(20, min(limit, 100)), "sort_dir": "DESC"},
        timeout=30
    )
    r.raise_for_status()
    
    reviews = r.json().get("reviews", [])
    
    # Фильтруем: UNPROCESSED но с комментариями
    filtered = [
        r for r in reviews 
        if r.get("status") == "UNPROCESSED" 
        and r.get("comments_amount", 0) > 0
    ]
    
    return filtered


def change_status(review_ids: List[str], status: str = "PROCESSED") -> Dict:
    """Меняет статус отзывов"""
    r = requests.post(
        f"{BASE_URL}/v1/review/change-status",
        headers=get_headers(),
        json={"review_ids": review_ids, "status": status},
        timeout=30
    )
    r.raise_for_status()
    return r.json()


def main():
    load_env()
    
    parser = argparse.ArgumentParser(description="Mark reviews with comments as PROCESSED")
    parser.add_argument("--limit", type=int, default=100, help="Max reviews to check")
    parser.add_argument("--dry-run", action="store_true", help="Test mode - show what would be updated")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"=== Ozon Reviews - Mark Processed [{mode}] ===\n")
    
    try:
        # Get reviews
        print("Fetching UNPROCESSED reviews with comments...")
        reviews = get_reviews_with_comments_unprocessed(limit=args.limit)
        
        print(f"Found {len(reviews)} UNPROCESSED reviews with comments\n")
        
        if not reviews:
            print("No reviews to update. All caught up!")
            return
        
        # Show preview
        print("Reviews to update:")
        for i, review in enumerate(reviews[:10], 1):
            print(f"  {i}. ID: {review['id'][:30]}...")
            print(f"      SKU: {review['sku']}, Comments: {review['comments_amount']}")
            print(f"      Published: {review.get('published_at', '')[:10]}")
            if review.get('text'):
                print(f"      Text: {review['text'][:50]}...")
            print()
        
        if len(reviews) > 10:
            print(f"  ... and {len(reviews) - 10} more\n")
        
        if args.dry_run:
            print(f"[DRY RUN] Would update {len(reviews)} reviews to PROCESSED")
            print(f"\nRun without --dry-run to actually update:")
            print(f"  python3 {sys.argv[0]}")
            return
        
        # Confirm (unless --yes)
        if not args.yes:
            print(f"Update {len(reviews)} reviews to PROCESSED? (y/N): ", end='', flush=True)
            try:
                response = input().strip().lower()
            except EOFError:
                # Non-interactive mode
                print("\nError: Running in non-interactive mode. Use --yes to skip confirmation.")
                print(f"  python3 {sys.argv[0]} --yes")
                sys.exit(1)
            if response != 'y':
                print("Cancelled.")
                return
        
        # Process in batches (max 100 per request)
        batch_size = 100
        total_updated = 0
        
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i + batch_size]
            review_ids = [r["id"] for r in batch]
            
            print(f"\nUpdating batch {i//batch_size + 1} ({len(batch)} reviews)...")
            result = change_status(review_ids, "PROCESSED")
            total_updated += len(batch)
            print(f"  ✓ Updated")
        
        # Summary
        print(f"\n{'='*50}")
        print(f"Done! Updated {total_updated} reviews to PROCESSED")
        
        if args.json:
            print(json.dumps({
                "updated": total_updated,
                "reviews": [{"id": r["id"], "sku": r["sku"]} for r in reviews]
            }, ensure_ascii=False, indent=2))
        
    except requests.exceptions.HTTPError as e:
        print(f"Error: API error {e.response.status_code} - {e.response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
