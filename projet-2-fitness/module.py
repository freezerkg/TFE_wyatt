"""
module.py — Module central du projet Suivi sportif & fitness
Projet 2 · 6e TTR Informatique · CEPES Jodoigne

Rôles :
  - Charger la DLL C via ctypes et déclarer les signatures
  - Valider tous les paramètres AVANT d'appeler le C
  - Fournir la table MET depuis la DB au C (Option 2)
  - Gérer la persistance SQLite (users, sessions, activite)
  - Exposer la logique métier (stats, historique IMC, etc.)
"""

import ctypes
import os
import sqlite3
from datetime import datetime, date, timedelta

# ═══════════════════════════════════════════════════════════════
#  1. CHARGEMENT DE LA DLL
# ═══════════════════════════════════════════════════════════════

# La DLL doit se trouver dans le même dossier que module.py
_DLL_PATH = os.path.join(os.path.dirname(__file__), "calculs.dll")

try:
    lib = ctypes.CDLL(_DLL_PATH)
except OSError as e:
    raise RuntimeError(
        f"Impossible de charger la DLL : {_DLL_PATH}\n"
        f"Lance d'abord : gcc -shared -o calculs.dll calculs.c -lm\n"
        f"Détail : {e}"
    )

# ───────────────────────────────────────────────────────────────
#  Déclaration des signatures ctypes
#  (argtypes = types des paramètres, restype = type de retour)
#  Sans ça, ctypes suppose que tout est int → résultats incorrects !
# ───────────────────────────────────────────────────────────────

# float calc_bmi(float weight_kg, float height_m)
lib.calc_bmi.argtypes = [ctypes.c_float, ctypes.c_float]
lib.calc_bmi.restype  = ctypes.c_float

# int bmi_category(float bmi)
lib.bmi_category.argtypes = [ctypes.c_float]
lib.bmi_category.restype  = ctypes.c_int

# float calories_burned(float weight_kg, float met, int minutes)
lib.calories_burned.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_int]
lib.calories_burned.restype  = ctypes.c_float

# float met_for_activity_ext(float* met_table, int table_size,
#                             int type_id, float intensity)
lib.met_for_activity_ext.argtypes = [
    ctypes.POINTER(ctypes.c_float),  # met_table  (tableau Python → C)
    ctypes.c_int,                    # table_size
    ctypes.c_int,                    # type_id
    ctypes.c_float                   # intensity
]
lib.met_for_activity_ext.restype = ctypes.c_float

# void calc_bmi_batch(float* w, float* h, float* out, int n)
lib.calc_bmi_batch.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int
]
lib.calc_bmi_batch.restype = None

# void calories_batch(float* w, float* met, int* mins, float* out, int n)
lib.calories_batch.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int
]
lib.calories_batch.restype = None


# ═══════════════════════════════════════════════════════════════
#  2. BASE DE DONNÉES SQLITE
# ═══════════════════════════════════════════════════════════════

_DB_PATH = os.path.join(os.path.dirname(__file__), "db.sqlite")


