from flask import request
from flask_restful import Resource


class TransformResource(Resource):
    def post(self, image_id: str):
        """
        Appliquer une transformation (crop, resize, etc.) sur une image.
        Étapes prévues :
        - Récupérer l'image par id
        - Appliquer la transformation demandée (payload)
        - Sauvegarder nouvelle image + métadonnées
        """
        payload = request.get_json(force=True)
        # TODO: implémenter la logique de transformation
        return {"transformed_from": image_id, "params": payload}, 200

