#!/usr/bin/env python3
"""
Запуск тестів LLM Attack Analysis System
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description=""):
    """Запуск команди з обробкою помилок"""
    print(f"\n🚀 {description}")
    print(f"Команда: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 хвилин таймаут
        )
        
        if result.returncode == 0:
            print("✅ Команда виконана успішно")
            if result.stdout:
                print("Вивід:")
                print(result.stdout)
        else:
            print("❌ Команда завершилася з помилкою")
            if result.stderr:
                print("Помилки:")
                print(result.stderr)
            if result.stdout:
                print("Вивід:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Команда перевищила час виконання")
        return False
    except Exception as e:
        print(f"❌ Помилка виконання команди: {e}")
        return False

def check_dependencies():
    """Перевірка наявності залежностей для тестування"""
    print("🔍 Перевірка залежностей для тестування...")
    
    required_packages = ['pytest', 'pytest-cov']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Відсутні пакети: {', '.join(missing_packages)}")
        print("Встановлюю...")
        
        install_command = f"pip install {' '.join(missing_packages)}"
        if not run_command(install_command, "Встановлення залежностей для тестування"):
            print("❌ Не вдалося встановити залежності")
            return False
    
    print("✅ Всі залежності для тестування встановлено")
    return True

def run_import_tests():
    """Запуск тестів імпортів"""
    return run_command(
        "python test_imports.py",
        "Тестування імпортів модулів"
    )

def run_unit_tests():
    """Запуск unit тестів"""
    return run_command(
        "python -m pytest tests/ -v",
        "Запуск unit тестів"
    )

def run_coverage_tests():
    """Запуск тестів з покриттям"""
    return run_command(
        "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term",
        "Запуск тестів з покриттям коду"
    )

def run_specific_test(test_file):
    """Запуск конкретного тесту"""
    return run_command(
        f"python -m pytest {test_file} -v",
        f"Запуск тесту {test_file}"
    )

def run_web_app_tests():
    """Запуск тестів веб-додатку"""
    return run_command(
        "python -m pytest tests/test_web_app.py -v",
        "Тестування веб-додатку"
    )

def run_security_tests():
    """Запуск тестів безпеки"""
    return run_command(
        "python -m pytest tests/test_security.py -v",
        "Тестування безпеки"
    )

def run_integration_tests():
    """Запуск інтеграційних тестів"""
    return run_command(
        "python -m pytest tests/test_integration.py -v",
        "Інтеграційне тестування"
    )

def generate_test_report():
    """Генерація звіту про тестування"""
    print("\n📊 Генерація звіту про тестування...")
    
    # Створення папки для звітів
    reports_dir = Path("test_reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Запуск тестів з генерацією звіту
    report_command = (
        "python -m pytest tests/ "
        "--cov=. "
        "--cov-report=html:test_reports/html "
        "--cov-report=xml:test_reports/coverage.xml "
        "--cov-report=term-missing "
        "--junitxml=test_reports/junit.xml "
        "-v"
    )
    
    success = run_command(report_command, "Генерація детального звіту")
    
    if success:
        print(f"\n📁 Звіти збережено в папці: {reports_dir.absolute()}")
        print("   - HTML звіт: test_reports/html/index.html")
        print("   - XML звіт: test_reports/coverage.xml")
        print("   - JUnit звіт: test_reports/junit.xml")
    
    return success

def main():
    """Головна функція"""
    print("🧪 Запуск тестів LLM Attack Analysis System")
    print("=" * 60)
    
    # Парсинг аргументів командного рядка
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "imports":
            run_import_tests()
            return
        elif command == "unit":
            run_unit_tests()
            return
        elif command == "coverage":
            run_coverage_tests()
            return
        elif command == "web":
            run_web_app_tests()
            return
        elif command == "security":
            run_security_tests()
            return
        elif command == "integration":
            run_integration_tests()
            return
        elif command == "report":
            generate_test_report()
            return
        elif command == "specific" and len(sys.argv) > 2:
            test_file = sys.argv[2]
            run_specific_test(test_file)
            return
        else:
            print("❌ Невідома команда або неправильні аргументи")
            show_help()
            return
    
    # Запуск всіх тестів
    print("🎯 Запуск повного набору тестів...")
    
    # Перевірка залежностей
    if not check_dependencies():
        print("❌ Не вдалося налаштувати залежності для тестування")
        sys.exit(1)
    
    # Тестування імпортів
    import_success = run_import_tests()
    
    # Unit тести
    unit_success = run_unit_tests()
    
    # Тести з покриттям
    coverage_success = run_coverage_tests()
    
    # Генерація звіту
    report_success = generate_test_report()
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 Підсумок тестування:")
    print(f"   Імпорти: {'✅' if import_success else '❌'}")
    print(f"   Unit тести: {'✅' if unit_success else '❌'}")
    print(f"   Покриття: {'✅' if coverage_success else '❌'}")
    print(f"   Звіт: {'✅' if report_success else '❌'}")
    
    total_success = sum([import_success, unit_success, coverage_success, report_success])
    total_tests = 4
    
    print(f"\n🎯 Загальний результат: {total_success}/{total_tests}")
    print(f"   Відсоток успіху: {(total_success/total_tests)*100:.1f}%")
    
    if total_success == total_tests:
        print("\n🎉 Всі тести пройдено успішно!")
        print("Система готова до роботи")
    else:
        print(f"\n⚠️  {total_tests - total_success} тестів мають проблеми")
        print("Перевірте логи та виправте помилки")
    
    return total_success == total_tests

def show_help():
    """Показати довідку"""
    help_text = """
Доступні команди:

  python run_tests.py              # Запуск всіх тестів
  python run_tests.py imports      # Тестування імпортів
  python run_tests.py unit         # Unit тести
  python run_tests.py coverage     # Тести з покриттям
  python run_tests.py web          # Тести веб-додатку
  python run_tests.py security     # Тести безпеки
  python run_tests.py integration  # Інтеграційні тести
  python run_tests.py report       # Генерація звіту
  python run_tests.py specific <file>  # Конкретний тест

Приклади:
  python run_tests.py specific tests/test_attack.py
  python run_tests.py coverage
  python run_tests.py report
"""
    print(help_text)

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Тестування перервано користувачем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критична помилка тестування: {e}")
        sys.exit(1)