def _get_conn() -> sqlite3.Connection:
    """Retourne une connexion SQLite avec accès par nom de colonne."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row   # permet row["colonne"] au lieu de row[0]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Crée les tables si elles n'existent pas encore.
    À appeler une seule fois au démarrage de l'API Flask (dans app.py).
    """
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                weight_kg  REAL    NOT NULL,
                height_m   REAL    NOT NULL,
                age        INTEGER,
                sex        TEXT    CHECK (sex IN ('M', 'F'))
            );

            CREATE TABLE IF NOT EXISTS activite (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                nom      TEXT    NOT NULL UNIQUE,
                met_base REAL    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS weight_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id),
                date       TEXT    NOT NULL,
                weight_kg  REAL    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL REFERENCES users(id),
                activite_id  INTEGER NOT NULL REFERENCES activite(id),
                duration_min INTEGER NOT NULL,
                met          REAL    NOT NULL,
                date         TEXT    NOT NULL,
                calories     REAL    NOT NULL
            );
        """)

        # Insertion des activités par défaut si la table est vide
        count = conn.execute("SELECT COUNT(*) FROM activite").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO activite (nom, met_base) VALUES (?, ?)",
                [
                    ("course",        8.0),
                    ("velo",          6.0),
                    ("natation",      7.0),
                    ("musculation",   4.0),
                    ("yoga",          2.5),
                    ("marche_rapide", 4.3),
                ]
            )


# ═══════════════════════════════════════════════════════════════
#  3. TABLE MET DYNAMIQUE (Option 2 — fournie par Python au C)
# ═══════════════════════════════════════════════════════════════

# Cache en mémoire pour éviter de recharger la DB à chaque calcul
_met_table_cache: ctypes.Array | None = None
_met_table_size:  int = 0


def build_met_table() -> tuple:
    """
    Charge les valeurs MET depuis la table `activite` en DB,
    les convertit en tableau ctypes.c_float et met à jour le cache.

    Retourne : (FloatArray, taille)

    Le tableau est indexé par (activite.id - 1) car les ID SQLite
    commencent à 1 mais les index C commencent à 0.
    """
    global _met_table_cache, _met_table_size

    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT met_base FROM activite ORDER BY id"
        ).fetchall()

    if not rows:
        raise RuntimeError("La table activite est vide. Lance init_db() d'abord.")

    FloatArray       = ctypes.c_float * len(rows)
    _met_table_cache = FloatArray(*[row["met_base"] for row in rows])
    _met_table_size  = len(rows)

    return _met_table_cache, _met_table_size


def _ensure_met_table():
    """Charge la table MET si elle n'est pas encore en cache."""
    if _met_table_cache is None:
        build_met_table()


# ═══════════════════════════════════════════════════════════════
#  4. WRAPPERS CTYPES AVEC VALIDATION PYTHON
# ═══════════════════════════════════════════════════════════════

# Labels IMC pour bmi_category_label()
_BMI_LABELS = [
    "Insuffisance pondérale",
    "Poids normal",
    "Surpoids",
    "Obésité grade 1",
    "Obésité grade 2",
    "Obésité grade 3",
]


