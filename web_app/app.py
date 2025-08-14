from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import os
import sys
from datetime import datetime
import threading
import time

# Додавання шляху до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.config_manager import ConfigManager
from utils.logger import logger
from attack.llm_attack_generator import LLMAttackGenerator
from defense.defense_analyzer import DefenseAnalyzer
from simulation.attack_simulator import AttackSimulator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Ініціалізація компонентів
config = ConfigManager()
attack_generator = LLMAttackGenerator()
defense_analyzer = DefenseAnalyzer()
attack_simulator = AttackSimulator()

# Глобальні змінні для зберігання стану
active_simulations = {}
simulation_results = {}

@app.route('/')
def index():
    """Головна сторінка"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Панель керування"""
    try:
        # Отримання статистики
        attack_stats = attack_generator.get_attack_statistics()
        defense_stats = defense_analyzer.get_defense_statistics()
        simulation_stats = attack_simulator.get_system_statistics()
        
        dashboard_data = {
            'attack_stats': attack_stats,
            'defense_stats': defense_stats,
            'simulation_stats': simulation_stats,
            'system_info': {
                'name': config.get('system.name', 'LLM Attack Analysis System'),
                'version': config.get('system.version', '1.0.0'),
                'status': 'active'
            }
        }
        
        return render_template('dashboard.html', data=dashboard_data)
        
    except Exception as e:
        logger.error(f"Помилка завантаження dashboard: {e}")
        return render_template('error.html', error=str(e))

@app.route('/attack')
def attack_page():
    """Сторінка генерації атак"""
    try:
        attack_types = attack_generator.get_available_attack_types()
        return render_template('attack.html', attack_types=attack_types)
    except Exception as e:
        logger.error(f"Помилка завантаження сторінки атак: {e}")
        return render_template('error.html', error=str(e))

@app.route('/defense')
def defense_page():
    """Сторінка аналізу захисту"""
    try:
        defense_stats = defense_analyzer.get_defense_statistics()
        return render_template('defense.html', defense_stats=defense_stats)
    except Exception as e:
        logger.error(f"Помилка завантаження сторінки захисту: {e}")
        return render_template('error.html', error=str(e))

@app.route('/simulation')
def simulation_page():
    """Сторінка симуляції атак"""
    try:
        running_sims = attack_simulator.get_running_simulations()
        simulation_stats = attack_simulator.get_system_statistics()
        
        return render_template('simulation.html', 
                             running_simulations=running_sims,
                             simulation_stats=simulation_stats)
    except Exception as e:
        logger.error(f"Помилка завантаження сторінки симуляції: {e}")
        return render_template('error.html', error=str(e))

@app.route('/network')
def network_page():
    """Сторінка аналізу мережі"""
    return render_template('network.html')

@app.route('/logs')
def logs_page():
    """Сторінка логів"""
    try:
        # Читання логів (спрощена версія)
        log_file = config.get('logging.file_path', 'logs/system.log')
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                # Останні 100 рядків
                lines = f.readlines()[-100:]
                for line in lines:
                    logs.append(line.strip())
        
        return render_template('logs.html', logs=logs)
        
    except Exception as e:
        logger.error(f"Помилка завантаження логів: {e}")
        return render_template('error.html', error=str(e))

# API endpoints

