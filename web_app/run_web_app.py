#!/usr/bin/env python3
"""
Скрипт для запуску веб-додатку LLM Attack Analysis System
"""

import os
import sys
import argparse
from pathlib import Path

# Додавання шляху до модулів
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def check_dependencies():
    """Перевірка залежностей"""
    required_packages = [
        'flask',
        'flask-socketio',
        'openai',
        'anthropic',
        'pyyaml',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Відсутні залежності:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nВстановіть їх командою:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ Всі залежності встановлено")
    return True

def check_config():
    """Перевірка конфігурації"""
    config_file = parent_dir / "config" / "config.yaml"
    
    if not config_file.exists():
        print("❌ Файл конфігурації не знайдено:")
        print(f"   {config_file}")
        print("\nСтворіть файл конфігурації або скопіюйте з прикладу")
        return False
    
    print("✅ Файл конфігурації знайдено")
    return True

def check_env_vars():
    """Перевірка змінних середовища"""
    required_vars = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Відсутні змінні середовища:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nСтворіть файл .env або встановіть змінні середовища")
        print("Приклад .env файлу:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("ANTHROPIC_API_KEY=your_anthropic_api_key_here")
        print("SECRET_KEY=your_secret_key_here")
        return False
    
    print("✅ Всі змінні середовища встановлено")
    return True

def create_env_template():
    """Створення шаблону .env файлу"""
    env_file = parent_dir / ".env"
    
    if env_file.exists():
        print("⚠️  Файл .env вже існує")
        return
    
    env_template = """# LLM Attack Analysis System Environment Variables
# Скопіюйте цей файл та заповніть своїми значеннями

# OpenAI API Key (отримайте на https://platform.openai.com/)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (отримайте на https://console.anthropic.com/)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Секретний ключ для Flask (згенеруйте випадковий рядок)
SECRET_KEY=your_secret_key_here

# Додаткові налаштування (опціонально)
# DEBUG=true
# LOG_LEVEL=INFO
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
        print(f"✅ Створено шаблон .env файлу: {env_file}")
    except Exception as e:
        print(f"❌ Помилка створення .env файлу: {e}")

def generate_secret_key():
    """Генерація секретного ключа"""
    import secrets
    return secrets.token_hex(32)

def main():
    """Головна функція"""
    parser = argparse.ArgumentParser(
        description="LLM Attack Analysis System - Web Application Launcher"
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Тільки перевірити залежності та конфігурацію'
    )
    
    parser.add_argument(
        '--create-env',
        action='store_true',
        help='Створити шаблон .env файлу'
    )
    
    parser.add_argument(
        '--generate-key',
        action='store_true',
        help='Згенерувати секретний ключ'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Хост для запуску (за замовчуванням: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Порт для запуску (за замовчуванням: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Запустити в режимі налагодження'
    )
    
    args = parser.parse_args()
    
    print("🚀 LLM Attack Analysis System - Web Application Launcher")
    print("=" * 60)
    
    # Генерація секретного ключа
    if args.generate_key:
        secret_key = generate_secret_key()
        print(f"\n🔑 Згенеровано секретний ключ:")
        print(f"SECRET_KEY={secret_key}")
        return
    
    # Створення .env файлу
    if args.create_env:
        create_env_template()
        return
    
    # Перевірка залежностей
    print("\n📦 Перевірка залежностей...")
    if not check_dependencies():
        sys.exit(1)
    
    # Перевірка конфігурації
    print("\n⚙️  Перевірка конфігурації...")
    if not check_config():
        sys.exit(1)
    
    # Перевірка змінних середовища
    print("\n🌍 Перевірка змінних середовища...")
    if not check_env_vars():
        print("\n💡 Поради:")
        print("1. Створіть файл .env в кореневій папці проекту")
        print("2. Додайте необхідні API ключі")
        print("3. Згенеруйте секретний ключ командою: python run_web_app.py --generate-key")
        print("\nАбо запустіть з --create-env для створення шаблону")
        sys.exit(1)
    
    # Тільки перевірка
    if args.check_only:
        print("\n✅ Всі перевірки пройдено успішно!")
        print("Система готова до запуску")
        return
    
    # Запуск додатку
    print("\n🚀 Запуск веб-додатку...")
    print(f"📍 Хост: {args.host}")
    print(f"🔌 Порт: {args.port}")
    print(f"🐛 Режим налагодження: {'Увімкнено' if args.debug else 'Вимкнено'}")
    print("\n🌐 Відкрийте браузер та перейдіть на:")
    print(f"   http://localhost:{args.port}")
    print("\n⏹️  Для зупинки натисніть Ctrl+C")
    print("=" * 60)
    
    try:
        # Імпорт та запуск додатку
        from app import app, socketio
        
        # Налаштування
        app.config['DEBUG'] = args.debug
        
        # Запуск
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug
        )
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Додаток зупинено користувачем")
    except Exception as e:
        print(f"\n❌ Помилка запуску додатку: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
