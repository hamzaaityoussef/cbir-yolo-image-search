import os
from flask_restful import Resource

from models.image_model import ImageModel


class DeleteResource(Resource):
    def delete(self, image_id: str):
        """
        Supprimer l'image et ses métadonnées.
        """
        image = ImageModel.find_by_id(image_id)
        if not image:
            return {"error": "not_found"}, 404

        if os.path.exists(image["path"]):
            os.remove(image["path"])

        ImageModel.delete(image_id)
        return {"deleted": image_id}, 200

