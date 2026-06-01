"""
tests_module.py — 10 tests Pytest obligatoires
Projet 2 · 6e TTR Informatique · CEPES Jodoigne

Structure de chaque test :
  1. ARRANGE  → préparer les données
  2. ACT      → appeler la fonction
  3. ASSERT   → vérifier le résultat

Lancer les tests :
  pytest tests_module.py -v
"""

import pytest
import os
import sqlite3
from datetime import date, timedelta

# ── On pointe la DB de test vers un fichier séparé
#    pour ne pas polluer la vraie base de données
os.environ["FITNESS_DB"] = "test_db.sqlite"

import module
module._DB_PATH = "test_db.sqlite"


# ═══════════════════════════════════════════════════════════════
#  FIXTURE — préparation/nettoyage avant chaque test
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def setup_db():
    """
    Prépare une DB propre avant chaque test en vidant les tables.
    On vide plutôt que supprimer le fichier pour éviter le
    PermissionError Windows (fichier encore ouvert par SQLite).
    autouse=True → s'applique automatiquement à tous les tests.
    """
    # ARRANGE — créer les tables si elles n'existent pas
    module.init_db()

    # Vider les tables dans le bon ordre (FK : sessions avant users)
    with module._get_conn() as conn:
        conn.execute("DELETE FROM sessions")
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM activite")
        # Réinitialise les compteurs AUTOINCREMENT
        conn.execute(
            "DELETE FROM sqlite_sequence WHERE name IN ('sessions','users','activite')"
        )

    # Remettre les activités par défaut et recharger la table MET
    module.init_db()
    module._met_table_cache = None
    module.build_met_table()

    yield   # ← le test s'exécute ici


# ═══════════════════════════════════════════════════════════════
#  TESTS 1–4 : Calculs IMC
# ═══════════════════════════════════════════════════════════════

def test_bmi_basic():
    """
    Test 1 — Vérifie que la formule IMC est correcte.
    70 kg / 1.75² = 22.857...
    pytest.approx(22.86, abs=0.01) tolère une marge de ±0.01
    car les flottants ne sont jamais exactement égaux.
    """
    # ARRANGE
    weight_kg = 70.0
    height_m  = 1.75

    # ACT
    result = module.calc_bmi(weight_kg, height_m)

    # ASSERT
    assert result == pytest.approx(22.86, abs=0.01)


def test_bmi_category_normal():
    """
    Test 2 — Un IMC de 22 doit retourner 'Poids normal'.
    La plage normale OMS est 18.5 – 24.9.
    """
    # ARRANGE
    bmi = 22.0

    # ACT
    label = module.bmi_category_label(bmi)

    # ASSERT
    assert label == "Poids normal"


def test_bmi_category_underweight():
    """
    Test 3 — Un IMC de 17 doit retourner 'Insuffisance pondérale'.
    En dessous de 18.5 selon l'OMS.
    """
    # ARRANGE
    bmi = 17.0

    # ACT
    label = module.bmi_category_label(bmi)

    # ASSERT
    assert label == "Insuffisance pondérale"


def test_bmi_category_obese_grade_2():
    """
    Test 4 — Un IMC de 37 doit retourner 'Obésité grade 2'.
    Grade 2 = entre 35.0 et 39.9 selon l'OMS.
    """
    # ARRANGE
    bmi = 37.0

    # ACT
    label = module.bmi_category_label(bmi)

    # ASSERT
    assert label == "Obésité grade 2"


# ═══════════════════════════════════════════════════════════════
#  TESTS 5–6 : Calculs calories et MET
# ═══════════════════════════════════════════════════════════════

def test_calories_burned_running_30min():
    """
    Test 5 — Calcul des calories pour une course de 30 minutes.
    Formule : MET × poids × durée_h
    8.0 × 70 × (30/60) = 8.0 × 70 × 0.5 = 280 kcal
    """
    # ARRANGE
    weight_kg = 70.0
    met       = 8.0    # MET course
    minutes   = 30

    # ACT
    result = module.calories_burned(weight_kg, met, minutes)

    # ASSERT
    assert result == pytest.approx(280.0, abs=0.1)


