"""
Wrapper pour la détection d'objets via YOLO.
Utilise ultralytics pour charger et exécuter le modèle YOLO personnalisé (best.pt).
"""

import os
from typing import Any, Dict, List
from ultralytics import YOLO

_model = None


def load_model():
    """
    Charge le modèle YOLO personnalisé best.pt (lazy loading, chargé une seule fois).
    Le modèle est chargé depuis le dossier fine_tuned_model/.
    """
    global _model
    if _model is None:
        # Chemin vers le modèle personnalisé
        model_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "fine_tuned_model", 
            "best.pt"
        )
        
        # Vérifier si le fichier existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modèle personnalisé non trouvé : {model_path}\n"
                "Assurez-vous que le fichier best.pt existe dans backend/fine_tuned_model/"
            )
        
        print(f"Chargement du modèle depuis : {model_path}")
        _model = YOLO(model_path)
        
        # Afficher les informations du modèle
        print(f"Modèle chargé avec succès!")
        print(f"Classes disponibles : {_model.names}")
        print(f"Nombre de classes : {len(_model.names)}")
        
    return _model


def detect_objects(image_path: str, conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
    """
    Détecte les objets dans une image en utilisant le modèle YOLO personnalisé (best.pt).
    
    Args:
        image_path: Chemin vers l'image à analyser
        conf_threshold: Seuil de confiance minimum (par défaut 0.25)
    
    Returns:
        Liste de dictionnaires contenant pour chaque objet détecté :
        - class: nom de la classe (selon les classes du modèle personnalisé)
        - confidence: score de confiance (0.0 à 1.0)
        - bbox: bounding box [x1, y1, x2, y2] en coordonnées pixel
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image non trouvée : {image_path}")
    
    model = load_model()
    
    # Lancer la détection avec un seuil de confiance ajustable
    # verbose=False pour éviter trop de logs
    results = model.predict(
        source=image_path,
        conf=conf_threshold,
        iou=0.45,  # Non-Maximum Suppression threshold
        verbose=False,
        device='cpu'  # Forcer CPU si problème avec GPU
    )
    
    detected = []
    
    # Parcourir les résultats
    for result in results:
        # Vérifier si des boxes ont été détectées
        if result.boxes is None or len(result.boxes) == 0:
            continue
        
        # Parcourir chaque box détectée
        for box in result.boxes:
            try:
                # Extraire la classe
                cls_id = int(box.cls.cpu().item())
                
                # Extraire la confiance
                confidence = float(box.conf.cpu().item())
                
                # Extraire les coordonnées de la bounding box
                xyxy = box.xyxy.cpu().numpy()[0]  # [x1, y1, x2, y2]
                bbox = [float(x) for x in xyxy]
                
                # Obtenir le nom de la classe
                class_name = model.names[cls_id] if cls_id in model.names else f"class_{cls_id}"
                
                detected.append({
                    "class": class_name,
                    "confidence": confidence,
                    "bbox": bbox
                })
                
            except Exception as e:
                print(f"Erreur lors du traitement d'une box : {str(e)}")
                continue
    
    print(f"Détection terminée : {len(detected)} objet(s) trouvé(s) dans {image_path}")
    
    return detected


def test_detection(image_path: str):
    """
    Fonction de test pour vérifier que la détection fonctionne.
    Affiche les résultats dans la console.
    
    Args:
        image_path: Chemin vers une image de test
    """
    print(f"\n{'='*60}")
    print(f"TEST DE DÉTECTION")
    print(f"{'='*60}")
    print(f"Image : {image_path}")
    
    try:
        # Tester avec différents seuils de confiance
        for conf in [0.01, 0.10, 0.25, 0.50]:
            print(f"\n--- Seuil de confiance : {conf} ---")
            detections = detect_objects(image_path, conf_threshold=conf)
            
            if len(detections) == 0:
                print("❌ Aucun objet détecté")
            else:
                print(f"✅ {len(detections)} objet(s) détecté(s) :")
                for i, det in enumerate(detections, 1):
                    print(f"  {i}. {det['class']} (confiance: {det['confidence']:.3f})")
    
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Test avec une image (à adapter selon votre structure)
    import sys
    
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
    else:
        # Chemin par défaut pour test
        test_image = os.path.join(
            os.path.dirname(__file__),
            "..",
            "uploads",
            "test_image.jpg"
        )
    
    if os.path.exists(test_image):
        test_detection(test_image)
    else:
        print(f"❌ Image de test non trouvée : {test_image}")
        print("Usage : python yolo_detection.py <chemin_vers_image>")