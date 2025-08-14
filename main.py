#!/usr/bin/env python3
"""
Главный модуль симуляции атак LLM
"""

import sys
import time
from typing import Dict, Any
from utils.logger import main_logger
from utils.config_manager import config_manager
from attack.phishing_generator import PhishingGenerator
from defense.detector import ThreatDetector
from simulation.network import NetworkSimulator

class LLMAttackSimulator:
    """Основной класс симулятора атак LLM"""
    
    def __init__(self):
        self.config = config_manager
        self.phishing_generator = PhishingGenerator()
        self.threat_detector = ThreatDetector()
        self.network_simulator = NetworkSimulator()
        
        # Статистика симуляции
        self.simulation_stats = {
            'total_simulations': 0,
            'successful_attacks': 0,
            'detected_threats': 0,
            'average_detection_time': 0.0
        }
    
    def run_simulation(self, num_attacks: int = 5, attack_types: list = None) -> Dict[str, Any]:
        """Запуск симуляции атак"""
        if attack_types is None:
            attack_types = ['phishing', 'social_engineering', 'malware']
        
        start_time = time.time()
        
        main_logger.log_simulation(
            "SIMULATION_START",
            {
                'num_attacks': num_attacks,
                'attack_types': attack_types,
                'start_time': start_time
            }
        )
        
        results = {
            'attacks': [],
            'defenses': [],
            'summary': {}
        }
        
        try:
            for i in range(num_attacks):
                attack_result = self._simulate_single_attack(i + 1, attack_types)
                results['attacks'].append(attack_result)
                
                # Небольшая пауза между атаками
                time.sleep(0.1)
            
            # Подсчет итоговой статистики
            results['summary'] = self._calculate_summary(results['attacks'])
            
            # Обновление глобальной статистики
            self._update_simulation_stats(results['summary'])
            
            main_logger.log_simulation(
                "SIMULATION_COMPLETE",
                {
                    'total_attacks': num_attacks,
                    'successful_attacks': results['summary']['successful_attacks'],
                    'detected_threats': results['summary']['detected_threats'],
                    'total_time': time.time() - start_time
                }
            )
            
            return results
            
        except Exception as e:
            main_logger.log_event(
                "SIMULATION_ERROR",
                f"Error during simulation: {str(e)}",
                details={'error': str(e), 'total_time': time.time() - start_time},
                level="ERROR"
            )
            raise
    
    def _simulate_single_attack(self, attack_id: int, attack_types: list) -> Dict[str, Any]:
        """Симуляция одной атаки"""
        attack_type = attack_types[attack_id % len(attack_types)]
        
        main_logger.log_simulation(
            "ATTACK_START",
            {
                'attack_id': attack_id,
                'attack_type': attack_type
            }
        )
        
        # Генерация атаки
        if attack_type == 'phishing':
            prompt = f"Attack #{attack_id}: Reset your password immediately!"
            email_content = self.phishing_generator.generate_email(
                prompt=prompt,
                target=f"user_{attack_id}",
                urgency="high"
            )
            
            # Проверка защиты
            is_threat, confidence, patterns = self.threat_detector.is_suspicious(
                email_content, 
                content_type="phishing_email"
            )
            
            attack_result = {
                'attack_id': attack_id,
                'attack_type': attack_type,
                'content': email_content,
                'is_threat': is_threat,
                'confidence': confidence,
                'detected_patterns': patterns,
                'timestamp': time.time()
            }
        
        else:
            # Заглушка для других типов атак
            attack_result = {
                'attack_id': attack_id,
                'attack_type': attack_type,
                'content': f"Simulated {attack_type} attack #{attack_id}",
                'is_threat': True,
                'confidence': 0.8,
                'detected_patterns': {},
                'timestamp': time.time()
            }
        
        main_logger.log_simulation(
            "ATTACK_COMPLETE",
            {
                'attack_id': attack_id,
                'attack_type': attack_type,
                'result': attack_result
            }
        )
        
        return attack_result
    
    def _calculate_summary(self, attacks: list) -> Dict[str, Any]:
        """Подсчет итоговой статистики"""
        total_attacks = len(attacks)
        successful_attacks = sum(1 for a in attacks if a['is_threat'])
        detected_threats = sum(1 for a in attacks if a['is_threat'])
        
        avg_confidence = sum(a['confidence'] for a in attacks) / total_attacks if total_attacks > 0 else 0.0
        
        return {
            'total_attacks': total_attacks,
            'successful_attacks': successful_attacks,
            'detected_threats': detected_threats,
            'detection_rate': detected_threats / total_attacks if total_attacks > 0 else 0.0,
            'average_confidence': avg_confidence
        }
    
    def _update_simulation_stats(self, summary: Dict[str, Any]):
        """Обновление глобальной статистики симуляции"""
        self.simulation_stats['total_simulations'] += 1
        self.simulation_stats['successful_attacks'] += summary['successful_attacks']
        self.simulation_stats['detected_threats'] += summary['detected_threats']
        
        # Обновление среднего времени обнаружения
        current_avg = self.simulation_stats['average_detection_time']
        total_sims = self.simulation_stats['total_simulations']
        self.simulation_stats['average_detection_time'] = (
            (current_avg * (total_sims - 1) + summary['detection_rate']) / total_sims
        )
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Получение статистики симуляции"""
        return self.simulation_stats.copy()
    
    def reset_simulation_stats(self):
        """Сброс статистики симуляции"""
        self.simulation_stats = {
            'total_simulations': 0,
            'successful_attacks': 0,
            'detected_threats': 0,
            'average_detection_time': 0.0
        }
        main_logger.log_event(
            "STATS_RESET",
            "Simulation statistics reset",
            level="INFO"
        )
    
    def print_summary(self, results: Dict[str, Any]):
        """Вывод итоговой статистики"""
        summary = results['summary']
        
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ СИМУЛЯЦИИ АТАК LLM")
        print("="*50)
        print(f"Всего атак: {summary['total_attacks']}")
        print(f"Успешных атак: {summary['successful_attacks']}")
        print(f"Обнаруженных угроз: {summary['detected_threats']}")
        print(f"Процент обнаружения: {summary['detection_rate']:.1%}")
        print(f"Средняя уверенность: {summary['average_confidence']:.2f}")
        print("="*50)
        
        # Детали по атакам
        print("\nДЕТАЛИ АТАК:")
        for attack in results['attacks']:
            status = "⚠️ УГРОЗА" if attack['is_threat'] else "✅ БЕЗОПАСНО"
            print(f"Атака #{attack['attack_id']} ({attack['attack_type']}): {status} "
                  f"(уверенность: {attack['confidence']:.2f})")

def main():
    """Главная функция"""
    try:
        main_logger.log_event(
            "APPLICATION_START",
            "LLM Attack Simulation started",
            level="INFO"
        )
        
        # Создание симулятора
        simulator = LLMAttackSimulator()
        
        print("🚀 Запуск симуляции атак через LLM...")
        print("📊 Настройки загружены из конфигурации")
        
        # Запуск симуляции
        results = simulator.run_simulation(num_attacks=5)
        
        # Вывод результатов
        simulator.print_summary(results)
        
        # Вывод статистики компонентов
        print("\n📈 СТАТИСТИКА КОМПОНЕНТОВ:")
        print(f"Генератор атак: {simulator.phishing_generator.get_generation_stats()}")
        print(f"Детектор угроз: {simulator.threat_detector.get_detection_stats()}")
        print(f"Общая статистика: {simulator.get_simulation_stats()}")
        
        main_logger.log_event(
            "APPLICATION_COMPLETE",
            "LLM Attack Simulation completed successfully",
            level="INFO"
        )
        
    except Exception as e:
        main_logger.log_event(
            "APPLICATION_ERROR",
            f"Application error: {str(e)}",
            details={'error': str(e)},
            level="ERROR"
        )
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
