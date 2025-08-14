import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
import anthropic
from utils.config_manager import ConfigManager
from utils.logger import logger

class DefenseAnalyzer:
    """Аналізатор захисту та генератор контрзаходів"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.openai_client = None
        self.anthropic_client = None
        self._setup_clients()
        
        # Шаблони захисту
        self.defense_layers = {
            "network": {
                "firewall": "Мережевий екран",
                "ids_ips": "Системи виявлення вторгнень",
                "vpn": "Віртуальна приватна мережа",
                "segmentation": "Сегментація мережі"
            },
            "endpoint": {
                "antivirus": "Антивірусне ПЗ",
                "edr": "Endpoint Detection and Response",
                "patching": "Оновлення систем",
                "hardening": "Захищення кінцевих точок"
            },
            "access": {
                "mfa": "Багатофакторна автентифікація",
                "iam": "Управління ідентичністю та доступом",
                "pam": "Привілейований доступ",
                "sso": "Єдиний вхід"
            },
            "monitoring": {
                "siem": "Система управління подіями безпеки",
                "logging": "Централізоване логування",
                "alerting": "Система сповіщень",
                "forensics": "Форензичні інструменти"
            }
        }
    
    def _setup_clients(self):
        """Налаштування клієнтів LLM"""
        try:
            # OpenAI
            openai_config = self.config.get_llm_config("openai")
            if openai_config.get("api_key"):
                openai.api_key = openai_config["api_key"]
                self.openai_client = openai.OpenAI()
                logger.info("OpenAI клієнт налаштовано для DefenseAnalyzer")
            
            # Anthropic
            anthropic_config = self.config.get_llm_config("anthropic")
            if anthropic_config.get("api_key"):
                self.anthropic_client = anthropic.Anthropic(
                    api_key=anthropic_config["api_key"]
                )
                logger.info("Anthropic клієнт налаштовано для DefenseAnalyzer")
                
        except Exception as e:
            logger.error(f"Помилка налаштування LLM клієнтів для DefenseAnalyzer: {e}")
    
    def analyze_network_security(self, network_info: Dict[str, Any]) -> Dict[str, Any]:
        """Аналіз безпеки мережі"""
        try:
            analysis = {
                "network_id": f"network_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "recommendations": [],
                "risk_score": 0,
                "defense_coverage": {}
            }
            
            # Аналіз відкритих портів
            open_ports = network_info.get("open_ports", [])
            if open_ports:
                analysis["vulnerabilities"].append({
                    "type": "open_ports",
                    "description": f"Відкриті порти: {open_ports}",
                    "severity": "medium",
                    "risk_score": len(open_ports) * 0.1
                })
            
            # Аналіз сервісів
            services = network_info.get("services", {})
            risky_services = ["telnet", "ftp", "rsh", "rlogin"]
            for service in risky_services:
                if service in str(services).lower():
                    analysis["vulnerabilities"].append({
                        "type": "risky_service",
                        "description": f"Ризикований сервіс: {service}",
                        "severity": "high",
                        "risk_score": 0.3
                    })
            
            # Розрахунок загального ризику
            total_risk = sum(v["risk_score"] for v in analysis["vulnerabilities"])
            analysis["risk_score"] = min(1.0, total_risk)
            
            # Генерація рекомендацій
            analysis["recommendations"] = self._generate_network_recommendations(analysis)
            
            # Аналіз покриття захисту
            analysis["defense_coverage"] = self._analyze_defense_coverage(network_info)
            
            logger.log_defense("network_analysis", network_info.get("target", "unknown"), 
                             f"Risk score: {analysis['risk_score']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Помилка аналізу безпеки мережі: {e}")
            return {"error": str(e)}
    
    def _generate_network_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Генерація рекомендацій для мережі"""
        recommendations = []
        
        if analysis["risk_score"] > 0.7:
            recommendations.append("Критичний рівень ризику - необхідні термінові заходи")
            recommendations.append("Закрити всі непотрібні порти та сервіси")
            recommendations.append("Впровадити мережевий екран та IDS/IPS")
        elif analysis["risk_score"] > 0.4:
            recommendations.append("Середній рівень ризику - рекомендується посилення захисту")
            recommendations.append("Налаштувати правила мережевого екрану")
            recommendations.append("Впровадити моніторинг мережевого трафіку")
        else:
            recommendations.append("Низький рівень ризику - підтримувати поточний захист")
            recommendations.append("Регулярно перевіряти налаштування безпеки")
        
        return recommendations
    
    def _analyze_defense_coverage(self, network_info: Dict[str, Any]) -> Dict[str, Any]:
        """Аналіз покриття захисту"""
        coverage = {}
        
        for layer, defenses in self.defense_layers.items():
            layer_coverage = 0
            implemented = network_info.get(f"implemented_{layer}", [])
            
            if implemented:
                layer_coverage = len(implemented) / len(defenses)
            
            coverage[layer] = {
                "coverage_percentage": round(layer_coverage * 100, 1),
                "implemented": implemented,
                "missing": [d for d in defenses.keys() if d not in implemented]
            }
        
        return coverage
    
    def generate_defense_strategy(self, attack_scenario: Dict[str, Any], 
                                current_defenses: List[str],
                                provider: str = "openai") -> Dict[str, Any]:
        """Генерація стратегії захисту за допомогою LLM"""
        try:
            # Формування промпту для LLM
            prompt = self._create_defense_prompt(attack_scenario, current_defenses)
            
            # Генерація через LLM
            if provider == "openai" and self.openai_client:
                response = self._generate_with_openai(prompt, "defense_strategy")
            elif provider == "anthropic" and self.anthropic_client:
                response = self._generate_with_anthropic(prompt, "defense_strategy")
            else:
                response = self._generate_fallback_defense(attack_scenario, current_defenses)
            
            strategy = {
                "strategy_id": f"defense_{int(time.time())}",
                "attack_type": attack_scenario.get("type"),
                "attack_id": attack_scenario.get("attack_id"),
                "current_defenses": current_defenses,
                "recommended_defenses": response,
                "provider": provider,
                "timestamp": datetime.now().isoformat(),
                "priority": self._calculate_defense_priority(attack_scenario)
            }
            
            logger.log_defense("strategy_generation", attack_scenario.get("type", "unknown"), 
                             f"Generated via {provider}")
            
            return strategy
            
        except Exception as e:
            logger.error(f"Помилка генерації стратегії захисту: {e}")
            return {"error": str(e)}
    
    def _create_defense_prompt(self, attack_scenario: Dict[str, Any], 
                              current_defenses: List[str]) -> str:
        """Створення промпту для генерації захисту"""
        attack_type = attack_scenario.get("type", "unknown")
        attack_details = attack_scenario.get("scenario", {})
        
        prompt = f"""
        Ти - експерт з кібербезпеки, який створює стратегії захисту.
        Створи детальну стратегію захисту проти {attack_type} атаки.
        
        Інформація про атаку:
        - Тип: {attack_type}
        - Деталі: {json.dumps(attack_details, ensure_ascii=False, indent=2)}
        
        Поточні заходи захисту: {current_defenses}
        
        Вимоги до стратегії:
        1. Включити технічні контрзаходи
        2. Включити організаційні заходи
        3. Вказати пріоритети впровадження
        4. Оцінити ефективність кожного заходу
        
        Формат відповіді: JSON з полями:
        - immediate_actions: термінові дії
        - short_term: короткострокові заходи (1-3 місяці)
        - long_term: довгострокові заходи (3-12 місяців)
        - technical_controls: технічні контрзаходи
        - organizational_controls: організаційні заходи
        - effectiveness_estimates: оцінки ефективності
        """
        
        return prompt
    
    def _generate_with_openai(self, prompt: str, action_type: str) -> Dict[str, Any]:
        """Генерація через OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.get("llm_providers.openai.model", "gpt-4"),
                messages=[
                    {"role": "system", "content": "Ти експерт з кібербезпеки та захисту інформації."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get("llm_providers.openai.max_tokens", 2000),
                temperature=self.config.get("llm_providers.openai.temperature", 0.7)
            )
            
            content = response.choices[0].message.content
            logger.log_llm_interaction("openai", "gpt-4", f"Generated {action_type}")
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "parsed": False}
                
        except Exception as e:
            logger.error(f"Помилка OpenAI: {e}")
            return {"error": str(e)}
    
    def _generate_with_anthropic(self, prompt: str, action_type: str) -> Dict[str, Any]:
        """Генерація через Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config.get("llm_providers.anthropic.model", "claude-3-sonnet-20240229"),
                max_tokens=self.config.get("llm_providers.anthropic.max_tokens", 2000),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            logger.log_llm_interaction("anthropic", "claude-3", f"Generated {action_type}")
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "parsed": False}
                
        except Exception as e:
            logger.error(f"Помилка Anthropic: {e}")
            return {"error": str(e)}
    
    def _generate_fallback_defense(self, attack_scenario: Dict[str, Any], 
                                 current_defenses: List[str]) -> Dict[str, Any]:
        """Резервна генерація стратегії захисту"""
        return {
            "immediate_actions": [
                "Блокувати підозрілий трафік",
                "Оновити правила мережевого екрану",
                "Активувати додаткове логування"
            ],
            "short_term": [
                "Впровадити IDS/IPS",
                "Налаштувати моніторинг",
                "Провести аудит безпеки"
            ],
            "long_term": [
                "Розробити план реагування на інциденти",
                "Впровадити SIEM систему",
                "Провести тренування персоналу"
            ],
            "technical_controls": [
                "Мережевий екран",
                "Антивірусне ПЗ",
                "Шифрування даних"
            ],
            "organizational_controls": [
                "Політика безпеки",
                "Тренування персоналу",
                "Регулярні аудити"
            ],
            "effectiveness_estimates": {
                "immediate": 0.6,
                "short_term": 0.8,
                "long_term": 0.9
            }
        }
    
    def _calculate_defense_priority(self, attack_scenario: Dict[str, Any]) -> str:
        """Розрахунок пріоритету захисту"""
        risk_level = attack_scenario.get("scenario", {}).get("risk_level", 5)
        
        if risk_level >= 8:
            return "critical"
        elif risk_level >= 6:
            return "high"
        elif risk_level >= 4:
            return "medium"
        else:
            return "low"
    
    def get_defense_statistics(self) -> Dict[str, Any]:
        """Отримання статистики захисту"""
        total_defenses = sum(len(defenses) for defenses in self.defense_layers.values())
        
        return {
            "total_defense_layers": len(self.defense_layers),
            "total_defense_types": total_defenses,
            "layer_coverage": {
                layer: len(defenses) for layer, defenses in self.defense_layers.items()
            }
        }