def calc_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calcule l'IMC via la DLL C.
    Validation Python : poids et taille doivent être strictement positifs.
    """
    if weight_kg <= 0:
        raise ValueError(f"Poids invalide : {weight_kg} (doit être > 0)")
    if height_m <= 0:
        raise ValueError(f"Taille invalide : {height_m} (doit être > 0)")
    if height_m > 3.0:
        raise ValueError(f"Taille suspecte : {height_m} m (max raisonnable : 3.0)")

    return float(lib.calc_bmi(weight_kg, height_m))


def bmi_category_label(bmi: float) -> str:
    """
    Retourne le label OMS de la catégorie IMC.
    Validation Python : l'IMC doit être positif.
    """
    if bmi <= 0:
        raise ValueError(f"IMC invalide : {bmi} (doit être > 0)")

    index = lib.bmi_category(ctypes.c_float(bmi))
    return _BMI_LABELS[index]


def calories_burned(weight_kg: float, met: float, minutes: int) -> float:
    """
    Calcule les calories brûlées via la DLL C.
    Validation Python avant appel C.
    """
    if weight_kg <= 0:
        raise ValueError(f"Poids invalide : {weight_kg}")
    if met <= 0:
        raise ValueError(f"MET invalide : {met}")
    if minutes <= 0:
        raise ValueError(f"Durée invalide : {minutes} min (doit être > 0)")
    if minutes > 600:
        raise ValueError(f"Durée suspecte : {minutes} min (max raisonnable : 600)")

    return float(lib.calories_burned(
        ctypes.c_float(weight_kg),
        ctypes.c_float(met),
        ctypes.c_int(minutes)
    ))


def met_for_activity(activite_id: int, intensity: float = 1.0) -> float:
    """
    Retourne le MET ajusté pour une activité, en utilisant la table
    chargée depuis la DB (Option 2 — table fournie par Python au C).

    activite_id : ID de la table `activite` (commence à 1 en SQLite)
    intensity   : facteur multiplicateur (0.8 léger / 1.0 normal / 1.2 intense)
    """
    _ensure_met_table()

    # Conversion ID SQLite (base 1) → index tableau C (base 0)
    type_id = activite_id - 1

    if type_id < 0 or type_id >= _met_table_size:
        raise ValueError(
            f"activite_id {activite_id} hors limite "
            f"(table a {_met_table_size} activités)"
        )
    if intensity <= 0:
        raise ValueError(f"Intensité invalide : {intensity} (doit être > 0)")

    return float(lib.met_for_activity_ext(
        _met_table_cache,
        ctypes.c_int(_met_table_size),
        ctypes.c_int(type_id),
        ctypes.c_float(intensity)
    ))


# ═══════════════════════════════════════════════════════════════
#  5. GESTION DES UTILISATEURS
# ═══════════════════════════════════════════════════════════════

def _validate_user_data(data: dict):
    """Validation commune pour save_user et update_user."""
    if not data.get("name", "").strip():
        raise ValueError("Le nom est obligatoire.")
    if data.get("weight_kg", 0) <= 0:
        raise ValueError("Le poids doit être positif.")
    if data.get("height_m", 0) <= 0:
        raise ValueError("La taille doit être positive.")
    if data.get("sex") not in ("M", "F", None):
        raise ValueError("Le sexe doit être 'M' ou 'F'.")
    if data.get("age") is not None and data["age"] < 0:
        raise ValueError("L'âge ne peut pas être négatif.")


def save_user(data: dict) -> dict:
    """
    Crée un nouvel utilisateur en base.
    data : {"name", "weight_kg", "height_m", "age"?, "sex"?}
    Retourne le dict de l'utilisateur créé avec son id.
    """
    _validate_user_data(data)

    with _get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO users (name, weight_kg, height_m, age, sex)
               VALUES (:name, :weight_kg, :height_m, :age, :sex)""",
            {
                "name":      data["name"].strip(),
                "weight_kg": data["weight_kg"],
                "height_m":  data["height_m"],
                "age":       data.get("age"),
                "sex":       data.get("sex"),
            }
        )
        user_id = cur.lastrowid
    # Appelé APRÈS le with pour que le commit soit effectué
    return get_user(user_id)


def get_user(user_id: int) -> dict:
    """
    Retourne un utilisateur par son ID, avec son IMC courant calculé.
    Lève ValueError si l'utilisateur n'existe pas.
    """
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()

    if row is None:
        raise ValueError(f"Utilisateur {user_id} introuvable.")

    user = dict(row)
    user["bmi"]          = calc_bmi(user["weight_kg"], user["height_m"])
    user["bmi_category"] = bmi_category_label(user["bmi"])
    return user


def update_user(user_id: int, data: dict) -> dict:
    """
    Met à jour le profil d'un utilisateur existant.
    Retourne le dict mis à jour avec le nouvel IMC.
    """
    get_user(user_id)   # lève ValueError si inexistant
    _validate_user_data(data)

    with _get_conn() as conn:
        conn.execute(
            """UPDATE users
               SET name=:name, weight_kg=:weight_kg, height_m=:height_m,
                   age=:age, sex=:sex
               WHERE id=:id""",
            {
                "id":        user_id,
                "name":      data["name"].strip(),
                "weight_kg": data["weight_kg"],
                "height_m":  data["height_m"],
                "age":       data.get("age"),
                "sex":       data.get("sex"),
            }
        )
    return get_user(user_id)


def list_users() -> list:
    """Retourne tous les utilisateurs avec leur IMC courant."""
    with _get_conn() as conn:
        rows = conn.execute("SELECT id FROM users ORDER BY name").fetchall()
    return [get_user(row["id"]) for row in rows]


# ═══════════════════════════════════════════════════════════════
#  6. GESTION DES SÉANCES
# ═══════════════════════════════════════════════════════════════

