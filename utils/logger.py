import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import yaml

class StructuredLogger:
    """Структурированный логгер с поддержкой JSON и ротации файлов"""
    
    def __init__(self, name: str, config_path: str = "config/config.yaml"):
        self.name = name
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию по умолчанию"""
        return {
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/simulation.log',
                'max_size': '10MB',
                'backup_count': 5,
                'console_output': True
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка логгера"""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.config['logging']['level']))
        
        # Очистка существующих обработчиков
        logger.handlers.clear()
        
        # Создание директории для логов
        log_dir = os.path.dirname(self.config['logging']['file'])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Настройка форматирования
        formatter = logging.Formatter(self.config['logging']['format'])
        
        # Файловый обработчик с ротацией
        file_handler = logging.handlers.RotatingFileHandler(
            self.config['logging']['file'],
            maxBytes=self._parse_size(self.config['logging']['max_size']),
            backupCount=self.config['logging']['backup_count'],
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Консольный обработчик
        if self.config['logging']['console_output']:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _parse_size(self, size_str: str) -> int:
        """Парсинг размера файла (например, '10MB' -> 10485760)"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def log_event(self, event_type: str, message: str, details: Optional[Dict[str, Any]] = None, level: str = "INFO"):
        """Логирование события с метаданными"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'message': message,
            'details': details or {},
            'logger': self.name
        }
        
        log_message = json.dumps(log_data, ensure_ascii=False, indent=2)
        
        if level.upper() == "DEBUG":
            self.logger.debug(log_message)
        elif level.upper() == "INFO":
            self.logger.info(log_message)
        elif level.upper() == "WARNING":
            self.logger.warning(log_message)
        elif level.upper() == "ERROR":
            self.logger.error(log_message)
        elif level.upper() == "CRITICAL":
            self.logger.critical(log_message)
        else:
            self.logger.info(log_message)
    
    def log_attack(self, attack_type: str, target: str, success: bool, details: Dict[str, Any]):
        """Логирование атаки"""
        self.log_event(
            event_type="ATTACK",
            message=f"{attack_type} attack on {target} - {'SUCCESS' if success else 'FAILED'}",
            details=details,
            level="WARNING" if success else "INFO"
        )
    
    def log_defense(self, defense_type: str, threat_detected: bool, confidence: float, details: Dict[str, Any]):
        """Логирование защиты"""
        self.log_event(
            event_type="DEFENSE",
            message=f"{defense_type} defense - Threat {'DETECTED' if threat_detected else 'NOT_DETECTED'} (confidence: {confidence})",
            details=details,
            level="WARNING" if threat_detected else "INFO"
        )
    
    def log_simulation(self, event: str, data: Dict[str, Any]):
        """Логирование симуляции"""
        self.log_event(
            event_type="SIMULATION",
            message=event,
            details=data,
            level="INFO"
        )

# Глобальный логгер для обратной совместимости
def log_event(message: str, level: str = "INFO"):
    """Простая функция логирования для обратной совместимости"""
    logger = StructuredLogger("legacy")
    logger.log_event("LEGACY", message, level=level)

# Создание основных логгеров
attack_logger = StructuredLogger("attack")
defense_logger = StructuredLogger("defense")
simulation_logger = StructuredLogger("simulation")
main_logger = StructuredLogger("main")