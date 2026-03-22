"""
Version simplifiée de HIBBI qui ne nécessite aucune dépendance externe
Ce fichier peut être converti en .exe avec uniquement la bibliothèque standard Python
"""

import os
import sys
import json
import datetime
import random
import string
import webbrowser
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

class HibbiSimple:
    """Version simplifiée de HIBBI sans dépendances externes"""
    
    def __init__(self):
        self.name = "HIBBI"
        self.version = "1.0.0"
        self.conversations = []
        self.user_preferences = {}
        
    def process_message(self, message):
        """Traite un message et génère une réponse"""
        message_lower = message.lower()
        
        # Détection d'intention simple
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
        return f"Je peux générer du code pour vous ! Votre demande '{message}' est intéressante. Dans la version complète, je créerais du code Python, JavaScript, HTML ou CSS selon vos besoins. Essayez de me dire quel langage vous préférez !"
    
    def _get_image_response(self, message):
        return f"Génial ! Je peux créer des images à partir de votre description '{message}'. Dans la version complète, je générerais une image unique basée sur votre texte. Décrivez ce que vous voulez voir !"
    
    def _get_search_response(self, message):
        return f"Je peux rechercher des informations pour vous concernant '{message}'. Dans la version complète, je ferais une recherche web et vous donnerais les résultats les plus pertinents."
    
    def _get_text_response(self, message):
        return f"Je peux écrire pour vous ! Votre demande '{message}' est créative. Dans la version complète, je rédigerais des paroles de rap, des histoires, des scripts ou d'autres textes selon vos besoins."
    
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

class HibbiHandler(SimpleHTTPRequestHandler):
    """Handler HTTP pour HIBBI"""
    
    def __init__(self, *args, **kwargs):
        self.hibbi = HibbiSimple()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Gère les requêtes GET"""
        if self.path == '/':
            self.serve_file('templates/index_simple.html')
        elif self.path.startswith('/static/'):
            self.serve_static_file()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Gère les requêtes POST"""
        if self.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_error(404)
    
    def serve_file(self, filename):
        """Sert un fichier HTML"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404)
    
    def serve_static_file(self):
        """Sert un fichier statique"""
        try:
            # Retirer /static/ du chemin
            file_path = self.path[1:]  # Enlever le /
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Déterminer le type de contenu
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', f'{content_type}; charset=utf-8')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)
    
    def handle_chat(self):
        """Gère les requêtes de chat"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            response = self.hibbi.process_message(message)
            
            response_data = {
                'response': response,
                'intent': 'conversation',
                'confidence': 0.8,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

def create_simple_html():
    """Crée une version HTML simplifiée"""
    html_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIBBI - Intelligence Artificielle</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            text-align: center;
            padding: 2rem;
            background: rgba(0,0,0,0.2);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .chat-container {
            flex: 1;
            max-width: 800px;
            margin: 2rem auto;
            width: 90%;
            display: flex;
            flex-direction: column;
        }
        
        .messages {
            flex: 1;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 1.5rem;
            overflow-y: auto;
            margin-bottom: 1rem;
            min-height: 400px;
        }
        
        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 10px;
            animation: slideIn 0.3s ease-out;
        }
        
        .hibbi-message {
            background: rgba(102, 126, 234, 0.3);
            border-left: 4px solid #667eea;
        }
        
        .user-message {
            background: rgba(118, 75, 162, 0.3);
            border-left: 4px solid #764ba2;
            text-align: right;
        }
        
        .message-sender {
            font-weight: bold;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        .input-container {
            display: flex;
            gap: 1rem;
        }
        
        .chat-input {
            flex: 1;
            padding: 1rem;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            background: rgba(255,255,255,0.9);
            color: #333;
        }
        
        .send-button {
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s;
        }
        
        .send-button:hover {
            transform: translateY(-2px);
        }
        
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .typing {
            font-style: italic;
            opacity: 0.7;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .features {
            text-align: center;
            padding: 1rem;
            background: rgba(0,0,0,0.2);
        }
        
        .features h3 {
            margin-bottom: 1rem;
        }
        
        .feature-list {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 10px;
            min-width: 120px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 HIBBI</h1>
        <p>Intelligence Artificielle Personnelle - Version Simplifiée</p>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message hibbi-message">
                <div class="message-sender">HIBBI</div>
                <div>Salut ! Je suis HIBBI, votre intelligence artificielle personnelle. Je peux discuter avec vous, répondre à vos questions et vous aider dans vos projets. Comment puis-je vous aider aujourd'hui ? 🚀</div>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="chatInput" class="chat-input" placeholder="Écrivez votre message..." />
            <button id="sendButton" class="send-button">Envoyer</button>
        </div>
    </div>
    
    <div class="features">
        <h3>🌟 Fonctionnalités de HIBBI</h3>
        <div class="feature-list">
            <div class="feature">💬 Chat Intelligent</div>
            <div class="feature">🎨 Génération d'Images</div>
            <div class="feature">💻 Génération de Code</div>
            <div class="feature">✍️ Création de Textes</div>
            <div class="feature">🔍 Recherche Web</div>
        </div>
    </div>
    
    <script>
        const messages = document.getElementById('messages');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = `
                <div class="message-sender">${sender === 'hibbi' ? 'HIBBI' : 'Vous'}</div>
                <div>${text}</div>
            `;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function addTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message hibbi-message typing';
            typingDiv.id = 'typing';
            typingDiv.innerHTML = `
                <div class="message-sender">HIBBI</div>
                <div>HIBBI réfléchit...</div>
            `;
            messages.appendChild(typingDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function removeTypingIndicator() {
            const typing = document.getElementById('typing');
            if (typing) {
                typing.remove();
            }
        }
        
        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            
            addMessage(message, 'user');
            chatInput.value = '';
            sendButton.disabled = true;
            addTypingIndicator();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                removeTypingIndicator();
                addMessage(data.response, 'hibbi');
            } catch (error) {
                removeTypingIndicator();
                addMessage('Désolé, une erreur est survenue. Réessayez.', 'hibbi');
            } finally {
                sendButton.disabled = false;
            }
        }
        
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        chatInput.focus();
    </script>
</body>
</html>'''
    
    # Créer le dossier templates s'il n'existe pas
    os.makedirs('templates', exist_ok=True)
    
    with open('templates/index_simple.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Fichier HTML simplifié créé")

def start_server():
    """Démarre le serveur web"""
    create_simple_html()
    
    PORT = 5000
    
    print(f"🚀 Démarrage de HIBBI sur le port {PORT}")
    print(f"🌐 Ouvrez votre navigateur sur: http://localhost:{PORT}")
    print("🛑 Appuyez sur Ctrl+C pour arrêter HIBBI")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), HibbiHandler) as httpd:
            print(f"✅ HIBBI est démarré et prêt !")
            
            # Ouvrir le navigateur automatiquement après 2 secondes
            def open_browser():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{PORT}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de HIBBI...")
        print("Au revoir ! 🤖")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    start_server()
