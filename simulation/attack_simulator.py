import json
import time
import random
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from utils.config_manager import ConfigManager
from utils.logger import logger

@dataclass
class SimulationEvent:
    """Подія симуляції"""
    timestamp: datetime
    event_type: str
    description: str
    severity: str
    source: str
    target: str
    metadata: Dict[str, Any]

class AttackSimulator:
    """Симулятор атак для тестування захисту"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.simulations = {}
        self.event_handlers = []
        self.running_simulations = {}
        
        # Налаштування симуляції
        self.max_concurrent = self.config.get("simulation.max_concurrent_attacks", 5)
        self.attack_duration = self.config.get("simulation.attack_duration", 300)
        self.recovery_time = self.config.get("simulation.recovery_time", 60)
        self.alert_threshold = self.config.get("simulation.alert_threshold", 0.8)
    
    def start_simulation(self, simulation_config: Dict[str, Any], 
                        callback: Optional[Callable] = None) -> str:
        """Запуск симуляції атаки"""
        try:
            sim_id = f"sim_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Перевірка лімітів
            if len(self.running_simulations) >= self.max_concurrent:
                raise Exception("Досягнуто ліміт одночасних симуляцій")
            
            # Створення симуляції
            simulation = {
                "id": sim_id,
                "config": simulation_config,
                "status": "running",
                "start_time": datetime.now(),
                "events": [],
                "metrics": {
                    "attack_success": 0,
                    "defense_success": 0,
                    "total_events": 0,
                    "risk_score": 0
                },
                "callback": callback
            }
            
            self.simulations[sim_id] = simulation
            self.running_simulations[sim_id] = simulation
            
            # Запуск симуляції в окремому потоці
            thread = threading.Thread(
                target=self._run_simulation,
                args=(sim_id,),
                daemon=True
            )
            thread.start()
            
            logger.log_simulation(sim_id, "started", f"Attack type: {simulation_config.get('attack_type')}")
            
            return sim_id
            
        except Exception as e:
            logger.error(f"Помилка запуску симуляції: {e}")
            raise
    
    def _run_simulation(self, sim_id: str):
        """Виконання симуляції в окремому потоці"""
        try:
            simulation = self.simulations[sim_id]
            config = simulation["config"]
            attack_type = config.get("attack_type", "generic")
            
            # Етапи симуляції
            stages = self._get_attack_stages(attack_type)
            
            for stage in stages:
                if simulation["status"] != "running":
                    break
                
                # Виконання етапу
                stage_result = self._execute_stage(stage, config, simulation)
                
                # Додавання події
                event = SimulationEvent(
                    timestamp=datetime.now(),
                    event_type=f"stage_{stage['name']}",
                    description=stage_result["description"],
                    severity=stage_result["severity"],
                    source="attack_simulator",
                    target=config.get("target", "unknown"),
                    metadata=stage_result
                )
                
                simulation["events"].append(asdict(event))
                simulation["metrics"]["total_events"] += 1
                
                # Оновлення метрик
                self._update_simulation_metrics(sim_id)
                
                # Перевірка умов завершення
                if self._should_stop_simulation(simulation):
                    break
                
                # Пауза між етапами
                time.sleep(stage.get("duration", 5))
            
            # Завершення симуляції
            self._complete_simulation(sim_id)
            
        except Exception as e:
            logger.error(f"Помилка виконання симуляції {sim_id}: {e}")
            self._fail_simulation(sim_id, str(e))
    
    def _get_attack_stages(self, attack_type: str) -> List[Dict[str, Any]]:
        """Отримання етапів атаки"""
        base_stages = [
            {
                "name": "reconnaissance",
                "description": "Розвідка цілі",
                "duration": 10,
                "success_rate": 0.8
            },
            {
                "name": "weaponization",
                "description": "Підготовка атаки",
                "duration": 15,
                "success_rate": 0.7
            },
            {
                "name": "delivery",
                "description": "Доставка атаки",
                "duration": 20,
                "success_rate": 0.6
            },
            {
                "name": "exploitation",
                "description": "Експлуатація вразливості",
                "duration": 25,
                "success_rate": 0.5
            },
            {
                "name": "installation",
                "description": "Встановлення зловмисного коду",
                "duration": 30,
                "success_rate": 0.4
            },
            {
                "name": "command_control",
                "description": "Встановлення командного каналу",
                "duration": 20,
                "success_rate": 0.3
            },
            {
                "name": "actions_objectives",
                "description": "Виконання цілей атаки",
                "duration": 40,
                "success_rate": 0.2
            }
        ]
        
        # Адаптація етапів для конкретного типу атаки
        if attack_type == "phishing":
            return base_stages[:4]  # Тільки перші 4 етапи
        elif attack_type == "malware":
            return base_stages[:6]  # Перші 6 етапів
        else:
            return base_stages
    
    def _execute_stage(self, stage: Dict[str, Any], config: Dict[str, Any], 
                       simulation: Dict[str, Any]) -> Dict[str, Any]:
        """Виконання етапу атаки"""
        stage_name = stage["name"]
        success_rate = stage["success_rate"]
        
        # Моделювання успішності етапу
        is_successful = random.random() < success_rate
        
        # Вплив захисту на успішність
        defense_modifier = self._calculate_defense_modifier(config.get("defenses", []))
        adjusted_success = is_successful and (random.random() > defense_modifier)
        
        if adjusted_success:
            simulation["metrics"]["attack_success"] += 1
            severity = "high"
            description = f"Етап '{stage['description']}' успішно виконано"
        else:
            simulation["metrics"]["defense_success"] += 1
            severity = "medium"
            description = f"Етап '{stage['description']}' заблоковано захистом"
        
        return {
            "stage": stage_name,
            "description": description,
            "severity": severity,
            "success": adjusted_success,
            "defense_modifier": defense_modifier
        }
    
    def _calculate_defense_modifier(self, defenses: List[str]) -> float:
        """Розрахунок модифікатора захисту"""
        if not defenses:
            return 0.0
        
        # Базовий модифікатор залежить від кількості заходів захисту
        base_modifier = min(0.8, len(defenses) * 0.15)
        
        # Додаткові модифікатори для специфічних заходів
        special_defenses = {
            "ids_ips": 0.1,
            "siem": 0.1,
            "edr": 0.15,
            "mfa": 0.2
        }
        
        additional_modifier = sum(
            special_defenses.get(defense, 0) 
            for defense in defenses 
            if defense in special_defenses
        )
        
        return min(0.9, base_modifier + additional_modifier)
    
    def _update_simulation_metrics(self, sim_id: str):
        """Оновлення метрик симуляції"""
        simulation = self.simulations[sim_id]
        metrics = simulation["metrics"]
        
        total_events = metrics["total_events"]
        if total_events > 0:
            # Розрахунок ризику на основі успішності атаки
            attack_ratio = metrics["attack_success"] / total_events
            metrics["risk_score"] = round(attack_ratio, 2)
            
            # Перевірка порогу сповіщень
            if attack_ratio > self.alert_threshold:
                self._trigger_alert(sim_id, attack_ratio)
    
    def _should_stop_simulation(self, simulation: Dict[str, Any]) -> bool:
        """Перевірка умов завершення симуляції"""
        # Завершення за часом
        elapsed = (datetime.now() - simulation["start_time"]).total_seconds()
        if elapsed > self.attack_duration:
            return True
        
        # Завершення за успішністю атаки
        if simulation["metrics"]["attack_success"] >= 5:
            return True
        
        # Завершення за блокуванням
        if simulation["metrics"]["defense_success"] >= 3:
            return True
        
        return False
    
    def _trigger_alert(self, sim_id: str, risk_score: float):
        """Спрацювання сповіщення"""
        alert_event = SimulationEvent(
            timestamp=datetime.now(),
            event_type="alert",
            description=f"Високий рівень ризику: {risk_score}",
            severity="critical",
            source="attack_simulator",
            target="system",
            metadata={"risk_score": risk_score, "threshold": self.alert_threshold}
        )
        
        simulation = self.simulations[sim_id]
        simulation["events"].append(asdict(alert_event))
        
        logger.warning(f"Сповіщення симуляції {sim_id}: рівень ризику {risk_score}")
    
    def _complete_simulation(self, sim_id: str):
        """Завершення симуляції"""
        simulation = self.simulations[sim_id]
        simulation["status"] = "completed"
        simulation["end_time"] = datetime.now()
        simulation["duration"] = (simulation["end_time"] - simulation["start_time"]).total_seconds()
        
        # Видалення з активних симуляцій
        if sim_id in self.running_simulations:
            del self.running_simulations[sim_id]
        
        # Виклик callback
        if simulation.get("callback"):
            try:
                simulation["callback"](simulation)
            except Exception as e:
                logger.error(f"Помилка callback симуляції {sim_id}: {e}")
        
        logger.log_simulation(sim_id, "completed", 
                            f"Duration: {simulation['duration']}s, Risk: {simulation['metrics']['risk_score']}")
    
    def _fail_simulation(self, sim_id: str, error: str):
        """Помилка симуляції"""
        simulation = self.simulations[sim_id]
        simulation["status"] = "failed"
        simulation["error"] = error
        simulation["end_time"] = datetime.now()
        
        if sim_id in self.running_simulations:
            del self.running_simulations[sim_id]
        
        logger.log_simulation(sim_id, "failed", error)
    
    def stop_simulation(self, sim_id: str) -> bool:
        """Зупинка симуляції"""
        if sim_id in self.running_simulations:
            simulation = self.running_simulations[sim_id]
            simulation["status"] = "stopped"
            simulation["end_time"] = datetime.now()
            
            del self.running_simulations[sim_id]
            
            logger.log_simulation(sim_id, "stopped", "Manually stopped")
            return True
        
        return False
    
    def get_simulation_status(self, sim_id: str) -> Optional[Dict[str, Any]]:
        """Отримання статусу симуляції"""
        return self.simulations.get(sim_id)
    
    def get_running_simulations(self) -> List[str]:
        """Отримання списку активних симуляцій"""
        return list(self.running_simulations.keys())
    
    def get_simulation_summary(self, sim_id: str) -> Dict[str, Any]:
        """Отримання зведення симуляції"""
        simulation = self.simulations.get(sim_id)
        if not simulation:
            return {}
        
        return {
            "id": simulation["id"],
            "status": simulation["status"],
            "attack_type": simulation["config"].get("attack_type"),
            "start_time": simulation["start_time"].isoformat() if simulation.get("start_time") else None,
            "end_time": simulation["end_time"].isoformat() if simulation.get("end_time") else None,
            "duration": simulation.get("duration", 0),
            "metrics": simulation["metrics"],
            "total_events": len(simulation["events"]),
            "risk_level": self._calculate_risk_level(simulation["metrics"]["risk_score"])
        }
    
    def _calculate_risk_level(self, risk_score: float) -> str:
        """Розрахунок рівня ризику"""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        elif risk_score >= 0.2:
            return "low"
        else:
            return "minimal"
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Отримання статистики системи"""
        total_simulations = len(self.simulations)
        completed_simulations = len([s for s in self.simulations.values() if s["status"] == "completed"])
        failed_simulations = len([s for s in self.simulations.values() if s["status"] == "failed"])
        running_simulations = len(self.running_simulations)
        
        if completed_simulations > 0:
            avg_risk = sum(
                s["metrics"]["risk_score"] 
                for s in self.simulations.values() 
                if s["status"] == "completed"
            ) / completed_simulations
        else:
            avg_risk = 0
        
        return {
            "total_simulations": total_simulations,
            "completed_simulations": completed_simulations,
            "failed_simulations": failed_simulations,
            "running_simulations": running_simulations,
            "average_risk_score": round(avg_risk, 2),
            "max_concurrent": self.max_concurrent,
            "attack_duration": self.attack_duration
        }
    
    def add_event_handler(self, handler: Callable):
        """Додавання обробника подій"""
        self.event_handlers.append(handler)
    
    def clear_simulations(self):
        """Очищення історії симуляцій"""
        self.simulations.clear()
        logger.info("Історію симуляцій очищено")
