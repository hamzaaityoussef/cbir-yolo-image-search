# Architecture et Utilisation du Système CBIR YOLO

## 🎯 Utilisation Spécifique du Système

### Objectif Principal
Développer un système de **recherche d'images par contenu (CBIR - Content-Based Image Retrieval)** qui combine :
- **Détection d'objets** avec YOLOv8n
- **Extraction de descripteurs visuels** pour caractériser le contenu
- **Recherche par similarité** basée sur ces descripteurs

### Cas d'Usage
1. **Recherche d'objets similaires** : Trouver des images contenant des objets visuellement similaires
2. **Exploration de collection** : Parcourir une collection d'images par contenu
3. **Indexation automatique** : Caractériser automatiquement les images uploadées

---

## 📁 Partie Multimédia - Où se trouve-t-elle ?

### 1. **Stockage des Images** (Multimédia - Fichiers)

**Localisation :**
```
backend/uploads/
```

**Fonction :**
- Stocke les fichiers images uploadés physiquement sur le disque
- Format : JPG, PNG, GIF, BMP, WEBP
- Géré par : `backend/routes/upload.py`

**Important :** Ce dossier est dans `.gitignore` - les images ne sont pas versionnées dans Git.

### 2. **Traitement Multimédia** (Extraction de Caractéristiques)

**Fichiers principaux :**

#### a) Détection d'Objets
- **Fichier :** `backend/utils/yolo_detection.py`
- **Fonction :** `detect_objects(image_path)`
- **Technologie :** YOLOv8n (modèle de deep learning)
- **Résultat :** Liste d'objets avec classes, confiance, bounding boxes

#### b) Extraction de Descripteurs Visuels
- **Fichier :** `backend/utils/descriptor_extraction.py`
- **Fonctions principales :**
  - `extract_descriptors(image_path)` → Descripteurs de l'image complète
  - `extract_object_descriptors(image, bbox)` → Descripteurs d'un objet spécifique

**Descripteurs extraits :**
1. **Histogrammes de couleurs** (RGB, HSV)
2. **Couleurs dominantes** (K-means clustering)
3. **Descripteurs de Tamura** (rugosité, contraste, orientation)
4. **Filtres de Gabor** (texture multi-échelle)
5. **Moments de Hu** (invariants géométriques)
6. **HOG** (Histogram of Oriented Gradients)

### 3. **Métadonnées Multimédia** (Base de Données)

**Localisation :** MongoDB Atlas (en ligne)

**Structure des données :**
```json
{
  "_id": "ObjectId",
  "filename": "image.jpg",
  "path": "backend/uploads/image_abc123.jpg",
  "uploaded_at": "2024-01-01T12:00:00",
  "detected_objects": [
    {
      "class": "dog",
      "confidence": 0.841,
      "bbox": [100, 150, 300, 400],
      "descriptors": {
        "color_histogram_rgb": {...},
        "color_histogram_hsv": {...},
        "dominant_colors": [...],
        "tamura": {...},
        "gabor": [...],
        "hu_moments": [...],
        "hog": [...]
      }
    }
  ],
  "descriptors": {
    // Descripteurs de l'image complète
  }
}
```

**Géré par :** `backend/models/image_model.py`

---

## 🔍 Comment Voir les Informations dans MongoDB

### Méthode 1 : Script Python (Recommandé)

**Fichier créé :** `backend/view_mongodb_data.py`

**Utilisation :**

```bash
cd backend
.venv\Scripts\activate  # Windows
python view_mongodb_data.py
```

**Commandes disponibles :**

1. **Lister toutes les images :**
   ```bash
   python view_mongodb_data.py list
   ```

2. **Afficher les statistiques :**
   ```bash
   python view_mongodb_data.py stats
   ```

3. **Voir les détails d'une image :**
   ```bash
   python view_mongodb_data.py show <image_id>
   ```

4. **Exporter en JSON :**
   ```bash
   python view_mongodb_data.py export mongodb_data.json
   ```

### Méthode 2 : MongoDB Compass (Interface Graphique)

1. **Télécharger MongoDB Compass :**
   - Allez sur https://www.mongodb.com/try/download/compass
   - Téléchargez et installez MongoDB Compass

2. **Se connecter :**
   - Ouvrez MongoDB Compass
   - Collez votre URI de connexion MongoDB Atlas :
     ```
     mongodb+srv://username:password@cluster.xxxxx.mongodb.net/cbir
     ```
   - Cliquez sur "Connect"

3. **Explorer les données :**
   - Sélectionnez la base de données `cbir`
   - Sélectionnez la collection `images`
   - Vous verrez toutes les images avec leurs métadonnées

### Méthode 3 : MongoDB Shell (mongosh)

