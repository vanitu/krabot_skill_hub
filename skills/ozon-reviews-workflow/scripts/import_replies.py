#!/usr/bin/env python3
"""
Ozon Reviews Import
Импорт AI-сгенерированных ответов в Ozon
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
    r = requests.post(
        f"{BASE_URL}/v1/review/change-status",
        headers=get_headers(),
        json={"review_ids": review_ids, "status": "PROCESSED"},
        timeout=30
    )
    r.raise_for_status()
    return r.json()


def main():
    load_env()
    
    parser = argparse.ArgumentParser(description="Import AI replies to Ozon")
    parser.add_argument("file", help="JSON file with replies")
    parser.add_argument("--dry-run", action="store_true", help="Show without sending")
    
    args = parser.parse_args()
    
    # Load replies
    with open(args.file) as f:
        replies = json.load(f)
    
    print(f"=== Ozon Reviews Import ===")
    print(f"File: {args.file}")
    print(f"Replies to import: {len(replies)}\n")
    
    if args.dry_run:
        print("[DRY RUN] Would import:")
        for item in replies:
            print(f"\n  {item['id'][:20]}...")
            print(f"  Reply: {item['ai_reply'][:60]}...")
        return
    
    # Send replies
    success_count = 0
    replied_ids = []
    
    for i, item in enumerate(replies, 1):
        review_id = item["id"]
        reply_text = item["ai_reply"]
        
        print(f"[{i}/{len(replies)}] {review_id[:20]}...")
        
        try:
            result = reply_to_review(review_id, reply_text)
            print(f"  ✓ Sent! Comment ID: {result.get('comment_id', 'unknown')[:20]}...")
            success_count += 1
            replied_ids.append(review_id)
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Update status
    if replied_ids:
        print(f"\nUpdating status to PROCESSED...")
        try:
            change_status(replied_ids)
            print(f"✓ Status updated for {len(replied_ids)} reviews!")
        except Exception as e:
            print(f"✗ Status update error: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Done! Imported {success_count}/{len(replies)} replies")


if __name__ == "__main__":
    main()
