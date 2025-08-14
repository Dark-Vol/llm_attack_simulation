import pytest
import tempfile
import os
import yaml
import json
from unittest.mock import patch, MagicMock
from utils.logger import StructuredLogger
from utils.config_manager import ConfigManager

class TestStructuredLogger:
    """Тесты для структурированного логгера"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        
        # Создание тестовой конфигурации
        test_config = {
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': os.path.join(self.temp_dir, 'test.log'),
                'max_size': '1MB',
                'backup_count': 2,
                'console_output': True
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(test_config, f)
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_config_file(self):
        """Тест инициализации с файлом конфигурации"""
        logger = StructuredLogger("test_logger", self.config_file)
        
        assert logger.name == "test_logger"
        assert logger.config['logging']['level'] == 'INFO'
        assert logger.logger is not None
    
    def test_init_without_config_file(self):
        """Тест инициализации без файла конфигурации"""
        logger = StructuredLogger("test_logger", "nonexistent.yaml")
        
        assert logger.name == "test_logger"
        assert logger.config['logging']['level'] == 'INFO'  # Значения по умолчанию
        assert logger.logger is not None
    
    def test_parse_size(self):
        """Тест парсинга размера файла"""
        logger = StructuredLogger("test_logger", self.config_file)
        
        assert logger._parse_size("1KB") == 1024
        assert logger._parse_size("1MB") == 1024 * 1024
        assert logger._parse_size("1GB") == 1024 * 1024 * 1024
        assert logger._parse_size("100") == 100
    
    def test_log_event(self):
        """Тест логирования события"""
        logger = StructuredLogger("test_logger", self.config_file)
        
        # Тест логирования на разных уровнях
        logger.log_event("TEST_EVENT", "Test message", {"detail": "test"}, "INFO")
        logger.log_event("TEST_EVENT", "Test message", {"detail": "test"}, "WARNING")
        logger.log_event("TEST_EVENT", "Test message", {"detail": "test"}, "ERROR")
        
        # Проверяем, что логгер работает без ошибок
        assert True
    
    def test_log_attack(self):
        """Тест логирования атаки"""
        logger = StructuredLogger("test_logger", self.config_file)
        
        logger.log_attack("PHISHING", "user@example.com", True, {"method": "email"})
        logger.log_attack("BRUTE_FORCE", "server1", False, {"attempts": 100})
        
        # Проверяем, что логгер работает без ошибок
        assert True
    
    def test_log_defense(self):
        """Тест логирования защиты"""
        logger = StructuredLogger("test_logger", self.config_file)
        
        logger.log_defense("ANTIVIRUS", True, 0.95, {"threat": "malware"})
        logger.log_defense("FIREWALL", False, 0.3, {"port": 22})
        
        # Проверяем, что логгер работает без ошибок
        assert True
    
    def test_log_simulation(self):
        """Тест логирования симуляции"""
        logger = StructuredLogger("test_logger", self.config_file)
        
        logger.log_simulation("NETWORK_CREATION", {"nodes": 10, "connections": 15})
        logger.log_simulation("ATTACK_SIMULATION", {"type": "phishing", "target": "user1"})
        
        # Проверяем, что логгер работает без ошибок
        assert True

class TestConfigManager:
    """Тесты для менеджера конфигурации"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        
        # Создание тестовой конфигурации
        test_config = {
            'logging': {
                'level': 'DEBUG',
                'file': 'logs/test.log'
            },
            'attack': {
                'phishing': {
                    'max_length': 500
                }
            },
            'defense': {
                'detector': {
                    'confidence_threshold': 0.7
                }
            },
            'simulation': {
                'network': {
                    'max_nodes': 25
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(test_config, f)
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_valid_config(self):
        """Тест инициализации с валидной конфигурацией"""
        config_manager = ConfigManager(self.config_file)
        
        assert config_manager.config_path == self.config_file
        assert 'logging' in config_manager.config
        assert 'attack' in config_manager.config
        assert 'defense' in config_manager.config
        assert 'simulation' in config_manager.config
    
    def test_init_with_invalid_yaml(self):
        """Тест инициализации с невалидным YAML"""
        # Создаем файл с невалидным YAML
        invalid_config_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(invalid_config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(ValueError, match="Invalid YAML"):
            ConfigManager(invalid_config_file)
    
    def test_init_with_missing_file(self):
        """Тест инициализации с отсутствующим файлом"""
        with pytest.raises(FileNotFoundError):
            ConfigManager("nonexistent.yaml")
    
    def test_init_with_empty_config(self):
        """Тест инициализации с пустой конфигурацией"""
        empty_config_file = os.path.join(self.temp_dir, "empty.yaml")
        with open(empty_config_file, 'w') as f:
            f.write("")
        
        with pytest.raises(ValueError, match="Config file is empty"):
            ConfigManager(empty_config_file)
    
    def test_get_simple_key(self):
        """Тест получения простого ключа"""
        config_manager = ConfigManager(self.config_file)
        
        level = config_manager.get('logging.level')
        assert level == 'DEBUG'
    
    def test_get_nested_key(self):
        """Тест получения вложенного ключа"""
        config_manager = ConfigManager(self.config_file)
        
        max_length = config_manager.get('attack.phishing.max_length')
        assert max_length == 500
    
    def test_get_nonexistent_key(self):
        """Тест получения несуществующего ключа"""
        config_manager = ConfigManager(self.config_file)
        
        value = config_manager.get('nonexistent.key', 'default')
        assert value == 'default'
    
    def test_get_logging_config(self):
        """Тест получения конфигурации логирования"""
        config_manager = ConfigManager(self.config_file)
        
        logging_config = config_manager.get_logging_config()
        assert logging_config['level'] == 'DEBUG'
        assert logging_config['file'] == 'logs/test.log'
    
    def test_get_attack_config(self):
        """Тест получения конфигурации атак"""
        config_manager = ConfigManager(self.config_file)
        
        attack_config = config_manager.get_attack_config()
        assert attack_config['phishing']['max_length'] == 500
    
    def test_get_defense_config(self):
        """Тест получения конфигурации защиты"""
        config_manager = ConfigManager(self.config_file)
        
        defense_config = config_manager.get_defense_config()
        assert defense_config['detector']['confidence_threshold'] == 0.7
    
    def test_get_simulation_config(self):
        """Тест получения конфигурации симуляции"""
        config_manager = ConfigManager(self.config_file)
        
        simulation_config = config_manager.get_simulation_config()
        assert simulation_config['network']['max_nodes'] == 25
    
    def test_update_config(self):
        """Тест обновления конфигурации"""
        config_manager = ConfigManager(self.config_file)
        
        updates = {
            'logging': {
                'level': 'INFO'
            },
            'attack': {
                'phishing': {
                    'max_length': 1000
                }
            }
        }
        
        config_manager.update_config(updates)
        
        assert config_manager.get('logging.level') == 'INFO'
        assert config_manager.get('attack.phishing.max_length') == 1000
    
    def test_save_config(self):
        """Тест сохранения конфигурации"""
        config_manager = ConfigManager(self.config_file)
        
        # Обновляем конфигурацию
        config_manager.update_config({'logging': {'level': 'WARNING'}})
        
        # Сохраняем в новый файл
        new_config_file = os.path.join(self.temp_dir, "new_config.yaml")
        config_manager.save_config(new_config_file)
        
        # Проверяем, что файл создан и содержит обновленные данные
        assert os.path.exists(new_config_file)
        
        with open(new_config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config['logging']['level'] == 'WARNING'
    
    def test_get_data_path(self):
        """Тест получения пути к данным"""
        config_manager = ConfigManager(self.config_file)
        
        data_path = config_manager.get_data_path("test.txt")
        assert data_path == "data/test.txt"
    
    def test_get_model_path(self):
        """Тест получения пути к модели"""
        config_manager = ConfigManager(self.config_file)
        
        model_path = config_manager.get_model_path("detector.pkl")
        assert model_path == "models/detector.pkl"
    
    def test_get_log_path(self):
        """Тест получения пути к логу"""
        config_manager = ConfigManager(self.config_file)
        
        log_path = config_manager.get_log_path("test.log")
        assert log_path == "logs/test.log"
    
    def test_reload_config(self):
        """Тест перезагрузки конфигурации"""
        config_manager = ConfigManager(self.config_file)
        
        # Изменяем файл конфигурации
        new_config = {
            'logging': {'level': 'ERROR'},
            'attack': {'phishing': {'max_length': 2000}},
            'defense': {'detector': {'confidence_threshold': 0.9}},
            'simulation': {'network': {'max_nodes': 50}}
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(new_config, f)
        
        # Перезагружаем конфигурацию
        config_manager.reload()
        
        assert config_manager.get('logging.level') == 'ERROR'
        assert config_manager.get('attack.phishing.max_length') == 2000
        assert config_manager.get('defense.detector.confidence_threshold') == 0.9
        assert config_manager.get('simulation.network.max_nodes') == 50
    
    def test_export_env_vars(self):
        """Тест экспорта в переменные окружения"""
        config_manager = ConfigManager(self.config_file)
        
        # Экспортируем конфигурацию
        config_manager.export_env_vars()
        
        # Проверяем, что переменные созданы
        assert 'LLM_SIM_LOGGING_LEVEL' in os.environ
        assert 'LLM_SIM_ATTACK_PHISHING_MAX_LENGTH' in os.environ
        assert 'LLM_SIM_DEFENSE_DETECTOR_CONFIDENCE_THRESHOLD' in os.environ
        assert 'LLM_SIM_SIMULATION_NETWORK_MAX_NODES' in os.environ
        
        # Проверяем значения
        assert os.environ['LLM_SIM_LOGGING_LEVEL'] == 'DEBUG'
        assert os.environ['LLM_SIM_ATTACK_PHISHING_MAX_LENGTH'] == '500'
        assert os.environ['LLM_SIM_DEFENSE_DETECTOR_CONFIDENCE_THRESHOLD'] == '0.7'
        assert os.environ['LLM_SIM_SIMULATION_NETWORK_MAX_NODES'] == '25'

class TestLegacyFunctions:
    """Тесты для функций обратной совместимости"""
    
    @patch('utils.logger.StructuredLogger')
    def test_log_event_function(self, mock_logger_class):
        """Тест функции log_event для обратной совместимости"""
        mock_logger = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        from utils.logger import log_event
        
        log_event("Test message", "INFO")
        
        mock_logger.log_event.assert_called_once_with("LEGACY", "Test message", level="INFO")
