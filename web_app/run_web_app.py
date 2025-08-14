#!/usr/bin/env python3
"""
Скрипт для запуска веб-приложения LLM Attack Simulation
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Проверка зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    required_packages = ['flask', 'yaml']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их: pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены\n")
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Зависимости установлены успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        return False

def create_directories():
    """Создание необходимых директорий"""
    print("📁 Создание директорий...")
    
    # Добавляем путь к основному проекту
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Создаем директории в корне проекта
    directories = ['logs', 'models', 'data']
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    print()

def start_web_app():
    """Запуск веб-приложения"""
    print("🚀 Запуск веб-приложения...")
    
    try:
        # Переходим в корень проекта для корректной работы с конфигурацией
        project_root = Path(__file__).parent.parent
        os.chdir(project_root)
        
        print(f"📁 Рабочая директория: {os.getcwd()}")
        print(f"📁 Путь к конфигурации: {project_root / 'config' / 'config.yaml'}")
        
        # Проверяем наличие конфигурации
        config_file = project_root / 'config' / 'config.yaml'
        if not config_file.exists():
            print(f"❌ Файл конфигурации не найден: {config_file}")
            return False
        
        print("✅ Конфигурация найдена")
        
        # Импортируем и запускаем приложение
        from web_app.app import app
        
        print("✅ Веб-приложение инициализировано успешно")
        print("🌐 Открытие в браузере...")
        
        # Открываем браузер через 2 секунды
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
        
        print("\n🎉 Веб-приложение запущено!")
        print("📱 Доступно по адресу: http://localhost:5000")
        print("🛑 Для остановки нажмите Ctrl+C")
        print("\n" + "="*60)
        
        # Запускаем Flask приложение
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Ошибка при запуске веб-приложения: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Главная функция"""
    print("🎯 LLM Attack Simulation - Веб-приложение")
    print("="*50)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n📦 Попытка установки зависимостей...")
        if not install_dependencies():
            print("❌ Не удалось установить зависимости")
            sys.exit(1)
        
        # Повторная проверка
        if not check_dependencies():
            print("❌ Зависимости не установлены")
            sys.exit(1)
    
    # Создаем директории
    create_directories()
    
    # Запускаем веб-приложение
    if not start_web_app():
        print("\n❌ Возникли проблемы при запуске")
        print("Проверьте логи и убедитесь, что все зависимости установлены")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Веб-приложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)
