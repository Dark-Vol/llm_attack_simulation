import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from attack.phishing_generator import PhishingGenerator

class TestPhishingGenerator:
    """Тесты для генератора фишинговых писем"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.keywords_file = os.path.join(self.temp_dir, "suspicious_keywords.txt")
        self.templates_file = os.path.join(self.temp_dir, "email_templates.txt")
        
        # Создание временных файлов
        with open(self.keywords_file, 'w') as f:
            f.write("urgent\npassword\naccount\nverify")
        
        with open(self.templates_file, 'w') as f:
            f.write("Your account needs verification: {link}\nReset password: {link}")
        
        # Мокаем конфигурацию
        self.mock_config = {
            'phishing': {
                'max_length': 1000,
                'suspicious_keywords_file': self.keywords_file,
                'email_templates_file': self.templates_file,
                'generation_timeout': 30
            }
        }
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('attack.phishing_generator.config_manager')
    def test_init_with_files(self, mock_config_manager):
        """Тест инициализации с существующими файлами"""
        mock_config_manager.get_attack_config.return_value = self.mock_config
        
        generator = PhishingGenerator()
        
        assert len(generator.suspicious_keywords) == 4
        assert len(generator.email_templates) == 2
        assert generator.generation_stats['total_generated'] == 0
    
    @patch('attack.phishing_generator.config_manager')
    def test_init_without_files(self, mock_config_manager):
        """Тест инициализации без файлов"""
        mock_config_manager.get_attack_config.return_value = self.mock_config
        mock_config_manager.get_data_path.side_effect = FileNotFoundError()
        
        generator = PhishingGenerator()
        
        # Должны использоваться значения по умолчанию
        assert len(generator.suspicious_keywords) > 0
        assert len(generator.email_templates) > 0
    
    @patch('attack.phishing_generator.config_manager')
    def test_generate_email_success(self, mock_config_manager):
        """Тест успешной генерации письма"""
        mock_config_manager.get_attack_config.return_value = self.mock_config
        
        generator = PhishingGenerator()
        email = generator.generate_email("Test prompt", "test_user", "high")
        
        assert email is not None
        assert len(email) > 0
        assert "Test prompt" in email
        assert generator.generation_stats['total_generated'] == 1
    
    @patch('attack.phishing_generator.config_manager')
    def test_generate_email_with_timeout(self, mock_config_manager):
        """Тест генерации с таймаутом"""
        mock_config_manager.get_attack_config.return_value = {
            'phishing': {
                'max_length': 1000,
                'suspicious_keywords_file': self.keywords_file,
                'email_templates_file': self.templates_file,
                'generation_timeout': 0.001  # Очень короткий таймаут
            }
        }
        
        generator = PhishingGenerator()
        
        with pytest.raises(TimeoutError):
            generator.generate_email("Test prompt", "test_user", "high")
        
        assert generator.generation_stats['failed_attacks'] == 1
    
    @patch('attack.phishing_generator.config_manager')
    def test_generate_email_length_limit(self, mock_config_manager):
        """Тест ограничения длины письма"""
        mock_config_manager.get_attack_config.return_value = {
            'phishing': {
                'max_length': 50,  # Короткий лимит
                'suspicious_keywords_file': self.keywords_file,
                'email_templates_file': self.templates_file,
                'generation_timeout': 30
            }
        }
        
        generator = PhishingGenerator()
        email = generator.generate_email("Very long prompt that exceeds the limit", "test_user", "high")
        
        assert len(email) <= 50
        assert email.endswith("...")
    
    @patch('attack.phishing_generator.config_manager')
    def test_urgency_levels(self, mock_config_manager):
        """Тест различных уровней срочности"""
        mock_config_manager.get_attack_config.return_value = self.mock_config
        
        generator = PhishingGenerator()
        
        # Тест низкой срочности
        email_low = generator.generate_email("Test", "user", "low")
        assert any(word in email_low for word in ["Please", "Kindly"])
        
        # Тест высокой срочности
        email_high = generator.generate_email("Test", "user", "high")
        assert any(word in email_high for word in ["URGENT", "IMMEDIATE", "CRITICAL"])
    
    @patch('attack.phishing_generator.config_manager')
    def test_get_generation_stats(self, mock_config_manager):
        """Тест получения статистики"""
        mock_config_manager.get_attack_config.return_value = self.mock_config
        
        generator = PhishingGenerator()
        
        # Генерируем несколько писем
        generator.generate_email("Test 1", "user1")
        generator.generate_email("Test 2", "user2")
        
        stats = generator.get_generation_stats()
        
        assert stats['total_generated'] == 2
        assert stats['successful_attacks'] == 0
        assert stats['failed_attacks'] == 0
    
    @patch('attack.phishing_generator.config_manager')
    def test_reset_stats(self, mock_config_manager):
        """Тест сброса статистики"""
        mock_config_manager.get_attack_config.return_value = self.mock_config
        
        generator = PhishingGenerator()
        
        # Генерируем письмо
        generator.generate_email("Test", "user")
        
        # Сбрасываем статистику
        generator.reset_stats()
        
        stats = generator.get_generation_stats()
        assert stats['total_generated'] == 0
        assert stats['successful_attacks'] == 0
        assert stats['failed_attacks'] == 0

class TestLegacyFunctions:
    """Тесты для функций обратной совместимости"""
    
    @patch('attack.phishing_generator.PhishingGenerator')
    def test_generate_email_function(self, mock_generator_class):
        """Тест функции generate_email для обратной совместимости"""
        mock_generator = MagicMock()
        mock_generator.generate_email.return_value = "Test email"
        mock_generator_class.return_value = mock_generator
        
        from attack.phishing_generator import generate_email
        
        result = generate_email("Test prompt", "test_user")
        
        assert result == "Test email"
        mock_generator.generate_email.assert_called_once_with("Test prompt", "test_user")
