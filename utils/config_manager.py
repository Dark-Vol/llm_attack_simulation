import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """Менеджер конфігурації системи"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = {}
        self._load_environment()
        self._load_config()
    
    def _load_environment(self):
        """Завантаження змінних середовища"""
        load_dotenv()
    
    def _load_config(self):
        """Завантаження конфігурації з файлу"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            # Заміна змінних середовища
            self._replace_environment_variables(self.config)
            
        except FileNotFoundError:
            print(f"Попередження: Файл конфігурації {self.config_path} не знайдено")
            self.config = {}
        except yaml.YAMLError as e:
            print(f"Помилка парсингу YAML: {e}")
            self.config = {}
    
    def _replace_environment_variables(self, obj: Any):
        """Рекурсивна заміна змінних середовища"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    obj[key] = os.getenv(env_var, "")
                elif isinstance(value, (dict, list)):
                    self._replace_environment_variables(value)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._replace_environment_variables(item)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Отримання значення конфігурації за ключем"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_llm_config(self, provider: str) -> Dict[str, Any]:
        """Отримання конфігурації LLM провайдера"""
        return self.get(f"llm_providers.{provider}", {})
    
    def get_network_config(self) -> Dict[str, Any]:
        """Отримання конфігурації мережі"""
        return self.get("network", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Отримання конфігурації безпеки"""
        return self.get("security", {})
    
    def get_web_config(self) -> Dict[str, Any]:
        """Отримання конфігурації веб-інтерфейсу"""
        return self.get("web_interface", {})
    
    def reload(self):
        """Перезавантаження конфігурації"""
        self._load_config()
    
    def is_debug_mode(self) -> bool:
        """Перевірка режиму налагодження"""
        return self.get("system.debug", False)
    
    def get_log_level(self) -> str:
        """Отримання рівня логування"""
        return self.get("system.log_level", "INFO")
