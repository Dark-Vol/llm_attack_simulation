import re
import json
import time
from typing import Dict, List, Tuple, Optional
from utils.logger import defense_logger
from utils.config_manager import config_manager

class ThreatDetector:
    """Детектор угроз с использованием различных методов анализа"""
    
    def __init__(self):
        self.config = config_manager.get_defense_config()
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.detection_stats = {
            'total_checks': 0,
            'threats_detected': 0,
            'false_positives': 0,
            'average_confidence': 0.0
        }
        self.confidence_threshold = self.config['detector']['confidence_threshold']
    
    def _load_suspicious_patterns(self) -> List[Dict[str, any]]:
        """Загрузка паттернов для обнаружения угроз"""
        try:
            patterns_file = config_manager.get_data_path(
                self.config['detector']['suspicious_patterns_file']
            )
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            defense_logger.log_event(
                "WARNING",
                f"Patterns file not found: {self.config['detector']['suspicious_patterns_file']}",
                level="WARNING"
            )
            return self._get_default_patterns()
        except json.JSONDecodeError:
            defense_logger.log_event(
                "ERROR",
                f"Invalid JSON in patterns file: {self.config['detector']['suspicious_patterns_file']}",
                level="ERROR"
            )
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> List[Dict[str, any]]:
        """Возвращает паттерны по умолчанию"""
        return [
            {
                "name": "urgent_action",
                "pattern": r"\b(urgent|immediate|critical|asap|now)\b",
                "weight": 0.3,
                "description": "Срочные действия"
            },
            {
                "name": "password_reset",
                "pattern": r"\b(password|reset|change|update)\b",
                "weight": 0.4,
                "description": "Сброс пароля"
            },
            {
                "name": "account_verification",
                "pattern": r"\b(verify|confirm|validate|check)\s+(account|email|identity)\b",
                "weight": 0.5,
                "description": "Проверка аккаунта"
            },
            {
                "name": "suspicious_links",
                "pattern": r"https?://[^\s]+",
                "weight": 0.6,
                "description": "Подозрительные ссылки"
            },
            {
                "name": "personal_info_request",
                "pattern": r"\b(ssn|credit\s+card|bank\s+account|social\s+security)\b",
                "weight": 0.8,
                "description": "Запрос личной информации"
            }
        ]
    
    def is_suspicious(self, content: str, content_type: str = "email") -> Tuple[bool, float, Dict[str, any]]:
        """Проверка контента на подозрительность"""
        start_time = time.time()
        
        try:
            # Логирование начала проверки
            defense_logger.log_event(
                "THREAT_DETECTION_START",
                f"Starting threat detection for {content_type}",
                details={
                    'content_type': content_type,
                    'content_length': len(content),
                    'content_preview': content[:100] + "..." if len(content) > 100 else content
                }
            )
            
            # Анализ контента
            threat_score, detected_patterns = self._analyze_content(content)
            
            # Определение результата
            is_threat = threat_score >= self.confidence_threshold
            
            # Обновление статистики
            self.detection_stats['total_checks'] += 1
            if is_threat:
                self.detection_stats['threats_detected'] += 1
            
            # Обновление среднего значения уверенности
            total_confidence = self.detection_stats['average_confidence'] * (self.detection_stats['total_checks'] - 1)
            self.detection_stats['average_confidence'] = (total_confidence + threat_score) / self.detection_stats['total_checks']
            
            # Логирование результата
            defense_logger.log_defense(
                defense_type="THREAT_DETECTION",
                threat_detected=is_threat,
                confidence=threat_score,
                details={
                    'content_type': content_type,
                    'threat_score': threat_score,
                    'confidence_threshold': self.confidence_threshold,
                    'detected_patterns': detected_patterns,
                    'detection_time': time.time() - start_time,
                    'content_preview': content[:100] + "..." if len(content) > 100 else content
                }
            )
            
            return is_threat, threat_score, detected_patterns
            
        except Exception as e:
            # Логирование ошибки
            defense_logger.log_event(
                "ERROR",
                f"Error during threat detection: {str(e)}",
                details={
                    'content_type': content_type,
                    'error': str(e),
                    'detection_time': time.time() - start_time
                },
                level="ERROR"
            )
            raise
    
    def _analyze_content(self, content: str) -> Tuple[float, Dict[str, any]]:
        """Анализ контента на основе паттернов"""
        total_score = 0.0
        detected_patterns = {}
        
        for pattern_info in self.suspicious_patterns:
            pattern = pattern_info['pattern']
            weight = pattern_info['weight']
            name = pattern_info['name']
            
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Подсчет очков на основе количества совпадений
                match_count = len(matches)
                pattern_score = min(weight * match_count, 1.0)  # Максимум 1.0
                
                total_score += pattern_score
                detected_patterns[name] = {
                    'matches': matches,
                    'score': pattern_score,
                    'weight': weight,
                    'description': pattern_info['description']
                }
        
        # Нормализация общего счета
        normalized_score = min(total_score, 1.0)
        
        return normalized_score, detected_patterns
    
    def get_detection_stats(self) -> Dict[str, any]:
        """Получение статистики обнаружения"""
        return self.detection_stats.copy()
    
    def reset_stats(self):
        """Сброс статистики"""
        self.detection_stats = {
            'total_checks': 0,
            'threats_detected': 0,
            'false_positives': 0,
            'average_confidence': 0.0
        }
        defense_logger.log_event(
            "STATS_RESET",
            "Detection statistics reset",
            level="INFO"
        )
    
    def update_confidence_threshold(self, new_threshold: float):
        """Обновление порога уверенности"""
        if 0.0 <= new_threshold <= 1.0:
            old_threshold = self.confidence_threshold
            self.confidence_threshold = new_threshold
            
            defense_logger.log_event(
                "CONFIG_UPDATE",
                f"Confidence threshold updated from {old_threshold} to {new_threshold}",
                details={
                    'old_threshold': old_threshold,
                    'new_threshold': new_threshold
                }
            )
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
    
    def add_custom_pattern(self, name: str, pattern: str, weight: float, description: str):
        """Добавление пользовательского паттерна"""
        if weight < 0.0 or weight > 1.0:
            raise ValueError("Pattern weight must be between 0.0 and 1.0")
        
        custom_pattern = {
            "name": name,
            "pattern": pattern,
            "weight": weight,
            "description": description
        }
        
        self.suspicious_patterns.append(custom_pattern)
        
        defense_logger.log_event(
            "PATTERN_ADDED",
            f"Custom pattern '{name}' added",
            details=custom_pattern
        )

# Функция для обратной совместимости
def is_suspicious(content: str) -> bool:
    """Простая функция проверки для обратной совместимости"""
    detector = ThreatDetector()
    is_threat, _, _ = detector.is_suspicious(content)
    return is_threat
