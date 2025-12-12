# Comment créer le fichier .env

## Étapes rapides

1. **Ouvrez un terminal** dans le dossier `backend/`

2. **Créez le fichier `.env`** avec l'une de ces méthodes :

### Méthode 1 : PowerShell (Windows)
```powershell
cd backend
@"
MONGO_URI=mongodb+srv://VOTRE_USERNAME:VOTRE_PASSWORD@cbir-yolo-image-search.uundhsd.mongodb.net/cbir?retryWrites=true&w=majority
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
"@ | Out-File -FilePath .env -Encoding utf8
```

Puis **éditez le fichier** `.env` avec un éditeur de texte pour remplacer :
- `VOTRE_USERNAME` → votre nom d'utilisateur MongoDB Atlas
- `VOTRE_PASSWORD` → votre mot de passe MongoDB Atlas

### Méthode 2 : Éditeur de texte (Recommandé)

1. Créez un nouveau fichier nommé `.env` dans le dossier `backend/`
2. Copiez-collez ce contenu :

```env
MONGO_URI=mongodb+srv://VOTRE_USERNAME:VOTRE_PASSWORD@cbir-yolo-image-search.uundhsd.mongodb.net/cbir?retryWrites=true&w=majority
MONGO_DB=cbir
UPLOAD_FOLDER=uploads
```

3. Remplacez `VOTRE_USERNAME` et `VOTRE_PASSWORD` par vos identifiants MongoDB Atlas

### Méthode 3 : Commande echo (Windows CMD)
```cmd
cd backend
echo MONGO_URI=mongodb+srv://VOTRE_USERNAME:VOTRE_PASSWORD@cbir-yolo-image-search.uundhsd.mongodb.net/cbir?retryWrites=true^&w=majority > .env
echo MONGO_DB=cbir >> .env
echo UPLOAD_FOLDER=uploads >> .env
```

⚠️ **Important** : Remplacez `VOTRE_USERNAME` et `VOTRE_PASSWORD` dans le fichier créé !

## Vérification

Après avoir créé le fichier `.env`, vérifiez qu'il contient bien votre URI MongoDB Atlas :

```bash
# Windows PowerShell
Get-Content backend\.env

# Windows CMD
type backend\.env
```

## Exemple de fichier .env correct

```env
MONGO_URI=mongodb+srv://cbir_user:MyPassword123@cbir-yolo-image-search.uundhsd.mongodb.net/cbir?retryWrites=true&w=majority
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

