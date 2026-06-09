from functools import wraps

import jwt
from flask import (
    request,
    jsonify,
    current_app,
    session,
    render_template,
    redirect,
    flash,
)

from . import auth
from models import User, db


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            if token.startswith("Bearer "):
                token = token[7:]

            data = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )

            current_user = User.query.get(data["sub"])

            if not current_user:
                return jsonify({"message": "Token is invalid!"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def apply_free_trial(user):
    user.plan = "free_trial"
    user.subscription_tier = "free_trial"
    user.leads_used = 0
    user.leads_limit = 5
    user.max_leads_per_search = 5


def login_user_session(user):
    session.permanent = True`r`n    session["user_id"] = user.id
    session["email"] = user.email
    session["role"] = user.role
    session["subscription_tier"] = getattr(user, "subscription_tier", "free_trial")
    session["plan"] = getattr(user, "plan", "free_trial")


@auth.route("/register-page", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email och lösenord krävs.", "warning")
        return redirect("/auth/register-page")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        flash("Det finns redan ett konto med den emailen.", "warning")
        return redirect("/auth/login-page")

    new_user = User(email=email)
    new_user.set_password(password)
    new_user.role = "user"

    apply_free_trial(new_user)

    db.session.add(new_user)
    db.session.commit()

    login_user_session(new_user)

    flash("Välkommen! Fyll i din företagsprofil så AI:n kan skriva personliga mail.", "success")
    return redirect("/leads/profile/setup")


@auth.route("/login-page", methods=["GET", "POST"])
def login_page():
    session.pop("_flashes", None)
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash("Fel email eller lösenord.", "warning")
        return redirect("/auth/login-page")

    login_user_session(user)

    return redirect("/leads/")


@auth.route("/logout")
def logout():
    session.pop("_flashes", None)
    session.clear()
    return redirect("/")


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required!"}), 400

    existing_user = User.query.filter_by(email=data["email"]).first()

    if existing_user:
        return jsonify({"message": "User already exists!"}), 409

    new_user = User(email=data["email"])
    new_user.set_password(data["password"])
    new_user.role = data.get("role", "user")

    apply_free_trial(new_user)

    db.session.add(new_user)
    db.session.commit()

    login_user_session(new_user)

    return jsonify({
        "message": "User created successfully!",
        "next": "/leads/profile/setup",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role,
            "plan": new_user.plan,
            "subscription_tier": new_user.subscription_tier,
            "leads_used": new_user.leads_used,
            "leads_limit": new_user.leads_limit,
            "remaining_leads": new_user.remaining_leads() if hasattr(new_user, "remaining_leads") else 5,
            "max_leads_per_search": new_user.max_leads_per_search,
        }
    }), 201


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required!"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials!"}), 401

    token = user.generate_auth_token()
    login_user_session(user)

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "plan": getattr(user, "plan", "free_trial"),
            "subscription_tier": getattr(user, "subscription_tier", "free_trial"),
            "leads_used": getattr(user, "leads_used", 0),
            "leads_limit": getattr(user, "leads_limit", 5),
            "remaining_leads": user.remaining_leads() if hasattr(user, "remaining_leads") else 5,
            "max_leads_per_search": getattr(user, "max_leads_per_search", 5),
            "gmail_connected": getattr(user, "gmail_connected", False),
        }
    }), 200


@auth.route("/profile", methods=["GET"])
@token_required
def profile(current_user):
    return jsonify({
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "plan": getattr(current_user, "plan", "free_trial"),
            "subscription_tier": getattr(current_user, "subscription_tier", "free_trial"),
            "leads_used": getattr(current_user, "leads_used", 0),
            "leads_limit": getattr(current_user, "leads_limit", 5),
            "remaining_leads": current_user.remaining_leads() if hasattr(current_user, "remaining_leads") else 5,
            "max_leads_per_search": getattr(current_user, "max_leads_per_search", 5),
            "gmail_connected": getattr(current_user, "gmail_connected", False),
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        }
    }), 200




