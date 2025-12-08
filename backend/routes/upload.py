import os
from flask import request, current_app
from flask_restful import Resource

from models.image_model import ImageModel
from utils.yolo_detection import detect_objects
from utils.descriptor_extraction import extract_descriptors


class UploadResource(Resource):
    def post(self):
        """
        Réception d'une ou plusieurs images.
        Étapes prévues :
        - Sauvegarder les fichiers dans uploads/
        - Lancer YOLO pour détecter les objets (detect_objects)
        - Extraire descripteurs (extract_descriptors)
        - Stocker métadonnées + descripteurs dans MongoDB
        """
        files = request.files.getlist("images")
        saved = []
        for file in files:
            filename = file.filename
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)

            # Placeholder YOLO + descripteurs (à implémenter)
            detected = detect_objects(save_path)
            descriptors = extract_descriptors(save_path)

            image_id = ImageModel.create(
                filename=filename,
                path=save_path,
                detected_objects=detected,
                descriptors=descriptors,
            )
            saved.append({"id": image_id, "filename": filename})

        return {"uploaded": saved}, 201

