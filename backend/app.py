import os
import sqlite3
import pandas as pd
from flask import Flask, jsonify, request, session, send_from_directory, redirect
from flask_cors import CORS
from werkzeug.security import check_password_hash
from backend.auth import create_database

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DB_PATH = os.path.join(PROJECT_ROOT, "users.db")
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "student_interventions.csv")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "edupulse-development-secret-key")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "0") == "1",
)

# Create the demo authentication database automatically on first run.
# The SQLite database is intentionally not committed to the public repository.
if not os.path.exists(DB_PATH):
    create_database()

# CORS is needed only for the separate local frontend server.
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
)

# Load final integrated dataset using an absolute project path.
df = pd.read_csv(DATA_PATH)


def management_required():
    return session.get("role") in ["management", "admin"]


def student_or_management_required():
    return session.get("role") in ["student", "management", "admin"]


# --------------------------------------------------
# FRONTEND ROUTES (used by the deployed single-service app)
# --------------------------------------------------

@app.route("/")
def home():
    return redirect("/login.html")


@app.route("/login.html")
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/index.html")
def management_page():
    if not management_required():
        return redirect("/login.html")
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/student.html")
def student_page():
    if session.get("role") != "student":
        if session.get("role") in ["management", "admin"]:
            return redirect("/index.html")
        return redirect("/login.html")
    return send_from_directory(FRONTEND_DIR, "student.html")


@app.route("/static/<path:filename>")
def frontend_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "EduPulse AI",
        "students": int(len(df)),
    })


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------

@app.route("/api/summary")
def summary():
    if not management_required():
        return jsonify({"error": "Access denied"}), 403

    return jsonify({
        "total_students": int(len(df)),
        "average_success_score": round(float(df["success_score"].mean()), 2),
        "risk_levels": df["overall_risk_level"].value_counts().to_dict(),
        "risk_types": df["primary_risk_type"].value_counts().to_dict(),
        "segments": df["student_segment"].value_counts().to_dict(),
    })


# --------------------------------------------------
# ALL STUDENTS
# --------------------------------------------------

@app.route("/api/students")
def students():
    if not management_required():
        return jsonify({"error": "Access denied"}), 403

    result = df[[
        "student_id", "name", "department", "semester", "cgpa",
        "success_score", "success_category", "overall_risk_level",
        "primary_risk_type", "student_segment"
    ]]
    return jsonify(result.to_dict(orient="records"))


# --------------------------------------------------
# SINGLE STUDENT
# --------------------------------------------------

@app.route("/api/student/<student_id>")
def student(student_id):
    role = session.get("role")
    logged_in_student = session.get("student_id")

    if role is None:
        return jsonify({"error": "Authentication required"}), 401

    if role == "student" and logged_in_student != student_id:
        return jsonify({"error": "Access denied"}), 403

    if role not in ["student", "management", "admin"]:
        return jsonify({"error": "Access denied"}), 403

    result = df[df["student_id"] == student_id]
    if result.empty:
        return jsonify({"error": "Student not found"}), 404

    row = result.iloc[0]
    return jsonify({
        "student_id": row["student_id"],
        "name": row["name"],
        "department": row["department"],
        "semester": int(row["semester"]),
        "cgpa": row["cgpa"],
        "success_score": row["success_score"],
        "success_category": row["success_category"],
        "overall_risk_level": row["overall_risk_level"],
        "primary_risk_type": row["primary_risk_type"],
        "student_segment": row["student_segment"],
        "risk_drivers": row["risk_drivers"],
        "strengths": None if pd.isna(row["strengths"]) else row["strengths"],
        "recommended_actions": None if pd.isna(row["recommended_actions"]) else row["recommended_actions"],
        "intervention_recommendations": None if pd.isna(row["intervention_recommendations"]) else row["intervention_recommendations"],
    })


# --------------------------------------------------
# TOP STUDENTS
# --------------------------------------------------

@app.route("/api/top-students")
def top_students():
    if not management_required():
        return jsonify({"error": "Access denied"}), 403
    result = df.nlargest(10, "success_score")[[
        "student_id", "name", "department", "success_score", "success_category"
    ]]
    return jsonify(result.to_dict(orient="records"))


# --------------------------------------------------
# AT-RISK STUDENTS
# --------------------------------------------------

@app.route("/api/at-risk")
def at_risk():
    if not management_required():
        return jsonify({"error": "Access denied"}), 403
    result = df[df["overall_risk_level"].isin(["High Risk", "Medium Risk"])].sort_values("success_score")
    result = result[[
        "student_id", "name", "department", "success_score",
        "overall_risk_level", "primary_risk_type", "student_segment"
    ]]
    return jsonify(result.to_dict(orient="records"))


# --------------------------------------------------
# PLACEMENT-UNPREPARED STUDENTS
# --------------------------------------------------

@app.route("/api/placement-unprepared")
def placement_unprepared():
    if not management_required():
        return jsonify({"error": "Access denied"}), 403
    result = df[df["student_segment"] == "Academic Strong / Placement Unprepared"].sort_values("success_score")
    result = result[[
        "student_id", "name", "department", "cgpa", "placement_score",
        "skills_score", "success_score", "student_segment", "intervention_recommendations"
    ]]
    return jsonify(result.to_dict(orient="records"))


# --------------------------------------------------
# SEARCH STUDENTS
# --------------------------------------------------

@app.route("/api/search")
def search():
    if not management_required():
        return jsonify({"error": "Access denied"}), 403

    query = request.args.get("q", "").lower().strip()
    if not query:
        return jsonify([])

    mask = (
        df["student_id"].astype(str).str.lower().str.contains(query, regex=False)
        | df["name"].astype(str).str.lower().str.contains(query, regex=False)
    )
    result = df[mask][[
        "student_id", "name", "department", "success_score",
        "overall_risk_level", "primary_risk_type"
    ]]
    return jsonify(result.to_dict(orient="records"))


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password, role, student_id FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()

    if user is None or not check_password_hash(user[1], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session.clear()
    session["username"] = user[0]
    session["role"] = user[2]
    session["student_id"] = user[3]

    return jsonify({
        "message": "Login successful",
        "username": user[0],
        "role": user[2],
        "student_id": user[3],
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"})


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print("Starting EduPulse AI Backend...")
    app.run(debug=True, host="0.0.0.0", port=port)
