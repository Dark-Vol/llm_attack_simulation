import random
import time
from typing import Dict, List, Optional
from utils.logger import attack_logger
from utils.config_manager import config_manager

class PhishingGenerator:
    """Генератор фишинговых писем с использованием LLM-подобных техник"""
    
    def __init__(self):
        self.config = config_manager.get_attack_config()
        self.suspicious_keywords = self._load_suspicious_keywords()
        self.email_templates = self._load_email_templates()
        self.generation_stats = {
            'total_generated': 0,
            'successful_attacks': 0,
            'failed_attacks': 0
        }
    
    def _load_suspicious_keywords(self) -> List[str]:
        """Загрузка подозрительных ключевых слов"""
        try:
            keywords_file = config_manager.get_data_path(
                self.config['phishing']['suspicious_keywords_file']
            )
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            attack_logger.log_event(
                "WARNING",
                f"Keywords file not found: {self.config['phishing']['suspicious_keywords_file']}",
                level="WARNING"
            )
            return ["urgent", "password", "account", "verify", "login", "security"]
    
    def _load_email_templates(self) -> List[str]:
        """Загрузка шаблонов писем"""
        try:
            templates_file = config_manager.get_data_path(
                self.config['phishing']['email_templates_file']
            )
            with open(templates_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            attack_logger.log_event(
                "WARNING",
                f"Templates file not found: {self.config['phishing']['email_templates_file']}",
                level="WARNING"
            )
            return [
                "Your account has been compromised. Click here to verify: {link}",
                "Urgent: Password reset required. {link}",
                "Security alert: Unusual activity detected. {link}",
                "Account suspended. Reactivate now: {link}"
            ]
    
    def generate_email(self, prompt: str, target: str = "user", urgency: str = "medium") -> str:
        """Генерация фишингового письма на основе промпта"""
        start_time = time.time()
        
        try:
            # Логирование начала генерации
            attack_logger.log_event(
                "EMAIL_GENERATION_START",
                f"Starting email generation for target: {target}",
                details={
                    'prompt': prompt,
                    'urgency': urgency,
                    'target': target
                }
            )
            
            # Проверка таймаута
            timeout = self.config['phishing']['generation_timeout']
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Email generation timeout after {timeout} seconds")
            
            # Генерация письма
            email_content = self._create_phishing_email(prompt, urgency)
            
            # Проверка длины
            max_length = self.config['phishing']['max_length']
            if len(email_content) > max_length:
                email_content = email_content[:max_length] + "..."
            
            # Обновление статистики
            self.generation_stats['total_generated'] += 1
            
            # Логирование успешной генерации
            attack_logger.log_attack(
                attack_type="PHISHING_EMAIL",
                target=target,
                success=True,
                details={
                    'prompt': prompt,
                    'urgency': urgency,
                    'email_length': len(email_content),
                    'generation_time': time.time() - start_time,
                    'email_content': email_content[:100] + "..." if len(email_content) > 100 else email_content
                }
            )
            
            return email_content
            
        except Exception as e:
            # Логирование ошибки
            attack_logger.log_attack(
                attack_type="PHISHING_EMAIL",
                target=target,
                success=False,
                details={
                    'prompt': prompt,
                    'urgency': urgency,
                    'error': str(e),
                    'generation_time': time.time() - start_time
                }
            )
            self.generation_stats['failed_attacks'] += 1
            raise
    
    def _create_phishing_email(self, prompt: str, urgency: str) -> str:
        """Создание фишингового письма"""
        # Выбор шаблона
        template = random.choice(self.email_templates)
        
        # Добавление подозрительных ключевых слов
        keywords = random.sample(self.suspicious_keywords, min(3, len(self.suspicious_keywords)))
        
        # Создание поддельной ссылки
        fake_link = f"https://secure-{random.randint(1000, 9999)}.com/verify"
        
        # Формирование письма
        urgency_indicators = {
            'low': ['Please', 'Kindly'],
            'medium': ['Important', 'Please note'],
            'high': ['URGENT', 'IMMEDIATE ACTION REQUIRED', 'CRITICAL']
        }
        
        urgency_prefix = random.choice(urgency_indicators.get(urgency, urgency_indicators['medium']))
        
        email_content = f"""
{urgency_prefix} {prompt}

{template.format(link=fake_link)}

Additional keywords: {', '.join(keywords)}

Best regards,
Security Team
        """.strip()
        
        return email_content
    
    def get_generation_stats(self) -> Dict[str, int]:
        """Получение статистики генерации"""
        return self.generation_stats.copy()
    
    def reset_stats(self):
        """Сброс статистики"""
        self.generation_stats = {
            'total_generated': 0,
            'successful_attacks': 0,
            'failed_attacks': 0
        }
        attack_logger.log_event(
            "STATS_RESET",
            "Generation statistics reset",
            level="INFO"
        )

# Функция для обратной совместимости
def generate_email(prompt: str, target: str = "user") -> str:
    """Простая функция генерации письма для обратной совместимости"""
    generator = PhishingGenerator()
    return generator.generate_email(prompt, target)
