from flask import Flask, request, jsonify, render_template, redirect
import module

app = Flask(__name__)

module.init_db()
module.build_met_table()


def ok(data, code=200):
    return jsonify({"status": "ok", "data": data}), code


def error(message, code=400):
    return jsonify({"status": "error", "data": message}), code


@app.route("/")
def index():
    return redirect("/dashboard")


@app.route("/api/users", methods=["GET"])
def get_users():
    try:
        users = module.list_users()
        return ok(users)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/users", methods=["POST"])
def create_user():
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
    try:
        user = module.get_user(user_id)
        return ok(user)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json()
        if not data:
            return error("Body JSON manquant.", 400)
        user = module.update_user(user_id, data)
        return ok(user)
    except ValueError as e:
        msg = str(e)
        if "introuvable" in msg:
            return error(msg, 404)
        return error(msg, 400)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    try:
        user_id = request.args.get("user_id", type=int)
        if user_id is None:
            return error("Parametre user_id manquant.", 400)
        week = request.args.get("week", type=int)
        sessions = module.list_sessions(user_id, week=week)
        return ok(sessions)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/sessions", methods=["POST"])
def create_session():
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


@app.route("/api/users/<int:user_id>/stats", methods=["GET"])
def get_stats(user_id):
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
    try:
        history = module.bmi_history(user_id)
        data = [{"date": d, "bmi": b} for d, b in history]
        return ok(data)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/activites", methods=["GET"])
def get_activites():
    try:
        activites = module.list_activites()
        return ok(activites)
    except Exception as e:
        return error(str(e), 500)


@app.route("/api/activites", methods=["POST"])
def create_activite():
    try:
        data = request.get_json()
        if not data:
            return error("Body JSON manquant.", 400)
        activite = module.save_activite(data)
        return ok(activite, 201)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(str(e), 500)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    print("=" * 50)
    print("  API Fitness demarree")
    print("  http://127.0.0.1:5000/api/users")
    print("  http://127.0.0.1:5000/dashboard")
    print("=" * 50)
    app.run(debug=False, host="127.0.0.1", port=5000)