def add_session(user_id: int, data: dict) -> dict:
    user = get_user(user_id) 

    activite_id  = data.get("activite_id")
    duration_min = data.get("duration_min")
    intensity    = data.get("intensity", 1.0)
    session_date = data.get("date", date.today().isoformat())

    if activite_id is None:
        raise ValueError("activite_id est obligatoire.")
    if duration_min is None or duration_min <= 0:
        raise ValueError("La durée doit être un entier positif.")
    if intensity <= 0:
        raise ValueError("L'intensité doit être positive.")

    with _get_conn() as conn:
        activite = conn.execute(
            "SELECT * FROM activite WHERE id = ?", (activite_id,)
        ).fetchone()
    if activite is None:
        raise ValueError(f"activite_id {activite_id} introuvable.")

    try:
        datetime.strptime(session_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Format de date invalide : {session_date}")

    met_ajuste = met_for_activity(activite_id, intensity)
    kcal = calories_burned(user["weight_kg"], met_ajuste, duration_min)

    with _get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO sessions
               (user_id, activite_id, duration_min, met, date, calories)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, activite_id, duration_min, met_ajuste,
             session_date, round(kcal, 2))
        )
        session_id = cur.lastrowid
        conn.commit()  # Valide l'insertion dans la DB

    return _get_session(session_id)


def _get_session(session_id: int) -> dict:
    """Retourne une séance par son ID avec le nom de l'activité."""
    with _get_conn() as conn:
        row = conn.execute(
            """SELECT s.*, a.nom AS activite_nom, a.met_base
               FROM sessions s
               JOIN activite a ON a.id = s.activite_id
               WHERE s.id = ?""",
            (session_id,)
        ).fetchone()
    if row is None:
        raise ValueError(f"Séance {session_id} introuvable.")
    return dict(row)


def list_sessions(user_id: int, week: int = None) -> list:
    """
    Retourne les séances d'un utilisateur.
    week : numéro de semaine ISO (optionnel, filtre sur l'année courante)
    """
    get_user(user_id)   # valide l'existence de l'utilisateur

    query  = """SELECT s.*, a.nom AS activite_nom
                FROM sessions s
                JOIN activite a ON a.id = s.activite_id
                WHERE s.user_id = ?"""
    params = [user_id]

    if week is not None:
        query  += " AND strftime('%W', s.date) = ?"
        params.append(f"{int(week):02d}")

    query += " ORDER BY s.date DESC"

    with _get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════════
#  7. STATISTIQUES
# ═══════════════════════════════════════════════════════════════

def weekly_stats(user_id: int) -> dict:
    """
    Statistiques de la semaine courante pour un utilisateur.
    Retourne : {total_min, total_kcal, count, by_type}
    """
    get_user(user_id)

    # Calcul du lundi et dimanche de la semaine courante
    today  = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT s.duration_min, s.calories, a.nom AS activite_nom
               FROM sessions s
               JOIN activite a ON a.id = s.activite_id
               WHERE s.user_id = ?
                 AND s.date BETWEEN ? AND ?""",
            (user_id, monday.isoformat(), sunday.isoformat())
        ).fetchall()

    total_min  = sum(r["duration_min"] for r in rows)
    total_kcal = sum(r["calories"]     for r in rows)

    # Répartition par type d'activité
    by_type: dict = {}
    for row in rows:
        nom = row["activite_nom"]
        if nom not in by_type:
            by_type[nom] = {"count": 0, "total_min": 0, "total_kcal": 0.0}
        by_type[nom]["count"]      += 1
        by_type[nom]["total_min"]  += row["duration_min"]
        by_type[nom]["total_kcal"] += row["calories"]

    return {
        "week_start":  monday.isoformat(),
        "week_end":    sunday.isoformat(),
        "total_min":   total_min,
        "total_kcal":  round(total_kcal, 2),
        "count":       len(rows),
        "by_type":     by_type,
    }


def monthly_stats(user_id: int) -> dict:
    """
    Statistiques du mois courant pour un utilisateur.
    Retourne : {total_min, total_kcal, count, by_type}
    """
    get_user(user_id)

    today      = date.today()
    month_str  = today.strftime("%Y-%m")  # ex. "2026-05"

    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT s.duration_min, s.calories, a.nom AS activite_nom
               FROM sessions s
               JOIN activite a ON a.id = s.activite_id
               WHERE s.user_id = ?
                 AND strftime('%Y-%m', s.date) = ?""",
            (user_id, month_str)
        ).fetchall()

    total_min  = sum(r["duration_min"] for r in rows)
    total_kcal = sum(r["calories"]     for r in rows)

    by_type: dict = {}
    for row in rows:
        nom = row["activite_nom"]
        if nom not in by_type:
            by_type[nom] = {"count": 0, "total_min": 0, "total_kcal": 0.0}
        by_type[nom]["count"]      += 1
        by_type[nom]["total_min"]  += row["duration_min"]
        by_type[nom]["total_kcal"] += row["calories"]

    return {
        "month":       month_str,
        "total_min":   total_min,
        "total_kcal":  round(total_kcal, 2),
        "count":       len(rows),
        "by_type":     by_type,
    }


