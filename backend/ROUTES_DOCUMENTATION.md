# Documentation des Routes API

Ce document explique le fonctionnement de toutes les routes de l'API Flask.

## Vue d'ensemble

L'API expose 6 endpoints principaux pour gérer les images et effectuer des recherches par contenu :

1. **POST /upload** - Uploader des images
2. **GET /images** - Lister toutes les images
3. **GET /download/<image_id>** - Télécharger une image
4. **DELETE /delete/<image_id>** - Supprimer une image
5. **POST /search** - Rechercher des images similaires
6. **POST /transform/<image_id>** - Appliquer des transformations

---

## 1. POST /upload

### Description
Upload une ou plusieurs images, détecte automatiquement les objets avec YOLOv8n, extrait tous les descripteurs visuels et stocke tout dans MongoDB.

### Fonctionnement détaillé
1. **Réception** : Reçoit les fichiers via `multipart/form-data` (champ `images`)
2. **Validation** : Vérifie les extensions autorisées (png, jpg, jpeg, gif, bmp, webp)
3. **Sauvegarde** : Enregistre les fichiers dans `uploads/` avec un nom unique
4. **Détection YOLO** : Détecte les objets dans chaque image (80 classes COCO)
5. **Extraction descripteurs** : Calcule tous les descripteurs visuels :
   - Histogrammes RGB et HSV
   - Couleurs dominantes (K-means)
   - Descripteurs de Tamura (rugosité, contraste, orientation)
   - Filtres de Gabor
   - Moments de Hu
   - HOG (Histogram of Oriented Gradients)
6. **Stockage MongoDB** : Sauvegarde les métadonnées avec les objets détectés et descripteurs

### Requête
```bash
curl -X POST http://localhost:5000/upload \
  -F "images=@image1.jpg" \
  -F "images=@image2.png"
```

### Réponse
```json
{
  "uploaded": [
    {
      "id": "507f1f77bcf86cd799439011",
      "filename": "image1_abc12345.jpg",
      "objects_detected": 3
    }
  ],
  "count": 1,
  "errors": []  // Si des erreurs se produisent
}
```

### Codes de statut
- **201** : Upload réussi
- **400** : Erreur de validation ou aucun fichier

---

## 2. GET /images

### Description
Liste toutes les images stockées avec leurs métadonnées (utile pour la galerie).

### Fonctionnement
1. Récupère toutes les images de MongoDB
2. Filtre optionnel par classe d'objet
3. Pagination (limit/offset)
4. Retourne les métadonnées sans les descripteurs complets (économie de bande passante)

### Paramètres de requête (optionnels)
- `object_class` : Filtrer par classe d'objet (ex: "person", "car")
- `limit` : Nombre max de résultats (défaut: 100)
- `offset` : Nombre de résultats à sauter (pagination)

### Requête
```bash
curl "http://localhost:5000/images?object_class=person&limit=10&offset=0"
```

### Réponse
```json
{
  "images": [
    {
      "id": "507f1f77bcf86cd799439011",
      "filename": "image1.jpg",
      "uploaded_at": "2024-01-01T12:00:00",
      "objects_detected": [
        {
          "class": "person",
          "confidence": 0.95,
          "bbox": [100, 150, 200, 300]
        }
      ],
      "objects_count": 1,
      "object_classes": ["person"]
    }
  ],
  "count": 1,
  "total": 50,
  "offset": 0,
  "limit": 10
}
```

---

## 3. GET /download/<image_id>

### Description
Télécharge une image par son ID MongoDB. L'image est servie directement au navigateur.

### Fonctionnement
1. Récupère l'image depuis MongoDB
2. Vérifie l'existence du fichier sur le disque
3. Détermine le type MIME (image/jpeg, image/png, etc.)
4. Envoie le fichier au client

### Requête
```bash
curl http://localhost:5000/download/507f1f77bcf86cd799439011 \
  --output image.jpg
```

### Réponse
- **200** : Fichier image (Content-Type: image/jpeg, etc.)
- **404** : Image non trouvée
- **500** : Erreur serveur

---

## 4. DELETE /delete/<image_id>

### Description
Supprime une image : à la fois le fichier physique et les métadonnées MongoDB.

### Fonctionnement
1. Récupère l'image depuis MongoDB
2. Supprime le fichier du disque (si existe)
3. Supprime les métadonnées de MongoDB

### Requête
```bash
curl -X DELETE http://localhost:5000/delete/507f1f77bcf86cd799439011
```

### Réponse
```json
{
  "deleted": "507f1f77bcf86cd799439011",
  "filename": "image1.jpg",
  "message": "Image supprimée avec succès"
}
```

### Codes de statut
- **200** : Suppression réussie
- **404** : Image non trouvée

---

## 5. POST /search

### Description
Recherche des images similaires par contenu visuel. Supporte 3 modes :
- Upload d'une nouvelle image
- Utilisation d'une image existante
- Recherche basée sur un objet spécifique

### Fonctionnement détaillé

#### Mode 1 : Upload d'une nouvelle image
1. Reçoit une nouvelle image
2. Détecte les objets et extrait les descripteurs
3. Compare avec toutes les images en base
4. Retourne les plus similaires

