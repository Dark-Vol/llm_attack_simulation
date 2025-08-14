#!/usr/bin/env python3
"""
Быстрый старт для демонстрации возможностей LLM Attack Simulation
"""

import os
import sys
import time
from pathlib import Path

def check_dependencies():
    """Проверка зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    required_packages = ['yaml', 'pytest']
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

def create_directories():
    """Создание необходимых директорий"""
    print("📁 Создание директорий...")
    
    directories = ['logs', 'models', 'data']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    print()

def run_demo():
    """Запуск демонстрации"""
    print("🚀 Запуск демонстрации...")
    
    try:
        # Импорт основных модулей
        from main import LLMAttackSimulator
        
        # Создание симулятора
        simulator = LLMAttackSimulator()
        
        print("📊 Запуск симуляции с 3 атаками...")
        
        # Запуск симуляции
        results = simulator.run_simulation(num_attacks=3)
        
        # Вывод результатов
        simulator.print_summary(results)
        
        print("\n🎯 Демонстрация отдельных модулей:")
        
        # Демонстрация генератора атак
        from attack.phishing_generator import PhishingGenerator
        generator = PhishingGenerator()
        
        print("\n📧 Генерация фишингового письма:")
        email = generator.generate_email("Verify your account", "demo@example.com", "high")
        print(f"Сгенерированное письмо:\n{email}")
        
        # Демонстрация детектора угроз
        from defense.detector import ThreatDetector
        detector = ThreatDetector()
        
        print("\n🛡️  Проверка на угрозы:")
        is_threat, confidence, patterns = detector.is_suspicious(email)
        print(f"Обнаружена угроза: {is_threat}")
        print(f"Уверенность: {confidence:.2f}")
        print(f"Обнаруженные паттерны: {list(patterns.keys())}")
        
        # Демонстрация симулятора сети
        from simulation.network import NetworkSimulator
        network_sim = NetworkSimulator()
        
        print("\n🌐 Создание тестовой сети:")
        nodes = network_sim.create_network(5)
        print(f"Создано узлов: {len(nodes)}")
        
        network_stats = network_sim.get_network_stats()
        print(f"Целостность сети: {network_stats['network_integrity']:.2f}")
        
        print("\n🎉 Демонстрация завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при запуске демонстрации: {e}")
        return False
    
    return True

def show_next_steps():
    """Показать следующие шаги"""
    print("\n" + "="*60)
    print("🚀 СЛЕДУЮЩИЕ ШАГИ")
    print("="*60)
    print("1. 📖 Изучите README.md для подробной документации")
    print("2. 🧪 Запустите тесты: python run_tests.py")
    print("3. ⚙️  Настройте конфигурацию в config/config.yaml")
    print("4. 🔧 Модифицируйте код под свои нужды")
    print("5. 📊 Анализируйте логи в папке logs/")
    print("6. 🤝 Внесите свой вклад в проект")
    print("="*60)

def main():
    """Главная функция"""
    print("🎯 LLM Attack Simulation - Быстрый старт")
    print("="*50)
    
    # Проверка зависимостей
    if not check_dependencies():
        sys.exit(1)
    
    # Создание директорий
    create_directories()
    
    # Запуск демонстрации
    if run_demo():
        show_next_steps()
        print("\n✅ Проект готов к использованию!")
    else:
        print("\n❌ Возникли проблемы при запуске")
        print("Проверьте логи и убедитесь, что все зависимости установлены")
        sys.exit(1)

if __name__ == "__main__":
    main()
