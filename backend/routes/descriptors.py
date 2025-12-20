"""
Endpoint pour obtenir les descripteurs détaillés d'une image ou d'un objet spécifique.
"""
from flask_restful import Resource
from flask import request
from models.image_model import ImageModel

class DescriptorsResource(Resource):
    """
    Endpoint: GET /descriptors/<image_id>
    Option: ?object_id=0 pour obtenir les descripteurs d'un objet spécifique
    """
    def get(self, image_id):
        image = ImageModel.find_by_id(image_id)
        if not image:
            return {"error": "Image non trouvée"}, 404

        object_id = request.args.get("object_id")
        if object_id is not None:
            try:
                object_id = int(object_id)
                detected_objects = image.get("detected_objects", [])
                if 0 <= object_id < len(detected_objects):
                    obj = detected_objects[object_id]
                    descriptors = obj.get("descriptors", {})
                    return {"object_id": object_id, "object_class": obj.get("class"), "descriptors": descriptors}, 200
                else:
                    return {"error": "Index d'objet invalide"}, 400
            except Exception:
                return {"error": "object_id invalide"}, 400
        else:
            descriptors = image.get("descriptors", {})
            return {"image_id": image_id, "descriptors": descriptors}, 200