@app.route('/api/generate_attack', methods=['POST'])
def api_generate_attack():
    """API для генерації атаки"""
    try:
        data = request.get_json()
        attack_type = data.get('attack_type')
        target_info = data.get('target_info', {})
        provider = data.get('provider', 'openai')
        
        if not attack_type:
            return jsonify({'error': 'Тип атаки не вказано'}), 400
        
        # Генерація атаки
        attack_scenario = attack_generator.generate_attack_scenario(
            attack_type, target_info, provider
        )
        
        if 'error' in attack_scenario:
            return jsonify(attack_scenario), 500
        
        return jsonify(attack_scenario)
        
    except Exception as e:
        logger.error(f"Помилка API генерації атаки: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_defense', methods=['POST'])
def api_analyze_defense():
    """API для аналізу захисту"""
    try:
        data = request.get_json()
        attack_scenario = data.get('attack_scenario')
        current_defenses = data.get('current_defenses', [])
        provider = data.get('provider', 'openai')
        
        if not attack_scenario:
            return jsonify({'error': 'Сценарій атаки не вказано'}), 400
        
        # Генерація стратегії захисту
        defense_strategy = defense_analyzer.generate_defense_strategy(
            attack_scenario, current_defenses, provider
        )
        
        if 'error' in defense_strategy:
            return jsonify(defense_strategy), 500
        
        return jsonify(defense_strategy)
        
    except Exception as e:
        logger.error(f"Помилка API аналізу захисту: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_simulation', methods=['POST'])
def api_start_simulation():
    """API для запуску симуляції"""
    try:
        data = request.get_json()
        simulation_config = data.get('simulation_config', {})
        
        if not simulation_config:
            return jsonify({'error': 'Конфігурація симуляції не вказана'}), 400
        
        # Callback для оновлення через WebSocket
        def simulation_callback(simulation_result):
            socketio.emit('simulation_update', {
                'simulation_id': simulation_result['id'],
                'status': simulation_result['status'],
                'metrics': simulation_result['metrics'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Запуск симуляції
        sim_id = attack_simulator.start_simulation(simulation_config, simulation_callback)
        
        return jsonify({
            'simulation_id': sim_id,
            'status': 'started',
            'message': 'Симуляцію запущено'
        })
        
    except Exception as e:
        logger.error(f"Помилка API запуску симуляції: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop_simulation', methods=['POST'])
def api_stop_simulation():
    """API для зупинки симуляції"""
    try:
        data = request.get_json()
        simulation_id = data.get('simulation_id')
        
        if not simulation_id:
            return jsonify({'error': 'ID симуляції не вказано'}), 400
        
        # Зупинка симуляції
        success = attack_simulator.stop_simulation(simulation_id)
        
        if success:
            return jsonify({
                'simulation_id': simulation_id,
                'status': 'stopped',
                'message': 'Симуляцію зупинено'
            })
        else:
            return jsonify({'error': 'Симуляцію не знайдено або вже зупинено'}), 404
        
    except Exception as e:
        logger.error(f"Помилка API зупинки симуляції: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation_status/<simulation_id>')
def api_simulation_status(simulation_id):
    """API для отримання статусу симуляції"""
    try:
        status = attack_simulator.get_simulation_status(simulation_id)
        
        if not status:
            return jsonify({'error': 'Симуляцію не знайдено'}), 404
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Помилка API статусу симуляції: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation_summary/<simulation_id>')
def api_simulation_summary(simulation_id):
    """API для отримання зведення симуляції"""
    try:
        summary = attack_simulator.get_simulation_summary(simulation_id)
        
        if not summary:
            return jsonify({'error': 'Симуляцію не знайдено'}), 404
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Помилка API зведення симуляції: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system_statistics')
def api_system_statistics():
    """API для отримання статистики системи"""
    try:
        stats = {
            'attack': attack_generator.get_attack_statistics(),
            'defense': defense_analyzer.get_defense_statistics(),
            'simulation': attack_simulator.get_system_statistics()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Помилка API статистики системи: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket events

@socketio.on('connect')
def handle_connect():
    """Обробка підключення WebSocket"""
    logger.info(f"WebSocket підключення: {request.sid}")
    emit('connected', {'message': 'Підключено до системи'})

@socketio.on('disconnect')
def handle_disconnect():
    """Обробка відключення WebSocket"""
    logger.info(f"WebSocket відключення: {request.sid}")

@socketio.on('request_simulation_update')
def handle_simulation_update_request(data):
    """Обробка запиту на оновлення симуляції"""
    try:
        simulation_id = data.get('simulation_id')
        if simulation_id:
            status = attack_simulator.get_simulation_status(simulation_id)
            if status:
                emit('simulation_update', {
                    'simulation_id': simulation_id,
                    'status': status['status'],
                    'metrics': status['metrics'],
                    'timestamp': datetime.now().isoformat()
                })
    except Exception as e:
        logger.error(f"Помилка WebSocket оновлення симуляції: {e}")

# Error handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Health check

@app.route('/health')
def health_check():
    """Перевірка стану системи"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'config_manager': 'ok',
                'logger': 'ok',
                'attack_generator': 'ok',
                'defense_analyzer': 'ok',
                'attack_simulator': 'ok'
            }
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Помилка health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    try:
        web_config = config.get_web_config()
        host = web_config.get('host', '0.0.0.0')
        port = web_config.get('port', 5000)
        debug = config.is_debug_mode()
        
        logger.info(f"Запуск веб-додатку на {host}:{port}")
        logger.info(f"Режим налагодження: {debug}")
        
        socketio.run(app, host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.critical(f"Критична помилка запуску веб-додатку: {e}")
        sys.exit(1)
