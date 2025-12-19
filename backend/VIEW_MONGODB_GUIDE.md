# Guide : Visualiser les Données MongoDB

## 🎯 Utilisation du Script Python

### Prérequis
Assurez-vous que :
1. Le fichier `.env` est configuré avec votre URI MongoDB Atlas
2. L'environnement virtuel est activé
3. Les dépendances sont installées

### Utilisation Basique

```bash
cd backend
.venv\Scripts\activate  # Windows
python view_mongodb_data.py
```

Le script vous proposera un menu interactif.

### Commandes Disponibles

#### 1. Lister toutes les images
```bash
python view_mongodb_data.py list
```

Affiche :
- Nom de chaque image
- Nombre d'objets détectés
- Classes d'objets
- Présence des descripteurs

#### 2. Afficher les statistiques
```bash
python view_mongodb_data.py stats
```

Affiche :
- Nombre total d'images
- Nombre total d'objets détectés
- Répartition par classe d'objet
- Nombre d'images/objets avec descripteurs

#### 3. Voir les détails d'une image
```bash
python view_mongodb_data.py show <image_id>
```

Exemple :
```bash
python view_mongodb_data.py show 507f1f77bcf86cd799439011
```

Affiche toutes les métadonnées et descripteurs complets.

#### 4. Exporter en JSON
```bash
python view_mongodb_data.py export mongodb_data.json
```

Exporte toutes les données dans un fichier JSON pour analyse.

---

## 🔍 Méthode Alternative : MongoDB Compass

### Installation
1. Téléchargez MongoDB Compass : https://www.mongodb.com/try/download/compass
2. Installez-le

### Connexion
1. Ouvrez MongoDB Compass
2. Collez votre URI de connexion :
   ```
   mongodb+srv://username:password@cluster.xxxxx.mongodb.net/cbir
   ```
3. Cliquez sur "Connect"

### Navigation
1. Base de données : `cbir`
2. Collection : `images`
3. Vous verrez toutes les images avec leurs données

### Requêtes Utiles dans Compass

**Trouver les images avec des chiens :**
```json
{"detected_objects.class": "dog"}
```

**Trouver les images avec plus de 2 objets :**
```json
{"$expr": {"$gt": [{"$size": "$detected_objects"}, 2]}}
```

**Trouver les images avec descripteurs complets :**
```json
{"descriptors.color_histogram_rgb": {"$exists": true}}
```

---

## 📊 Structure des Données dans MongoDB

### Collection : `images`

Chaque document contient :

```json
{
  "_id": "ObjectId(...)",
  "filename": "image.jpg",
  "path": "backend/uploads/image_abc123.jpg",
  "uploaded_at": "2024-01-15T10:30:00Z",
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
    // Descripteurs de l'image complète (même structure)
  }
}
```

---

## 🎨 Partie Multimédia - Localisation

### 1. Fichiers Images (Multimédia Physique)
- **Localisation :** `backend/uploads/`
- **Type :** Fichiers binaires (JPG, PNG, GIF, BMP, WEBP)
- **Gestion :** Flask sauvegarde les fichiers uploadés

### 2. Traitement Multimédia (Code)
- **Détection :** `backend/utils/yolo_detection.py`
- **Extraction descripteurs :** `backend/utils/descriptor_extraction.py`
- **Pipeline :** `backend/routes/upload.py` (lignes 91-138)

### 3. Métadonnées Multimédia (Base de Données)
- **Base :** MongoDB Atlas (`cbir`)
- **Collection :** `images`
- **Gestion :** `backend/models/image_model.py`

---

## 🔬 Exemple de Sortie du Script

```
================================================================================
📚 LISTE DE TOUTES LES IMAGES DANS MONGODB
================================================================================

✅ Total: 3 image(s) trouvée(s)

================================================================================
📷 Image: cat_dog_abc123.jpg
   ID: 507f1f77bcf86cd799439011
   Chemin: backend/uploads/cat_dog_abc123.jpg
   Date d'upload: 2024-01-15 10:30:00

   🎯 Objets détectés: 3

   Objet #1:
      - Classe: dog
      - Confiance: 84.1%
      - Bounding Box: [100, 150, 300, 400]
      - ✅ Descripteurs extraits:
         • Histogrammes RGB/HSV: Oui
         • Couleurs dominantes: Oui
         • Tamura: Oui
         • Gabor: Oui
         • Moments de Hu: Oui
         • HOG: Oui

   Objet #2:
      - Classe: cat
      - Confiance: 79.9%
      - Bounding Box: [350, 200, 500, 450]
      - ✅ Descripteurs extraits:
         ...
```

---

## 💡 Astuces

1. **Voir seulement les images récentes :**
   Utilisez MongoDB Compass avec un filtre de date

2. **Exporter pour analyse :**
   ```bash
   python view_mongodb_data.py export data.json
   ```
   Puis ouvrez `data.json` dans un éditeur de texte

3. **Vérifier qu'un objet a des descripteurs :**
   Dans MongoDB Compass, filtrez :
   ```json
   {"detected_objects.descriptors": {"$exists": true}}
   ```

4. **Compter les objets par classe :**
   Utilisez `python view_mongodb_data.py stats`


