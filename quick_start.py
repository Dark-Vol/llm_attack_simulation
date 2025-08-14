#!/usr/bin/env python3
"""
Швидкий старт LLM Attack Analysis System
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Виведення баннера системи"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    LLM Attack Analysis System                                ║
    ║    Інтегрований системний аналіз адаптивних атак            ║
    ║    з застосуванням LLM (GPT/Claude)                         ║
    ║                                                              ║
    ║    Моделювання, симуляція та контрзаходи                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Перевірка версії Python"""
    if sys.version_info < (3, 8):
        print("❌ Потрібна Python 3.8 або новіша версія")
        print(f"   Поточна версія: {sys.version}")
        return False
    
    print(f"✅ Python версія: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Встановлення залежностей"""
    print("\n📦 Встановлення залежностей...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Залежності встановлено успішно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка встановлення залежностей: {e}")
        return False

def create_env_file():
    """Створення .env файлу"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ Файл .env вже існує")
        return True
    
    print("\n🌍 Створення .env файлу...")
    
    env_content = """# LLM Attack Analysis System Environment Variables
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
            f.write(env_content)
        print("✅ Файл .env створено")
        return True
    except Exception as e:
        print(f"❌ Помилка створення .env файлу: {e}")
        return False

def generate_secret_key():
    """Генерація секретного ключа"""
    import secrets
    return secrets.token_hex(32)

def setup_environment():
    """Налаштування середовища"""
    print("\n⚙️  Налаштування середовища...")
    
    # Створення необхідних папок
    folders = ['logs', 'data', 'web_app/logs']
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
    
    print("✅ Папки створено")
    
    # Створення .env файлу
    if not create_env_file():
        return False
    
    # Генерація секретного ключа
    secret_key = generate_secret_key()
    print(f"🔑 Згенеровано секретний ключ: {secret_key[:16]}...")
    
    return True

def run_health_check():
    """Запуск перевірки здоров'я системи"""
    print("\n🏥 Перевірка здоров'я системи...")
    
    try:
        result = subprocess.run([
            sys.executable, "web_app/run_web_app.py", "--check-only"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Система готова до роботи")
            return True
        else:
            print("❌ Помилка перевірки системи")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Помилка запуску перевірки: {e}")
        return False

def show_next_steps():
    """Показати наступні кроки"""
    print("\n🎯 Наступні кроки:")
    print("1. Відредагуйте файл .env та додайте свої API ключі")
    print("2. Запустіть систему командою:")
    print("   python web_app/run_web_app.py")
    print("3. Відкрийте браузер та перейдіть на http://localhost:5000")
    print("\n📚 Детальна документація: README.md")
    print("🔧 Допомога: python web_app/run_web_app.py --help")

def main():
    """Головна функція"""
    print_banner()
    
    print("🚀 Швидкий старт LLM Attack Analysis System")
    print("=" * 60)
    
    # Перевірка Python
    if not check_python_version():
        sys.exit(1)
    
    # Встановлення залежностей
    if not install_dependencies():
        print("\n💡 Спробуйте встановити залежності вручну:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Налаштування середовища
    if not setup_environment():
        print("\n💡 Спробуйте налаштувати середовище вручну")
        sys.exit(1)
    
    # Перевірка здоров'я
    if not run_health_check():
        print("\n💡 Система потребує додаткового налаштування")
        show_next_steps()
        sys.exit(1)
    
    print("\n🎉 Вітаємо! Система успішно налаштована!")
    show_next_steps()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Процес перервано користувачем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        sys.exit(1)
