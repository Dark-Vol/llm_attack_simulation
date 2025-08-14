import pytest
from unittest.mock import patch, MagicMock
from simulation.network import NetworkNode, NetworkSimulator

class TestNetworkNode:
    """Тесты для узла сети"""
    
    def test_node_creation(self):
        """Тест создания узла"""
        node = NetworkNode("test_node", "user")
        
        assert node.node_id == "test_node"
        assert node.node_type == "user"
        assert len(node.connections) == 0
        assert len(node.vulnerabilities) == 0
        assert len(node.attack_history) == 0
        assert node.is_compromised == False
        assert 0.1 <= node.security_level <= 1.0
    
    def test_add_connection(self):
        """Тест добавления соединения"""
        node1 = NetworkNode("node1", "user")
        node2 = NetworkNode("node2", "server")
        
        node1.add_connection(node2)
        
        assert node2 in node1.connections
        assert node1 in node2.connections
    
    def test_add_vulnerability(self):
        """Тест добавления уязвимости"""
        node = NetworkNode("test_node", "user")
        
        node.add_vulnerability("weak_password", 0.5)
        
        assert len(node.vulnerabilities) == 1
        assert node.vulnerabilities[0]['type'] == "weak_password"
        assert node.vulnerabilities[0]['severity'] == 0.5
        assert 'discovered' in node.vulnerabilities[0]
    
    def test_record_attack_success(self):
        """Тест записи успешной атаки"""
        node = NetworkNode("test_node", "user")
        
        attack_details = {"method": "phishing", "source": "attacker"}
        node.record_attack("phishing", True, attack_details)
        
        assert len(node.attack_history) == 1
        assert node.attack_history[0]['type'] == "phishing"
        assert node.attack_history[0]['success'] == True
        assert node.is_compromised == True
    
    def test_record_attack_failure(self):
        """Тест записи неуспешной атаки"""
        node = NetworkNode("test_node", "user")
        
        attack_details = {"method": "brute_force", "source": "attacker"}
        node.record_attack("brute_force", False, attack_details)
        
        assert len(node.attack_history) == 1
        assert node.attack_history[0]['type'] == "brute_force"
        assert node.attack_history[0]['success'] == False
        assert node.is_compromised == False
    
    def test_get_security_score_no_vulnerabilities(self):
        """Тест оценки безопасности без уязвимостей"""
        node = NetworkNode("test_node", "user")
        node.security_level = 0.8
        
        score = node.get_security_score()
        
        assert score == 0.8
    
    def test_get_security_score_with_vulnerabilities(self):
        """Тест оценки безопасности с уязвимостями"""
        node = NetworkNode("test_node", "user")
        node.security_level = 0.8
        
        node.add_vulnerability("weak_password", 0.3)
        node.add_vulnerability("open_port", 0.2)
        
        score = node.get_security_score()
        
        # Ожидаемая оценка: 0.8 - (0.3 + 0.2) * 0.1 = 0.8 - 0.05 = 0.75
        expected_score = 0.8 - (0.3 + 0.2) * 0.1
        assert abs(score - expected_score) < 0.001
    
    def test_get_security_score_compromised(self):
        """Тест оценки безопасности скомпрометированного узла"""
        node = NetworkNode("test_node", "user")
        node.security_level = 0.8
        
        node.record_attack("phishing", True, {})
        
        score = node.get_security_score()
        
        # Ожидаемая оценка: 0.8 - 0.5 = 0.3
        expected_score = 0.8 - 0.5
        assert abs(score - expected_score) < 0.001

