#!/usr/bin/env python3
"""
Веб-приложение для LLM Attack Simulation
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sys
import os
import json
import time
from datetime import datetime

# Добавляем путь к основному проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import LLMAttackSimulator
from attack.phishing_generator import PhishingGenerator
from defense.detector import ThreatDetector
from simulation.network import NetworkSimulator
from utils.config_manager import config_manager
from utils.logger import main_logger

app = Flask(__name__)
app.secret_key = 'llm_attack_sim_secret_key_2024'

# Глобальные экземпляры
simulator = None
phishing_generator = None
threat_detector = None
network_simulator = None

def initialize_components():
    """Инициализация компонентов симуляции"""
    global simulator, phishing_generator, threat_detector, network_simulator
    
    try:
        simulator = LLMAttackSimulator()
        phishing_generator = PhishingGenerator()
        threat_detector = ThreatDetector()
        network_simulator = NetworkSimulator()
        main_logger.log_event("WEB_APP_START", "Web application components initialized", level="INFO")
        return True
    except Exception as e:
        main_logger.log_event("WEB_APP_ERROR", f"Failed to initialize components: {e}", level="ERROR")
        return False

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Панель управления"""
    try:
        # Получаем статистику
        attack_stats = phishing_generator.get_generation_stats() if phishing_generator else {}
        defense_stats = threat_detector.get_detection_stats() if threat_detector else {}
        network_stats = network_simulator.get_network_stats() if network_simulator else {}
        
        # Получаем конфигурацию
        config = {
            'logging': config_manager.get_logging_config(),
            'attack': config_manager.get_attack_config(),
            'defense': config_manager.get_defense_config(),
            'simulation': config_manager.get_simulation_config()
        }
        
        return render_template('dashboard.html', 
                             attack_stats=attack_stats,
                             defense_stats=defense_stats,
                             network_stats=network_stats,
                             config=config)
    except Exception as e:
        flash(f'Ошибка при загрузке панели: {e}', 'error')
        return render_template('dashboard.html', 
                             attack_stats={}, 
                             defense_stats={}, 
                             network_stats={}, 
                             config={})

@app.route('/simulation')
def simulation():
    """Страница симуляции"""
    return render_template('simulation.html')

@app.route('/attack')
def attack():
    """Страница атак"""
    try:
        # Получаем подозрительные ключевые слова
        keywords = phishing_generator.suspicious_keywords if phishing_generator else []
        templates = phishing_generator.email_templates if phishing_generator else []
        
        return render_template('attack.html', 
                             keywords=keywords[:20],  # Показываем первые 20
                             templates=templates[:10],  # Показываем первые 10
                             stats=phishing_generator.get_generation_stats() if phishing_generator else {})
    except Exception as e:
        flash(f'Ошибка при загрузке страницы атак: {e}', 'error')
        return render_template('attack.html', keywords=[], templates=[], stats={})

@app.route('/defense')
def defense():
    """Страница защиты"""
    try:
        # Получаем паттерны угроз
        patterns = threat_detector.suspicious_patterns if threat_detector else []
        
        return render_template('defense.html', 
                             patterns=patterns[:15],  # Показываем первые 15
                             stats=threat_detector.get_detection_stats() if threat_detector else {})
    except Exception as e:
        flash(f'Ошибка при загрузке страницы защиты: {e}', 'error')
        return render_template('defense.html', patterns=[], stats={})

@app.route('/network')
def network():
    """Страница сети"""
    try:
        network_stats = network_simulator.get_network_stats() if network_simulator else {}
        return render_template('network.html', stats=network_stats)
    except Exception as e:
        flash(f'Ошибка при загрузке страницы сети: {e}', 'error')
        return render_template('network.html', stats={})

@app.route('/logs')
def logs():
    """Страница логов"""
    try:
        # Читаем последние логи
        log_file = config_manager.get('logging.file', 'logs/simulation.log')
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Показываем последние 100 строк
                logs = lines[-100:] if len(lines) > 100 else lines
        
        return render_template('logs.html', logs=logs)
    except Exception as e:
        flash(f'Ошибка при загрузке логов: {e}', 'error')
        return render_template('logs.html', logs=[])

