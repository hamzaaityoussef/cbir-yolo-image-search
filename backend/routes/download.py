"""
Route pour télécharger une image.
Permet de récupérer une image stockée par son ID MongoDB.
"""

import os
from flask import send_file, jsonify
from flask_restful import Resource

from models.image_model import ImageModel


class DownloadResource(Resource):
    """
    Endpoint: GET /download/<image_id>
    
    Fonctionnement:
    1. Récupère l'image depuis MongoDB par son ID
    2. Vérifie que le fichier existe sur le disque
    3. Envoie le fichier au client avec le bon Content-Type
    
    Paramètres:
    - image_id: ID MongoDB de l'image
    
    Réponse:
    - 200: Fichier image (Content-Type: image/jpeg, image/png, etc.)
    - 404: Image non trouvée
    - 500: Erreur serveur
    """
    
    def get(self, image_id: str):
        """Télécharge une image par son ID."""
        # Récupérer l'image depuis MongoDB
        image = ImageModel.find_by_id(image_id)
        
        if not image:
            return {"error": "Image non trouvée"}, 404
        
        file_path = image.get("path")
        
        if not file_path or not os.path.exists(file_path):
            return {"error": "Fichier image introuvable sur le serveur"}, 404
        
        try:
            # Déterminer le type MIME à partir de l'extension
            _, ext = os.path.splitext(file_path)
            mimetype_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mimetype = mimetype_map.get(ext.lower(), 'application/octet-stream')
            
            # Envoyer le fichier
            return send_file(
                file_path,
                mimetype=mimetype,
                as_attachment=False,  # Afficher dans le navigateur plutôt que télécharger
                download_name=image.get("filename", "image")
            )
        except Exception as e:
            return {"error": f"Erreur lors du téléchargement: {str(e)}"}, 500
