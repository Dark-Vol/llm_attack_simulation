import time
import random
from typing import Dict, List, Any, Optional
from utils.logger import simulation_logger
from utils.config_manager import config_manager

class NetworkNode:
    """Узел сети для симуляции"""
    
    def __init__(self, node_id: str, node_type: str = "user"):
        self.node_id = node_id
        self.node_type = node_type
        self.connections = []
        self.vulnerabilities = []
        self.attack_history = []
        self.is_compromised = False
        self.security_level = random.uniform(0.1, 1.0)
        
    def add_connection(self, target_node: 'NetworkNode'):
        """Добавление соединения с другим узлом"""
        if target_node not in self.connections:
            self.connections.append(target_node)
            target_node.connections.append(self)
    
    def add_vulnerability(self, vulnerability_type: str, severity: float):
        """Добавление уязвимости к узлу"""
        self.vulnerabilities.append({
            'type': vulnerability_type,
            'severity': severity,
            'discovered': time.time()
        })
    
    def record_attack(self, attack_type: str, success: bool, details: Dict[str, Any]):
        """Запись атаки на узел"""
        attack_record = {
            'timestamp': time.time(),
            'type': attack_type,
            'success': success,
            'details': details
        }
        self.attack_history.append(attack_record)
        
        if success:
            self.is_compromised = True
    
    def get_security_score(self) -> float:
        """Получение оценки безопасности узла"""
        base_score = self.security_level
        
        # Уменьшение оценки за уязвимости
        vulnerability_penalty = sum(v['severity'] for v in self.vulnerabilities) * 0.1
        
        # Уменьшение оценки за компрометацию
        compromise_penalty = 0.5 if self.is_compromised else 0.0
        
        return max(0.0, base_score - vulnerability_penalty - compromise_penalty)