def test_met_lookup_course():
    """
    Test 6 — L'activité id=1 (course) doit retourner un MET de 8.0
    depuis la table activite en DB, avec une intensité neutre de 1.0.
    Vérifie que Python charge bien la table depuis la DB et la passe au C.
    """
    # ARRANGE
    activite_id = 1     # course dans la table activite
    intensity   = 1.0   # facteur neutre

    # ACT
    met = module.met_for_activity(activite_id, intensity)

    # ASSERT
    assert met == pytest.approx(8.0, abs=0.01)


# ═══════════════════════════════════════════════════════════════
#  TESTS 7–9 : Persistance et statistiques
# ═══════════════════════════════════════════════════════════════

def test_save_session_roundtrip():
    """
    Test 7 — Crée un utilisateur, ajoute une séance,
    et vérifie que la séance est bien retrouvée en DB
    avec les bonnes valeurs (user_id, activite_id, durée, calories).
    """
    # ARRANGE — créer un utilisateur
    user = module.save_user({
        "name":      "Marie",
        "weight_kg": 62.0,
        "height_m":  1.68,
        "age":       17,
        "sex":       "F"
    })

    # ACT — ajouter une séance de course de 45 minutes
    session = module.add_session(user["id"], {
        "activite_id":  1,      # course
        "duration_min": 45,
        "intensity":    1.0,
        "date":         "2026-05-15"
    })

    # ASSERT — vérifier les valeurs sauvegardées
    assert session["user_id"]      == user["id"]
    assert session["activite_id"]  == 1
    assert session["duration_min"] == 45
    # 8.0 × 62 × (45/60) = 372 kcal
    assert session["calories"] == pytest.approx(372.0, abs=0.5)


def test_weekly_stats_aggregation():
    """
    Test 8 — Ajoute 2 séances cette semaine et vérifie
    que weekly_stats retourne les bons totaux.
    total_min  = 30 + 45 = 75
    count      = 2
    """
    # ARRANGE — créer un utilisateur
    user = module.save_user({
        "name":      "Lucas",
        "weight_kg": 75.0,
        "height_m":  1.80,
        "age":       18,
        "sex":       "M"
    })

    # Date dans la semaine courante
    today = date.today().isoformat()

    # ACT — ajouter 2 séances
    module.add_session(user["id"], {
        "activite_id":  1,
        "duration_min": 30,
        "intensity":    1.0,
        "date":         today
    })
    module.add_session(user["id"], {
        "activite_id":  4,      # musculation
        "duration_min": 45,
        "intensity":    1.0,
        "date":         today
    })

    stats = module.weekly_stats(user["id"])

    # ASSERT
    assert stats["count"]     == 2
    assert stats["total_min"] == 75


def test_bmi_history_returns_chronological():
    """
    Test 9 — Vérifie que bmi_history retourne les dates
    dans l'ordre chronologique (du plus ancien au plus récent).
    """
    # ARRANGE — créer un utilisateur
    user = module.save_user({
        "name":      "Sophie",
        "weight_kg": 58.0,
        "height_m":  1.65,
        "age":       20,
        "sex":       "F"
    })

    today      = date.today()
    date_old   = (today - timedelta(days=10)).isoformat()
    date_mid   = (today - timedelta(days=5)).isoformat()
    date_today = today.isoformat()

    # ACT — ajouter 3 séances à des dates différentes (ordre mélangé)
    module.add_session(user["id"], {
        "activite_id": 5, "duration_min": 30,
        "intensity": 1.0, "date": date_mid
    })
    module.add_session(user["id"], {
        "activite_id": 5, "duration_min": 30,
        "intensity": 1.0, "date": date_old
    })
    module.add_session(user["id"], {
        "activite_id": 5, "duration_min": 30,
        "intensity": 1.0, "date": date_today
    })

    history = module.bmi_history(user["id"])
    dates   = [entry[0] for entry in history]

    # ASSERT — les dates doivent être triées du plus ancien au plus récent
    assert dates == sorted(dates)
    assert len(history) == 3


# ═══════════════════════════════════════════════════════════════
#  TEST 10 : Validation Python
# ═══════════════════════════════════════════════════════════════

def test_validate_negative_weight_rejected():
    """
    Test 10 — Un poids négatif doit lever une ValueError.
    C'est la validation Python qui bloque AVANT d'appeler le C.
    pytest.raises(ValueError) vérifie que l'exception est bien levée.
    """
    # ARRANGE
    weight_kg = -10.0
    height_m  = 1.75

    # ACT + ASSERT — on s'attend à une ValueError
    with pytest.raises(ValueError):
        module.calc_bmi(weight_kg, height_m)