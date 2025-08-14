import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional
from utils.config_manager import ConfigManager

class Logger:
    """Система логування для LLM Attack Analysis System"""
    
    def __init__(self, name: str = "llm_attack_system"):
        self.name = name
        self.config = ConfigManager()
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Налаштування логера"""
        logger = logging.getLogger(self.name)
        
        if logger.handlers:
            return logger
        
        logger.setLevel(self._get_log_level())
        
        # Форматування
        formatter = logging.Formatter(
            self.config.get("logging.format", 
                           "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        
        # Консольний хендлер
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Файловий хендлер
        log_file = self.config.get("logging.file_path", "logs/system.log")
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self._parse_size(self.config.get("logging.max_file_size", "10MB")),
                backupCount=self.config.get("logging.backup_count", 5)
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _get_log_level(self) -> int:
        """Отримання рівня логування"""
        level_str = self.config.get_log_level().upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level_str, logging.INFO)
    
    def _parse_size(self, size_str: str) -> int:
        """Парсинг розміру файлу"""
        size_str = size_str.upper()
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('B'):
            return int(size_str[:-1])
        else:
            return int(size_str)
    
    def debug(self, message: str):
        """Логування на рівні DEBUG"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Логування на рівні INFO"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Логування на рівні WARNING"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Логування на рівні ERROR"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Логування на рівні CRITICAL"""
        self.logger.critical(message)
    
    def log_attack(self, attack_type: str, target: str, details: str):
        """Логування атаки"""
        message = f"ATTACK: {attack_type} -> {target} | {details}"
        self.warning(message)
    
    def log_defense(self, defense_type: str, target: str, details: str):
        """Логування захисту"""
        message = f"DEFENSE: {defense_type} -> {target} | {details}"
        self.info(message)
    
    def log_llm_interaction(self, provider: str, model: str, action: str):
        """Логування взаємодії з LLM"""
        message = f"LLM: {provider}/{model} | {action}"
        self.info(message)
    
    def log_network_scan(self, target: str, ports: list, results: dict):
        """Логування сканування мережі"""
        message = f"NETWORK_SCAN: {target} | Ports: {ports} | Results: {results}"
        self.info(message)
    
    def log_simulation(self, sim_id: str, action: str, details: str):
        """Логування симуляції"""
        message = f"SIMULATION[{sim_id}]: {action} | {details}"
        self.info(message)

# Глобальний екземпляр логера
logger = Logger()
