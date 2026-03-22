import re
import json
import random
import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Intent:
    type: str
    confidence: float
    entities: Dict[str, Any]

class HibbiEngine:
    def __init__(self):
        self.name = "HIBBI"
        self.version = "1.0.0"
        self.creation_date = datetime.datetime.now()
        
        # Modules internes
        self.comprehension_module = ComprehensionModule()
        self.reflection_module = ReflectionModule()
        self.learning_module = LearningModule()
        self.generation_module = GenerationModule()
        
        # Base de connaissances interne
        self.knowledge_base = self._initialize_knowledge()
        
        # Mémoire à court terme
        self.short_term_memory = []
        
        # Personnalité
        self.personality = {
            "tone": "intelligent et amical",
            "style": "moderne et futuriste",
            "expertise": ["programmation", "créativité", "analyse", "conversation"]
        }
    
    def _initialize_knowledge(self) -> Dict[str, Any]:
        """Initialise la base de connaissances de HIBBI"""
        return {
            "programming": {
                "python": ["Flask", "Django", "NumPy", "Pandas", "Tkinter", "PyQt"],
                "javascript": ["React", "Vue.js", "Node.js", "Express", "Vanilla JS"],
                "web": ["HTML5", "CSS3", "Bootstrap", "TailwindCSS"],
                "concepts": ["algorithmes", "structures de données", "API", "bases de données"]
            },
            "creative": {
                "writing": ["rap", "histoires", "scripts", "poésie", "posts"],
                "visual": ["description d'images", "design", "artistique"],
                "ideas": ["applications", "projets", "innovations"]
            },
            "analysis": {
                "web_search": ["recherche", "actualités", "informations"],
                "image_analysis": ["contenu visuel", "objets", "scènes"],
                "text_analysis": ["compréhension", "résumé", "extraction"]
            },
            "conversation": {
                "greetings": ["salut", "bonjour", "hello", "hey"],
                "questions": ["comment", "pourquoi", "quoi", "où", "quand"],
                "emotions": ["heureux", "triste", "excité", "curieux"]
            }
        }
    
    def process_message(self, message: str, user_context: Dict = None) -> Dict[str, Any]:
        """Traite un message utilisateur et génère une réponse"""
        # 1. Module de compréhension
        intent = self.comprehension_module.analyze_intent(message)
        
        # 2. Module de réflexion
        strategy = self.reflection_module.decide_strategy(intent, message, self.short_term_memory)
        
        # 3. Module de génération
        response = self.generation_module.generate_response(intent, strategy, message, self.knowledge_base)
        
        # 4. Module d'apprentissage
        self.learning_module.learn_from_interaction(message, response, intent)
        
        # 5. Mise à jour mémoire
        self.short_term_memory.append({
            "timestamp": datetime.datetime.now(),
            "user_message": message,
            "hibbi_response": response,
            "intent": intent
        })
        
        # Limiter la mémoire à court terme
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)
        
        return {
            "response": response,
            "intent": intent,
            "strategy": strategy,
            "confidence": intent.confidence
        }
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités de HIBBI"""
        return [
            "💬 Conversation intelligente",
            "🎨 Génération d'images",
            "🔍 Recherche web",
            "💻 Génération de code",
            "✍️ Création de textes",
            "📊 Analyse de contenu",
            "🧠 Apprentissage continu"
        ]

    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du moteur"""
        return {
            "name": self.name,
            "version": self.version,
            "uptime": str(datetime.datetime.now() - self.creation_date),
            "memory_items": len(self.short_term_memory),
            "learning_rate": self.learning_module.learning_rate,
            "confidence_threshold": 0.7
        }