```bash
# Se connecter à MongoDB Atlas
mongosh "mongodb+srv://username:password@cluster.xxxxx.mongodb.net/cbir"

# Lister toutes les images
db.images.find().pretty()

# Compter les images
db.images.countDocuments()

# Trouver une image par ID
db.images.findOne({_id: ObjectId("...")})

# Trouver les images avec des objets spécifiques
db.images.find({"detected_objects.class": "dog"})

# Voir les statistiques
db.images.aggregate([
  {
    $project: {
      filename: 1,
      objects_count: { $size: "$detected_objects" }
    }
  }
])
```

### Méthode 4 : Via l'API REST

**Lister toutes les images :**
```bash
curl http://localhost:5000/images
```

**Voir une image spécifique :**
```bash
curl http://localhost:5000/images | jq '.images[0]'
```

---

## 📊 Structure des Données Multimédia

### Pipeline de Traitement

```
1. Upload Image
   ↓
2. Sauvegarde physique (backend/uploads/)
   ↓
3. Détection YOLO (backend/utils/yolo_detection.py)
   ↓
4. Pour chaque objet détecté :
   - Crop de l'objet (bounding box)
   - Extraction descripteurs (backend/utils/descriptor_extraction.py)
   ↓
5. Extraction descripteurs image complète
   ↓
6. Stockage MongoDB (métadonnées + descripteurs)
```

### Données Stockées

**Pour chaque image :**
- ✅ Fichier physique sur disque
- ✅ Métadonnées (nom, chemin, date)
- ✅ Objets détectés (classes, confiance, positions)
- ✅ Descripteurs de l'image complète
- ✅ Descripteurs de chaque objet individuel

**Pour chaque objet détecté :**
- ✅ Classe (dog, cat, person, etc.)
- ✅ Score de confiance
- ✅ Bounding box [x1, y1, x2, y2]
- ✅ **Descripteurs visuels complets** :
  - Histogrammes RGB/HSV
  - Couleurs dominantes
  - Tamura (rugosité, contraste, orientation)
  - Gabor (texture)
  - Moments de Hu (forme)
  - HOG (gradients)

---

## 🎨 Partie Multimédia - Résumé

| Composant | Localisation | Type | Description |
|-----------|-------------|------|-------------|
| **Fichiers images** | `backend/uploads/` | Fichiers | Images physiques stockées |
| **Détection objets** | `backend/utils/yolo_detection.py` | Code Python | YOLOv8n pour détecter objets |
| **Extraction descripteurs** | `backend/utils/descriptor_extraction.py` | Code Python | 6 types de descripteurs visuels |
| **Métadonnées** | MongoDB Atlas | Base de données | Toutes les informations structurées |
| **API REST** | `backend/routes/*.py` | Endpoints | Accès aux données via HTTP |
| **Interface Web** | `frontend/` | Angular | Visualisation et interaction |

---

## 🔬 Exemple de Données MongoDB

Voici à quoi ressemble une entrée complète dans MongoDB :

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "filename": "cat_dog_abc123.jpg",
  "path": "backend/uploads/cat_dog_abc123.jpg",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "detected_objects": [
    {
      "class": "dog",
      "confidence": 0.841,
      "bbox": [100, 150, 300, 400],
      "descriptors": {
        "color_histogram_rgb": {
          "r": [0.01, 0.02, ...],
          "g": [0.015, 0.025, ...],
          "b": [0.012, 0.022, ...]
        },
        "dominant_colors": [
          {"rgb": [245, 220, 180], "proportion": 0.35},
          {"rgb": [200, 150, 100], "proportion": 0.28}
        ],
        "tamura": {
          "roughness": 12.5,
          "contrast": 8.3,
          "directionality": 0.65
        },
        "gabor": [0.123, 0.456, ...],
        "hu_moments": [2.1, 1.5, 0.8, ...],
        "hog": [0.01, 0.02, 0.015, ...]
      }
    }
  ],
  "descriptors": {
    // Même structure pour l'image complète
  }
}
```

---

## 📝 Notes Importantes

1. **Fichiers images** : Stockés localement dans `backend/uploads/` (non versionnés)
2. **Descripteurs** : Calculés une seule fois à l'upload et stockés en base
3. **Recherche** : Utilise les descripteurs stockés (pas de recalcul)
4. **Performance** : Les descripteurs sont pré-calculés pour accélérer la recherche

---

## 🚀 Prochaines Étapes

Pour explorer vos données :
1. Utilisez `python backend/view_mongodb_data.py list` pour voir toutes les images
2. Utilisez MongoDB Compass pour une interface graphique
3. Utilisez l'API REST `/images` pour accéder via HTTP

