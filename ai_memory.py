import json
import pickle
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import os

@dataclass
class MemoryEntry:
    timestamp: datetime.datetime
    user_message: str
    hibbi_response: str
    intent_type: str
    confidence: float
    entities: Dict[str, Any]
    context: Dict[str, Any]
    importance: float = 0.5

@dataclass
class UserProfile:
    user_id: str
    name: Optional[str] = None
    preferences: Dict[str, Any] = None
    interaction_count: int = 0
    first_interaction: Optional[datetime.datetime] = None
    last_interaction: Optional[datetime.datetime] = None
    favorite_topics: List[str] = None
    communication_style: str = "standard"
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.favorite_topics is None:
            self.favorite_topics = []

class AIMemory:
    """Système de mémoire avancé pour HIBBI"""
    
    def __init__(self, memory_file: str = "hibbi_memory.pkl"):
        self.memory_file = memory_file
        self.short_term_memory: List[MemoryEntry] = []
        self.long_term_memory: List[MemoryEntry] = []
        self.user_profiles: Dict[str, UserProfile] = {}
        self.knowledge_graph: Dict[str, List[str]] = {}
        self.emotional_memory: Dict[str, float] = {}
        
        # Configuration
        self.max_short_term = 50
        self.max_long_term = 1000
        self.importance_threshold = 0.7
        
        # Charger la mémoire existante
        self.load_memory()
    
    def add_memory(self, user_id: str, user_message: str, hibbi_response: str, 
                   intent_type: str, confidence: float, entities: Dict[str, Any], 
                   context: Dict[str, Any] = None) -> None:
        """Ajoute une nouvelle entrée de mémoire"""
        if context is None:
            context = {}
        
        # Créer l'entrée de mémoire
        entry = MemoryEntry(
            timestamp=datetime.datetime.now(),
            user_message=user_message,
            hibbi_response=hibbi_response,
            intent_type=intent_type,
            confidence=confidence,
            entities=entities,
            context=context,
            importance=self._calculate_importance(user_message, intent_type, confidence)
        )
        
        # Ajouter à la mémoire à court terme
        self.short_term_memory.append(entry)
        
        # Mettre à jour le profil utilisateur
        self._update_user_profile(user_id, entry)
        
        # Mettre à jour le graphe de connaissances
        self._update_knowledge_graph(entry)
        
        # Mettre à jour la mémoire émotionnelle
        self._update_emotional_memory(entry)
        
        # Transférer vers la mémoire à long terme si nécessaire
        if entry.importance >= self.importance_threshold:
            self._transfer_to_long_term(entry)
        
        # Limiter la mémoire à court terme
        if len(self.short_term_memory) > self.max_short_term:
            self._consolidate_short_term()
        
        # Limiter la mémoire à long terme
        if len(self.long_term_memory) > self.max_long_term:
            self._consolidate_long_term()
        
        # Sauvegarder périodiquement
        if len(self.short_term_memory) % 10 == 0:
            self.save_memory()
    
    def _calculate_importance(self, message: str, intent_type: str, confidence: float) -> float:
        """Calcule l'importance d'une mémoire"""
        importance = confidence * 0.5
        
        # Points pour les types d'intention spécifiques
        intent_importance = {
            "greeting": 0.2,
            "conversation": 0.4,
            "question": 0.6,
            "code_generation": 0.8,
            "image_generation": 0.8,
            "web_search": 0.7,
            "text_creation": 0.9,
            "analysis": 0.8
        }
        
        importance += intent_importance.get(intent_type, 0.5) * 0.3
        
        # Points pour la longueur du message
        if len(message) > 50:
            importance += 0.1
        if len(message) > 100:
            importance += 0.1
        
        return min(importance, 1.0)
    
    def _update_user_profile(self, user_id: str, entry: MemoryEntry) -> None:
        """Met à jour le profil utilisateur"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        profile = self.user_profiles[user_id]
        
        # Mettre à jour les compteurs
        profile.interaction_count += 1
        profile.last_interaction = entry.timestamp
        
        if profile.first_interaction is None:
            profile.first_interaction = entry.timestamp
        
        # Mettre à jour les sujets préférés
        if entry.intent_type not in profile.favorite_topics:
            profile.favorite_topics.append(entry.intent_type)
        
        # Mettre à jour les préférences
        if entry.entities:
            for key, value in entry.entities.items():
                if key not in profile.preferences:
                    profile.preferences[key] = []
                if isinstance(value, str) and value not in profile.preferences[key]:
                    profile.preferences[key].append(value)
    
    def _update_knowledge_graph(self, entry: MemoryEntry) -> None:
        """Met à jour le graphe de connaissances"""
        # Extraire les concepts clés du message
        words = entry.user_message.lower().split()
        
        for word in words:
            if len(word) > 3:  # Ignorer les mots courts
                if word not in self.knowledge_graph:
                    self.knowledge_graph[word] = []
                
                # Ajouter des connexions basées sur l'intention
                if entry.intent_type not in self.knowledge_graph[word]:
                    self.knowledge_graph[word].append(entry.intent_type)
                
                # Ajouter des connexions basées sur les entités
                for entity_key, entity_value in entry.entities.items():
                    if isinstance(entity_value, str) and entity_value not in self.knowledge_graph[word]:
                        self.knowledge_graph[word].append(entity_value)
    
    def _update_emotional_memory(self, entry: MemoryEntry) -> None:
        """Met à jour la mémoire émotionnelle"""
        # Détecter les émotions dans le message
        positive_words = ["bon", "excellent", "super", "génial", "parfait", "merci", "bravo"]
        negative_words = ["mauvais", "nul", "échec", "problème", "erreur", "difficile"]
        
        message_lower = entry.user_message.lower()
        
        emotion_score = 0.0
        for word in positive_words:
            if word in message_lower:
                emotion_score += 0.1
        
        for word in negative_words:
            if word in message_lower:
                emotion_score -= 0.1
        
        # Stocker l'émotion par type d'intention
        if entry.intent_type not in self.emotional_memory:
            self.emotional_memory[entry.intent_type] = 0.0
        
        self.emotional_memory[entry.intent_type] = (
            self.emotional_memory[entry.intent_type] * 0.9 + emotion_score * 0.1
        )
    
    def _transfer_to_long_term(self, entry: MemoryEntry) -> None:
        """Transfère une entrée vers la mémoire à long terme"""
        self.long_term_memory.append(entry)
    
    def _consolidate_short_term(self) -> None:
        """Consolide la mémoire à court terme"""
        # Garder les entrées les plus importantes
        self.short_term_memory.sort(key=lambda x: x.importance, reverse=True)
        self.short_term_memory = self.short_term_memory[:self.max_short_term]
    
    def _consolidate_long_term(self) -> None:
        """Consolide la mémoire à long terme"""
        # Supprimer les entrées les plus anciennes et moins importantes
        self.long_term_memory.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        self.long_term_memory = self.long_term_memory[:self.max_long_term]
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Récupère les mémoires pertinentes pour une requête"""
        query_lower = query.lower()
        relevant_memories = []
        
        # Chercher dans la mémoire à court terme
        for memory in self.short_term_memory:
            score = self._calculate_relevance_score(query_lower, memory)
            if score > 0.3:
                relevant_memories.append((memory, score))
        
        # Chercher dans la mémoire à long terme
        for memory in self.long_term_memory:
            score = self._calculate_relevance_score(query_lower, memory)
            if score > 0.3:
                relevant_memories.append((memory, score))
        
        # Trier par pertinence et retourner les meilleures
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in relevant_memories[:limit]]
    
    def _calculate_relevance_score(self, query: str, memory: MemoryEntry) -> float:
        """Calcule le score de pertinence d'une mémoire"""
        score = 0.0
        
        # Mots dans le message utilisateur
        query_words = set(query.split())
        memory_words = set(memory.user_message.lower().split())
        
        # Overlap de mots
        word_overlap = len(query_words.intersection(memory_words))
        if word_overlap > 0:
            score += word_overlap / len(query_words) * 0.4
        
        # Type d'intention correspondant
        if memory.intent_type in query:
            score += 0.3
        
        # Importance de la mémoire
        score += memory.importance * 0.2
        
        # Récence (mémoires plus récentes sont plus pertinentes)
        days_old = (datetime.datetime.now() - memory.timestamp).days
        recency_score = max(0, 1 - days_old / 30)  # Décroissance sur 30 jours
        score += recency_score * 0.1
        
        return min(score, 1.0)
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Récupère le profil d'un utilisateur"""
        return self.user_profiles.get(user_id)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la mémoire"""
        return {
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "user_profiles_count": len(self.user_profiles),
            "knowledge_graph_size": len(self.knowledge_graph),
            "emotional_memory_size": len(self.emotional_memory),
            "total_interactions": sum(p.interaction_count for p in self.user_profiles.values())
        }
    
    def search_knowledge(self, concept: str) -> List[str]:
        """Recherche des concepts connexes dans le graphe de connaissances"""
        return self.knowledge_graph.get(concept.lower(), [])
    
    def get_emotional_trends(self) -> Dict[str, float]:
        """Retourne les tendances émotionnelles"""
        return self.emotional_memory.copy()
    
    def save_memory(self) -> None:
        """Sauvegarde la mémoire sur le disque"""
        try:
            memory_data = {
                "short_term_memory": [asdict(entry) for entry in self.short_term_memory],
                "long_term_memory": [asdict(entry) for entry in self.long_term_memory],
                "user_profiles": {uid: asdict(profile) for uid, profile in self.user_profiles.items()},
                "knowledge_graph": self.knowledge_graph,
                "emotional_memory": self.emotional_memory
            }
            
            # Convertir les datetime en string pour la sérialisation
            for memory_list in [memory_data["short_term_memory"], memory_data["long_term_memory"]]:
                for entry in memory_list:
                    if entry["timestamp"]:
                        entry["timestamp"] = entry["timestamp"].isoformat()
            
            for profile in memory_data["user_profiles"].values():
                if profile["first_interaction"]:
                    profile["first_interaction"] = profile["first_interaction"].isoformat()
                if profile["last_interaction"]:
                    profile["last_interaction"] = profile["last_interaction"].isoformat()
            
            with open(self.memory_file, 'wb') as f:
                pickle.dump(memory_data, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la mémoire: {e}")
    
    def load_memory(self) -> None:
        """Charge la mémoire depuis le disque"""
        if not os.path.exists(self.memory_file):
            return
        
        try:
            with open(self.memory_file, 'rb') as f:
                memory_data = pickle.load(f)
            
            # Reconstruire les objets depuis les données
            self.short_term_memory = [
                MemoryEntry(
                    timestamp=datetime.datetime.fromisoformat(entry["timestamp"]) if entry["timestamp"] else None,
                    user_message=entry["user_message"],
                    hibbi_response=entry["hibbi_response"],
                    intent_type=entry["intent_type"],
                    confidence=entry["confidence"],
                    entities=entry["entities"],
                    context=entry["context"],
                    importance=entry["importance"]
                )
                for entry in memory_data.get("short_term_memory", [])
            ]
            
            self.long_term_memory = [
                MemoryEntry(
                    timestamp=datetime.datetime.fromisoformat(entry["timestamp"]) if entry["timestamp"] else None,
                    user_message=entry["user_message"],
                    hibbi_response=entry["hibbi_response"],
                    intent_type=entry["intent_type"],
                    confidence=entry["confidence"],
                    entities=entry["entities"],
                    context=entry["context"],
                    importance=entry["importance"]
                )
                for entry in memory_data.get("long_term_memory", [])
            ]
            
            self.user_profiles = {
                uid: UserProfile(
                    user_id=profile["user_id"],
                    name=profile.get("name"),
                    preferences=profile.get("preferences", {}),
                    interaction_count=profile.get("interaction_count", 0),
                    first_interaction=datetime.datetime.fromisoformat(profile["first_interaction"]) if profile.get("first_interaction") else None,
                    last_interaction=datetime.datetime.fromisoformat(profile["last_interaction"]) if profile.get("last_interaction") else None,
                    favorite_topics=profile.get("favorite_topics", []),
                    communication_style=profile.get("communication_style", "standard")
                )
                for uid, profile in memory_data.get("user_profiles", {}).items()
            }
            
            self.knowledge_graph = memory_data.get("knowledge_graph", {})
            self.emotional_memory = memory_data.get("emotional_memory", {})
            
        except Exception as e:
            print(f"Erreur lors du chargement de la mémoire: {e}")
    
    def clear_memory(self) -> None:
        """Efface toute la mémoire"""
        self.short_term_memory.clear()
        self.long_term_memory.clear()
        self.user_profiles.clear()
        self.knowledge_graph.clear()
        self.emotional_memory.clear()
        
        # Supprimer le fichier de mémoire
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
