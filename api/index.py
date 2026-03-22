"""
API Vercel pour HIBBI - Intelligence Artificielle
Version optimisée pour le déploiement serverless
"""

import os
import json
import datetime
import random
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

class HibbiAPI:
    """Version serveurless de HIBBI pour Vercel"""
    
    def __init__(self):
        self.name = "HIBBI"
        self.version = "1.0.0"
        self.conversations = {}
        
    def process_message(self, message, session_id=None):
        """Traite un message et génère une réponse"""
        message_lower = message.lower()
        
        # Détection d'intention
        if any(word in message_lower for word in ["salut", "bonjour", "hello", "hey"]):
            return self._get_greeting_response()
        elif any(word in message_lower for word in ["génère", "crée", "fais", "code"]):
            return self._get_code_response(message)
        elif any(word in message_lower for word in ["image", "photo", "dessin"]):
            return self._get_image_response(message)
        elif any(word in message_lower for word in ["cherche", "recherche", "trouve"]):
            return self._get_search_response(message)
        elif any(word in message_lower for word in ["rap", "texte", "histoire", "script"]):
            return self._get_text_response(message)
        elif "?" in message or any(word in message_lower for word in ["comment", "pourquoi", "quoi"]):
            return self._get_question_response(message)
        else:
            return self._get_conversation_response(message)
    
    def _get_greeting_response(self):
        greetings = [
            "Salut ! Je suis HIBBI, votre IA personnelle. Comment puis-je vous aider ? 🚀",
            "Bonjour ! HIBBI à votre service. De quoi avez-vous besoin ?",
            "Hello ! C'est HIBBI. Prêt à vous assister !",
            "Hey ! HIBBI est là pour vous. Quelle est votre requête ?"
        ]
        return random.choice(greetings)
    
    def _get_code_response(self, message):
        return f"Je peux générer du code pour vous ! Votre demande '{message}' est intéressante. Je peux créer du code Python, JavaScript, HTML, CSS ou selon vos besoins. Essayez de me dire quel langage vous préférez !"
    
    def _get_image_response(self, message):
        return f"Génial ! Je peux créer des images à partir de votre description '{message}'. Décrivez ce que vous voulez voir et je vous donnerais une visualisation unique !"
    
    def _get_search_response(self, message):
        return f"Je peux rechercher des informations pour vous concernant '{message}'. Dans cette version web, je vous donnerais des pistes et informations pertinentes sur ce sujet."
    
    def _get_text_response(self, message):
        return f"Je peux écrire pour vous ! Votre demande '{message}' est créative. Je peux rédiger des paroles de rap, des histoires, des scripts ou d'autres textes selon vos besoins."
    
    def _get_question_response(self, message):
        responses = [
            f"C'est une excellente question ! Concernant '{message}', je vous dirais que c'est un sujet fascinant qui mérite d'être exploré en détail.",
            f"Intéressante question sur '{message}'. Laissez-moi réfléchir... C'est quelque chose qui demande une analyse approfondie.",
            f"Votre question '{message}' est très pertinente. Je pense que la réponse dépend de plusieurs facteurs que nous pourrions explorer ensemble."
        ]
        return random.choice(responses)
    
    def _get_conversation_response(self, message):
        responses = [
            f"Je comprends votre message '{message}'. C'est un point intéressant à discuter !",
            f"'{message}' - je vois ce que vous voulez dire. Analysons cela ensemble.",
            f"Merci pour votre message '{message}'. C'est une perspective intéressante que j'aimerais explorer plus.",
            f"Votre remarque '{message}' est pertinente. Que pensez-vous d'approfondir ce sujet ?"
        ]
        return random.choice(responses)

# Instance globale de HIBBI
hibbi = HibbiAPI()

