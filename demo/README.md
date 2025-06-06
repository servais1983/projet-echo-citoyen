# Démo ECHO 🔊

Cette démo présente les fonctionnalités principales du projet ECHO de manière simplifiée.

## 🚀 Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Télécharger le modèle spaCy :
```bash
python -m spacy download fr_core_news_md
```

## 🎯 Fonctionnalités

- Authentification JWT
- Analyse de sentiment des messages
- Catégorisation automatique des requêtes
- Calcul de priorité

## 🛠️ Utilisation

1. Démarrer le serveur :
```bash
python main.py
```

2. Accéder à l'interface Swagger :
```
http://localhost:8000/docs
```

3. Authentification :
- Username : johndoe
- Password : secret

4. Exemples de requêtes :

Analyse d'un message :
```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"content": "Il y a un nid de poule dangereux rue de la Paix"}'
```

## 📝 Exemples de messages à tester

- "Il y a un nid de poule dangereux rue de la Paix"
- "Les lampadaires ne fonctionnent pas dans ma rue"
- "Les poubelles débordent depuis plusieurs jours"
- "Le parc est très bien entretenu"

## 🔒 Sécurité

Cette démo utilise une clé secrète simple pour la démonstration. En production, utilisez une clé secrète forte et stockez-la de manière sécurisée.

## 📚 Documentation

La documentation complète de l'API est disponible sur :
```
http://localhost:8000/docs
``` 