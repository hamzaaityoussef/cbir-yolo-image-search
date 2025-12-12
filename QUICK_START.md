# 🚀 Démarrage Rapide

## Étapes essentielles (5 minutes)

### 1. MongoDB Atlas (2 min)

1. Créez un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (gratuit)
2. Créez un cluster FREE (M0)
3. Dans **Network Access** → **Add IP Address** → **Allow Access from Anywhere**
4. Dans **Database Access** → Créez un utilisateur (username + password)
5. Dans **Database** → **Connect** → **Connect your application** → Copiez la chaîne de connexion

### 2. Configuration Backend (1 min)

```bash
cd backend

# Créer environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou source .venv/bin/activate  # Linux/Mac

# Installer dépendances
pip install -r requirements.txt

# Créer fichier .env
copy .env.example .env  # Windows
# ou cp .env.example .env  # Linux/Mac
```

**Éditez `.env`** et remplacez :
```env
MONGO_URI=mongodb+srv://VOTRE_USERNAME:VOTRE_PASSWORD@cluster0.xxxxx.mongodb.net/cbir?retryWrites=true&w=majority
```

### 3. Configuration Frontend (1 min)

```bash
cd frontend
npm install
```

### 4. Démarrer (1 min)

**Terminal 1 - Backend :**
```bash
cd backend
.venv\Scripts\activate  # Windows
python app.py
```

**Terminal 2 - Frontend :**
```bash
cd frontend
npm start
```

### 5. Tester

- Backend : http://localhost:5000/health
- Frontend : http://localhost:4200

---

📖 **Guide complet** : Voir [SETUP_GUIDE.md](SETUP_GUIDE.md) pour plus de détails


