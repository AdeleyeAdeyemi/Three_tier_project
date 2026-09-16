from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection

app = Flask(__name__)

app.config["SECRET_KEY"] = "change-this-in-production"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CORS(app, supports_credentials=True)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "backend"
    })


@app.route("/api/database/health")
def database_health():
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT 1 AS result")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "status": "ok",
            "database": "connected",
            "result": result["result"]
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "message": str(error)
        }), 500


@app.route("/api/platform")
def platform():
    return jsonify({
        "timestamp": "2026-09-16 12:00",
        "title": "Platform is running",
        "messages": [
            "Application started successfully"
        ],
        "errors": []
    })

@app.route("/api/products")
def products():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, description, price, stock
            FROM products
            ORDER BY id
        """)

        products = cursor.fetchall()

        return jsonify({
            "products": products
        })

    finally:
        cursor.close()
        connection.close()

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()

    if not email or not password or not first_name or not last_name:
        return jsonify({
            "error": "Email, password, first name and last name are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "error": "An account with this email already exists"
            }), 409

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (
                email,
                password_hash,
                first_name,
                last_name
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, first_name, last_name, created_at
            """,
            (
                email,
                password_hash,
                first_name,
                last_name
            )
        )

        user = cursor.fetchone()

        connection.commit()

        return jsonify({
            "message": "Account created successfully",
            "user": user
        }), 201

    except Exception:
        connection.rollback()

        return jsonify({
            "error": "Unable to create account"
        }), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, email, password_hash, first_name, last_name
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        if not check_password_hash(user["password_hash"], password):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        session["user_id"] = user["id"]

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            }
        }), 200

    finally:
        cursor.close()
        connection.close()

@app.route("/api/users/me")
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Authentication required"
        }), 401

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, email, first_name, last_name, created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            session.clear()

            return jsonify({
                "error": "User not found"
            }), 404

        return jsonify({
            "user": user
        })

    finally:
        cursor.close()
        connection.close()

@app.route("/api/users/me", methods=["PUT"])
def update_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip().lower()

    if not first_name or not last_name or not email:
        return jsonify({
            "error": "First name, last name and email are required"
        }), 400

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
              AND id != %s
            """,
            (email, user_id)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "error": "An account with this email already exists"
            }), 409

        cursor.execute(
            """
            UPDATE users
            SET
                first_name = %s,
                last_name = %s,
                email = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, email, first_name, last_name, created_at, updated_at
            """,
            (
                first_name,
                last_name,
                email,
                user_id
            )
        )

        user = cursor.fetchone()

        connection.commit()

        return jsonify({
            "message": "Profile updated successfully",
            "user": user
        }), 200

    except Exception:
        connection.rollback()

        return jsonify({
            "error": "Unable to update profile"
        }), 500

    finally:
        cursor.close()
        connection.close()

@app.route("/api/dashboard")
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Authentication required"
        }), 401

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, email, first_name, last_name, created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            session.clear()

            return jsonify({
                "error": "User not found"
            }), 404

        return jsonify({
            "message": "Dashboard loaded successfully",
            "user": user
        })

    finally:
        cursor.close()
        connection.close()


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "message": "Logout successful"
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
