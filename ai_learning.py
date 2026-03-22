import numpy as np
import json
import pickle
import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import math
import random

@dataclass
class LearningPattern:
    pattern_id: str
    input_pattern: str
    output_pattern: str
    success_rate: float
    usage_count: int
    last_used: datetime.datetime
    context_tags: List[str]
    confidence_score: float

@dataclass
class LearningMetrics:
    total_interactions: int
    successful_responses: int
    average_confidence: float
    learning_rate: float
    improvement_trend: float
    knowledge_expansion: float

class AILearning:
    """Système d'apprentissage automatique avancé pour HIBBI"""
    
    def __init__(self, learning_file: str = "hibbi_learning.pkl"):
        self.learning_file = learning_file
        
        # Base d'apprentissage
        self.patterns: Dict[str, LearningPattern] = {}
        self.response_templates: Dict[str, List[str]] = defaultdict(list)
        self.success_patterns: Dict[str, float] = defaultdict(float)
        self.failure_patterns: Dict[str, float] = defaultdict(float)
        
        # Métriques d'apprentissage
        self.metrics = LearningMetrics(
            total_interactions=0,
            successful_responses=0,
            average_confidence=0.0,
            learning_rate=0.1,
            improvement_trend=0.0,
            knowledge_expansion=0.0
        )
        
        # Modèles de prédiction simples
        self.intent_predictor = {}
        self.response_quality_predictor = {}
        
        # Historique d'apprentissage
        self.learning_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.min_pattern_usage = 3
        self.success_threshold = 0.7
        self.learning_decay = 0.95
        
        # Charger les données d'apprentissage
        self.load_learning_data()
    
    def learn_from_interaction(self, user_message: str, hibbi_response: str, 
                             intent_type: str, confidence: float, 
                             user_feedback: Optional[float] = None,
                             context: Dict[str, Any] = None) -> None:
        """Apprend d'une interaction utilisateur"""
        if context is None:
            context = {}
        
        # Mettre à jour les métriques
        self.metrics.total_interactions += 1
        
        if confidence > self.success_threshold:
            self.metrics.successful_responses += 1
        
        # Mettre à jour la confiance moyenne
        self.metrics.average_confidence = (
            (self.metrics.average_confidence * (self.metrics.total_interactions - 1) + confidence) 
            / self.metrics.total_interactions
        )
        
        # Extraire et stocker les patterns
        self._extract_patterns(user_message, hibbi_response, intent_type, confidence)
        
        # Apprendre les templates de réponse
        self._learn_response_templates(intent_type, hibbi_response, confidence)
        
        # Mettre à jour les prédicteurs
        self._update_predictors(user_message, intent_type, confidence)
        
        # Apprendre du feedback utilisateur
        if user_feedback is not None:
            self._learn_from_feedback(user_message, hibbi_response, user_feedback)
        
        # Analyser les tendances
        self._analyze_trends()
        
        # Ajouter à l'historique
        self.learning_history.append({
            "timestamp": datetime.datetime.now(),
            "user_message": user_message,
            "hibbi_response": hibbi_response,
            "intent_type": intent_type,
            "confidence": confidence,
            "user_feedback": user_feedback,
            "context": context
        })
        
        # Sauvegarder périodiquement
        if self.metrics.total_interactions % 10 == 0:
            self.save_learning_data()
    
    def _extract_patterns(self, user_message: str, hibbi_response: str, 
                          intent_type: str, confidence: float) -> None:
        """Extrait et stocke des patterns d'apprentissage"""
        # Normaliser le message
        normalized_input = self._normalize_text(user_message)
        normalized_output = self._normalize_text(hibbi_response)
        
        # Créer un ID de pattern
        pattern_id = f"{intent_type}_{hash(normalized_input[:50])}"
        
        # Mettre à jour ou créer le pattern
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.usage_count += 1
            pattern.last_used = datetime.datetime.now()
            
            # Mettre à jour le taux de succès
            pattern.success_rate = (
                (pattern.success_rate * (pattern.usage_count - 1) + confidence) 
                / pattern.usage_count
            )
            
            # Mettre à jour le score de confiance
            pattern.confidence_score = min(pattern.confidence_score * 1.05, 1.0)
        else:
            pattern = LearningPattern(
                pattern_id=pattern_id,
                input_pattern=normalized_input,
                output_pattern=normalized_output,
                success_rate=confidence,
                usage_count=1,
                last_used=datetime.datetime.now(),
                context_tags=[intent_type],
                confidence_score=confidence
            )
            self.patterns[pattern_id] = pattern
        
        # Mettre à jour les patterns de succès/échec
        if confidence > self.success_threshold:
            self.success_patterns[intent_type] += confidence * self.learning_rate
        else:
            self.failure_patterns[intent_type] += (1 - confidence) * self.learning_rate
    
    def _learn_response_templates(self, intent_type: str, response: str, confidence: float) -> None:
        """Apprend des templates de réponse réussis"""
        if confidence > self.success_threshold and len(response) > 20:
            # Extraire des templates potentiels
            templates = self._extract_templates(response)
            
            for template in templates:
                if template not in self.response_templates[intent_type]:
                    self.response_templates[intent_type].append(template)
    
    def _extract_templates(self, response: str) -> List[str]:
        """Extrait des templates variables d'une réponse"""
        templates = []
        
        # Remplacer les mots spécifiques par des placeholders
        words = response.split()
        template_words = []
        
        for word in words:
            # Détecter les variables potentielles
            if any(char.isdigit() for char in word):
                template_words.append("{number}")
            elif word.startswith(("http", "www")):
                template_words.append("{url}")
            elif len(word) > 8 and word.isalpha():
                template_words.append("{concept}")
            else:
                template_words.append(word)
        
        template = " ".join(template_words)
        
        # Ne garder que les templates avec des variables
        if "{number}" in template or "{url}" in template or "{concept}" in template:
            templates.append(template)
        
        return templates
    
    def _update_predictors(self, user_message: str, intent_type: str, confidence: float) -> None:
        """Met à jour les modèles de prédiction"""
        # Prédicteur d'intention
        features = self._extract_features(user_message)
        
        if intent_type not in self.intent_predictor:
            self.intent_predictor[intent_type] = {}
        
        for feature in features:
            if feature not in self.intent_predictor[intent_type]:
                self.intent_predictor[intent_type][feature] = 0.5
            
            # Apprentissage par renforcement simple
            self.intent_predictor[intent_type][feature] = (
                self.intent_predictor[intent_type][feature] * 0.9 + confidence * 0.1
            )
    
    def _extract_features(self, text: str) -> List[str]:
        """Extrait des caractéristiques du texte"""
        features = []
        words = text.lower().split()
        
        # Features lexicales
        features.append(f"length_{len(words)}")
        features.append(f"has_question_{'?' in text}")
        features.append(f"has_exclamation_{'!' in text}")
        
        # Features de contenu
        question_words = ["comment", "pourquoi", "quoi", "où", "quand", "quel", "quelle"]
        features.append(f"has_question_word_{any(qw in text.lower() for qw in question_words)}")
        
        # Features techniques
        tech_words = ["code", "python", "javascript", "html", "css", "programme", "fonction"]
        features.append(f"has_tech_word_{any(tw in text.lower() for tw in tech_words)}")
        
        # Features créatifs
        creative_words = ["crée", "génère", "imagine", "invente", "écris", "rap", "histoire"]
        features.append(f"has_creative_word_{any(cw in text.lower() for cw in creative_words)}")
        
        return features
    
    def _learn_from_feedback(self, user_message: str, hibbi_response: str, feedback: float) -> None:
        """Apprend du feedback utilisateur explicite"""
        # Renforcer ou affaiblir les patterns basés sur le feedback
        normalized_input = self._normalize_text(user_message)
        
        for pattern_id, pattern in self.patterns.items():
            if pattern.input_pattern in normalized_input or normalized_input in pattern.input_pattern:
                # Ajuster le score de confiance
                if feedback > 0.7:
                    pattern.confidence_score = min(pattern.confidence_score * 1.1, 1.0)
                    pattern.success_rate = min(pattern.success_rate * 1.05, 1.0)
                elif feedback < 0.3:
                    pattern.confidence_score = max(pattern.confidence_score * 0.9, 0.1)
                    pattern.success_rate = max(pattern.success_rate * 0.95, 0.1)
    
    def _analyze_trends(self) -> None:
        """Analyse les tendances d'apprentissage"""
        if len(self.learning_history) < 10:
            return
        
        # Calculer la tendance d'amélioration
        recent_interactions = self.learning_history[-10:]
        older_interactions = self.learning_history[-20:-10] if len(self.learning_history) >= 20 else self.learning_history[:-10]
        
        if older_interactions:
            recent_avg_confidence = np.mean([i["confidence"] for i in recent_interactions])
            older_avg_confidence = np.mean([i["confidence"] for i in older_interactions])
            
            self.metrics.improvement_trend = recent_avg_confidence - older_avg_confidence
        
        # Calculer l'expansion des connaissances
        unique_intents = len(set(i["intent_type"] for i in self.learning_history))
        self.metrics.knowledge_expansion = unique_intents / 10.0  # Normalisé
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour l'apprentissage"""
        return text.lower().strip()
    
    def predict_intent(self, user_message: str) -> Tuple[str, float]:
        """Prédit l'intention avec apprentissage"""
        features = self._extract_features(user_message)
        
        intent_scores = {}
        
        for intent_type, feature_weights in self.intent_predictor.items():
            score = 0.0
            feature_count = 0
            
            for feature in features:
                if feature in feature_weights:
                    score += feature_weights[feature]
                    feature_count += 1
            
            if feature_count > 0:
                intent_scores[intent_type] = score / feature_count
        
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]
        
        return "conversation", 0.5
    
    def generate_improved_response(self, intent_type: str, context: Dict[str, Any]) -> Optional[str]:
        """Génère une réponse améliorée basée sur l'apprentissage"""
        if intent_type in self.response_templates and self.response_templates[intent_type]:
            # Choisir un template basé sur le succès
            templates = self.response_templates[intent_type]
            weights = [self.success_patterns.get(intent_type, 0.5)] * len(templates)
            
            # Ajouter de la variété
            if len(templates) > 1:
                weights = [w + random.random() * 0.1 for w in weights]
            
            # Choisir le template pondéré
            total_weight = sum(weights)
            if total_weight > 0:
                probabilities = [w / total_weight for w in weights]
                chosen_template = np.random.choice(templates, p=probabilities)
                
                # Personnaliser le template
                return self._personalize_template(chosen_template, context)
        
        return None
    
    def _personalize_template(self, template: str, context: Dict[str, Any]) -> str:
        """Personnalise un template avec le contexte"""
        personalized = template
        
        # Remplacer les placeholders
        if "{concept}" in personalized and "concept" in context:
            personalized = personalized.replace("{concept}", context["concept"])
        
        if "{number}" in personalized and "number" in context:
            personalized = personalized.replace("{number}", str(context["number"]))
        
        if "{url}" in personalized and "url" in context:
            personalized = personalized.replace("{url}", context["url"])
        
        return personalized
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Retourne des insights sur l'apprentissage"""
        return {
            "total_patterns": len(self.patterns),
            "successful_patterns": sum(1 for p in self.patterns.values() if p.success_rate > self.success_threshold),
            "average_pattern_usage": np.mean([p.usage_count for p in self.patterns.values()]) if self.patterns else 0,
            "best_performing_intent": max(self.success_patterns.items(), key=lambda x: x[1])[0] if self.success_patterns else None,
            "learning_velocity": self.metrics.improvement_trend,
            "knowledge_domains": list(self.response_templates.keys()),
            "confidence_evolution": [h["confidence"] for h in self.learning_history[-20:]]
        }
    
    def optimize_patterns(self) -> None:
        """Optimise les patterns d'apprentissage"""
        # Supprimer les patterns peu utilisés et peu performants
        patterns_to_remove = []
        
        for pattern_id, pattern in self.patterns.items():
            if pattern.usage_count < self.min_pattern_usage and pattern.success_rate < 0.3:
                patterns_to_remove.append(pattern_id)
        
        for pattern_id in patterns_to_remove:
            del self.patterns[pattern_id]
        
        # Décroissance des poids
        for intent_type in self.success_patterns:
            self.success_patterns[intent_type] *= self.learning_decay
        
        for intent_type in self.failure_patterns:
            self.failure_patterns[intent_type] *= self.learning_decay
    
    def save_learning_data(self) -> None:
        """Sauvegarde les données d'apprentissage"""
        try:
            learning_data = {
                "patterns": {pid: asdict(pattern) for pid, pattern in self.patterns.items()},
                "response_templates": dict(self.response_templates),
                "success_patterns": dict(self.success_patterns),
                "failure_patterns": dict(self.failure_patterns),
                "metrics": asdict(self.metrics),
                "intent_predictor": self.intent_predictor,
                "learning_history": self.learning_history[-100:]  # Garder seulement les 100 derniers
            }
            
            # Convertir les datetime
            for pattern in learning_data["patterns"].values():
                pattern["last_used"] = pattern["last_used"].isoformat()
            
            for entry in learning_data["learning_history"]:
                entry["timestamp"] = entry["timestamp"].isoformat()
            
            with open(self.learning_file, 'wb') as f:
                pickle.dump(learning_data, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données d'apprentissage: {e}")
    
    def load_learning_data(self) -> None:
        """Charge les données d'apprentissage"""
        import os
        if not os.path.exists(self.learning_file):
            return
        
        try:
            with open(self.learning_file, 'rb') as f:
                learning_data = pickle.load(f)
            
            # Reconstruire les objets
            self.patterns = {
                pid: LearningPattern(
                    pattern_id=p["pattern_id"],
                    input_pattern=p["input_pattern"],
                    output_pattern=p["output_pattern"],
                    success_rate=p["success_rate"],
                    usage_count=p["usage_count"],
                    last_used=datetime.datetime.fromisoformat(p["last_used"]),
                    context_tags=p["context_tags"],
                    confidence_score=p["confidence_score"]
                )
                for pid, p in learning_data.get("patterns", {}).items()
            }
            
            self.response_templates = defaultdict(list, learning_data.get("response_templates", {}))
            self.success_patterns = defaultdict(float, learning_data.get("success_patterns", {}))
            self.failure_patterns = defaultdict(float, learning_data.get("failure_patterns", {}))
            
            metrics_data = learning_data.get("metrics", {})
            self.metrics = LearningMetrics(
                total_interactions=metrics_data.get("total_interactions", 0),
                successful_responses=metrics_data.get("successful_responses", 0),
                average_confidence=metrics_data.get("average_confidence", 0.0),
                learning_rate=metrics_data.get("learning_rate", 0.1),
                improvement_trend=metrics_data.get("improvement_trend", 0.0),
                knowledge_expansion=metrics_data.get("knowledge_expansion", 0.0)
            )
            
            self.intent_predictor = learning_data.get("intent_predictor", {})
            self.learning_history = learning_data.get("learning_history", [])
            
            # Convertir les timestamps
            for entry in self.learning_history:
                entry["timestamp"] = datetime.datetime.fromisoformat(entry["timestamp"])
                
        except Exception as e:
            print(f"Erreur lors du chargement des données d'apprentissage: {e}")
    
    def reset_learning(self) -> None:
        """Réinitialise l'apprentissage"""
        self.patterns.clear()
        self.response_templates.clear()
        self.success_patterns.clear()
        self.failure_patterns.clear()
        self.intent_predictor.clear()
        self.learning_history.clear()
        
        self.metrics = LearningMetrics(
            total_interactions=0,
            successful_responses=0,
            average_confidence=0.0,
            learning_rate=0.1,
            improvement_trend=0.0,
            knowledge_expansion=0.0
        )
        
        # Supprimer le fichier
        import os
        if os.path.exists(self.learning_file):
            os.remove(self.learning_file)
