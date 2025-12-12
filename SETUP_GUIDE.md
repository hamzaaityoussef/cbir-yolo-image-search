# Guide de Configuration et Démarrage

Ce guide vous accompagne étape par étape pour configurer et démarrer le projet CBIR avec YOLO.

## 📋 Table des matières

1. [Configuration MongoDB Atlas](#1-configuration-mongodb-atlas)
2. [Configuration Backend](#2-configuration-backend)
3. [Configuration Frontend](#3-configuration-frontend)
4. [Démarrage du projet](#4-démarrage-du-projet)
5. [Test de l'API](#5-test-de-lapi)
6. [Dépannage](#6-dépannage)

---

## 1. Configuration MongoDB Atlas

### Étape 1.1 : Créer un compte MongoDB Atlas

1. Allez sur [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Cliquez sur **"Try Free"** ou **"Sign Up"**
3. Créez un compte (gratuit)

### Étape 1.2 : Créer un cluster

1. Une fois connecté, cliquez sur **"Build a Database"**
2. Choisissez le plan **FREE (M0)** - gratuit pour toujours
3. Sélectionnez un **Cloud Provider** et une **Region** (choisissez la plus proche de vous)
4. Cliquez sur **"Create"** (cela peut prendre 1-3 minutes)

### Étape 1.3 : Configurer l'accès réseau

1. Dans le menu de gauche, allez dans **"Network Access"**
2. Cliquez sur **"Add IP Address"**
3. Cliquez sur **"Allow Access from Anywhere"** (pour le développement)
   - Ou ajoutez votre IP spécifique pour plus de sécurité
4. Cliquez sur **"Confirm"**

### Étape 1.4 : Créer un utilisateur de base de données

1. Dans le menu de gauche, allez dans **"Database Access"**
2. Cliquez sur **"Add New Database User"**
3. Choisissez **"Password"** comme méthode d'authentification
4. Entrez un **Username** (ex: `cbir_user`)
5. Générez un **Password** (cliquez sur "Autogenerate Secure Password" ou créez-en un)
   - ⚠️ **IMPORTANT** : Sauvegardez ce mot de passe, vous en aurez besoin !
6. Donnez les permissions **"Read and write to any database"**
7. Cliquez sur **"Add User"**

### Étape 1.5 : Obtenir la chaîne de connexion

1. Dans le menu de gauche, allez dans **"Database"**
2. Cliquez sur **"Connect"** sur votre cluster
3. Choisissez **"Connect your application"**
4. Dans la section **"Select your driver and version"** :
   - **Driver** : Sélectionnez **"Python"** (déjà sélectionné par défaut)
   - **Version** : Sélectionnez **"3.12 or later"** (recommandé)
5. Dans la section **"Install your driver"** :
   - MongoDB vous donnera la commande à exécuter, par exemple :
     ```bash
     python -m pip install "pymongo[srv]==3.12"
     ```
   - ⚠️ **Note** : Si vous utilisez un environnement virtuel, activez-le d'abord avant d'installer
6. Dans la section **"Add your connection string into your application code"** :
   - Vous verrez une chaîne de connexion qui ressemble à :
     ```
     mongodb+srv://<db_username>:<db_password>@cbir-yolo-image-search.xxxxx.mongodb.net/?appName=CBIR-YOLO-IMAGE-SEARCH
     ```
7. **Copiez cette chaîne de connexion** (bouton copier à droite de la chaîne)
8. **Remplacez les placeholders** :
   - `<db_username>` → votre nom d'utilisateur créé à l'étape 1.4
   - `<db_password>` → votre mot de passe créé à l'étape 1.4
   - ⚠️ **Important** : Si votre mot de passe contient des caractères spéciaux, vous devrez les encoder en URL (ex: `@` devient `%40`, `#` devient `%23`)
9. **Ajoutez le nom de la base de données** avant le `?` :
   - Remplacez `...mongodb.net/?appName=...` par `...mongodb.net/cbir?retryWrites=true&w=majority`
   - Ou gardez `appName` si vous préférez : `...mongodb.net/cbir?retryWrites=true&w=majority&appName=CBIR-YOLO-IMAGE-SEARCH`

**Exemple final :**
Si votre chaîne originale est :
```
mongodb+srv://<db_username>:<db_password>@cbir-yolo-image-search.uundhsd.mongodb.net/?appName=CBIR-YOLO-IMAGE-SEARCH
```

Et vos identifiants sont :
- Username : `cbir_user`
- Password : `MyPassword123`

Votre chaîne finale sera :
```
mongodb+srv://cbir_user:MyPassword123@cbir-yolo-image-search.uundhsd.mongodb.net/cbir?retryWrites=true&w=majority
```

**Ou avec appName :**
```
mongodb+srv://cbir_user:MyPassword123@cbir-yolo-image-search.uundhsd.mongodb.net/cbir?retryWrites=true&w=majority&appName=CBIR-YOLO-IMAGE-SEARCH
```

---

## 2. Configuration Backend

### Étape 2.1 : Créer l'environnement virtuel Python

```bash
cd backend
python -m venv .venv
```

**Windows :**
```bash
.venv\Scripts\activate
```

**Linux/Mac :**
```bash
source .venv/bin/activate
```

### Étape 2.2 : Installer les dépendances

```bash
pip install -r requirements.txt
```

⚠️ **Note** : L'installation peut prendre plusieurs minutes car elle inclut PyTorch et YOLO.

### Étape 2.3 : Configurer les variables d'environnement

1. Créez un fichier `.env` dans le dossier `backend/` :
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. Ouvrez le fichier `.env` et remplacez les valeurs :
   ```env
   MONGO_URI=mongodb+srv://votre_username:votre_password@cluster0.xxxxx.mongodb.net/cbir?retryWrites=true&w=majority
   MONGO_DB=cbir
   UPLOAD_FOLDER=uploads
   ```

3. ⚠️ **Sécurité** : Le fichier `.env` est déjà dans `.gitignore`, ne le commitez jamais !

### Étape 2.4 : Vérifier la configuration

Vérifiez que le dossier `uploads/` existe :
```bash
# Il devrait déjà exister, sinon il sera créé automatiquement
```

---

## 3. Configuration Frontend

### Étape 3.1 : Installer les dépendances Node.js

```bash
cd frontend
npm install
```

### Étape 3.2 : Configurer l'URL de l'API

Ouvrez `frontend/src/app/services/api.service.ts` et vérifiez que l'URL de base est correcte :

```typescript
private apiUrl = 'http://localhost:5000';  // Backend Flask
```

---

## 4. Démarrage du projet

### Étape 4.1 : Démarrer le Backend (Flask)

```bash
cd backend
# Activez l'environnement virtuel si ce n'est pas déjà fait
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac

python app.py
```

Vous devriez voir :
```
 * Running on http://0.0.0.0:5000
```

Le backend est maintenant accessible sur `http://localhost:5000`

### Étape 4.2 : Démarrer le Frontend (Angular)

Ouvrez un **nouveau terminal** :

```bash
cd frontend
npm start
# ou
ng serve
```

Le frontend sera accessible sur `http://localhost:4200`

---

## 5. Test de l'API

### Test 1 : Vérifier que l'API fonctionne

```bash
curl http://localhost:5000/health
```

Réponse attendue :
```json
{"status": "ok"}
```

### Test 2 : Tester la connexion MongoDB

Si vous voyez "ok" au test 1, MongoDB est probablement connecté. Pour vérifier, essayez de lister les images :

```bash
curl http://localhost:5000/images
```

Réponse attendue (si aucune image n'est encore uploadée) :
```json
{"images": [], "count": 0, "total": 0, "offset": 0, "limit": 100}
```

### Test 3 : Uploader une image de test

```bash
curl -X POST http://localhost:5000/upload \
  -F "images=@chemin/vers/votre/image.jpg"
```

---

## 6. Dépannage

### Problème : Erreur de connexion MongoDB

**Symptômes :**
```
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions :**
1. Vérifiez que votre IP est autorisée dans MongoDB Atlas (Network Access)
2. Vérifiez que le username/password dans `.env` sont corrects
3. Vérifiez que la chaîne de connexion est complète (avec `/cbir?retryWrites=true&w=majority`)

### Problème : Module non trouvé

**Symptômes :**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution :**
```bash
cd backend
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Problème : Port déjà utilisé

**Symptômes :**
```
Address already in use
```

**Solution :**
- Changez le port dans `backend/app.py` :
  ```python
  application.run(host="0.0.0.0", port=5001, debug=True)  # Port 5001 au lieu de 5000
  ```
- Ou arrêtez le processus qui utilise le port 5000

### Problème : YOLO ne télécharge pas le modèle

**Symptômes :**
```
Error downloading yolov8n.pt
```

**Solution :**
- Vérifiez votre connexion internet
- Le modèle sera téléchargé automatiquement au premier appel (peut prendre quelques minutes)

### Problème : CORS dans le navigateur

**Symptômes :**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution :**
- Vérifiez que `flask-cors` est installé : `pip install flask-cors`
- Vérifiez que CORS est activé dans `backend/app.py` : `CORS(app)`

---

## 📝 Checklist de démarrage

- [ ] Compte MongoDB Atlas créé
- [ ] Cluster MongoDB créé (FREE tier)
- [ ] IP autorisée dans Network Access
- [ ] Utilisateur de base de données créé
- [ ] Chaîne de connexion MongoDB copiée
- [ ] Fichier `.env` créé avec la bonne URI
- [ ] Environnement virtuel Python créé et activé
- [ ] Dépendances backend installées (`pip install -r requirements.txt`)
- [ ] Dépendances frontend installées (`npm install`)
- [ ] Backend démarré et accessible sur `http://localhost:5000`
- [ ] Frontend démarré et accessible sur `http://localhost:4200`
- [ ] Test `/health` retourne `{"status": "ok"}`

---

## 🚀 Prochaines étapes

Une fois tout configuré :

1. **Tester l'upload** : Uploadez quelques images via l'interface Angular
2. **Vérifier la détection** : Vérifiez que YOLO détecte bien les objets
3. **Tester la recherche** : Essayez de rechercher des images similaires
4. **Tester les transformations** : Appliquez des transformations aux images

---

## 📚 Ressources utiles

- [Documentation MongoDB Atlas](https://docs.atlas.mongodb.com/)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation Angular](https://angular.io/docs)
- [Documentation YOLOv8](https://docs.ultralytics.com/)

---

**Besoin d'aide ?** Vérifiez les logs du backend et du frontend pour plus de détails sur les erreurs.

