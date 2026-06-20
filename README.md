[README.md](https://github.com/user-attachments/files/29157889/README.md)
# Fitness Tracker — Suivi sportif & calcul de calories

Application de suivi d'entraînement personnel combinant **C, Python, Flask et C#** :
calcul de l'IMC, des calories brûlées (formule MET), statistiques hebdo/mensuelles,
dashboard web temps réel et application desktop Windows.

## Pourquoi ce projet ?

La plupart des trackers fitness cachent leurs calculs derrière une API tierce. Ici,
le moteur de calcul est **écrit à la main en C**, compilé en DLL, et appelé depuis
Python via `ctypes` — avec un vrai benchmark comparant Python pur, ctypes scalaire
et ctypes batch pour démontrer l'intérêt (et les pièges) de l'interop C/Python.

## Stack technique

| Couche | Technologie | Rôle |
|---|---|---|
| Calcul | C (DLL) | IMC, calories, MET — formules pures, sans validation |
| Logique métier | Python (`ctypes`, SQLite) | Validation, persistance, agrégation de stats |
| API | Flask (REST) | Expose les données en JSON, calcule via la DLL |
| Dashboard | HTML / JS / Chart.js | Visualisation temps réel (3 graphiques, refresh 30s) |
| Application desktop | C# (.NET 8, WinForms) | GUI Windows consommant l'API via `HttpClient` |

Aucun calcul n'est dupliqué entre les couches : le C# et le dashboard ne font
**que** afficher ce que l'API leur envoie.

## Architecture

```
calculs.c  →  calculs.dll
                  │
                  ▼ (ctypes)
            module.py  ──────────────►  db.sqlite
                  │
                  ▼
              app.py (Flask API)
              ┌────────┴────────┐
              ▼                 ▼
   dashboard.html (JS)   GUI C# (.NET / WinForms)
```

## Démarrage rapide

```bash
cd projet-2-fitness
python app.py
```

Puis ouvre `http://127.0.0.1:5000/dashboard`.

Pour l'installation complète (dépendances, compilation de la DLL, GUI C#),
voir **[INSTALLATION.md](./INSTALLATION.md)**.

## Tests

```bash
pytest tests_module.py -v
```

10 tests couvrant le calcul d'IMC, les catégories OMS, les calories, la
persistance SQLite et la validation des entrées.

## Benchmark

```bash
python benchmark.py
```

Compare 3 stratégies d'appel à la DLL (Python pur / ctypes scalaire / ctypes
batch) sur 100 000 éléments, avec progression en direct dans le terminal.

## Licence

Projet académique — CEPES Jodoigne, section TTR Informatique.