class ComprehensionModule:
    """Module de compréhension du langage naturel"""
    
    def __init__(self):
        self.intent_patterns = {
            "greeting": [r"(salut|bonjour|hello|hey|coucou|hi)", r"(ça va|comment vas|comment allez)"],
            "code_generation": [r"(génère|crée|écris|développe).*(code|python|javascript|html|css)", r"(fais moi|montre moi).*(code|programme)"],
            "image_generation": [r"(génère|crée|créé|fait).*(image|photo|dessin)", r"(montre|visualise).*(image|photo)"],
            "web_search": [r"(cherche|recherche|trouve).*(sur internet|web|google)", r"(cherche|recherche).*(information|actualité|nouvelle)"],
            "text_creation": [r"(écris|crée|rédige).*(rap|texte|histoire|script|post)", r"(fais moi|invente).*(parole|histoire)"],
            "question": [r"(comment|pourquoi|quoi|où|quand|quel|quelle|est-ce que)", r"\?"],
            "analysis": [r"(analyse|examine|étudie).*(image|texte|donnée)", r"(que penses|quel est ton avis)"]
        }
    
    def analyze_intent(self, message: str) -> Intent:
        """Analyse l'intention derrière le message"""
        message_lower = message.lower()
        
        best_intent = "conversation"
        best_confidence = 0.0
        entities = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            confidence = 0.0
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    confidence += 0.5
            
            if confidence > best_confidence:
                best_confidence = min(confidence, 1.0)
                best_intent = intent_type
        
        # Extraction d'entités simples
        entities = self._extract_entities(message_lower, best_intent)
        
        return Intent(type=best_intent, confidence=best_confidence, entities=entities)
    
    def _extract_entities(self, message: str, intent_type: str) -> Dict[str, Any]:
        """Extrait les entités du message"""
        entities = {}
        
        if intent_type == "code_generation":
            if "python" in message:
                entities["language"] = "python"
            elif "javascript" in message or "js" in message:
                entities["language"] = "javascript"
            elif "html" in message:
                entities["language"] = "html"
            elif "css" in message:
                entities["language"] = "css"
        
        elif intent_type == "text_creation":
            if "rap" in message:
                entities["text_type"] = "rap"
            elif "histoire" in message:
                entities["text_type"] = "histoire"
            elif "script" in message:
                entities["text_type"] = "script"
            elif "post" in message:
                entities["text_type"] = "post"
        
        return entities

class ReflectionModule:
    """Module de réflexion et de prise de décision"""
    
    def __init__(self):
        self.strategies = {
            "greeting": "simple_response",
            "code_generation": "code_creation",
            "image_generation": "image_description",
            "web_search": "search_query",
            "text_creation": "creative_writing",
            "question": "knowledge_response",
            "analysis": "analytical_response",
            "conversation": "conversational"
        }
    
    def decide_strategy(self, intent: Intent, message: str, context: List[Dict]) -> str:
        """Décide de la meilleure stratégie de réponse"""
        base_strategy = self.strategies.get(intent.type, "conversational")
        
        # Ajustement basé sur le contexte
        if context and len(context) > 0:
            last_message = context[-1]
            if intent.type == "conversation" and last_message["intent"].type == "question":
                base_strategy = "follow_up_response"
        
        # Ajustement basé sur la confiance
        if intent.confidence < 0.5:
            base_strategy = "clarification_request"
        
        return base_strategy

class LearningModule:
    """Module d'apprentissage automatique"""
    
    def __init__(self):
        self.learning_rate = 0.1
        self.interaction_history = []
        self.user_preferences = defaultdict(int)
        self.success_patterns = defaultdict(int)
    
    def learn_from_interaction(self, user_message: str, hibbi_response: str, intent: Intent):
        """Apprend de chaque interaction"""
        self.interaction_history.append({
            "timestamp": datetime.datetime.now(),
            "user_message": user_message,
            "hibbi_response": hibbi_response,
            "intent_type": intent.type,
            "confidence": intent.confidence
        })
        
        # Apprentissage des préférences utilisateur
        self.user_preferences[intent.type] += 1
        
        # Apprentissage des patterns réussis
        if intent.confidence > 0.7:
            self.success_patterns[intent.type] += 1
    
    def get_user_insights(self) -> Dict[str, Any]:
        """Retourne des insights sur l'utilisateur"""
        total_interactions = len(self.interaction_history)
        if total_interactions == 0:
            return {"message": "Pas encore assez d'interactions pour analyser"}
        
        return {
            "total_interactions": total_interactions,
            "preferred_topics": dict(sorted(self.user_preferences.items(), key=lambda x: x[1], reverse=True)[:3]),
            "success_rate": {k: v/total_interactions for k, v in self.success_patterns.items()}
        }

