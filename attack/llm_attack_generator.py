import json
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
import anthropic
from utils.config_manager import ConfigManager
from utils.logger import logger

class LLMAttackGenerator:
    """Генератор атак з використанням LLM моделей"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.openai_client = None
        self.anthropic_client = None
        self._setup_clients()
        
        # Шаблони атак
        self.attack_templates = {
            "phishing": {
                "description": "Фішинг атака з використанням соціальної інженерії",
                "complexity": "medium",
                "success_rate": 0.7
            },
            "social_engineering": {
                "description": "Соціальна інженерія через різні канали комунікації",
                "complexity": "high",
                "success_rate": 0.8
            },
            "credential_harvesting": {
                "description": "Збір облікових даних через фальшиві форми",
                "complexity": "medium",
                "success_rate": 0.6
            },
            "malware_distribution": {
                "description": "Розповсюдження шкідливого ПЗ через LLM-генерований контент",
                "complexity": "high",
                "success_rate": 0.5
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
                logger.info("OpenAI клієнт налаштовано")
            
            # Anthropic
            anthropic_config = self.config.get_llm_config("anthropic")
            if anthropic_config.get("api_key"):
                self.anthropic_client = anthropic.Anthropic(
                    api_key=anthropic_config["api_key"]
                )
                logger.info("Anthropic клієнт налаштовано")
                
        except Exception as e:
            logger.error(f"Помилка налаштування LLM клієнтів: {e}")
    
    def generate_attack_scenario(self, attack_type: str, target_info: Dict[str, Any], 
                               provider: str = "openai") -> Dict[str, Any]:
        """Генерація сценарію атаки за допомогою LLM"""
        try:
            if attack_type not in self.attack_templates:
                raise ValueError(f"Невідомий тип атаки: {attack_type}")
            
            template = self.attack_templates[attack_type]
            
            # Формування промпту для LLM
            prompt = self._create_attack_prompt(attack_type, target_info, template)
            
            # Генерація через LLM
            if provider == "openai" and self.openai_client:
                response = self._generate_with_openai(prompt, attack_type)
            elif provider == "anthropic" and self.anthropic_client:
                response = self._generate_with_anthropic(prompt, attack_type)
            else:
                response = self._generate_fallback(attack_type, target_info, template)
            
            # Логування
            logger.log_attack(attack_type, target_info.get("target", "unknown"), 
                            f"Generated via {provider}")
            
            return {
                "attack_id": f"attack_{int(time.time())}_{random.randint(1000, 9999)}",
                "type": attack_type,
                "target": target_info,
                "scenario": response,
                "template": template,
                "provider": provider,
                "timestamp": datetime.now().isoformat(),
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Помилка генерації атаки: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def _create_attack_prompt(self, attack_type: str, target_info: Dict[str, Any], 
                             template: Dict[str, Any]) -> str:
        """Створення промпту для LLM"""
        target_description = target_info.get("description", "корпоративна мережа")
        target_industry = target_info.get("industry", "технології")
        
        prompt = f"""
        Ти - експерт з кібербезпеки, який аналізує потенційні вразливості. 
        Створи детальний сценарій {attack_type} атаки для {target_description} 
        в галузі {target_industry}.
        
        Вимоги:
        1. Атака повинна бути реалістичною та адаптивною
        2. Включити етапи: розвідка, підготовка, виконання, закриття слідів
        3. Описати технічні деталі та соціальні аспекти
        4. Вказати потенційні контрзаходи
        
        Формат відповіді: JSON з полями:
        - title: назва атаки
        - description: опис
        - stages: етапи атаки
        - technical_details: технічні деталі
        - social_aspects: соціальні аспекти
        - countermeasures: контрзаходи
        - risk_level: рівень ризику (1-10)
        """
        
        return prompt
    
    def _generate_with_openai(self, prompt: str, attack_type: str) -> Dict[str, Any]:
        """Генерація через OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.get("llm_providers.openai.model", "gpt-4"),
                messages=[
                    {"role": "system", "content": "Ти експерт з кібербезпеки та етичного хакінгу."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get("llm_providers.openai.max_tokens", 2000),
                temperature=self.config.get("llm_providers.openai.temperature", 0.7)
            )
            
            content = response.choices[0].message.content
            logger.log_llm_interaction("openai", "gpt-4", f"Generated {attack_type} attack")
            
            # Спроба парсингу JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "parsed": False}
                
        except Exception as e:
            logger.error(f"Помилка OpenAI: {e}")
            return {"error": str(e)}
    
    def _generate_with_anthropic(self, prompt: str, attack_type: str) -> Dict[str, Any]:
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
            logger.log_llm_interaction("anthropic", "claude-3", f"Generated {attack_type} attack")
            
            # Спроба парсингу JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "parsed": False}
                
        except Exception as e:
            logger.error(f"Помилка Anthropic: {e}")
            return {"error": str(e)}
    
    def _generate_fallback(self, attack_type: str, target_info: Dict[str, Any], 
                          template: Dict[str, Any]) -> Dict[str, Any]:
        """Резервна генерація без LLM"""
        return {
            "title": f"Стандартна {attack_type} атака",
            "description": template["description"],
            "stages": [
                "Розвідка цілі",
                "Підготовка атаки", 
                "Виконання",
                "Закриття слідів"
            ],
            "technical_details": "Базові техніки атаки",
            "social_aspects": "Стандартні соціальні методи",
            "countermeasures": "Базові заходи захисту",
            "risk_level": 5
        }
    
    def analyze_attack_effectiveness(self, attack_scenario: Dict[str, Any], 
                                   target_defenses: List[str]) -> Dict[str, Any]:
        """Аналіз ефективності атаки проти захисту"""
        try:
            # Простий аналіз ефективності
            base_success = attack_scenario.get("template", {}).get("success_rate", 0.5)
            defense_strength = len(target_defenses) * 0.1
            
            effectiveness = max(0.1, base_success - defense_strength)
            
            return {
                "attack_id": attack_scenario.get("attack_id"),
                "effectiveness_score": round(effectiveness, 2),
                "defense_analysis": target_defenses,
                "recommendations": self._generate_recommendations(effectiveness, target_defenses),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Помилка аналізу ефективності: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, effectiveness: float, defenses: List[str]) -> List[str]:
        """Генерація рекомендацій на основі ефективності"""
        recommendations = []
        
        if effectiveness > 0.7:
            recommendations.append("Високий рівень загрози - необхідні термінові заходи")
            recommendations.append("Розглянути додаткові шари захисту")
        elif effectiveness > 0.4:
            recommendations.append("Середній рівень загрози - рекомендується посилення захисту")
            recommendations.append("Оновити існуючі заходи захисту")
        else:
            recommendations.append("Низький рівень загрози - захист ефективний")
            recommendations.append("Підтримувати поточний рівень безпеки")
        
        return recommendations
    
    def get_available_attack_types(self) -> List[str]:
        """Отримання доступних типів атак"""
        return list(self.attack_templates.keys())
    
    def get_attack_statistics(self) -> Dict[str, Any]:
        """Отримання статистики атак"""
        return {
            "total_templates": len(self.attack_templates),
            "complexity_distribution": {
                "low": len([t for t in self.attack_templates.values() if t["complexity"] == "low"]),
                "medium": len([t for t in self.attack_templates.values() if t["complexity"] == "medium"]),
                "high": len([t for t in self.attack_templates.values() if t["complexity"] == "high"])
            },
            "average_success_rate": sum(t["success_rate"] for t in self.attack_templates.values()) / len(self.attack_templates)
        }
