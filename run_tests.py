#!/usr/bin/env python3
"""
Скрипт для запуска тестов проекта LLM Attack Simulation
"""

import sys
import subprocess
import argparse
import os

def run_command(command, description):
    """Выполнение команды с выводом описания"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Выполняется: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"\n✅ {description} завершено успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} завершено с ошибкой (код: {e.returncode})")
        return False

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Запуск тестов для проекта LLM Attack Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python run_tests.py                    # Запуск всех тестов
  python run_tests.py --unit            # Только unit тесты
  python run_tests.py --coverage        # С покрытием кода
  python run_tests.py --lint            # Проверка стиля кода
  python run_tests.py --all             # Все проверки
        """
    )
    
    parser.add_argument(
        '--unit', 
        action='store_true', 
        help='Запуск только unit тестов'
    )
    
    parser.add_argument(
        '--integration', 
        action='store_true', 
        help='Запуск только integration тестов'
    )
    
    parser.add_argument(
        '--coverage', 
        action='store_true', 
        help='Запуск тестов с покрытием кода'
    )
    
    parser.add_argument(
        '--lint', 
        action='store_true', 
        help='Проверка стиля кода с flake8'
    )
    
    parser.add_argument(
        '--format', 
        action='store_true', 
        help='Форматирование кода с black'
    )
    
    parser.add_argument(
        '--type-check', 
        action='store_true', 
        help='Проверка типов с mypy'
    )
    
    parser.add_argument(
        '--all', 
        action='store_true', 
        help='Выполнить все проверки'
    )
    
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true', 
        help='Подробный вывод'
    )
    
    args = parser.parse_args()
    
    # Если не указаны аргументы, запускаем все тесты
    if not any([args.unit, args.integration, args.coverage, args.lint, args.format, args.type_check, args.all]):
        args.all = True
    
    success = True
    
    # Проверка зависимостей
    print("🔍 Проверка зависимостей...")
    try:
        import pytest
        import yaml
        print("✅ Все зависимости установлены")
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False
    
    # Форматирование кода
    if args.format or args.all:
        success &= run_command(
            "black --check --diff .",
            "Проверка форматирования кода (black)"
        )
    
    # Проверка стиля кода
    if args.lint or args.all:
        success &= run_command(
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "Проверка стиля кода (flake8)"
        )
    
    # Проверка типов
    if args.type_check or args.all:
        success &= run_command(
            "mypy . --ignore-missing-imports",
            "Проверка типов (mypy)"
        )
    
    # Unit тесты
    if args.unit or args.all:
        if args.coverage:
            success &= run_command(
                "pytest tests/ -m unit --cov=attack --cov=defense --cov=simulation --cov=utils --cov-report=term-missing",
                "Unit тесты с покрытием кода"
            )
        else:
            success &= run_command(
                "pytest tests/ -m unit -v",
                "Unit тесты"
            )
    
    # Integration тесты
    if args.integration or args.all:
        if args.coverage:
            success &= run_command(
                "pytest tests/ -m integration --cov=attack --cov=defense --cov=simulation --cov=utils --cov-report=term-missing",
                "Integration тесты с покрытием кода"
            )
        else:
            success &= run_command(
                "pytest tests/ -m integration -v",
                "Integration тесты"
            )
    
    # Все тесты с покрытием
    if args.coverage and not (args.unit or args.integration):
        success &= run_command(
            "pytest tests/ --cov=attack --cov=defense --cov=simulation --cov=utils --cov-report=term-missing --cov-report=html:htmlcov",
            "Все тесты с покрытием кода"
        )
    
    # Итоговый результат
    print(f"\n{'='*60}")
    if success:
        print("🎉 Все проверки завершены успешно!")
        print("📊 Отчеты о покрытии кода доступны в папке htmlcov/")
    else:
        print("⚠️  Некоторые проверки завершились с ошибками")
        print("Проверьте вывод выше для деталей")
    print(f"{'='*60}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