class NetworkSimulator:
    """Симулятор сети для моделирования атак"""
    
    def __init__(self):
        self.config = config_manager.get_simulation_config()
        self.nodes = {}
        self.connections = []
        self.simulation_stats = {
            'total_nodes': 0,
            'compromised_nodes': 0,
            'total_attacks': 0,
            'successful_attacks': 0,
            'network_integrity': 1.0
        }
        
        simulation_logger.log_event(
            "NETWORK_INIT",
            "Network simulator initialized",
            details={'config': self.config}
        )
    
    def create_network(self, num_nodes: int = None) -> Dict[str, NetworkNode]:
        """Создание сети с заданным количеством узлов"""
        if num_nodes is None:
            num_nodes = self.config['network']['max_nodes']
        
        simulation_logger.log_event(
            "NETWORK_CREATION_START",
            f"Creating network with {num_nodes} nodes",
            details={'num_nodes': num_nodes}
        )
        
        # Создание узлов
        node_types = ['user', 'server', 'router', 'database']
        for i in range(num_nodes):
            node_type = random.choice(node_types)
            node_id = f"{node_type}_{i+1}"
            
            node = NetworkNode(node_id, node_type)
            
            # Добавление случайных уязвимостей
            if random.random() < 0.3:  # 30% вероятность уязвимости
                vulnerability_types = ['weak_password', 'outdated_software', 'open_port', 'misconfiguration']
                vulnerability_type = random.choice(vulnerability_types)
                severity = random.uniform(0.1, 0.8)
                node.add_vulnerability(vulnerability_type, severity)
            
            self.nodes[node_id] = node
        
        # Создание соединений между узлами
        self._create_connections()
        
        # Обновление статистики
        self.simulation_stats['total_nodes'] = len(self.nodes)
        self.simulation_stats['network_integrity'] = self._calculate_network_integrity()
        
        simulation_logger.log_event(
            "NETWORK_CREATION_COMPLETE",
            f"Network created successfully with {len(self.nodes)} nodes",
            details={
                'total_nodes': len(self.nodes),
                'total_connections': len(self.connections),
                'network_integrity': self.simulation_stats['network_integrity']
            }
        )
        
        return self.nodes
    
    def _create_connections(self):
        """Создание соединений между узлами"""
        node_list = list(self.nodes.values())
        
        # Создание базовой связности (каждый узел соединен хотя бы с одним другим)
        for i, node in enumerate(node_list):
            if i > 0:
                target = random.choice(node_list[:i])
                node.add_connection(target)
                self.connections.append((node.node_id, target.node_id))
        
        # Добавление случайных дополнительных соединений
        max_connections = min(len(node_list) * 2, 50)  # Ограничение на количество соединений
        
        while len(self.connections) < max_connections:
            node1 = random.choice(node_list)
            node2 = random.choice(node_list)
            
            if node1 != node2 and (node1.node_id, node2.node_id) not in self.connections:
                node1.add_connection(node2)
                self.connections.append((node1.node_id, node2.node_id))
    
    def simulate_attack(self, attack_type: str, target_node_id: str = None) -> Dict[str, Any]:
        """Симуляция атаки на сеть"""
        if not self.nodes:
            raise ValueError("Network not created. Call create_network() first.")
        
        # Выбор целевого узла
        if target_node_id is None:
            target_node_id = random.choice(list(self.nodes.keys()))
        
        target_node = self.nodes[target_node_id]
        
        simulation_logger.log_event(
            "ATTACK_SIMULATION_START",
            f"Simulating {attack_type} attack on {target_node_id}",
            details={
                'attack_type': attack_type,
                'target_node': target_node_id,
                'target_type': target_node.node_type
            }
        )
        
        # Расчет вероятности успеха атаки
        success_probability = self._calculate_attack_success(attack_type, target_node)
        attack_success = random.random() < success_probability
        
        # Детали атаки
        attack_details = {
            'attack_type': attack_type,
            'target_node': target_node_id,
            'target_vulnerabilities': len(target_node.vulnerabilities),
            'target_security_score': target_node.get_security_score(),
            'success_probability': success_probability,
            'timestamp': time.time()
        }
        
        # Запись атаки в узел
        target_node.record_attack(attack_type, attack_success, attack_details)
        
        # Обновление статистики
        self.simulation_stats['total_attacks'] += 1
        if attack_success:
            self.simulation_stats['successful_attacks'] += 1
            self.simulation_stats['compromised_nodes'] = sum(
                1 for node in self.nodes.values() if node.is_compromised
            )
        
        # Обновление целостности сети
        self.simulation_stats['network_integrity'] = self._calculate_network_integrity()
        
        simulation_logger.log_simulation(
            f"{attack_type.upper()}_ATTACK",
            {
                'attack_details': attack_details,
                'success': attack_success,
                'network_stats': self.simulation_stats.copy()
            }
        )
        
        return {
            'attack_type': attack_type,
            'target_node': target_node_id,
            'success': attack_success,
            'details': attack_details,
            'network_stats': self.simulation_stats.copy()
        }
    
    def _calculate_attack_success(self, attack_type: str, target_node: NetworkNode) -> float:
        """Расчет вероятности успеха атаки"""
        base_success_rate = 0.3
        
        # Модификаторы на основе типа атаки
        attack_modifiers = {
            'phishing': 0.4,
            'brute_force': 0.2,
            'exploit': 0.6,
            'social_engineering': 0.5
        }
        
        attack_modifier = attack_modifiers.get(attack_type, 0.3)
        
        # Модификаторы на основе уязвимостей узла
        vulnerability_modifier = sum(v['severity'] for v in target_node.vulnerabilities) * 0.2
        
        # Модификаторы на основе уровня безопасности
        security_modifier = (1.0 - target_node.get_security_score()) * 0.3
        
        # Итоговая вероятность
        final_success_rate = base_success_rate + attack_modifier + vulnerability_modifier + security_modifier
        
        return min(0.95, max(0.05, final_success_rate))  # Ограничение от 5% до 95%
    
    def _calculate_network_integrity(self) -> float:
        """Расчет целостности сети"""
        if not self.nodes:
            return 1.0
        
        total_security_score = sum(node.get_security_score() for node in self.nodes.values())
        compromised_nodes = sum(1 for node in self.nodes.values() if node.is_compromised)
        
        # Базовая целостность на основе среднего уровня безопасности
        base_integrity = total_security_score / len(self.nodes)
        
        # Штраф за скомпрометированные узлы
        compromise_penalty = (compromised_nodes / len(self.nodes)) * 0.5
        
        return max(0.0, base_integrity - compromise_penalty)
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Получение статистики сети"""
        return {
            'total_nodes': len(self.nodes),
            'compromised_nodes': sum(1 for node in self.nodes.values() if node.is_compromised),
            'total_connections': len(self.connections),
            'network_integrity': self._calculate_network_integrity(),
            'node_types': {
                node_type: sum(1 for node in self.nodes.values() if node.node_type == node_type)
                for node_type in set(node.node_type for node in self.nodes.values())
            },
            'vulnerability_distribution': {
                'nodes_with_vulnerabilities': sum(1 for node in self.nodes.values() if node.vulnerabilities),
                'total_vulnerabilities': sum(len(node.vulnerabilities) for node in self.nodes.values())
            }
        }
    
    def reset_network(self):
        """Сброс сети"""
        self.nodes.clear()
        self.connections.clear()
        self.simulation_stats = {
            'total_nodes': 0,
            'compromised_nodes': 0,
            'total_attacks': 0,
            'successful_attacks': 0,
            'network_integrity': 1.0
        }
        
        simulation_logger.log_event(
            "NETWORK_RESET",
            "Network reset completed",
            level="INFO"
        )