import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from defense.detector import ThreatDetector

class TestThreatDetector:
    """Тесты для детектора угроз"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.patterns_file = os.path.join(self.temp_dir, "suspicious_patterns.json")
        
        # Создание временного файла с паттернами
        test_patterns = [
            {
                "name": "urgent_action",
                "pattern": r"\b(urgent|immediate|critical)\b",
                "weight": 0.3,
                "description": "Срочные действия"
            },
            {
                "name": "password_reset",
                "pattern": r"\b(password|reset)\b",
                "weight": 0.4,
                "description": "Сброс пароля"
            }
        ]
        
        with open(self.patterns_file, 'w') as f:
            json.dump(test_patterns, f)
        
        # Мокаем конфигурацию
        self.mock_config = {
            'detector': {
                'confidence_threshold': 0.8,
                'model_path': 'models/detector.pkl',
                'suspicious_patterns_file': self.patterns_file
            }
        }
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('defense.detector.config_manager')
    def test_init_with_files(self, mock_config_manager):
        """Тест инициализации с существующими файлами"""
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        assert len(detector.suspicious_patterns) == 2
        assert detector.confidence_threshold == 0.8
        assert detector.detection_stats['total_checks'] == 0
    
    @patch('defense.detector.config_manager')
    def test_init_without_files(self, mock_config_manager):
        """Тест инициализации без файлов"""
        mock_config_manager.get_defense_config.return_value = self.mock_config
        mock_config_manager.get_data_path.side_effect = FileNotFoundError()
        
        detector = ThreatDetector()
        
        # Должны использоваться паттерны по умолчанию
        assert len(detector.suspicious_patterns) > 0
    
    @patch('defense.detector.config_manager')
    def test_is_suspicious_high_threat(self, mock_config_manager):
        """Тест обнаружения высокой угрозы"""
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        # Контент с множественными подозрительными элементами
        suspicious_content = "URGENT: Reset your password immediately! Click here: https://fake.com"
        
        is_threat, confidence, patterns = detector.is_suspicious(suspicious_content)
        
        assert is_threat == True
        assert confidence > 0.8
        assert len(patterns) > 0
        assert detector.detection_stats['threats_detected'] == 1
    
    @patch('defense.detector.config_manager')
    def test_is_suspicious_low_threat(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        # Контент с низкой угрозой
        low_threat_content = "Hello, how are you today?"
        
        is_threat, confidence, patterns = detector.is_suspicious(low_threat_content)
        
        assert is_threat == False
        assert confidence < 0.8
        assert detector.detection_stats['total_checks'] == 1
    
    @patch('defense.detector.config_manager')
    def test_is_suspicious_medium_threat(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        # Контент со средней угрозой
        medium_threat_content = "Please reset your password when convenient"
        
        is_threat, confidence, patterns = detector.is_suspicious(medium_threat_content)
        
        # Результат зависит от порога уверенности
        assert confidence > 0
        assert detector.detection_stats['total_checks'] == 1
    
    @patch('defense.detector.config_manager')
    def test_analyze_content_patterns(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        content = "URGENT password reset required"
        threat_score, detected_patterns = detector._analyze_content(content)
        
        assert threat_score > 0
        assert 'urgent_action' in detected_patterns
        assert 'password_reset' in detected_patterns
    
    @patch('defense.detector.config_manager')
    def test_get_detection_stats(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        # Выполняем несколько проверок
        detector.is_suspicious("Test content 1")
        detector.is_suspicious("URGENT password reset")
        
        stats = detector.get_detection_stats()
        
        assert stats['total_checks'] == 2
        assert stats['threats_detected'] >= 1
        assert stats['average_confidence'] > 0
    
    @patch('defense.detector.config_manager')
    def test_reset_stats(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        # Выполняем проверку
        detector.is_suspicious("Test content")
        
        # Сбрасываем статистику
        detector.reset_stats()
        
        stats = detector.get_detection_stats()
        assert stats['total_checks'] == 0
        assert stats['threats_detected'] == 0
        assert stats['average_confidence'] == 0.0
    
    @patch('defense.detector.config_manager')
    def test_update_confidence_threshold(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        old_threshold = detector.confidence_threshold
        
        # Обновляем порог
        detector.update_confidence_threshold(0.5)
        
        assert detector.confidence_threshold == 0.5
        assert detector.confidence_threshold != old_threshold
    
    @patch('defense.detector.config_manager')
    def test_update_confidence_threshold_invalid(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        # Тест недопустимых значений
        with pytest.raises(ValueError):
            detector.update_confidence_threshold(1.5)
        
        with pytest.raises(ValueError):
            detector.update_confidence_threshold(-0.1)
    
    @patch('defense.detector.config_manager')
    def test_add_custom_pattern(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        initial_patterns = len(detector.suspicious_patterns)
        
        # Добавляем пользовательский паттерн
        detector.add_custom_pattern(
            "test_pattern",
            r"\btest\b",
            0.5,
            "Test pattern"
        )
        
        assert len(detector.suspicious_patterns) == initial_patterns + 1
        
        # Проверяем, что паттерн работает
        content = "This is a test message"
        threat_score, patterns = detector._analyze_content(content)
        
        assert threat_score > 0
        assert 'test_pattern' in patterns
    
    @patch('defense.detector.config_manager')
    def test_add_custom_pattern_invalid_weight(self, mock_config_manager):
        mock_config_manager.get_defense_config.return_value = self.mock_config
        
        detector = ThreatDetector()
        
        # Тест недопустимого веса
        with pytest.raises(ValueError):
            detector.add_custom_pattern("test", r"\btest\b", 1.5, "Test")
        
        with pytest.raises(ValueError):
            detector.add_custom_pattern("test", r"\btest\b", -0.1, "Test")

class TestLegacyFunctions:
    """Тесты для функций обратной совместимости"""
    
    @patch('defense.detector.ThreatDetector')
    def test_is_suspicious_function(self, mock_detector_class):
        mock_detector = MagicMock()
        mock_detector.is_suspicious.return_value = (True, 0.9, {})
        mock_detector_class.return_value = mock_detector
        
        from defense.detector import is_suspicious
        
        result = is_suspicious("Test content")
        
        assert result == True
        mock_detector.is_suspicious.assert_called_once_with("Test content")
