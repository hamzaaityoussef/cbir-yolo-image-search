# CBIR & YOLO Image Search (Flask + Angular + MongoDB)

Projet académique pour le module "Multimedia Mining and Indexing". Cette base de code fournit le squelette complet pour :
- Un backend Flask (API REST) avec endpoints vides pour l'upload, la suppression, la recherche par descripteurs, etc.
- Un frontend Angular pour l'upload, la galerie, la recherche et la vue des descripteurs.
- Une base MongoDB pour stocker les métadonnées (chemins, objets détectés, descripteurs, date).

## Prérequis
- Python 3.10+ et pip
- Node.js 18+ et npm
- MongoDB en local ou accessible via URI

## Backend (Flask)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
# créer un fichier .env avec MONGO_URI, MONGO_DB, UPLOAD_FOLDER
python app.py
```

Endpoints (à compléter) :
- `POST /upload` : uploader une ou plusieurs images
- `GET /download/<id>` : télécharger une image
- `DELETE /delete/<id>` : supprimer une image et ses métadonnées
- `POST /search` : recherche d'objets similaires (YOLO + descripteurs)
- `POST /transform/<id>` : appliquer une transformation (crop, resize, etc.)

Points d'entrée du code :
- `routes/*.py` : ressources Flask-RESTful
- `utils/yolo_detection.py` : wrapper YOLOv8n (détection objets)
- `utils/descriptor_extraction.py` : extraction des descripteurs (couleur, texture, Hu, Gabor, etc.)
- `models/image_model.py` : accès MongoDB et structure des documents
- `uploads/` : stockage des images (ignoré par git)

## Frontend (Angular)
```bash
cd frontend
npm install
npm start            # proxy Angular si besoin, sinon npm run build
```
Composants :
- `image-upload` : formulaire pour uploader une ou plusieurs images
- `image-gallery` : liste des images, boutons download/delete/transform
- `image-search` : sélection d’une image requête et affichage des résultats
- `descriptor-view` : affichage des descripteurs pour une image/objet

Services :
- `api.service.ts` : appels HTTP vers l’API Flask (upload/download/delete/search/transform)

## Notes d’implémentation YOLO & descripteurs
- Ajouter le chargement du modèle YOLOv8n dans `utils/yolo_detection.py` (bibliothèque `ultralytics` recommandée).
- Les descripteurs couleur/texture/forme sont à implémenter dans `utils/descriptor_extraction.py` (histogrammes, Tamura, Gabor, moments de Hu, etc.).
- Stocker dans MongoDB les métadonnées : nom de fichier, chemin, objets détectés (classes, bounding boxes, scores), descripteurs visuels, date d’upload.

## Structure
```
backend/
  app.py
  config.py
  models/
  routes/
  utils/
  uploads/
frontend/
  src/
    app/
      components/
      services/
```

## Sécurité et CORS
- `flask-cors` est activé pour accepter les requêtes Angular.
- Ne pas exposer le fichier `.env` (contient URI Mongo, secrets).

## Licences / données
- Ne pas committer les images ou datasets volumineux (`uploads/` ignoré).
- ImageNet : sélectionner 15 catégories pertinentes pour le mini-projet.

