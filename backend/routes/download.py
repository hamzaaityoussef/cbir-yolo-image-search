from flask import send_file
from flask_restful import Resource

from models.image_model import ImageModel


class DownloadResource(Resource):
    def get(self, image_id: str):
        """
        Télécharger une image par son id.
        """
        image = ImageModel.find_by_id(image_id)
        if not image:
            return {"error": "not_found"}, 404

        return send_file(image["path"], as_attachment=True)

