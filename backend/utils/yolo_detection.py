"""
Wrapper pour la détection d'objets via YOLOv8n.
Remplacer les stubs par l'appel réel au modèle (ultralytics YOLO).
"""

from typing import Any, Dict, List


def load_model():
    """
    Charger le modèle YOLOv8n.
    Exemple avec ultralytics:
    from ultralytics import YOLO
    return YOLO("yolov8n.pt")
    """
    return None


def detect_objects(image_path: str) -> List[Dict[str, Any]]:
    """
    Retourner une liste d'objets détectés :
    [
      {"class": "person", "confidence": 0.9, "bbox": [x1,y1,x2,y2]}
    ]
    """
    # TODO: brancher le modèle réel
    return []

