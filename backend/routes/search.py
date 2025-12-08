"""
Route pour la recherche d'images similaires par contenu.
Permet de rechercher des images similaires à une image requête,
optionnellement en se concentrant sur un objet spécifique détecté.
"""

import os
import cv2
import numpy as np
from flask import request, jsonify
from flask_restful import Resource

from models.image_model import ImageModel
from utils.descriptor_extraction import extract_descriptors
from utils.similarity_search import search_similar_images


class SearchResource(Resource):
    """
    Endpoint: POST /search
    
    Fonctionnement:
    1. Reçoit soit:
       - Une image requête (fichier) à analyser
       - Un image_id existant + optionnellement un objet_id pour se concentrer sur un objet
    2. Extrait les descripteurs de l'image requête (ou de l'objet sélectionné)
    3. Compare avec toutes les images en base
    4. Retourne les images les plus similaires triées par score
    
    Format de la requête (option 1 - nouvelle image):
    {
        "type": "upload",
        "image": <fichier multipart>
    }
    
    Format de la requête (option 2 - image existante):
    {
        "type": "existing",
        "image_id": "mongodb_id",
        "object_id": 0  // Optionnel: index de l'objet dans detected_objects
    }
    
    Format de la requête (option 3 - objet spécifique):
    {
        "type": "object",
        "image_id": "mongodb_id",
        "object_class": "person"  // Filtrer par classe d'objet
    }
    
    Réponse:
    {
        "query_info": {
            "image_id": "...",
            "objects_detected": [...]
        },
        "results": [
            {
                "image_id": "...",
                "filename": "...",
                "similarity_score": 0.123,
                "detected_objects": [...]
            },
            ...
        ],
        "count": 10
    }
    """
    
    def post(self):
        """Recherche des images similaires."""
        search_type = request.form.get("type", "upload")
        
        query_descriptors = None
        query_info = {}
        
        try:
            if search_type == "upload":
                # Nouvelle image uploadée
                if 'image' not in request.files:
                    return {"error": "Aucune image fournie"}, 400
                
                file = request.files['image']
                if file.filename == '':
                    return {"error": "Fichier vide"}, 400
                
                # Sauvegarder temporairement
                import tempfile
                temp_path = os.path.join(tempfile.gettempdir(), file.filename)
                file.save(temp_path)
                
                try:
                    # Détecter les objets et extraire les descripteurs
                    from utils.yolo_detection import detect_objects
                    detected = detect_objects(temp_path)
                    query_descriptors = extract_descriptors(temp_path)
                    
                    query_info = {
                        "type": "upload",
                        "filename": file.filename,
                        "objects_detected": detected
                    }
                finally:
                    # Nettoyer le fichier temporaire
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            elif search_type == "existing":
                # Image existante en base
                image_id = request.form.get("image_id") or request.json.get("image_id")
                if not image_id:
                    return {"error": "image_id requis"}, 400
                
                image = ImageModel.find_by_id(image_id)
                if not image:
                    return {"error": "Image non trouvée"}, 404
                
                # Optionnel: se concentrer sur un objet spécifique
                object_id = request.form.get("object_id") or request.json.get("object_id")
                
                if object_id is not None:
                    # Extraire les descripteurs d'un objet spécifique (crop de l'objet)
                    object_id = int(object_id)
                    detected_objects = image.get("detected_objects", [])
                    
                    if 0 <= object_id < len(detected_objects):
                        obj = detected_objects[object_id]
                        bbox = obj.get("bbox", [])
                        
                        # Charger l'image et cropper l'objet
                        img = cv2.imread(image["path"])
                        if img is not None and len(bbox) == 4:
                            x1, y1, x2, y2 = [int(coord) for coord in bbox]
                            x1, y1 = max(0, x1), max(0, y1)
                            x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
                            
                            cropped = img[y1:y2, x1:x2]
                            
                            # Sauvegarder temporairement le crop
                            import tempfile
                            temp_path = os.path.join(tempfile.gettempdir(), f"crop_{image_id}.jpg")
                            cv2.imwrite(temp_path, cropped)
                            
                            try:
                                query_descriptors = extract_descriptors(temp_path)
                            finally:
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                            
                            query_info = {
                                "type": "object",
                                "image_id": image_id,
                                "object_index": object_id,
                                "object_class": obj.get("class"),
                                "bbox": bbox
                            }
                        else:
                            # Fallback: utiliser les descripteurs de l'image complète
                            query_descriptors = image.get("descriptors", {})
                            query_info = {
                                "type": "existing",
                                "image_id": image_id
                            }
                    else:
                        return {"error": "Index d'objet invalide"}, 400
                else:
                    # Utiliser les descripteurs de l'image complète
                    query_descriptors = image.get("descriptors", {})
                    query_info = {
                        "type": "existing",
                        "image_id": image_id,
                        "objects_detected": image.get("detected_objects", [])
                    }
            
            else:
                return {"error": "Type de recherche invalide"}, 400
            
            if not query_descriptors:
                return {"error": "Impossible d'extraire les descripteurs"}, 500
            
            # Récupérer toutes les images de la base
            all_images = ImageModel.all()
            
            # Filtrer par classe d'objet si demandé
            object_class_filter = request.form.get("object_class") or (request.json.get("object_class") if request.is_json else None)
            if object_class_filter:
                filtered_images = []
                for img in all_images:
                    detected = img.get("detected_objects", [])
                    if any(obj.get("class") == object_class_filter for obj in detected):
                        filtered_images.append(img)
                all_images = filtered_images
            
            # Rechercher les images similaires
            top_k = int(request.form.get("top_k", 10) or (request.json.get("top_k", 10) if request.is_json else 10))
            similar_images = search_similar_images(query_descriptors, all_images, top_k=top_k)
            
            # Construire la réponse
            results = []
            for image_id, similarity_score in similar_images:
                image = ImageModel.find_by_id(image_id)
                if image:
                    results.append({
                        "image_id": image_id,
                        "filename": image.get("filename"),
                        "similarity_score": round(similarity_score, 4),
                        "detected_objects": image.get("detected_objects", []),
                        "uploaded_at": image.get("uploaded_at").isoformat() if image.get("uploaded_at") else None
                    })
            
            return {
                "query_info": query_info,
                "results": results,
                "count": len(results)
            }, 200
            
        except Exception as e:
            return {"error": f"Erreur lors de la recherche: {str(e)}"}, 500
