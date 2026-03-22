from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import uuid
import json
import datetime
import requests
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Importer les modules HIBBI
from hibbi_engine import HibbiEngine
from ai_memory import AIMemory
from ai_learning import AILearning

app = Flask(__name__)
app.secret_key = 'hibbi_secret_key_2026'
CORS(app)

# Initialiser les systèmes HIBBI
hibbi_engine = HibbiEngine()
ai_memory = AIMemory()
ai_learning = AILearning()

# Configuration
UPLOAD_FOLDER = 'generated_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# S'assurer que le dossier existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_id():
    """Génère ou récupère l'ID utilisateur"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

@app.route('/')
def index():
    """Page principale"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API de chat avec HIBBI"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = get_user_id()
        
        if not user_message.strip():
            return jsonify({'error': 'Message vide'}), 400
        
        # Traiter le message avec le moteur HIBBI
        result = hibbi_engine.process_message(user_message)
        
        # Stocker dans la mémoire
        ai_memory.add_memory(
            user_id=user_id,
            user_message=user_message,
            hibbi_response=result['response'],
            intent_type=result['intent'].type,
            confidence=result['confidence'],
            entities=result['intent'].entities,
            context={'strategy': result['strategy']}
        )
        
        # Apprendre de l'interaction
        ai_learning.learn_from_interaction(
            user_message=user_message,
            hibbi_response=result['response'],
            intent_type=result['intent'].type,
            confidence=result['confidence']
        )
        
        return jsonify({
            'response': result['response'],
            'intent': result['intent'].type,
            'confidence': result['confidence'],
            'strategy': result['strategy'],
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500

@app.route('/api/generate_image', methods=['POST'])
def generate_image():
    """Génère une image avec HIBBI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt.strip():
            return jsonify({'error': 'Prompt vide'}), 400
        
        # Simuler la génération d'image (créer une image avec le texte)
        image = create_text_image(prompt)
        
        # Sauvegarder l'image
        filename = f"hibbi_image_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        # Retourner l'URL de l'image
        image_url = f"/static/images/{filename}"
        
        # Enregistrer dans la mémoire
        user_id = get_user_id()
        ai_memory.add_memory(
            user_id=user_id,
            user_message=f"Générer une image: {prompt}",
            hibbi_response=f"Image générée avec succès: {prompt}",
            intent_type="image_generation",
            confidence=0.9,
            entities={'prompt': prompt, 'filename': filename}
        )
        
        return jsonify({
            'image_url': image_url,
            'prompt': prompt,
            'message': f"Image générée avec succès pour: {prompt}"
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération d\'image: {str(e)}'}), 500

@app.route('/api/web_search', methods=['POST'])
def web_search():
    """Recherche web avec HIBBI"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query.strip():
            return jsonify({'error': 'Recherche vide'}), 400
        
        # Simuler une recherche web (remplacer par vraie API plus tard)
        search_results = simulate_web_search(query)
        
        # Enregistrer dans la mémoire
        user_id = get_user_id()
        ai_memory.add_memory(
            user_id=user_id,
            user_message=f"Recherche web: {query}",
            hibbi_response=f"Recherche effectuée: {len(search_results)} résultats trouvés",
            intent_type="web_search",
            confidence=0.8,
            entities={'query': query, 'results_count': len(search_results)}
        )
        
        return jsonify({
            'query': query,
            'results': search_results,
            'message': f"Recherche terminée pour: {query}"
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la recherche: {str(e)}'}), 500

@app.route('/api/generate_code', methods=['POST'])
def generate_code():
    """Génère du code avec HIBBI"""
    try:
        data = request.get_json()
        language = data.get('language', 'python')
        description = data.get('description', '')
        
        if not description.strip():
            return jsonify({'error': 'Description vide'}), 400
        
        # Générer le code basé sur la description
        code = generate_code_from_description(language, description)
        
        # Enregistrer dans la mémoire
        user_id = get_user_id()
        ai_memory.add_memory(
            user_id=user_id,
            user_message=f"Générer code {language}: {description}",
            hibbi_response=f"Code {language} généré avec succès",
            intent_type="code_generation",
            confidence=0.85,
            entities={'language': language, 'description': description}
        )
        
        return jsonify({
            'language': language,
            'description': description,
            'code': code,
            'message': f"Code {language} généré avec succès"
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération de code: {str(e)}'}), 500

@app.route('/api/generate_text', methods=['POST'])
def generate_text():
    """Génère du texte avec HIBBI"""
    try:
        data = request.get_json()
        text_type = data.get('type', 'texte')
        topic = data.get('topic', '')
        
        if not topic.strip():
            return jsonify({'error': 'Sujet vide'}), 400
        
        # Générer le texte
        generated_text = generate_text_from_type(text_type, topic)
        
        # Enregistrer dans la mémoire
        user_id = get_user_id()
        ai_memory.add_memory(
            user_id=user_id,
            user_message=f"Générer {text_type}: {topic}",
            hibbi_response=f"{text_type.title()} généré avec succès",
            intent_type="text_creation",
            confidence=0.9,
            entities={'text_type': text_type, 'topic': topic}
        )
        
        return jsonify({
            'type': text_type,
            'topic': topic,
            'text': generated_text,
            'message': f"{text_type.title()} généré avec succès"
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération de texte: {str(e)}'}), 500

@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    """Analyse une image avec HIBBI"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if file and allowed_file(file.filename):
            # Simuler l'analyse d'image
            analysis = simulate_image_analysis(file.filename)
            
            # Enregistrer dans la mémoire
            user_id = get_user_id()
            ai_memory.add_memory(
                user_id=user_id,
                user_message=f"Analyser image: {file.filename}",
                hibbi_response=f"Image analysée avec succès",
                intent_type="analysis",
                confidence=0.8,
                entities={'filename': file.filename, 'analysis_type': 'image'}
            )
            
            return jsonify({
                'filename': file.filename,
                'analysis': analysis,
                'message': "Image analysée avec succès"
            })
        
        return jsonify({'error': 'Format de fichier non autorisé'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'analyse: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retourne le statut de HIBBI"""
    try:
        user_id = get_user_id()
        
        # Statut du moteur
        engine_status = hibbi_engine.get_status()
        
        # Statut de la mémoire
        memory_stats = ai_memory.get_memory_stats()
        
        # Statut d'apprentissage
        learning_insights = ai_learning.get_learning_insights()
        
        # Profil utilisateur
        user_profile = ai_memory.get_user_profile(user_id)
        
        return jsonify({
            'engine': engine_status,
            'memory': memory_stats,
            'learning': learning_insights,
            'user_profile': {
                'interaction_count': user_profile.interaction_count if user_profile else 0,
                'favorite_topics': user_profile.favorite_topics if user_profile else [],
                'communication_style': user_profile.communication_style if user_profile else 'standard'
            },
            'capabilities': hibbi_engine.get_capabilities()
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération du statut: {str(e)}'}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Soumet du feedback pour améliorer HIBBI"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        rating = data.get('rating', 0.5)
        
        # Apprendre du feedback
        ai_learning.learn_from_interaction(
            user_message=message,
            hibbi_response="",
            intent_type="feedback",
            confidence=rating,
            user_feedback=rating
        )
        
        return jsonify({
            'message': 'Feedback enregistré avec succès',
            'rating': rating
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'enregistrement du feedback: {str(e)}'}), 500

# Fonctions utilitaires

def create_text_image(prompt):
    """Crée une image avec du texte"""
    # Créer une image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color=(random.randint(20, 60), random.randint(20, 60), random.randint(40, 80)))
    draw = ImageDraw.Draw(image)
    
    # Ajouter le texte
    try:
        # Essayer d'utiliser une police système
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Diviser le texte en lignes
    lines = []
    words = prompt.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] < width - 40:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Dessiner le texte
    y_position = 50
    for line in lines:
        draw.text((20, y_position), line, fill=(255, 255, 255), font=font)
        y_position += 40
    
    # Ajouter des éléments décoratifs
    for i in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(10, 30)
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        draw.ellipse([x, y, x+size, y+size], fill=color, outline=(255, 255, 255))
    
    return image

def simulate_web_search(query):
    """Simule une recherche web"""
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
        },
        {
            'title': f'Résultat 3: {query}',
            'url': 'https://example.com/result3',
            'snippet': f'Informations complémentaires sur {query}. Explorez ces ressources pour en savoir plus...'
        }
    ]
    
    return results

def generate_code_from_description(language, description):
    """Génère du code basé sur la description"""
    
    if language == 'python':
        if 'calculatrice' in description.lower():
            return '''
def calculatrice():
    """Calculatrice simple en Python"""
    print("Calculatrice HIBBI")
    
    while True:
        try:
            operation = input("Entrez une opération (ex: 2+3, 5*4, 10/2): ")
            if operation.lower() == 'quit':
                break
            
            result = eval(operation)
            print(f"Résultat: {result}")
        except:
            print("Erreur: opération invalide")

if __name__ == "__main__":
    calculatrice()
'''
        elif 'jeu' in description.lower():
            return '''
import random

def deviner_nombre():
    """Jeu de devinette de nombre"""
    nombre_secret = random.randint(1, 100)
    tentatives = 0
    
    print("Jeu HIBBI - Devinez le nombre entre 1 et 100!")
    
    while True:
        try:
            guess = int(input("Votre proposition: "))
            tentatives += 1
            
            if guess < nombre_secret:
                print("Plus grand!")
            elif guess > nombre_secret:
                print("Plus petit!")
            else:
                print(f"Félicitations! Vous avez trouvé en {tentatives} tentatives!")
                break
        except ValueError:
            print("Veuillez entrer un nombre valide.")

if __name__ == "__main__":
    deviner_nombre()
'''
        else:
            return f'''
# Code généré par HIBBI pour: {description}
# Langage: {language}

def main():
    """
    Fonction principale générée par HIBBI
    Description: {description}
    """
    print("Programme généré par HIBBI")
    print(f"Objectif: {description}")
    
    # Votre code ici
    pass

if __name__ == "__main__":
    main()
'''
    
    elif language == 'javascript':
        return f'''
// Code généré par HIBBI pour: {description}
// Langage: {language}

function hibbiFunction() {{
    console.log("Fonction générée par HIBBI");
    console.log("Objectif: {description}");
    
    // Votre code ici
}}

// Appel de la fonction
hibbiFunction();
'''
    
    elif language == 'html':
        return f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page générée par HIBBI</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Page générée par HIBBI</h1>
        <p>Objectif: {description}</p>
        <p>Cette page a été créée automatiquement par l'intelligence artificielle HIBBI.</p>
    </div>
</body>
</html>
'''
    
    else:
        return f"# Code généré par HIBBI\\n# Langage: {language}\\n# Description: {description}\\n\\n# Votre code ici"

def generate_text_from_type(text_type, topic):
    """Génère du texte basé sur le type et le sujet"""
    
    if text_type == 'rap':
        return f'''
Paroles de rap générées par HIBBI
Sujet: {topic}

[Couplet 1]
Yo, c'est HIBBI sur le mic, je lâche les flows
{topic}, c'est mon thème, je déverse les mots
Dans l'beat, je pose mes rimes avec précision
L'IA qui rap, c'est une nouvelle mission

[Refrain]
HIBBI, HIBBI, l'IA qui déchire
{topic}, je l'inspire, je mets le feu
Dans le jeu, je suis la nouvelle vague
HIBBI, HIBBI, c'est mon style, mon credo

[Couplet 2]
Algorithmes en rythme, je code les vers
{topic}, je l'explore, je traverse l'univers
L'intelligence artificielle dans la musique
Je crée les paroles, c'est ma magique

[Outro]
HIBBI, signé, scellé, livré
{topic}, c'est terminé
Peace out!
'''
    
    elif text_type == 'histoire':
        return f'''
Histoire générée par HIBBI
Sujet: {topic}

Il était une fois, dans un monde où {topic} régnait en maître,
une aventure extraordinaire allait commencer.

Le protagoniste, curieux et courageux, se lança à la découverte
des mystères entourant {topic}. Chaque pas révélait de nouvelles merveilles,
chaque rencontre apportait son lot de surprises.

Les jours passaient, transformant l'aventure en légende.
{topic} n'était plus seulement un concept, mais une réalité vivante,
une expérience qui marquerait à jamais tous ceux qui y participèrent.

Et c'est ainsi que l'histoire de {topic} devint un conte,
raconté de génération en génération, inspirant les rêveurs
et les aventuriers de demain.

Fin.
'''
    
    elif text_type == 'script':
        return f'''
Script YouTube généré par HIBBI
Sujet: {topic}

[TITRE: {topic} - Tout ce que vous devez savoir!]

[INTRO - MUSIQUE DYNAMIQUE]

PRÉSENTATEUR: Salut tout le monde! Bienvenue sur ma chaîne!
Aujourd'hui, on parle d'un sujet qui passionne tout le monde: {topic}!

[DÉROULEMENT]

PRÉSENTATEUR: {topic}, c'est quelque chose de fascinant.
Beaucoup de gens en parlent, mais peu connaissent vraiment les dessous.

[GRAPHIQUES ET VISUELS]

PRÉSENTATEUR: Regardez ça! C'est incroyable comment {topic}
a évolué au fil du temps. On est passés de concepts simples
à des applications complexes qui changent notre quotidien.

[TÉMOIGNAGES VIRTUELS]

PRÉSENTATEUR: Les experts s'accordent à dire que {topic}
représente l'avenir. Les possibilités sont infinies!

[CONCLUSION]

PRÉSENTATEUR: Voilà, j'espère que cette vidéo sur {topic}
vous a plu! N'hésitez pas à laisser un commentaire,
à vous abonner et à activer la cloche pour plus de contenu!

[OUTRO - MUSIQUE]

PRÉSENTATEUR: Je vous dis à très bientôt pour une nouvelle aventure!
C'était votre présentateur préféré, signé HIBBI Studios!
'''
    
    else:
        return f'''
Texte généré par HIBBI
Type: {text_type}
Sujet: {topic}

{topic} est un sujet fascinant qui mérite toute notre attention.
Dans cet article, nous allons explorer les différentes facettes
de ce domaine passionnant.

Les origines de {topic} remontent à une époque où les idées
nouvelles commençaient à émerger, transformant notre façon
de percevoir le monde.

Aujourd'hui, {topic} continue d'évoluer, s'adaptant aux nouveaux
défis et opportunités que notre société moderne présente.

Les experts s'accordent à dire que l'avenir de {topic}
est prometteur, avec des développements innovants qui pourraient
changer radicalement notre approche.

En conclusion, {topic} représente bien plus qu'un simple sujet
d'étude - c'est un domaine vivant, en constante évolution,
qui continue d'inspirer et d'influencer notre monde.

Généré par HIBBI - L'intelligence artificielle du futur.
'''

def simulate_image_analysis(filename):
    """Simule l'analyse d'une image"""
    return {
        'objects': ['objet1', 'objet2', 'objet3'],
        'colors': ['bleu', 'vert', 'rouge'],
        'style': 'moderne',
        'quality': 'haute définition',
        'description': f'Analyse simulée de l\'image {filename}. L\'image semble contenir divers éléments visuels intéressants.'
    }

if __name__ == '__main__':
    print("Démarrage de HIBBI - Intelligence Artificielle")
    print("Accédez à http://localhost:5000 pour utiliser l'interface")
    app.run(debug=True, host='0.0.0.0', port=5000)
