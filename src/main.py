#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from scanner import run


def parse_args():
    parser = argparse.ArgumentParser(
        description="V2Ray Auto Scanner - автоматический поиск рабочих VLESS узлов"
    )
    parser.add_argument(
        "--subs",
        type=str,
        help="Список подписок через запятую (переопределяет settings.json)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Количество узлов для сохранения в output (по умолчанию из settings.json)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    custom_subscriptions = None
    if args.subs:
        custom_subscriptions = [s.strip() for s in args.subs.split(",") if s.strip()]
        print(f"[*] Использую кастомные подписки: {len(custom_subscriptions)} шт.")
    
    run(custom_subscriptions=custom_subscriptions)


if __name__ == "__main__":
    main()
