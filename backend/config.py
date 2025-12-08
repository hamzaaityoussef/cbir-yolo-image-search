import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/cbir")
MONGO_DB = os.getenv("MONGO_DB", "cbir")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "uploads"))

# Créer le dossier uploads si absent
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

