#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импортов всех модулей проекта
"""

import sys
import os

def test_imports():
    """Тестирование импортов всех модулей"""
    print("🔍 Тестирование импортов модулей проекта...")
    print("=" * 60)
    
    # Добавляем текущую директорию в Python path
    current_dir = os.getcwd()
    print(f"📁 Текущая директория: {current_dir}")
    print(f"📁 Python path: {sys.path}")
    print()
    
    # Тестируем основные модули
    modules_to_test = [
        'utils.config_manager',
        'utils.logger', 
        'attack.phishing_generator',
        'defense.detector',
        'simulation.network',
        'main'
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            print(f"📦 Тестирую импорт: {module_name}")
            module = __import__(module_name)
            print(f"✅ {module_name} - УСПЕШНО")
            results[module_name] = "SUCCESS"
        except ImportError as e:
            print(f"❌ {module_name} - ОШИБКА: {e}")
            results[module_name] = f"ERROR: {e}"
        except Exception as e:
            print(f"⚠️  {module_name} - ПРЕДУПРЕЖДЕНИЕ: {e}")
            results[module_name] = f"WARNING: {e}"
        print()
    
    # Тестируем создание экземпляров классов
    print("🔧 Тестирование создания экземпляров классов...")
    print("=" * 60)
    
    try:
        from utils.config_manager import ConfigManager
        print("📦 Создаю ConfigManager...")
        config_manager = ConfigManager()
        print("✅ ConfigManager создан успешно")
        results['ConfigManager_instance'] = "SUCCESS"
    except Exception as e:
        print(f"❌ Ошибка создания ConfigManager: {e}")
        results['ConfigManager_instance'] = f"ERROR: {e}"
    
    try:
        from utils.logger import StructuredLogger
        print("📦 Создаю StructuredLogger...")
        logger = StructuredLogger("test_logger")
        print("✅ StructuredLogger создан успешно")
        results['StructuredLogger_instance'] = "SUCCESS"
    except Exception as e:
        print(f"❌ Ошибка создания StructuredLogger: {e}")
        results['StructuredLogger_instance'] = f"ERROR: {e}"
    
    try:
        from attack.phishing_generator import PhishingGenerator
        print("📦 Создаю PhishingGenerator...")
        phishing_gen = PhishingGenerator()
        print("✅ PhishingGenerator создан успешно")
        results['PhishingGenerator_instance'] = "SUCCESS"
    except Exception as e:
        print(f"❌ Ошибка создания PhishingGenerator: {e}")
        results['PhishingGenerator_instance'] = f"ERROR: {e}"
    
    try:
        from defense.detector import ThreatDetector
        print("📦 Создаю ThreatDetector...")
        detector = ThreatDetector()
        print("✅ ThreatDetector создан успешно")
        results['ThreatDetector_instance'] = "SUCCESS"
    except Exception as e:
        print(f"❌ Ошибка создания ThreatDetector: {e}")
        results['ThreatDetector_instance'] = f"ERROR: {e}"
    
    try:
        from simulation.network import NetworkSimulator
        print("📦 Создаю NetworkSimulator...")
        network_sim = NetworkSimulator()
        print("✅ NetworkSimulator создан успешно")
        results['NetworkSimulator_instance'] = "SUCCESS"
    except Exception as e:
        print(f"❌ Ошибка создания NetworkSimulator: {e}")
        results['NetworkSimulator_instance'] = f"ERROR: {e}"
    
    try:
        from main import LLMAttackSimulator
        print("📦 Создаю LLMAttackSimulator...")
        simulator = LLMAttackSimulator()
        print("✅ LLMAttackSimulator создан успешно")
        results['LLMAttackSimulator_instance'] = "SUCCESS"
    except Exception as e:
        print(f"❌ Ошибка создания LLMAttackSimulator: {e}")
        results['LLMAttackSimulator_instance'] = f"ERROR: {e}"
    
    # Итоговый отчет
    print("\n📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    success_count = sum(1 for result in results.values() if result == "SUCCESS")
    total_count = len(results)
    
    print(f"✅ Успешно: {success_count}/{total_count}")
    print(f"❌ Ошибки: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 Все модули работают корректно!")
    else:
        print("\n⚠️  Есть проблемы с некоторыми модулями:")
        for module, result in results.items():
            if result != "SUCCESS":
                print(f"   - {module}: {result}")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
