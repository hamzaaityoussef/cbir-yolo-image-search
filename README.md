# CBIR & YOLO Image Search (Flask + Angular + MongoDB)

Projet académique pour le module "Multimedia Mining and Indexing". Application Web complète pour l'exploration d'une collection d'images par contenu et détection d'objets.

## ✨ Fonctionnalités

- **Détection d'objets** : YOLOv8n pour détecter 80 classes d'objets (personnes, véhicules, animaux, etc.)
- **Extraction de descripteurs** : Histogrammes RGB/HSV, couleurs dominantes, Tamura, Gabor, moments de Hu, HOG
- **Recherche par similarité** : Recherche d'images similaires basée sur le contenu visuel
- **Transformations d'images** : Crop, resize, rotation, flip, ajustement luminosité/contraste
- **Interface Web** : Frontend Angular avec upload, galerie, recherche et visualisation

## 📋 Prérequis

- Python 3.10+ et pip
- Node.js 18+ et npm
- MongoDB (local ou Atlas) :
  - **Option 1** : MongoDB local ([Télécharger](https://www.mongodb.com/try/download/community))
  - **Option 2** : MongoDB Atlas (gratuit en ligne, pas besoin d'installation locale)

## 🚀 Démarrage Rapide

**Voir [QUICK_START.md](QUICK_START.md) pour un guide de démarrage en 5 minutes**

**Ou [SETUP_GUIDE.md](SETUP_GUIDE.md) pour un guide détaillé complet**

## ⚙️ Installation

### Backend (Flask)

1. **Créer l'environnement virtuel :**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou source .venv/bin/activate  # Linux/Mac
```

2. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

3. **Configurer MongoDB :**
   
   **Option A - MongoDB Local (Recommandé) :**
   - Installez MongoDB localement : [Télécharger MongoDB Community](https://www.mongodb.com/try/download/community)
   - Démarrez le service MongoDB sur votre machine
   - Créez le fichier `.env` dans `backend/` :
   ```env
   MONGO_URI=mongodb://localhost:27017/cbir
   MONGO_DB=cbir
   UPLOAD_FOLDER=uploads
   ```
   
   **Option B - MongoDB Atlas (Cloud) :**
   - Créez un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Créez un cluster FREE
   - Configurez Network Access et Database Access
   - Créez le fichier `.env` dans `backend/` :
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/cbir?retryWrites=true&w=majority
   MONGO_DB=cbir
   UPLOAD_FOLDER=uploads
   ```
   
   📖 **Voir [backend/CREATE_ENV_FILE.md](backend/CREATE_ENV_FILE.md) pour un guide détaillé**

6. **Démarrer le serveur :**
```bash
python app.py
```

Le backend sera accessible sur `http://localhost:5000`

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

### Frontend (Angular)

1. **Installer les dépendances :**
```bash
cd frontend
npm install
```

2. **Démarrer le serveur de développement :**
```bash
npm start
# ou
ng serve
```

Le frontend sera accessible sur `http://localhost:4200`
Composants :
- `image-upload` : formulaire pour uploader une ou plusieurs images
- `image-gallery` : liste des images, boutons download/delete/transform
- `image-search` : sélection d’une image requête et affichage des résultats
- `descriptor-view` : affichage des descripteurs pour une image/objet

Services :
- `api.service.ts` : appels HTTP vers l’API Flask (upload/download/delete/search/transform)

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** : Guide complet de configuration étape par étape
- **[QUICK_START.md](QUICK_START.md)** : Démarrage rapide en 5 minutes
- **[backend/ROUTES_DOCUMENTATION.md](backend/ROUTES_DOCUMENTATION.md)** : Documentation complète de l'API REST

## 🔧 Implémentation

### YOLO & Descripteurs
- ✅ **YOLO personnalisé (best.pt)** : Détection d'objets implémentée dans `utils/yolo_detection.py`
  - Le modèle personnalisé se trouve dans `backend/fine_tuned_model/best.pt`
  - Si le fichier n'existe pas, une erreur sera levée avec des instructions
- ✅ **Descripteurs visuels** : Tous implémentés dans `utils/descriptor_extraction.py` :
  - Histogrammes RGB et HSV
  - Couleurs dominantes (K-means)
  - Descripteurs de Tamura (rugosité, contraste, orientation)
  - Filtres de Gabor
  - Moments de Hu
  - HOG (Histogram of Oriented Gradients)
- ✅ **MongoDB** : Stockage des métadonnées (nom, chemin, objets détectés, descripteurs, date)

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

## 🔐 Sécurité

- `flask-cors` est activé pour accepter les requêtes Angular
- Le fichier `.env` est dans `.gitignore` - **ne jamais le commiter**
- MongoDB Atlas : Utilisez des mots de passe forts et limitez l'accès IP en production

## 📝 Notes

- Les images uploadées sont stockées dans `backend/uploads/` (ignoré par git)
- Le modèle YOLO personnalisé (`best.pt`) doit être présent dans `backend/fine_tuned_model/`
- Si vous n'avez pas de modèle personnalisé, vous pouvez utiliser le modèle pré-entraîné en modifiant `backend/utils/yolo_detection.py`

## 🐛 Dépannage

Voir la section "Dépannage" dans [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📄 Licence

Projet académique - Module "Multimedia Mining and Indexing"