def save_weight(user_id: int, weight_kg: float, date_str: str = None) -> dict:
    """
    Enregistre une mesure de poids pour un utilisateur.
    Permet de construire un vrai historique pondéral.
    date_str : "YYYY-MM-DD" (défaut : aujourd'hui)
    """
    get_user(user_id)   # valide l'existence

    if weight_kg <= 0:
        raise ValueError("Le poids doit être positif.")

    if date_str is None:
        date_str = date.today().isoformat()

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Format de date invalide : {date_str}")

    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO weight_history (user_id, date, weight_kg) VALUES (?, ?, ?)",
            (user_id, date_str, weight_kg)
        )

    return {"user_id": user_id, "date": date_str, "weight_kg": weight_kg}


def bmi_history(user_id: int) -> list:
    """
    Retourne l'historique IMC dans l'ordre chronologique.
    Utilise weight_history si disponible pour un vrai historique pondéral.
    Sinon, utilise le poids actuel de l'utilisateur.

    Retourne : [(date, bmi), ...]
    """
    user = get_user(user_id)

    with _get_conn() as conn:
        # Vérifie si on a un historique pondéral
        weights = conn.execute(
            """SELECT date, weight_kg FROM weight_history
               WHERE user_id = ? ORDER BY date ASC""",
            (user_id,)
        ).fetchall()

    if weights:
        # Vrai historique : IMC calculé avec le poids de chaque mesure
        return [
            (row["date"], round(calc_bmi(row["weight_kg"], user["height_m"]), 2))
            for row in weights
        ]
    else:
        # Fallback : IMC courant pour chaque date de séance
        with _get_conn() as conn:
            rows = conn.execute(
                """SELECT DISTINCT date FROM sessions
                   WHERE user_id = ? ORDER BY date ASC""",
                (user_id,)
            ).fetchall()
        bmi = calc_bmi(user["weight_kg"], user["height_m"])
        return [(row["date"], round(bmi, 2)) for row in rows]


# ═══════════════════════════════════════════════════════════════
#  8. FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════

def list_activites() -> list:
    """Retourne toutes les activités disponibles depuis la DB."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM activite ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


def save_activite(data: dict) -> dict:
    """
    Ajoute une nouvelle activité dans la table activite.
    data : {"nom", "met_base"}
    Recharge automatiquement la table MET dans le C après insertion.
    Retourne le dict de l'activité créée.
    """
    if not data.get("nom", "").strip():
        raise ValueError("Le nom de l'activité est obligatoire.")
    if data.get("met_base", 0) <= 0:
        raise ValueError("Le MET de base doit être positif.")

    with _get_conn() as conn:
        # Vérifie que le nom n'existe pas déjà (UNIQUE KEY)
        existing = conn.execute(
            "SELECT id FROM activite WHERE nom = ?",
            (data["nom"].strip(),)
        ).fetchone()
        if existing:
            raise ValueError(f"L'activité '{data['nom']}' existe déjà.")

        cur = conn.execute(
            "INSERT INTO activite (nom, met_base) VALUES (?, ?)",
            (data["nom"].strip(), data["met_base"])
        )
        activite_id = cur.lastrowid

    # Recharge la table MET dans le C pour inclure la nouvelle activité
    build_met_table()

    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM activite WHERE id = ?", (activite_id,)
        ).fetchone()
    return dict(row)