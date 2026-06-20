# Guide d'installation

Ce guide suppose une machine Windows vierge, sans aucun outil de développement
installé.

## 1. Prérequis système

| Outil | Version | Pourquoi |
|---|---|---|
| Windows | 10/11 64-bit | Le projet n'a pas été teste sur d'autres OS |
| Python | 3.10+ **64-bit** | Doit correspondre a l'architecture de la DLL |
| GCC / MinGW | n'importe laquelle | Compile `calculs.c` en `calculs.dll` |
| .NET SDK | 8.0 | Execute la GUI C# |
| JetBrains Rider (ou Visual Studio) | recent | Ouvre et lance le projet C# |

**Verifier l'architecture de ton Python avant tout** (ca evite l'erreur la plus
frequente du projet, voir section Depannage #1) :

```bash
python -c "import struct; print(struct.calcsize('P') * 8)"
```

Le resultat (`32` ou `64`) doit correspondre au flag utilise pour compiler la DLL
a l'etape 3.

## 2. Installation des dependances

### Python

```bash
pip install flask pytest
```

### NuGet (cote C#, dans Rider : clic droit projet → Manage NuGet Packages)

```
System.Windows.Forms.DataVisualization
System.Data.SqlClient
```

(Le second package n'est jamais utilise directement — il corrige un bug de
chargement interne de `DataVisualization` sur .NET moderne, voir Depannage #5.)

## 3. Compilation de la DLL C

Depuis le dossier du projet, dans une invite de commandes (**cmd**, pas
PowerShell — voir Depannage #3) :

```bash
gcc -m64 -shared -o calculs.dll calculs.c -lm -Wl,--export-all-symbols
```

Remplacer `-m64` par `-m32` si l'etape 1 a renvoye `32`.

`calculs.dll` doit se trouver dans le **meme dossier** que `module.py`.

## 4. Configuration de la base de donnees

Aucune configuration manuelle necessaire : `db.sqlite` et les tables
(`users`, `sessions`, `activite`) sont creees automatiquement au premier
lancement de l'API (fonction `init_db()` dans `module.py`).

Pour generer des donnees de demonstration :

```bash
python generator.py
```

## 5. Lancement — developpement

```bash
cd projet-2-fitness
python app.py
```

Ouvrir ensuite :
- `http://127.0.0.1:5000/dashboard` — dashboard web
- `http://127.0.0.1:5000/api/users` — API brute (verification)

Pour la GUI C# : ouvrir `GUI/Projet2.sln` dans Rider, verifier que Flask tourne
deja, puis lancer le projet (▶).

## 6. Lancement — production (suggestion)

Le serveur Flask integre (`app.run()`) n'est pas concu pour la production.
Pour un deploiement reel :

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

Pour la GUI, generer un executable autonome :

```bash
dotnet publish -c Release -r win-x64 --self-contained
```

## 7. Tests

```bash
pytest tests_module.py -v
```

## 8. Arborescence du projet

```
projet-2-fitness/
├── calculs.c                  # Calculs purs (IMC, calories, MET) - aucune validation
├── calculs.dll                # Compile a partir de calculs.c
├── module.py                  # Pont ctypes + validation + SQLite + logique metier
├── tests_module.py             # 10 tests Pytest
├── app.py                     # API REST Flask
├── generator.py                # Genere des utilisateurs/seances de demo
├── benchmark.py                 # Compare Python pur / ctypes scalaire / ctypes batch
├── db.sqlite                   # Cree automatiquement au premier lancement
├── templates/
│   └── dashboard.html          # Dashboard Chart.js (3 graphiques, refresh 30s)
└── GUI/
    └── Projet2/                 # Application C# WinForms (.NET 8)
        ├── Program.cs
        ├── Models.cs            # Classes miroir du JSON Flask
        ├── ApiClient.cs         # Toutes les requetes HTTP - aucun calcul
        ├── LoginForm.cs
        ├── MenuForm.cs
        ├── ProfileForm.cs
        ├── AddSessionForm.cs
        ├── StatsForm.cs
        └── HistoryForm.cs
```

## 9. Depannage — erreurs frequentes

### 1. `OSError: [WinError 193] %1 n'est pas une application Win32 valide`

**Cause** : la DLL et Python n'ont pas la meme architecture (32 vs 64 bits).

**Solution** : verifier l'architecture Python (etape 1) et recompiler la DLL
avec le bon flag (`-m32` ou `-m64`).

### 2. `AttributeError: function 'calc_bmi' not found`

**Cause** : la DLL a ete compilee sans exporter ses fonctions.

**Solution** : ajouter `-Wl,--export-all-symbols` a la commande de compilation.

### 3. Erreurs de syntaxe en collant une commande `gcc` dans le terminal

**Cause** : PowerShell interprete certains caracteres (`-`) differemment de
l'invite de commandes classique.

**Solution** : utiliser **cmd** (`Windows + R` → `cmd`), ou prefixer la
commande par `&` si PowerShell est impose.

### 4. Le dashboard reste bloque sur "Selectionner un utilisateur" / erreur CORS

**Cause** : le fichier `dashboard.html` a ete ouvert via un serveur autre que
Flask (ex. VS Code Live Server sur le port 5500), ce qui declenche une
politique CORS du navigateur.

**Solution** : toujours acceder au dashboard via
`http://127.0.0.1:5000/dashboard`, jamais via un autre port.

### 5. `System.IO.FileNotFoundException: ... System.Data.SqlClient ...` en ouvrant StatsForm

**Cause** : bug connu du portage de `System.Windows.Forms.DataVisualization`
sur .NET moderne — son moteur de rendu cherche `System.Data.SqlClient` meme
sans aucune utilisation de SQL Server.

**Solution** : installer le package NuGet `System.Data.SqlClient` (jamais
utilise directement, juste necessaire pour satisfaire cette dependance interne).

### 6. `gcc.exe: ... Le chemin d'acces specifie est introuvable`

**Cause** : GCC/MinGW n'est pas installe, ou le chemin utilise dans la
commande est incorrect.

**Solution** : verifier le chemin reel via Code::Blocks (Settings → Compiler →
Toolchain executables), ou installer MinGW-w64 depuis winlibs.com si absent.

### 7. Le serveur Flask met plusieurs secondes a repondre

**Cause** : la resolution DNS de `localhost` sur Windows peut etre lente.

**Solution** : utiliser `http://127.0.0.1:5000` plutot que `http://localhost:5000`.