class TestNetworkSimulator:
    """Тесты для симулятора сети"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_config = {
            'network': {
                'max_nodes': 50,
                'connection_timeout': 30,
                'retry_attempts': 3
            }
        }
    
    @patch('simulation.network.config_manager')
    def test_init(self, mock_config_manager):
        """Тест инициализации симулятора"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        
        assert len(simulator.nodes) == 0
        assert len(simulator.connections) == 0
        assert simulator.simulation_stats['total_nodes'] == 0
        assert simulator.simulation_stats['network_integrity'] == 1.0
    
    @patch('simulation.network.config_manager')
    def test_create_network(self, mock_config_manager):
        """Тест создания сети"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        nodes = simulator.create_network(5)
        
        assert len(nodes) == 5
        assert len(simulator.nodes) == 5
        assert simulator.simulation_stats['total_nodes'] == 5
        assert len(simulator.connections) > 0
    
    @patch('simulation.network.config_manager')
    def test_create_network_default_size(self, mock_config_manager):
        """Тест создания сети с размером по умолчанию"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        nodes = simulator.create_network()
        
        assert len(nodes) == 50  # max_nodes из конфигурации
        assert simulator.simulation_stats['total_nodes'] == 50
    
    @patch('simulation.network.config_manager')
    def test_simulate_attack(self, mock_config_manager):
        """Тест симуляции атаки"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        simulator.create_network(3)
        
        result = simulator.simulate_attack("phishing")
        
        assert 'attack_type' in result
        assert 'target_node' in result
        assert 'success' in result
        assert 'details' in result
        assert 'network_stats' in result
        assert simulator.simulation_stats['total_attacks'] == 1
    
    @patch('simulation.network.config_manager')
    def test_simulate_attack_no_network(self, mock_config_manager):
        """Тест симуляции атаки без сети"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        
        with pytest.raises(ValueError, match="Network not created"):
            simulator.simulate_attack("phishing")
    
    @patch('simulation.network.config_manager')
    def test_simulate_attack_specific_target(self, mock_config_manager):
        """Тест симуляции атаки на конкретный узел"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        nodes = simulator.create_network(3)
        
        target_node_id = list(nodes.keys())[0]
        result = simulator.simulate_attack("brute_force", target_node_id)
        
        assert result['target_node'] == target_node_id
        assert result['attack_type'] == "brute_force"
    
    @patch('simulation.network.config_manager')
    def test_calculate_attack_success(self, mock_config_manager):
        """Тест расчета вероятности успеха атаки"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        simulator.create_network(3)
        
        # Получаем первый узел
        target_node = list(simulator.nodes.values())[0]
        
        # Тест различных типов атак
        phishing_success = simulator._calculate_attack_success("phishing", target_node)
        brute_force_success = simulator._calculate_attack_success("brute_force", target_node)
        
        assert 0.05 <= phishing_success <= 0.95
        assert 0.05 <= brute_force_success <= 0.95
        assert phishing_success != brute_force_success
    
    @patch('simulation.network.config_manager')
    def test_calculate_network_integrity(self, mock_config_manager):
        """Тест расчета целостности сети"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        
        # Сеть без узлов
        integrity_empty = simulator._calculate_network_integrity()
        assert integrity_empty == 1.0
        
        # Сеть с узлами
        simulator.create_network(3)
        integrity_with_nodes = simulator._calculate_network_integrity()
        
        assert 0.0 <= integrity_with_nodes <= 1.0
    
    @patch('simulation.network.config_manager')
    def test_get_network_stats(self, mock_config_manager):
        """Тест получения статистики сети"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        simulator.create_network(5)
        
        stats = simulator.get_network_stats()
        
        assert 'total_nodes' in stats
        assert 'compromised_nodes' in stats
        assert 'total_connections' in stats
        assert 'network_integrity' in stats
        assert 'node_types' in stats
        assert 'vulnerability_distribution' in stats
        
        assert stats['total_nodes'] == 5
        assert stats['compromised_nodes'] == 0
        assert stats['total_connections'] > 0
    
    @patch('simulation.network.config_manager')
    def test_reset_network(self, mock_config_manager):
        """Тест сброса сети"""
        mock_config_manager.get_simulation_config.return_value = self.mock_config
        
        simulator = NetworkSimulator()
        simulator.create_network(3)
        
        # Проверяем, что сеть создана
        assert len(simulator.nodes) == 3
        
        # Сбрасываем сеть
        simulator.reset_network()
        
        assert len(simulator.nodes) == 0
        assert len(simulator.connections) == 0
        assert simulator.simulation_stats['total_nodes'] == 0
        assert simulator.simulation_stats['network_integrity'] == 1.0

class TestAttackSuccessCalculation:
    """Тесты для расчета успеха атак"""
    
    @patch('simulation.network.config_manager')
    def test_attack_success_modifiers(self, mock_config_manager):
        """Тест модификаторов успеха атаки"""
        mock_config_manager.get_simulation_config.return_value = {
            'network': {'max_nodes': 10, 'connection_timeout': 30, 'retry_attempts': 3}
        }
        
        simulator = NetworkSimulator()
        simulator.create_network(3)
        
        target_node = list(simulator.nodes.values())[0]
        
        # Тест базовой вероятности
        base_success = simulator._calculate_attack_success("unknown", target_node)
        assert base_success >= 0.3  # Базовая вероятность
        
        # Тест различных типов атак
        exploit_success = simulator._calculate_attack_success("exploit", target_node)
        social_success = simulator._calculate_attack_success("social_engineering", target_node)
        
        assert exploit_success > base_success
        assert social_success > base_success
    
    @patch('simulation.network.config_manager')
    def test_vulnerability_impact(self, mock_config_manager):
        """Тест влияния уязвимостей на успех атаки"""
        mock_config_manager.get_simulation_config.return_value = {
            'network': {'max_nodes': 10, 'connection_timeout': 30, 'retry_attempts': 3}
        }
        
        simulator = NetworkSimulator()
        simulator.create_network(3)
        
        target_node = list(simulator.nodes.values())[0]
        
        # Атака на узел без уязвимостей
        success_no_vuln = simulator._calculate_attack_success("phishing", target_node)
        
        # Добавляем уязвимость
        target_node.add_vulnerability("weak_password", 0.5)
        success_with_vuln = simulator._calculate_attack_success("phishing", target_node)
        
        assert success_with_vuln > success_no_vuln
