"""
Wrapper pour la détection d'objets via YOLOv8n.
Utilise ultralytics pour charger et exécuter le modèle YOLOv8n.
"""

from typing import Any, Dict, List
from ultralytics import YOLO

_model = None


def load_model():
    """
    Charge le modèle YOLOv8n (lazy loading, chargé une seule fois).
    Le modèle sera téléchargé automatiquement au premier appel.
    """
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")  # Télécharge automatiquement si absent
    return _model


def detect_objects(image_path: str) -> List[Dict[str, Any]]:
    """
    Détecte les objets dans une image en utilisant YOLOv8n.
    
    Args:
        image_path: Chemin vers l'image à analyser
    
    Returns:
        Liste de dictionnaires contenant pour chaque objet détecté :
        - class: nom de la classe (ex: "person", "car", "dog")
        - confidence: score de confiance (0.0 à 1.0)
        - bbox: bounding box [x1, y1, x2, y2] en coordonnées pixel
    """
    model = load_model()
    results = model(image_path)
    detected = []
    
    for r in results:
        for box in r.boxes:
            detected.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            })
    
    return detected