#### Mode 2 : Image existante
1. Utilise les descripteurs déjà stockés d'une image
2. Compare avec les autres images
3. Retourne les résultats

#### Mode 3 : Objet spécifique
1. Crop l'objet sélectionné depuis l'image
2. Extrait les descripteurs de l'objet uniquement
3. Compare avec les autres images/objets

### Algorithme de similarité
Utilise une combinaison pondérée de distances :
- Histogrammes : Distance Chi-square
- Couleurs dominantes : Distance euclidienne
- Tamura : Distance euclidienne normalisée
- Gabor : Similarité cosinus
- Moments de Hu : Distance euclidienne
- HOG : Similarité cosinus

### Requête (Mode 1 - Upload)
```bash
curl -X POST http://localhost:5000/search \
  -F "type=upload" \
  -F "image=@query.jpg" \
  -F "top_k=10"
```

### Requête (Mode 2 - Image existante)
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "type": "existing",
    "image_id": "507f1f77bcf86cd799439011",
    "top_k": 10
  }'
```

### Requête (Mode 3 - Objet spécifique)
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "type": "existing",
    "image_id": "507f1f77bcf86cd799439011",
    "object_id": 0,
    "top_k": 10
  }'
```

### Réponse
```json
{
  "query_info": {
    "type": "existing",
    "image_id": "507f1f77bcf86cd799439011",
    "objects_detected": [...]
  },
  "results": [
    {
      "image_id": "507f1f77bcf86cd799439012",
      "filename": "similar_image.jpg",
      "similarity_score": 0.1234,
      "detected_objects": [...],
      "uploaded_at": "2024-01-01T12:00:00"
    }
  ],
  "count": 10
}
```

### Codes de statut
- **200** : Recherche réussie
- **400** : Paramètres invalides
- **404** : Image requête non trouvée
- **500** : Erreur serveur

---

## 6. POST /transform/<image_id>

### Description
Applique des transformations à une image existante et crée une nouvelle image transformée.

### Transformations supportées

#### 1. Crop
Découpe une région de l'image.
```json
{
  "transform": "crop",
  "params": {
    "x": 100,
    "y": 100,
    "width": 200,
    "height": 200
  }
}
```

#### 2. Resize
Redimensionne l'image.
```json
{
  "transform": "resize",
  "params": {
    "width": 800,
    "height": 600
  }
}
// ou avec scale
{
  "transform": "resize",
  "params": {
    "scale": 0.5
  }
}
```

#### 3. Rotate
Fait tourner l'image.
```json
{
  "transform": "rotate",
  "params": {
    "angle": 90
  }
}
```

#### 4. Flip
Retourne l'image.
```json
{
  "transform": "flip",
  "params": {
    "direction": "horizontal"  // ou "vertical", "both"
  }
}
```

#### 5. Brightness/Contrast
Ajuste la luminosité et le contraste.
```json
{
  "transform": "brightness",
  "params": {
    "brightness": 1.2,  // >1 = plus lumineux
    "contrast": 1.5     // >1 = plus de contraste
  }
}
```

### Fonctionnement
1. Récupère l'image source depuis MongoDB
2. Charge l'image depuis le disque
3. Applique la transformation demandée
4. Sauvegarde la nouvelle image transformée
5. Détecte les objets et extrait les descripteurs de la nouvelle image
6. Stocke la nouvelle image dans MongoDB

### Requête
```bash
curl -X POST http://localhost:5000/transform/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{
    "transform": "crop",
    "params": {
      "x": 100,
      "y": 100,
      "width": 200,
      "height": 200
    }
  }'
```

### Réponse
```json
{
  "transformed_image_id": "507f1f77bcf86cd799439013",
  "original_image_id": "507f1f77bcf86cd799439011",
  "filename": "image1_transformed_xyz789.jpg",
  "transform": "crop",
  "params": {...},
  "objects_detected": 2
}
```

### Codes de statut
- **201** : Transformation réussie
- **400** : Paramètres invalides
- **404** : Image source non trouvée
- **500** : Erreur serveur

---

## Endpoint supplémentaire

### GET /health

Vérifie que l'API est opérationnelle.

```bash
curl http://localhost:5000/health
```

Réponse :
```json
{
  "status": "ok"
}
```

---

## Gestion des erreurs

Toutes les routes retournent des erreurs au format JSON :

```json
{
  "error": "Message d'erreur descriptif"
}
```

Codes de statut HTTP standards :
- **200** : Succès
- **201** : Créé (upload, transform)
- **400** : Requête invalide
- **404** : Ressource non trouvée
- **500** : Erreur serveur

---

## Notes techniques

1. **CORS** : Activé pour permettre les requêtes depuis le frontend Angular
2. **Validation** : Les extensions de fichiers sont validées avant l'upload
3. **Noms uniques** : Les fichiers uploadés reçoivent un suffixe UUID pour éviter les collisions
4. **Performance** : Les descripteurs sont calculés une seule fois à l'upload et stockés en base
5. **Recherche** : La similarité combine plusieurs métriques pour une meilleure précision

