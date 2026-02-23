#!/usr/bin/env python3
"""
Ozon Reviews Workflow - Полный цикл обработки отзывов
Оркестратор для регулярной обработки отзывов по стратегии:
1. 5★ без текста → автоответ
2. 4-5★ с текстом → AI (экспорт/анализ/импорт)
3. 1-3★ → AI с особыми инструкциями (претензии)
"""

import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

WORKSPACE = Path.home() / ".openclaw" / "workspace"

def run_command(cmd: List[str], description: str) -> bool:
    """Выполняет команду и показывает результат"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"❌ Ошибка: {result.stderr}")
        return False

def step1_auto_5star_no_text(dry_run: bool = False) -> Dict:
    """
    Шаг 1: 5★ без текста → автоответ
    """
    print("\n" + "="*60)
    print("📋 ШАГ 1: 5★ без текста → Автоответ")
    print("="*60)
    
    cmd = [
        "python3", "skills/ozon-reviews-workflow/scripts/autoreply.py",
        "--limit", "100"
    ]
    
    if dry_run:
        cmd.append("--dry-run")
    
    success = run_command(cmd, "Запуск автоответов на 5★ без текста")
    
    return {
        "step": 1,
        "name": "5star_autoreply",
        "success": success,
        "dry_run": dry_run
    }

def step2_ai_4_5_with_text(confirm_each: bool = False, dry_run: bool = False) -> Dict:
    """
    Шаг 2: 4-5★ с текстом → AI анализ
    """
    print("\n" + "="*60)
    print("📋 ШАГ 2: 4-5★ с текстом → AI анализ")
    print("="*60)
    
    output_file = f"ai_reviews_4_5_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    
    # Экспорт
    cmd_export = [
        "python3", "skills/ozon-reviews-workflow/scripts/ai_reply.py",
        "--export",
        "--rating-min", "4",
        "--rating-max", "5",
        "--output", output_file
    ]
    
    if not run_command(cmd_export, "Экспорт отзывов 4-5★ для AI"):
        return {"step": 2, "name": "ai_4_5_export", "success": False}
    
    print(f"\n✅ Отзывы экспортированы в: {output_file}")
    print(f"\n⏸️  СЛЕДУЮЩИЙ ШАГ:")
    print(f"   1. Передай файл AI (мне) для анализа")
    print(f"   2. Получи файл с ответами (например: {output_file.replace('.json', '_replied.json')})")
    print(f"   3. Запусти импорт:")
    print(f"      python3 skills/ozon-reviews-workflow/scripts/ai_reply.py --import-file {output_file.replace('.json', '_replied.json')}")
    
    return {
        "step": 2,
        "name": "ai_4_5_export",
        "success": True,
        "file": output_file,
        "next_action": "Передай файл AI для анализа"
    }

def step3_ai_1_3_negative(confirm_each: bool = False, dry_run: bool = False) -> Dict:
    """
    Шаг 3: 1-3★ (негатив) → AI с особыми инструкциями
    """
    print("\n" + "="*60)
    print("📋 ШАГ 3: 1-3★ (негатив/претензии) → AI с особыми инструкциями")
    print("="*60)
    
    output_file = f"ai_reviews_negative_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    
    # Экспорт
    cmd_export = [
        "python3", "skills/ozon-reviews-workflow/scripts/ai_reply.py",
        "--export",
        "--rating-min", "1",
        "--rating-max", "3",
        "--output", output_file
    ]
    
    if not run_command(cmd_export, "Экспорт отзывов 1-3★ для AI"):
        return {"step": 3, "name": "ai_negative_export", "success": False}
    
    print(f"\n✅ Отзывы экспортированы в: {output_file}")
    print(f"\n⚠️  ВАЖНО: Для негативных отзывов (1-3★) используй специальные инструкции:")
    print(f"   - Больше эмпатии и извинений")
    print(f"   - Конкретные решения (возврат/замена)")
    print(f"   - Приглашение в личные сообщения")
    print(f"   - Не шаблонные ответы, а персональные")
    print(f"\n⏸️  СЛЕДУЮЩИЙ ШАГ:")
    print(f"   1. Передай файл AI (мне) с пометкой 'негативные отзывы'")
    print(f"   2. Получи файл с ответами")
    print(f"   3. Запусти импорт:")
    print(f"      python3 skills/ozon-reviews-workflow/scripts/ai_reply.py --import-file [файл]")
    
    return {
        "step": 3,
        "name": "ai_negative_export",
        "success": True,
        "file": output_file,
        "next_action": "Передай файл AI для анализа (особые инструкции для негатива)"
    }

def full_workflow(dry_run: bool = False, auto_5star: bool = True):
    """
    Полный рабочий процесс
    """
    print("\n" + "="*60)
    print("🚀 OZON REVIEWS WORKFLOW - Полный цикл")
    print("="*60)
    print(f"Режим: {'ТЕСТОВЫЙ (dry-run)' if dry_run else 'РЕАЛЬНАЯ ОТПРАВКА'}")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    results = []
    
    # Шаг 1: 5★ без текста (авто)
    if auto_5star:
        result = step1_auto_5star_no_text(dry_run)
        results.append(result)
        
        if not result["success"]:
            print("\n❌ Ошибка на шаге 1. Останавливаемся.")
            return results
    
    # Шаг 2: 4-5★ с текстом (AI)
    result = step2_ai_4_5_with_text(dry_run=dry_run)
    results.append(result)
    
    # Шаг 3: 1-3★ (негатив, AI)
    result = step3_ai_1_3_negative(dry_run=dry_run)
    results.append(result)
    
    # Итог
    print("\n" + "="*60)
    print("📊 ИТОГ РАБОЧЕГО ПРОЦЕССА")
    print("="*60)
    
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"{status} Шаг {r['step']}: {r['name']}")
    
    print(f"\n⏭️  Следующие действия:")
    print(f"   1. Дождись экспорта файлов отзывов")
    print(f"   2. Передай их мне (AI) для анализа")
    print(f"   3. Получи файлы с ответами")
    print(f"   4. Импортируй ответы командой:")
    print(f"      python3 skills/ozon-reviews-workflow/scripts/ai_reply.py --import-file [файл]")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Ozon Reviews Workflow - Полный цикл обработки",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Полный цикл (тест)
  python3 workflow.py --dry-run
  
  # Только 5★ авто
  python3 workflow.py --step1-only
  
  # Только экспорт для AI (4-5★)
  python3 workflow.py --step2-only
  
  # Только негатив (1-3★)
  python3 workflow.py --step3-only
  
  # Полный цикл (реальная отправка 5★ + экспорт для AI)
  python3 workflow.py
        """
    )
    
    parser.add_argument("--dry-run", action="store_true",
                        help="Тестовый режим без реальной отправки")
    parser.add_argument("--step1-only", action="store_true",
                        help="Только шаг 1: 5★ без текста (авто)")
    parser.add_argument("--step2-only", action="store_true",
                        help="Только шаг 2: 4-5★ с текстом (AI)")
    parser.add_argument("--step3-only", action="store_true",
                        help="Только шаг 3: 1-3★ негатив (AI)")
    parser.add_argument("--no-auto-5star", action="store_true",
                        help="Пропустить автоответы 5★ (только экспорт для AI)")
    
    args = parser.parse_args()
    
    # Определяем что запускать
    if args.step1_only:
        step1_auto_5star_no_text(args.dry_run)
    elif args.step2_only:
        step2_ai_4_5_with_text(dry_run=args.dry_run)
    elif args.step3_only:
        step3_ai_1_3_negative(dry_run=args.dry_run)
    else:
        full_workflow(
            dry_run=args.dry_run,
            auto_5star=not args.no_auto_5star
        )

if __name__ == "__main__":
    main()
