"""
generator.py — Générateur de données de test
Projet 2 · 6e TTR Informatique · CEPES Jodoigne

Crée des utilisateurs et des séances fictives sur 8 semaines
pour pouvoir tester le dashboard et la GUI C#.

Utilisation :
  python generator.py
  python generator.py --clean    ← vide la DB avant de générer
"""

import sys
import random
from datetime import date, timedelta
import module

# ═══════════════════════════════════════════════════════════════
#  CONFIG DES DONNÉES FICTIVES
# ═══════════════════════════════════════════════════════════════

# Profils utilisateurs à créer
USERS = [
    {"name": "Marie",   "weight_kg": 62.0, "height_m": 1.68, "age": 17, "sex": "F"},
    {"name": "Lucas",   "weight_kg": 78.0, "height_m": 1.82, "age": 18, "sex": "M"},
    {"name": "Sophie",  "weight_kg": 55.0, "height_m": 1.65, "age": 16, "sex": "F"},
    {"name": "Antoine", "weight_kg": 90.0, "height_m": 1.75, "age": 19, "sex": "M"},
]

# Nombre de semaines de données à générer en arrière
WEEKS_BACK = 8

# Nombre de séances par semaine (min, max) par utilisateur
SESSIONS_PER_WEEK = (2, 5)

# Durées possibles en minutes
DURATIONS = [20, 30, 45, 60, 75, 90]

# Intensités possibles
INTENSITIES = [0.8, 1.0, 1.0, 1.2]   # 1.0 plus fréquent


# ═══════════════════════════════════════════════════════════════
#  FONCTIONS
# ═══════════════════════════════════════════════════════════════

def clean_db():
    """Vide toutes les séances et tous les utilisateurs."""
    print("️  Nettoyage de la base de données...")
    with module._get_conn() as conn:
        conn.execute("DELETE FROM sessions")
        conn.execute("DELETE FROM users")
        conn.execute(
            "DELETE FROM sqlite_sequence WHERE name IN ('sessions','users')"
        )
    print("   Base vidée.\n")


def get_activites() -> list:
    """Récupère les activités depuis la DB."""
    return module.list_activites()


def generate_weight_history(user_id: int, base_weight: float):
    """
    Simule une évolution réaliste du poids sur WEEKS_BACK semaines.
    Le poids varie légèrement chaque semaine (+/- 0.5 kg max).
    """
    today   = date.today()
    weight  = base_weight

    for week in range(WEEKS_BACK, -1, -1):
        monday = today - timedelta(days=today.weekday()) - timedelta(weeks=week)

        # Variation hebdomadaire aléatoire entre -0.4 et +0.3 kg
        # Légèrement biaisé vers la perte (fitness oblige !)
        variation = random.uniform(-0.4, 0.3)
        weight    = round(max(40.0, weight + variation), 1)

        module.save_weight(user_id, weight, monday.isoformat())


def generate_sessions_for_user(user_id: int, activites: list):
    """
    Génère des séances aléatoires sur WEEKS_BACK semaines
    pour un utilisateur donné.
    """
    today  = date.today()
    count  = 0

    for week in range(WEEKS_BACK, -1, -1):
        # Lundi de la semaine
        monday = today - timedelta(days=today.weekday()) - timedelta(weeks=week)

        # Nombre aléatoire de séances cette semaine
        nb_sessions = random.randint(*SESSIONS_PER_WEEK)

        # Jours aléatoires dans la semaine (sans doublon)
        days = random.sample(range(7), min(nb_sessions, 7))

        for day_offset in days:
            session_date = monday + timedelta(days=day_offset)

            # Ne pas générer dans le futur
            if session_date > today:
                continue

            activite  = random.choice(activites)
            duration  = random.choice(DURATIONS)
            intensity = random.choice(INTENSITIES)

            module.add_session(user_id, {
                "activite_id":  activite["id"],
                "duration_min": duration,
                "intensity":    intensity,
                "date":         session_date.isoformat(),
            })
            count += 1

    return count


# ═══════════════════════════════════════════════════════════════
#  SCRIPT PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    # Option --clean : vide la DB avant de générer
    if "--clean" in sys.argv:
        clean_db()

    print(" Initialisation de la base de données...")
    module.init_db()
    module.build_met_table()

    activites = get_activites()
    print(f"   {len(activites)} activités disponibles : "
          f"{', '.join(a['nom'] for a in activites)}\n")

    total_sessions = 0

    for user_data in USERS:
        print(f" Création de l'utilisateur : {user_data['name']}")

        # Vérifie si l'utilisateur existe déjà
        existing = [
            u for u in module.list_users()
            if u["name"] == user_data["name"]
        ]

        if existing:
            user = existing[0]
            print(f"   Déjà existant (id={user['id']}), "
                  f"IMC={user['bmi']:.1f} — {user['bmi_category']}")
        else:
            user = module.save_user(user_data)
            bmi  = module.calc_bmi(user_data["weight_kg"], user_data["height_m"])
            print(f"   Créé (id={user['id']}), "
                  f"IMC={bmi:.1f} — {module.bmi_category_label(bmi)}")

        # Génère l'historique pondéral
        generate_weight_history(user["id"], user_data["weight_kg"])

        # Génère les séances
        nb = generate_sessions_for_user(user["id"], activites)
        total_sessions += nb
        print(f"   {nb} séances générées sur {WEEKS_BACK} semaines\n")

    print("=" * 50)
    print(f"  Generation terminee !")
    print(f"  {len(USERS)} utilisateurs")
    print(f"  {total_sessions} seances au total")
    print(f"  Historique ponderal genere sur {WEEKS_BACK} semaines")
    print(f"\n  Lance le dashboard : python app.py")
    print(f"  Puis ouvre : http://127.0.0.1:5000/dashboard")
    print("=" * 50)


if __name__ == "__main__":
    main()