@app.route('/config')
def config_page():
    """Страница конфигурации"""
    try:
        config = {
            'logging': config_manager.get_logging_config(),
            'attack': config_manager.get_attack_config(),
            'defense': config_manager.get_defense_config(),
            'simulation': config_manager.get_simulation_config(),
            'testing': config_manager.get_testing_config()
        }
        return render_template('config.html', config=config)
    except Exception as e:
        flash(f'Ошибка при загрузке конфигурации: {e}', 'error')
        return render_template('config.html', config={})

# API маршруты
@app.route('/api/run_simulation', methods=['POST'])
def api_run_simulation():
    """API для запуска симуляции"""
    try:
        data = request.get_json()
        num_attacks = data.get('num_attacks', 5)
        
        if not simulator:
            return jsonify({'error': 'Симулятор не инициализирован'}), 500
        
        results = simulator.run_simulation(num_attacks=num_attacks)
        
        main_logger.log_event("WEB_SIMULATION", f"Web simulation run with {num_attacks} attacks", level="INFO")
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        main_logger.log_event("WEB_SIMULATION_ERROR", f"Web simulation failed: {e}", level="ERROR")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_phishing', methods=['POST'])
def api_generate_phishing():
    """API для генерации фишингового письма"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Verify your account')
        target = data.get('target', 'user@example.com')
        urgency = data.get('urgency', 'medium')
        
        if not phishing_generator:
            return jsonify({'error': 'Генератор не инициализирован'}), 500
        
        email = phishing_generator.generate_email(prompt, target, urgency)
        
        return jsonify({
            'success': True,
            'email': email,
            'stats': phishing_generator.get_generation_stats()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check_threat', methods=['POST'])
def api_check_threat():
    """API для проверки угрозы"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not threat_detector:
            return jsonify({'error': 'Детектор не инициализирован'}), 500
        
        is_threat, confidence, patterns = threat_detector.is_suspicious(content)
        
        return jsonify({
            'success': True,
            'is_threat': is_threat,
            'confidence': confidence,
            'patterns': patterns,
            'stats': threat_detector.get_detection_stats()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_network', methods=['POST'])
def api_create_network():
    """API для создания сети"""
    try:
        data = request.get_json()
        num_nodes = data.get('num_nodes', 10)
        
        if not network_simulator:
            return jsonify({'error': 'Симулятор сети не инициализирован'}), 500
        
        nodes = network_simulator.create_network(num_nodes)
        stats = network_simulator.get_network_stats()
        
        return jsonify({
            'success': True,
            'nodes_created': len(nodes),
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate_attack', methods=['POST'])
def api_simulate_attack():
    """API для симуляции атаки на сеть"""
    try:
        data = request.get_json()
        attack_type = data.get('attack_type', 'phishing')
        target_node = data.get('target_node', None)
        
        if not network_simulator:
            return jsonify({'error': 'Симулятор сети не инициализирован'}), 500
        
        result = network_simulator.simulate_attack(attack_type, target_node)
        
        return jsonify({
            'success': True,
            'result': result,
            'stats': network_simulator.get_network_stats()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_stats')
def api_get_stats():
    """API для получения общей статистики"""
    try:
        stats = {
            'attack': phishing_generator.get_generation_stats() if phishing_generator else {},
            'defense': threat_detector.get_detection_stats() if threat_detector else {},
            'network': network_simulator.get_network_stats() if network_simulator else {},
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_stats', methods=['POST'])
def api_reset_stats():
    """API для сброса статистики"""
    try:
        if phishing_generator:
            phishing_generator.reset_stats()
        if threat_detector:
            threat_detector.reset_stats()
        if network_simulator:
            network_simulator.reset_network()
        
        main_logger.log_event("WEB_RESET", "Statistics reset via web interface", level="INFO")
        
        return jsonify({'success': True, 'message': 'Статистика сброшена'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Обработчик 404 ошибки"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик 500 ошибки"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Инициализируем компоненты
    if initialize_components():
        print("✅ Веб-приложение инициализировано успешно")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Ошибка инициализации веб-приложения")
        sys.exit(1)