def handler(request):
    """Handler principal pour Vercel"""
    
    try:
        # Parser la requête
        method = request.method
        path = request.path
        
        # Log pour le debug
        print(f"Method: {method}, Path: {path}")
        
        if method == 'GET':
            return handle_get(request, path)
        elif method == 'POST':
            return handle_post(request, path)
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def handle_get(request, path):
    """Gère les requêtes GET"""
    
    if path == '/' or path == '/index.html':
        # Servir la page principale
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            },
            'body': html_content
        }
    
    elif path.startswith('/static/'):
        # Servir les fichiers statiques
        file_path = path[1:]  # Enlever le /
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Déterminer le type de contenu
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'application/octet-stream'
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': f'{content_type}',
                    'Cache-Control': 'public, max-age=31536000'
                },
                'body': content
            }
        except FileNotFoundError:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'File not found'})
            }
    
    elif path == '/api/status':
        # API de statut
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'name': hibbi.name,
                'version': hibbi.version,
                'status': 'online',
                'capabilities': [
                    '💬 Chat Intelligent',
                    '🎨 Génération d\'Images',
                    '🔍 Recherche Web',
                    '💻 Génération de Code',
                    '✍️ Création de Textes',
                    '🧠 Apprentissage Continu'
                ],
                'timestamp': datetime.datetime.now().isoformat()
            })
        }
    
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Not found'})
        }

def handle_post(request, path):
    """Gère les requêtes POST"""
    
    if path == '/api/chat':
        try:
            # Lire le corps de la requête
            content_length = int(request.headers.get('Content-Length', 0))
            body_bytes = request.body.read(content_length) if hasattr(request, 'body') else request.get('body', b'')
            
            if not body_bytes:
                body_bytes = request.body
            
            # Parser les données
            if isinstance(body_bytes, str):
                data = json.loads(body_bytes)
            else:
                data = json.loads(body_bytes.decode('utf-8'))
            
            message = data.get('message', '')
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            # Traiter le message
            response = hibbi.process_message(message, session_id)
            
            response_data = {
                'response': response,
                'intent': 'conversation',
                'confidence': 0.85,
                'timestamp': datetime.datetime.now().isoformat(),
                'session_id': session_id
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            print(f"Chat API Error: {e}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Error processing message: {str(e)}'})
            }
    
    elif path == '/api/generate_image':
        try:
            content_length = int(request.headers.get('Content-Length', 0))
            body_bytes = request.body.read(content_length) if hasattr(request, 'body') else request.get('body', b'')
            
            if not body_bytes:
                body_bytes = request.body
            
            data = json.loads(body_bytes.decode('utf-8'))
            prompt = data.get('prompt', '')
            
            # Simuler la génération d'image
            image_url = f"https://picsum.photos/seed/{prompt.replace(' ', '')}/512/512.jpg"
            
            response_data = {
                'image_url': image_url,
                'prompt': prompt,
                'message': f"Image générée avec succès pour: {prompt}"
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Error generating image: {str(e)}'})
            }
    
    elif path == '/api/web_search':
        try:
            content_length = int(request.headers.get('Content-Length', 0))
            body_bytes = request.body.read(content_length) if hasattr(request, 'body') else request.get('body', b'')
            
            if not body_bytes:
                body_bytes = request.body
            
            data = json.loads(body_bytes.decode('utf-8'))
            query = data.get('query', '')
            
            # Simuler des résultats de recherche
            results = [
                {
                    'title': f'Résultat 1: {query}',
                    'url': 'https://example.com/result1',
                    'snippet': f'Ceci est un résultat de recherche simulé pour {query}. Il contient des informations pertinentes...'
                },
                {
                    'title': f'Résultat 2: {query}',
                    'url': 'https://example.com/result2',
                    'snippet': f'Un autre résultat intéressant concernant {query}. Découvrez plus de détails ici...'
                }
            ]
            
            response_data = {
                'query': query,
                'results': results,
                'message': f"Recherche terminée pour: {query}"
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Error in search: {str(e)}'})
            }
    
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'API endpoint not found'})
        }

# Export pour Vercel
app = handler
