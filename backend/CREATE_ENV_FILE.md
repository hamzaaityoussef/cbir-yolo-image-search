# Comment créer le fichier .env

## Configuration MongoDB

Ce projet supporte deux options pour MongoDB :
1. **MongoDB local** (recommandé pour le développement)
2. **MongoDB Atlas** (cloud, nécessite un compte)

## Option 1 : MongoDB Local (Recommandé)

### Prérequis
- Installer MongoDB localement : [Télécharger MongoDB](https://www.mongodb.com/try/download/community)
- Démarrer le service MongoDB sur votre machine

### Créer le fichier .env

**Méthode 1 : PowerShell (Windows)**
```powershell
cd backend
@"
MONGO_URI=mongodb://localhost:27017/cbir
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
"@ | Out-File -FilePath .env -Encoding utf8
```

**Méthode 2 : Éditeur de texte (Recommandé)**

1. Créez un nouveau fichier nommé `.env` dans le dossier `backend/`
2. Copiez-collez ce contenu :

```env
MONGO_URI=mongodb://localhost:27017/cbir
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
```

**Méthode 3 : Commande echo (Windows CMD)**
```cmd
cd backend
echo MONGO_URI=mongodb://localhost:27017/cbir > .env
echo MONGO_DB=cbir >> .env
echo UPLOAD_FOLDER=uploads >> .env
```

## Option 2 : MongoDB Atlas (Cloud)

### Prérequis
- Créer un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Créer un cluster FREE (M0)
- Configurer Network Access et Database Access

### Créer le fichier .env

**Méthode 1 : PowerShell (Windows)**
```powershell
cd backend
@"
MONGO_URI=mongodb+srv://VOTRE_USERNAME:VOTRE_PASSWORD@cluster0.xxxxx.mongodb.net/cbir?retryWrites=true&w=majority
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
"@ | Out-File -FilePath .env -Encoding utf8
```

Puis **éditez le fichier** `.env` avec un éditeur de texte pour remplacer :
- `VOTRE_USERNAME` → votre nom d'utilisateur MongoDB Atlas
- `VOTRE_PASSWORD` → votre mot de passe MongoDB Atlas
- `cluster0.xxxxx` → votre cluster MongoDB Atlas

**Méthode 2 : Éditeur de texte (Recommandé)**

1. Créez un nouveau fichier nommé `.env` dans le dossier `backend/`
2. Copiez-collez ce contenu :

```env
MONGO_URI=mongodb+srv://VOTRE_USERNAME:VOTRE_PASSWORD@cluster0.xxxxx.mongodb.net/cbir?retryWrites=true&w=majority
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
```

3. Remplacez `VOTRE_USERNAME`, `VOTRE_PASSWORD` et `cluster0.xxxxx` par vos identifiants MongoDB Atlas

## Vérification

Après avoir créé le fichier `.env`, vérifiez qu'il contient bien votre configuration :

```bash
# Windows PowerShell
Get-Content backend\.env

# Windows CMD
type backend\.env
```

## Exemples de fichier .env

### Pour MongoDB Local
```env
MONGO_URI=mongodb://localhost:27017/cbir
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
```

### Pour MongoDB Atlas
```env
MONGO_URI=mongodb+srv://cbir_user:MyPassword123@cluster0.xxxxx.mongodb.net/cbir?retryWrites=true&w=majority
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
```

## Notes importantes

- ⚠️ Si votre mot de passe contient des caractères spéciaux (`@`, `#`, `%`, etc.), vous devez les encoder en URL :
  - `@` → `%40`
  - `#` → `%23`
  - `%` → `%25`
  - `&` → `%26`
  - Espace → `%20`

- Le fichier `.env` est déjà dans `.gitignore`, il ne sera pas commité dans Git (c'est normal et sécurisé)

- Après avoir créé/modifié le fichier `.env`, **redémarrez votre serveur Flask** pour que les changements soient pris en compte

