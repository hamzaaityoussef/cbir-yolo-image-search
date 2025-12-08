"""
Route pour supprimer une image.
Supprime à la fois le fichier sur le disque et les métadonnées dans MongoDB.
"""

import os
from flask_restful import Resource

from models.image_model import ImageModel


class DeleteResource(Resource):
    """
    Endpoint: DELETE /delete/<image_id>
    
    Fonctionnement:
    1. Récupère l'image depuis MongoDB par son ID
    2. Supprime le fichier physique du disque (si existe)
    3. Supprime les métadonnées de MongoDB
    
    Paramètres:
    - image_id: ID MongoDB de l'image à supprimer
    
    Réponse:
    {
        "deleted": "image_id",
        "message": "Image supprimée avec succès"
    }
    - 200: Suppression réussie
    - 404: Image non trouvée
    """
    
    def delete(self, image_id: str):
        """Supprime une image et ses métadonnées."""
        # Récupérer l'image depuis MongoDB
        image = ImageModel.find_by_id(image_id)
        
        if not image:
            return {"error": "Image non trouvée"}, 404
        
        file_path = image.get("path")
        
        # Supprimer le fichier physique s'il existe
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Logger l'erreur mais continuer la suppression des métadonnées
                print(f"Erreur lors de la suppression du fichier {file_path}: {str(e)}")
        
        # Supprimer les métadonnées de MongoDB
        try:
            ImageModel.delete(image_id)
        except Exception as e:
            return {"error": f"Erreur lors de la suppression des métadonnées: {str(e)}"}, 500
        
        return {
            "deleted": image_id,
            "filename": image.get("filename"),
            "message": "Image supprimée avec succès"
        }, 200
