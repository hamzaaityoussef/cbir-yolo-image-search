# Configuration MongoDB Local et Modèle YOLO Personnalisé

## ✅ Modifications effectuées

### 1. Modèle YOLO personnalisé (best.pt)

Le fichier `backend/utils/yolo_detection.py` a été mis à jour pour utiliser votre modèle personnalisé `best.pt` au lieu du modèle pré-entraîné `yolov8n.pt`.

**Emplacement du modèle :** `backend/fine_tuned_model/best.pt`

Le code vérifie automatiquement si le fichier existe et affiche un message d'erreur clair s'il est absent.

### 2. Configuration MongoDB Local

Le fichier `backend/config.py` utilise déjà MongoDB local par défaut si aucune variable d'environnement n'est définie :
- URI par défaut : `mongodb://localhost:27017/cbir`

## 📝 Étapes pour finaliser la configuration

### Étape 1 : Créer le fichier .env

Créez un fichier `.env` dans le dossier `backend/` avec ce contenu :

```env
MONGO_URI=mongodb://localhost:27017/cbir
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
```

**Méthode PowerShell :**
```powershell
cd backend
@"
MONGO_URI=mongodb://localhost:27017/cbir
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
"@ | Out-File -FilePath .env -Encoding utf8
```

**Méthode manuelle :**
1. Créez un nouveau fichier nommé `.env` dans `backend/`
2. Copiez-collez le contenu ci-dessus

### Étape 2 : Installer et démarrer MongoDB Local

1. **Télécharger MongoDB Community :**
   - Windows : [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
   - Sélectionnez votre version Windows et téléchargez l'installateur MSI

2. **Installer MongoDB :**
   - Exécutez l'installateur
   - Choisissez "Complete" installation
   - Cochez "Install MongoDB as a Service"
   - MongoDB démarrera automatiquement comme service Windows

3. **Vérifier que MongoDB fonctionne :**
   ```powershell
   # Vérifier le service
   Get-Service MongoDB
   
   # Ou tester la connexion
   mongosh
   ```

### Étape 3 : Vérifier le modèle YOLO

Assurez-vous que le fichier `backend/fine_tuned_model/best.pt` existe. Si vous avez un modèle personnalisé, placez-le à cet emplacement.

### Étape 4 : Tester la configuration

1. **Démarrer le backend :**
   ```powershell
   cd backend
   .venv\Scripts\activate
   python app.py
   ```

2. **Vérifier les logs :**
   - Le serveur devrait démarrer sans erreur
   - Si vous voyez une erreur concernant le modèle, vérifiez que `best.pt` existe
   - Si vous voyez une erreur MongoDB, vérifiez que le service MongoDB est démarré

## 🔧 Dépannage

### Erreur : "Modèle personnalisé non trouvé"
- Vérifiez que `backend/fine_tuned_model/best.pt` existe
- Vérifiez les permissions du fichier

### Erreur : "Connection refused" ou erreur MongoDB
- Vérifiez que MongoDB est démarré : `Get-Service MongoDB`
- Si le service n'est pas démarré : `Start-Service MongoDB`
- Vérifiez que le port 27017 n'est pas utilisé par un autre processus

### Erreur : "Module not found" ou erreur Python
- Activez l'environnement virtuel : `.venv\Scripts\activate`
- Réinstallez les dépendances : `pip install -r requirements.txt`

## 📚 Documentation supplémentaire

- **Configuration .env détaillée :** [CREATE_ENV_FILE.md](CREATE_ENV_FILE.md)
- **Guide de démarrage rapide :** [../QUICK_START.md](../QUICK_START.md)
- **Guide complet :** [../SETUP_GUIDE.md](../SETUP_GUIDE.md)

