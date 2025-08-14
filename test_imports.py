#!/usr/bin/env python3
"""
Тестування імпортів всіх модулів LLM Attack Analysis System
"""

import sys
import importlib
from pathlib import Path

def test_import(module_name, description=""):
    """Тестування імпорту модуля"""
    try:
        module = importlib.import_module(module_name)
        print(f"✅ {module_name} - імпортовано успішно")
        if description:
            print(f"   {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - помилка імпорту: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - помилка: {e}")
        return False

def test_utils():
    """Тестування утиліт"""
    print("\n🔧 Тестування утиліт:")
    
    modules = [
        ("utils.config_manager", "Менеджер конфігурації"),
        ("utils.logger", "Система логування")
    ]
    
    success_count = 0
    for module_name, description in modules:
        if test_import(module_name, description):
            success_count += 1
    
    return success_count, len(modules)

def test_attack():
    """Тестування модуля атак"""
    print("\n🐛 Тестування модуля атак:")
    
    modules = [
        ("attack.llm_attack_generator", "Генератор атак з LLM")
    ]
    
    success_count = 0
    for module_name, description in modules:
        if test_import(module_name, description):
            success_count += 1
    
    return success_count, len(modules)

def test_defense():
    """Тестування модуля захисту"""
    print("\n🛡️  Тестування модуля захисту:")
    
    modules = [
        ("defense.defense_analyzer", "Аналізатор захисту")
    ]
    
    success_count = 0
    for module_name, description in modules:
        if test_import(module_name, description):
            success_count += 1
    
    return success_count, len(modules)

def test_simulation():
    """Тестування модуля симуляції"""
    print("\n🎮 Тестування модуля симуляції:")
    
    modules = [
        ("simulation.attack_simulator", "Симулятор атак")
    ]
    
    success_count = 0
    for module_name, description in modules:
        if test_import(module_name, description):
            success_count += 1
    
    return success_count, len(modules)

def test_web_app():
    """Тестування веб-додатку"""
    print("\n🌐 Тестування веб-додатку:")
    
    # Перевірка наявності Flask
    try:
        import flask
        print("✅ Flask - імпортовано успішно")
        flask_available = True
    except ImportError:
        print("❌ Flask - не встановлено")
        flask_available = False
    
    if flask_available:
        modules = [
            ("web_app.app", "Веб-додаток Flask")
        ]
        
        success_count = 0
        for module_name, description in modules:
            if test_import(module_name, description):
                success_count += 1
        
        return success_count, len(modules)
    else:
        return 0, 1

def test_external_dependencies():
    """Тестування зовнішніх залежностей"""
    print("\n📦 Тестування зовнішніх залежностей:")
    
    dependencies = [
        ("openai", "OpenAI API клієнт"),
        ("anthropic", "Anthropic API клієнт"),
        ("yaml", "YAML парсер"),
        ("flask", "Flask веб-фреймворк"),
        ("flask_socketio", "Flask-SocketIO"),
        ("cryptography", "Криптографічні функції"),
        ("numpy", "NumPy для обчислень"),
        ("pandas", "Pandas для аналізу даних")
    ]
    
    success_count = 0
    for module_name, description in dependencies:
        if test_import(module_name, description):
            success_count += 1
    
    return success_count, len(dependencies)

def test_config_files():
    """Тестування конфігураційних файлів"""
    print("\n⚙️  Тестування конфігураційних файлів:")
    
    config_files = [
        ("config/config.yaml", "Основний конфігураційний файл"),
        ("requirements.txt", "Файл залежностей Python"),
        ("README.md", "Документація проекту")
    ]
    
    success_count = 0
    for file_path, description in config_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - знайдено")
            print(f"   {description}")
            success_count += 1
        else:
            print(f"❌ {file_path} - не знайдено")
    
    return success_count, len(config_files)

def main():
    """Головна функція тестування"""
    print("🧪 Тестування імпортів LLM Attack Analysis System")
    print("=" * 60)
    
    total_success = 0
    total_modules = 0
    
    # Тестування утиліт
    success, count = test_utils()
    total_success += success
    total_modules += count
    
    # Тестування модуля атак
    success, count = test_attack()
    total_success += success
    total_modules += count
    
    # Тестування модуля захисту
    success, count = test_defense()
    total_success += success
    total_modules += count
    
    # Тестування модуля симуляції
    success, count = test_simulation()
    total_success += success
    total_modules += count
    
    # Тестування веб-додатку
    success, count = test_web_app()
    total_success += success
    total_modules += count
    
    # Тестування зовнішніх залежностей
    success, count = test_external_dependencies()
    total_success += success
    total_modules += count
    
    # Тестування конфігураційних файлів
    success, count = test_config_files()
    total_success += success
    total_modules += count
    
    # Підсумок
    print("\n" + "=" * 60)
    print(f"📊 Підсумок тестування:")
    print(f"   Успішно: {total_success}/{total_modules}")
    print(f"   Відсоток успіху: {(total_success/total_modules)*100:.1f}%")
    
    if total_success == total_modules:
        print("\n🎉 Всі модулі успішно імпортовано!")
        print("Система готова до роботи")
    else:
        print(f"\n⚠️  {total_modules - total_success} модулів мають проблеми")
        print("Перевірте встановлення залежностей")
        print("Команда: pip install -r requirements.txt")
    
    return total_success == total_modules

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Критична помилка тестування: {e}")
        sys.exit(1)
