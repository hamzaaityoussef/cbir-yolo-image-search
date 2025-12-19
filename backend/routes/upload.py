"""
Route pour l'upload d'images.
Permet d'uploader une ou plusieurs images, détecte les objets avec YOLO,
extrait les descripteurs visuels et stocke tout dans MongoDB.
"""

import os
import uuid
from flask import request, current_app, jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename

import cv2

from models.image_model import ImageModel
from utils.yolo_detection import detect_objects
from utils.descriptor_extraction import extract_descriptors, extract_object_descriptors


# Extensions autorisées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}


def allowed_file(filename: str) -> bool:
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class UploadResource(Resource):
    """
    Endpoint: POST /upload
    
    Fonctionnement:
    1. Reçoit une ou plusieurs images via multipart/form-data
    2. Valide les extensions de fichiers
    3. Sauvegarde les fichiers dans le dossier uploads/
    4. Pour chaque image:
       - Détecte les objets avec YOLOv8n
       - Extrait tous les descripteurs visuels (couleur, texture, forme)
       - Stocke les métadonnées dans MongoDB
    
    Format de la requête:
    - Content-Type: multipart/form-data
    - Champ: "images" (peut être multiple)
    
    Réponse:
    {
        "uploaded": [
            {"id": "image_id_1", "filename": "image1.jpg"},
            {"id": "image_id_2", "filename": "image2.jpg"}
        ],
        "errors": []  # Si des erreurs se produisent
    }
    """
    
    def post(self):
        """Gère l'upload d'une ou plusieurs images."""
        if 'images' not in request.files:
            return {"error": "Aucun fichier fourni"}, 400
        
        files = request.files.getlist("images")
        if not files or files[0].filename == '':
            return {"error": "Aucun fichier sélectionné"}, 400
        
        uploaded = []
        errors = []
        
        for file in files:
            if not file or not file.filename:
                continue
            
            # Vérifier l'extension
            if not allowed_file(file.filename):
                errors.append({
                    "filename": file.filename,
                    "error": "Extension non autorisée"
                })
                continue
            
            try:
                # Générer un nom de fichier unique pour éviter les collisions
                original_filename = secure_filename(file.filename)
                name, ext = os.path.splitext(original_filename)
                unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
                
                # Sauvegarder le fichier
                save_path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], 
                    unique_filename
                )
                file.save(save_path)
                
                # Détecter les objets avec YOLO
                detected_objects = []
                try:
                    detected_objects = detect_objects(save_path)
                except Exception as e:
                    # Si YOLO échoue, continuer quand même
                    print(f"Erreur YOLO pour {unique_filename}: {str(e)}")
                
                # Charger l'image pour extraire les descripteurs
                image = cv2.imread(save_path)
                if image is None:
                    errors.append({
                        "filename": unique_filename,
                        "error": "Impossible de charger l'image"
                    })
                    if os.path.exists(save_path):
                        os.remove(save_path)
                    continue
                
                # Extraire les descripteurs visuels de l'image complète
                descriptors = {}
                try:
                    descriptors = extract_descriptors(save_path)
                except Exception as e:
                    errors.append({
                        "filename": unique_filename,
                        "error": f"Erreur extraction descripteurs image: {str(e)}"
                    })
                    # Supprimer le fichier si l'extraction échoue
                    if os.path.exists(save_path):
                        os.remove(save_path)
                    continue
                
                # Extraire les descripteurs pour chaque objet détecté
                for obj in detected_objects:
                    try:
                        bbox = obj.get("bbox", [])
                        if len(bbox) == 4:
                            # Extraire les descripteurs de cet objet spécifique
                            object_descriptors = extract_object_descriptors(image, bbox)
                            # Ajouter les descripteurs à l'objet
                            obj["descriptors"] = object_descriptors
                    except Exception as e:
                        # Si l'extraction échoue pour un objet, continuer avec les autres
                        print(f"Erreur extraction descripteurs pour objet {obj.get('class', 'unknown')}: {str(e)}")
                        obj["descriptors"] = {}
                
                # Stocker dans MongoDB
                image_id = ImageModel.create(
                    filename=unique_filename,
                    path=save_path,
                    detected_objects=detected_objects,
                    descriptors=descriptors,
                )
                
                uploaded.append({
                    "id": image_id,
                    "filename": unique_filename,
                    "objects_detected": len(detected_objects)
                })
                
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
                # Nettoyer le fichier en cas d'erreur
                if 'save_path' in locals() and os.path.exists(save_path):
                    os.remove(save_path)
        
        response = {
            "uploaded": uploaded,
            "count": len(uploaded)
        }
        
        if errors:
            response["errors"] = errors
        
        status_code = 201 if uploaded else 400
        return response, status_code
