import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Менеджер конфигурации для централизованного управления настройками"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    raise ValueError("Config file is empty")
                return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
    
    def _validate_config(self):
        """Валидация конфигурации"""
        required_sections = ['logging', 'attack', 'defense', 'simulation']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Получение значения по пути (например, 'logging.level')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Получение конфигурации логирования"""
        return self.config.get('logging', {})
    
    def get_attack_config(self) -> Dict[str, Any]:
        """Получение конфигурации атак"""
        return self.config.get('attack', {})
    
    def get_defense_config(self) -> Dict[str, Any]:
        """Получение конфигурации защиты"""
        return self.config.get('defense', {})
    
    def get_simulation_config(self) -> Dict[str, Any]:
        """Получение конфигурации симуляции"""
        return self.config.get('simulation', {})
    
    def get_testing_config(self) -> Dict[str, Any]:
        """Получение конфигурации тестирования"""
        return self.config.get('testing', {})
    
    def update_config(self, updates: Dict[str, Any]):
        """Обновление конфигурации"""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        self.config = deep_update(self.config, updates)
        self._validate_config()
    
    def save_config(self, output_path: Optional[str] = None):
        """Сохранение конфигурации в файл"""
        if output_path is None:
            output_path = self.config_path
        
        # Создание директории если не существует
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def get_data_path(self, filename: str) -> str:
        """Получение полного пути к файлу данных"""
        data_dir = "data"
        return os.path.join(data_dir, filename)
    
    def get_model_path(self, filename: str) -> str:
        """Получение полного пути к файлу модели"""
        model_dir = "models"
        return os.path.join(model_dir, filename)
    
    def get_log_path(self, filename: str) -> str:
        """Получение полного пути к файлу лога"""
        log_dir = "logs"
        return os.path.join(log_dir, filename)
    
    def reload(self):
        """Перезагрузка конфигурации из файла"""
        self.config = self._load_config()
        self._validate_config()
    
    def export_env_vars(self):
        """Экспорт конфигурации в переменные окружения"""
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key.upper(), str(v)))
            return dict(items)
        
        env_vars = flatten_dict(self.config)
        for key, value in env_vars.items():
            os.environ[f"LLM_SIM_{key}"] = value

# Глобальный экземпляр конфигурации
config_manager = ConfigManager()
