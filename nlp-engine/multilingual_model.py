"""
Module de classification multilingue pour le projet ECHO.
Ce module utilise des modèles transformers pour analyser et classifier les requêtes
citoyennes dans plusieurs langues.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Catégories de requêtes
CATEGORIES = [
    "infrastructure",  # routes, éclairage, etc.
    "environnement",   # pollution, déchets, etc.
    "securite",        # police, urgences, etc.
    "social",          # aide sociale, logement, etc.
    "administration",  # papiers, procédures, etc.
]

class MultilingualClassifier:
    """
    Classifieur multilingue basé sur XLM-RoBERTa pour catégoriser les requêtes citoyennes
    dans différentes langues.
    """
    
    def __init__(self, model_name: str = "xlm-roberta-base", num_labels: int = len(CATEGORIES)):
        """
        Initialise le classifieur multilingue.
        
        Args:
            model_name: Nom du modèle pré-entraîné à utiliser
            num_labels: Nombre de catégories de classification
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        logger.info(f"Modèle initialisé sur {self.device}")
        
    def train(self, dataset: Dict[str, Any], output_dir: str = "./model-output"):
        """
        Entraîne le modèle sur un dataset spécifique.
        
        Args:
            dataset: Dataset d'entraînement (format transformers Dataset)
            output_dir: Répertoire où sauvegarder le modèle entraîné
        """
        logger.info(f"Début de l'entraînement sur {len(dataset['train'])} exemples")
        
        # Configuration de l'entraînement
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=3,
            weight_decay=0.01,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            logging_dir="./logs",
        )
        
        # Initialisation du trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset["train"],
            eval_dataset=dataset["validation"],
            tokenizer=self.tokenizer,
        )
        
        # Entraînement du modèle
        trainer.train()
        
        # Sauvegarde du modèle final
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Entraînement terminé, modèle sauvegardé dans {output_dir}")
        
        # Évaluation du modèle
        eval_results = trainer.evaluate()
        logger.info(f"Résultats d'évaluation: {eval_results}")
        
        return eval_results
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Prédit la catégorie d'une requête citoyenne.
        
        Args:
            text: Texte de la requête à classifier
            
        Returns:
            Dictionnaire contenant la catégorie prédite et le score de confiance
        """
        # Préparation des inputs
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Prédiction
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
        # Conversion en probabilités
        probs = torch.nn.functional.softmax(logits, dim=-1)
        
        # Obtention de la classe prédite et du score
        predicted_class_idx = torch.argmax(probs, dim=-1).item()
        confidence_score = probs[0, predicted_class_idx].item()
        
        # Construction du résultat
        result = {
            "category": CATEGORIES[predicted_class_idx],
            "category_id": predicted_class_idx,
            "confidence": confidence_score,
            "all_scores": {
                category: probs[0, i].item() 
                for i, category in enumerate(CATEGORIES)
            }
        }
        
        return result
    
    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Prédit les catégories pour une liste de requêtes.
        
        Args:
            texts: Liste des textes à classifier
            
        Returns:
            Liste de dictionnaires contenant les prédictions
        """
        # Préparation des inputs
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Prédiction
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
        # Conversion en probabilités
        probs = torch.nn.functional.softmax(logits, dim=-1)
        
        # Construction des résultats
        results = []
        for i, text_probs in enumerate(probs):
            predicted_class_idx = torch.argmax(text_probs).item()
            confidence_score = text_probs[predicted_class_idx].item()
            
            result = {
                "text": texts[i][:50] + "..." if len(texts[i]) > 50 else texts[i],
                "category": CATEGORIES[predicted_class_idx],
                "category_id": predicted_class_idx,
                "confidence": confidence_score,
                "all_scores": {
                    category: text_probs[j].item() 
                    for j, category in enumerate(CATEGORIES)
                }
            }
            results.append(result)
            
        return results
    
    def load_model(self, model_path: str):
        """
        Charge un modèle pré-entraîné.
        
        Args:
            model_path: Chemin vers le modèle sauvegardé
        """
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.to(self.device)
        logger.info(f"Modèle chargé depuis {model_path}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation du classifieur
    classifier = MultilingualClassifier()
    
    # Exemples de requêtes en différentes langues
    requests = [
        "L'éclairage public ne fonctionne plus dans ma rue depuis trois jours.",  # Français
        "There is a large pothole on Main Street that needs urgent repair.",      # Anglais
        "Necesito ayuda para obtener mi certificado de residencia.",              # Espagnol
        "Es gibt zu viele Abfälle im Stadtpark.",                                # Allemand
    ]
    
    # Classification des requêtes (simulation sans entraînement)
    print("Simulation de prédiction (modèle non entraîné):")
    for request in requests:
        # En production, on utiliserait le modèle entraîné
        # Ici, nous simulons juste les résultats pour démonstration
        import random
        category = random.choice(CATEGORIES)
        print(f"Requête: {request[:50]}...")
        print(f"Catégorie prédite: {category}")
        print("-" * 50)
