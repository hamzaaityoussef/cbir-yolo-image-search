"""
Route pour lister toutes les images stockées.
Utile pour afficher la galerie d'images dans le frontend.
"""

from flask import request
from flask_restful import Resource

from models.image_model import ImageModel


class ListResource(Resource):
    """
    Endpoint: GET /images
    
    Fonctionnement:
    1. Récupère toutes les images de MongoDB
    2. Retourne les métadonnées (sans les descripteurs complets pour économiser la bande passante)
    3. Optionnel: filtre par classe d'objet détectée
    
    Paramètres de requête (optionnels):
    - object_class: Filtrer les images contenant cette classe d'objet
    - limit: Nombre maximum de résultats (défaut: 100)
    - offset: Nombre de résultats à sauter (pour pagination)
    
    Réponse:
    {
        "images": [
            {
                "id": "...",
                "filename": "...",
                "uploaded_at": "2024-01-01T00:00:00",
                "objects_detected": [
                    {"class": "person", "confidence": 0.9, ...}
                ],
                "objects_count": 2
            },
            ...
        ],
        "count": 10,
        "total": 50
    }
    """
    
    def get(self):
        """Liste toutes les images avec leurs métadonnées."""
        # Paramètres de requête
        object_class = request.args.get("object_class")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        
        # Récupérer toutes les images
        all_images = ImageModel.all()
        
        # Filtrer par classe d'objet si demandé
        if object_class:
            filtered_images = []
            for img in all_images:
                detected = img.get("detected_objects", [])
                if any(obj.get("class") == object_class for obj in detected):
                    filtered_images.append(img)
            all_images = filtered_images
        
        total = len(all_images)
        
        # Pagination
        paginated_images = all_images[offset:offset + limit]
        
        # Construire la réponse (sans les descripteurs complets)
        images_data = []
        for img in paginated_images:
            detected_objects = img.get("detected_objects", [])
            
            # Extraire seulement les classes uniques pour l'affichage
            classes = list(set([obj.get("class") for obj in detected_objects if obj.get("class")]))
            
            images_data.append({
                "id": str(img["_id"]),
                "filename": img.get("filename"),
                "uploaded_at": img.get("uploaded_at").isoformat() if img.get("uploaded_at") else None,
                "objects_detected": detected_objects,
                "objects_count": len(detected_objects),
                "object_classes": classes
            })
        
        return {
            "images": images_data,
            "count": len(images_data),
            "total": total,
            "offset": offset,
            "limit": limit
        }, 200