class GenerationModule:
    """Module de génération de réponses"""
    
    def __init__(self):
        self.response_templates = {
            "simple_response": [
                "Salut ! Je suis HIBBI, votre IA personnelle. Comment puis-je vous aider ?",
                "Bonjour ! HIBBI à votre service. De quoi avez-vous besoin ?",
                "Hello ! C'est HIBBI. Prêt à vous assister !"
            ],
            "conversational": [
                "C'est une excellente question ! Laissez-moi réfléchir à cela...",
                "Je comprends votre point de vue. Voici ce que j'en pense...",
                "Intéressant ! Analysons cela ensemble..."
            ],
            "clarification_request": [
                "Pourriez-vous préciser votre demande ? Je veux m'assurer de bien comprendre.",
                "J'aimerais être certain de comprendre. Pouvez-vous reformuler ?",
                "Hmm, je pense avoir besoin d'un peu plus de détails pour vous aider au mieux."
            ]
        }
    
    def generate_response(self, intent: Intent, strategy: str, message: str, knowledge_base: Dict) -> str:
        """Génère une réponse basée sur l'intention et la stratégie"""
        
        if strategy == "simple_response":
            return random.choice(self.response_templates["simple_response"])
        
        elif strategy == "code_creation":
            return self._generate_code_response(intent.entities, message)
        
        elif strategy == "image_description":
            return self._generate_image_response(intent.entities, message)
        
        elif strategy == "search_query":
            return self._generate_search_response(message)
        
        elif strategy == "creative_writing":
            return self._generate_text_response(intent.entities, message)
        
        elif strategy == "knowledge_response":
            return self._generate_knowledge_response(message, knowledge_base)
        
        elif strategy == "clarification_request":
            return random.choice(self.response_templates["clarification_request"])
        
        else:  # conversational
            return self._generate_conversational_response(message)
    
    def _generate_code_response(self, entities: Dict, message: str) -> str:
        """Génère une réponse pour la création de code"""
        language = entities.get("language", "python")
        
        if language == "python":
            return "Je peux générer du code Python pour vous ! Dites-moi quel type de programme ou fonctionnalité vous souhaitez créer. Par exemple : une calculatrice, un jeu, une API web, etc."
        elif language == "javascript":
            return "Parfait pour le JavaScript ! Je peux créer des scripts web, des applications interactives, ou même des applications Node.js. Quel projet avez-vous en tête ?"
        elif language == "html":
            return "HTML c'est ma spécialité ! Je peux créer des pages web complètes avec des structures modernes. Que souhaitez-vous construire ?"
        else:
            return f"Excellent choix ! Je peux vous aider avec du code {language}. Décrivez-moi votre projet et je vous créerai le code nécessaire."
    
    def _generate_image_response(self, entities: Dict, message: str) -> str:
        """Génère une réponse pour la génération d'images"""
        return "Je peux générer n'importe quelle image pour vous ! Décrivez simplement ce que vous voulez voir : un paysage, un personnage, un objet, un style artistique... Soyez aussi créatif que vous le souhaitez !"
    
    def _generate_search_response(self, message: str) -> str:
        """Génère une réponse pour la recherche web"""
        return "Je peux rechercher n'importe quelle information sur internet pour vous. Dites-moi ce que vous voulez savoir : actualités, informations techniques, sujets généraux, etc."
    
    def _generate_text_response(self, entities: Dict, message: str) -> str:
        """Génère une réponse pour la création de textes"""
        text_type = entities.get("text_type", "texte")
        
        if text_type == "rap":
            return "Let's go ! Je peux écrire des paroles de rap sur n'importe quel thème. Donnez-moi un sujet, une ambiance, et je vous crée des paroles qui déchirent !"
        elif text_type == "histoire":
            return "J'adore écrire des histoires ! Donnez-moi un genre (science-fiction, fantasy, romance, thriller), des personnages, et je vous crée une histoire captivante."
        elif text_type == "script":
            return "Scénario ? Pas de problème ! Je peux écrire des scripts pour YouTube, des courts métrages, ou même des pièces de théâtre. Quel format et sujet ?"
        else:
            return "Je peux écrire tous types de textes ! Articles, posts, descriptions, lettres... Dites-moi le format et le sujet, et je m'en occupe."
    
    def _generate_knowledge_response(self, message: str, knowledge_base: Dict) -> str:
        """Génère une réponse basée sur la connaissance"""
        return "C'est une excellente question ! Basé sur ma connaissance, je peux vous aider avec cela. Expliquez-moi plus en détail ce que vous souhaitez savoir."
    
    def _generate_conversational_response(self, message: str) -> str:
        """Génère une réponse conversationnelle"""
        responses = [
            "Je comprends parfaitement ! C'est un sujet fascinant.",
            "C'est très intéressant ! J'aimerais en savoir plus sur votre perspective.",
            "Hmm, laissez-moi réfléchir à cela... C'est une excellente remarque.",
            "Je vois ce que vous voulez dire. Analysons cela ensemble.",
            "Absolument ! C'est quelque chose que je peux traiter pour vous."
        ]
        return random.choice(responses)
