"""
Route pour appliquer des transformations aux images.
Permet de créer de nouvelles images à partir d'images existantes
en appliquant des transformations (crop, resize, rotation, etc.).
"""

import os
import uuid
import cv2
import numpy as np
from flask import request, jsonify, current_app
from flask_restful import Resource

from models.image_model import ImageModel
from utils.yolo_detection import detect_objects
from utils.descriptor_extraction import extract_descriptors


class TransformResource(Resource):
    """
    Endpoint: POST /transform/<image_id>
    
    Fonctionnement:
    1. Récupère l'image originale par son ID
    2. Applique la transformation demandée (crop, resize, rotation, etc.)
    3. Sauvegarde la nouvelle image transformée
    4. Détecte les objets et extrait les descripteurs de la nouvelle image
    5. Stocke la nouvelle image dans MongoDB
    
    Paramètres URL:
    - image_id: ID de l'image source
    
    Format de la requête (JSON):
    {
        "transform": "crop",  // ou "resize", "rotate", "flip", "brightness", "contrast"
        "params": {
            // Pour crop:
            "x": 100, "y": 100, "width": 200, "height": 200
            // Pour resize:
            "width": 800, "height": 600  // ou "scale": 0.5
            // Pour rotate:
            "angle": 90  // degrés
            // Pour flip:
            "direction": "horizontal"  // ou "vertical", "both"
            // Pour brightness/contrast:
            "brightness": 1.2, "contrast": 1.5
        }
    }
    
    Réponse:
    {
        "transformed_image_id": "...",
        "original_image_id": "...",
        "filename": "transformed_image.jpg",
        "transform": "crop",
        "objects_detected": [...]
    }
    """
    
    def post(self, image_id: str):
        """Applique une transformation à une image."""
        # Récupérer l'image source
        original_image = ImageModel.find_by_id(image_id)
        if not original_image:
            return {"error": "Image source non trouvée"}, 404
        
        # Charger l'image
        image_path = original_image["path"]
        if not os.path.exists(image_path):
            return {"error": "Fichier image introuvable"}, 404
        
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Impossible de charger l'image"}, 500
        
        # Récupérer les paramètres de transformation
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        transform_type = data.get("transform", "resize")
        params = data.get("params", {})
        
        # Appliquer la transformation
        try:
            transformed_img = self._apply_transform(img, transform_type, params)
        except Exception as e:
            return {"error": f"Erreur lors de la transformation: {str(e)}"}, 400
        
        # Générer un nouveau nom de fichier
        original_filename = original_image["filename"]
        name, ext = os.path.splitext(original_filename)
        new_filename = f"{name}_transformed_{uuid.uuid4().hex[:8]}{ext}"
        new_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename)
        
        # Sauvegarder l'image transformée
        cv2.imwrite(new_path, transformed_img)
        
        # Détecter les objets et extraire les descripteurs
        detected_objects = []
        try:
            detected_objects = detect_objects(new_path)
        except Exception as e:
            print(f"Erreur YOLO pour {new_filename}: {str(e)}")
        
        descriptors = {}
        try:
            descriptors = extract_descriptors(new_path)
        except Exception as e:
            return {"error": f"Erreur extraction descripteurs: {str(e)}"}, 500
        
        # Stocker la nouvelle image dans MongoDB
        new_image_id = ImageModel.create(
            filename=new_filename,
            path=new_path,
            detected_objects=detected_objects,
            descriptors=descriptors,
        )
        
        return {
            "transformed_image_id": new_image_id,
            "original_image_id": image_id,
            "filename": new_filename,
            "transform": transform_type,
            "params": params,
            "objects_detected": len(detected_objects)
        }, 201
    
    def _apply_transform(self, img: np.ndarray, transform_type: str, params: dict) -> np.ndarray:
        """
        Applique une transformation à une image.
        
        Args:
            img: Image OpenCV (BGR)
            transform_type: Type de transformation
            params: Paramètres de la transformation
        
        Returns:
            Image transformée
        """
        h, w = img.shape[:2]
        
        if transform_type == "crop":
            # Crop: x, y, width, height
            x = int(params.get("x", 0))
            y = int(params.get("y", 0))
            width = int(params.get("width", w))
            height = int(params.get("height", h))
            
            # S'assurer que les coordonnées sont valides
            x = max(0, min(x, w))
            y = max(0, min(y, h))
            width = max(1, min(width, w - x))
            height = max(1, min(height, h - y))
            
            return img[y:y+height, x:x+width]
        
        elif transform_type == "resize":
            # Resize: width, height ou scale
            if "scale" in params:
                scale = float(params["scale"])
                new_w = int(w * scale)
                new_h = int(h * scale)
            else:
                new_w = int(params.get("width", w))
                new_h = int(params.get("height", h))
            
            return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        elif transform_type == "rotate":
            # Rotation: angle en degrés
            angle = float(params.get("angle", 0))
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Calculer les nouvelles dimensions
            cos = np.abs(matrix[0, 0])
            sin = np.abs(matrix[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))
            
            # Ajuster la matrice de rotation
            matrix[0, 2] += (new_w / 2) - center[0]
            matrix[1, 2] += (new_h / 2) - center[1]
            
            return cv2.warpAffine(img, matrix, (new_w, new_h), flags=cv2.INTER_LINEAR)
        
        elif transform_type == "flip":
            # Flip: horizontal, vertical, both
            direction = params.get("direction", "horizontal")
            
            if direction == "horizontal":
                return cv2.flip(img, 1)
            elif direction == "vertical":
                return cv2.flip(img, 0)
            elif direction == "both":
                return cv2.flip(img, -1)
            else:
                return img
        
        elif transform_type == "brightness" or transform_type == "contrast":
            # Ajustement de luminosité/contraste
            brightness = float(params.get("brightness", 1.0))
            contrast = float(params.get("contrast", 1.0))
            
            # Convertir en float pour les calculs
            img_float = img.astype(np.float32)
            
            # Appliquer brightness (ajout) et contrast (multiplication)
            adjusted = (img_float * contrast) + (brightness - 1.0) * 128
            
            # Clamper les valeurs entre 0 et 255
            adjusted = np.clip(adjusted, 0, 255)
            
            return adjusted.astype(np.uint8)
        
        else:
            raise ValueError(f"Type de transformation inconnu: {transform_type}")
