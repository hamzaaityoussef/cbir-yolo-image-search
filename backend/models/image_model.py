from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient

from config import MONGO_DB, MONGO_URI


def get_db():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB]


class ImageModel:
    """Gestion des documents Image dans MongoDB."""

    collection_name = "images"

    @classmethod
    def collection(cls):
        return get_db()[cls.collection_name]

    @classmethod
    def create(
        cls,
        filename: str,
        path: str,
        detected_objects: Optional[List[Dict[str, Any]]] = None,
        descriptors: Optional[Dict[str, Any]] = None,
    ) -> str:
        doc = {
            "filename": filename,
            "path": path,
            "detected_objects": detected_objects or [],
            "descriptors": descriptors or {},
            "uploaded_at": datetime.utcnow(),
        }
        result = cls.collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, image_id: str) -> Optional[Dict[str, Any]]:
        return cls.collection().find_one({"_id": cls._to_object_id(image_id)})

    @classmethod
    def delete(cls, image_id: str) -> None:
        cls.collection().delete_one({"_id": cls._to_object_id(image_id)})

    @classmethod
    def all(cls) -> List[Dict[str, Any]]:
        return list(cls.collection().find())

    @staticmethod
    def _to_object_id(image_id: str):
        from bson import ObjectId

        try:
            return ObjectId(image_id)
        except Exception:
            return None

