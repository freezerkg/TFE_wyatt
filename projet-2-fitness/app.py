"""
app.py — API REST Flask
Projet 2 · 6e TTR Informatique · CEPES Jodoigne

Lancer le serveur :
  python app.py

Endpoints :
  GET    /api/users
  POST   /api/users
  GET    /api/users/<id>
  PUT    /api/users/<id>
  GET    /api/sessions?user_id=
  POST   /api/sessions
  GET    /api/users/<id>/stats
  GET    /api/users/<id>/bmi-history
  GET    /dashboard
"""

from flask import Flask, request, jsonify, render_template
import module

# ═══════════════════════════════════════════════════════════════
#  1. INITIALISATION DE L'APPLICATION
# ═══════════════════════════════════════════════════════════════

app = Flask(__name__)

# Initialise la DB et charge la table MET au démarrage
module.init_db()
module.build_met_table()


# ═══════════════════════════════════════════════════════════════
#  2. FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════

def ok(data, code=200):
    """Retourne une réponse JSON de succès."""
    return jsonify({"status": "ok", "data": data}), code


def error(message, code=400):
    """Retourne une réponse JSON d'erreur."""
    return jsonify({"status": "error", "data": message}), code


# ═══════════════════════════════════════════════════════════════
#  3. ENDPOINTS UTILISATEURS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/users", methods=["GET"])
def get_users():
    """
    GET /api/users
    Retourne la liste de tous les utilisateurs avec leur IMC courant.
    Code 200 si succès, 500 si erreur serveur inattendue.
    """
    try:
        users = module.list_users()
        return ok(users)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/users", methods=["POST"])
def create_user():
    """
    POST /api/users
    Crée un nouvel utilisateur.
    Body JSON : {"name", "weight_kg", "height_m", "age"?, "sex"?}
    Code 201 si créé, 400 si données invalides.
    """
    try:
        data = request.get_json()
        if not data:
            return error("Body JSON manquant.", 400)

        user = module.save_user(data)
        return ok(user, 201)

    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    GET /api/users/<id>
    Retourne le détail d'un utilisateur avec son IMC courant et sa catégorie.
    Code 200 si trouvé, 404 si inexistant.
    """
    try:
        user = module.get_user(user_id)
        return ok(user)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    PUT /api/users/<id>
    Met à jour le profil d'un utilisateur existant.
    Body JSON : {"name", "weight_kg", "height_m", "age"?, "sex"?}
    Code 200 si mis à jour, 400 si données invalides, 404 si inexistant.
    """
    try:
        data = request.get_json()
        if not data:
            return error("Body JSON manquant.", 400)

        user = module.update_user(user_id, data)
        return ok(user)

    except ValueError as e:
        # Distingue "non trouvé" (404) de "données invalides" (400)
        msg = str(e)
        if "introuvable" in msg:
            return error(msg, 404)
        return error(msg, 400)
    except Exception as e:
        return error(str(e), 500)


# ═══════════════════════════════════════════════════════════════
#  4. ENDPOINTS SÉANCES
# ═══════════════════════════════════════════════════════════════

@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """
    GET /api/sessions?user_id=<id>&week=<num>
    Retourne les séances d'un utilisateur.
    Paramètre week optionnel pour filtrer par numéro de semaine.
    Code 200 si succès, 400 si user_id manquant, 404 si user inexistant.
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if user_id is None:
            return error("Paramètre user_id manquant.", 400)

        week = request.args.get("week", type=int)

        sessions = module.list_sessions(user_id, week=week)
        return ok(sessions)

    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/sessions", methods=["POST"])
def create_session():
    """
    POST /api/sessions
    Ajoute une séance sportive.
    Les calories sont calculées automatiquement côté serveur via la DLL C.
    Body JSON : {"user_id", "activite_id", "duration_min", "intensity"?, "date"?}
    Code 201 si créée, 400 si données invalides, 404 si user inexistant.
    """
    try:
        data = request.get_json()
        if not data:
            return error("Body JSON manquant.", 400)

        user_id = data.get("user_id")
        if user_id is None:
            return error("user_id est obligatoire.", 400)

        session = module.add_session(user_id, data)
        return ok(session, 201)

    except ValueError as e:
        msg = str(e)
        if "introuvable" in msg:
            return error(msg, 404)
        return error(msg, 400)
    except Exception as e:
        return error(str(e), 500)


# ═══════════════════════════════════════════════════════════════
#  5. ENDPOINTS STATISTIQUES
# ═══════════════════════════════════════════════════════════════

@app.route("/api/users/<int:user_id>/stats", methods=["GET"])
def get_stats(user_id):
    """
    GET /api/users/<id>/stats
    Retourne les statistiques hebdomadaires et mensuelles.
    Code 200 si succès, 404 si user inexistant.
    """
    try:
        stats = {
            "weekly":  module.weekly_stats(user_id),
            "monthly": module.monthly_stats(user_id),
        }
        return ok(stats)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/users/<int:user_id>/bmi-history", methods=["GET"])
def get_bmi_history(user_id):
    """
    GET /api/users/<id>/bmi-history
    Retourne l'historique IMC dans l'ordre chronologique.
    Format : [{"date": "2026-05-15", "bmi": 22.86}, ...]
    Code 200 si succès, 404 si user inexistant.
    """
    try:
        history = module.bmi_history(user_id)
        # Convertit les tuples (date, bmi) en dicts pour le JSON
        data = [{"date": d, "bmi": b} for d, b in history]
        return ok(data)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


# ═══════════════════════════════════════════════════════════════
#  6. ENDPOINT ACTIVITES (bonus utile pour la GUI C#)
# ═══════════════════════════════════════════════════════════════

@app.route("/api/activites", methods=["GET"])
def get_activites():
    """
    GET /api/activites
    Retourne la liste des activités disponibles.
    Utilisé par la GUI C# pour remplir les ComboBox.
    """
    try:
        activites = module.list_activites()
        return ok(activites)
    except Exception as e:
        return error(str(e), 500)


# ═══════════════════════════════════════════════════════════════
#  7. DASHBOARD
# ═══════════════════════════════════════════════════════════════

@app.route("/dashboard")
def dashboard():
    """
    GET /dashboard
    Affiche le dashboard web avec les 3 graphiques Chart.js.
    Rafraîchissement automatique toutes les 30 secondes.
    """
    return render_template("dashboard.html")


# ═══════════════════════════════════════════════════════════════
#  8. DÉMARRAGE DU SERVEUR
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  API Fitness démarrée")
    print("  http://localhost:5000/api/users")
    print("  http://localhost:5000/dashboard")
    print("=" * 50)
    app.run(debug=True, port=5000)