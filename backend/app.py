import os
import sqlite3
import pandas as pd
from flask import Flask, jsonify, request, session, send_from_directory, redirect
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
import math
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

@app.route("/add-student.html")
def add_student_page():
    if not management_required():
        return redirect("/login.html")
    return send_from_directory(FRONTEND_DIR, "add-student.html")


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
# ADD STUDENT
# --------------------------------------------------

@app.route("/api/students", methods=["POST"])
def create_student():
    global df

    if not management_required():
        return jsonify({"error": "Access denied"}), 403

    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    department = str(payload.get("department", "")).strip().upper()
    if not name:
        return jsonify({"error": "Student name is required"}), 400
    if len(name) > 100:
        return jsonify({"error": "Student name must be 100 characters or fewer"}), 400
    if department not in {"AIML", "CSE", "ECE", "EEE", "IT"}:
        return jsonify({"error": "Choose a valid department"}), 400

    # Validate all numeric fields and constrain them to sensible input ranges.
    numeric_specs = {
        "semester": (1, 8, True), "cgpa": (0, 10, False),
        "internal_marks": (0, 100, False), "backlogs": (0, 4, True),
        "attendance_percentage": (0, 100, False), "login_frequency": (0, 30, True),
        "assignment_completion": (0, 100, False), "events": (0, 14, True),
        "clubs": (0, 4, True), "hackathons": (0, 5, True),
        "aptitude_score": (0, 100, False), "coding_score": (0, 100, False),
        "mock_interview_score": (0, 100, False), "technical_skill": (0, 100, False),
        "soft_skill": (0, 100, False), "satisfaction": (0, 100, False),
        "faculty_feedback": (0, 100, False),
    }
    values = {}
    for field, (minimum, maximum, is_integer) in numeric_specs.items():
        try:
            value = float(payload[field])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": f"Enter a valid value for {field.replace('_', ' ')}"}), 400
        if not math.isfinite(value) or value < minimum or value > maximum:
            return jsonify({"error": f"{field.replace('_', ' ').capitalize()} must be between {minimum} and {maximum}"}), 400
        values[field] = int(value) if is_integer else value

    # Generate the next student ID from the current integrated dataset.
    ids = df["student_id"].astype(str).str.extract(r"STU(\d+)$", expand=False).dropna()
    next_number = int(ids.astype(int).max()) + 1 if not ids.empty else 1
    student_id = f"STU{next_number:03d}"
    username = "student" + student_id.replace("STU", "")
    default_password = "student123"

    def normalize(value, minimum, maximum):
        return max(0.0, min(100.0, ((value - minimum) / (maximum - minimum)) * 100))

    def reverse_normalize(value, minimum, maximum):
        return max(0.0, min(100.0, ((maximum - value) / (maximum - minimum)) * 100))

    # Reuse the project's current Student Success Score weights.
    academic_score = (
        normalize(values["cgpa"], 5, 10) * 0.50
        + normalize(values["internal_marks"], 40, 100) * 0.30
        + reverse_normalize(values["backlogs"], 0, 4) * 0.20
    )
    attendance_score = normalize(values["attendance_percentage"], 50, 100)
    lms_score = normalize(values["login_frequency"], 1, 30) * 0.40 + normalize(values["assignment_completion"], 30, 100) * 0.60
    engagement_score = normalize(values["events"], 0, 14) * 0.30 + normalize(values["clubs"], 0, 4) * 0.30 + normalize(values["hackathons"], 0, 5) * 0.40
    placement_score = values["aptitude_score"] * 0.30 + values["coding_score"] * 0.40 + values["mock_interview_score"] * 0.30
    skills_score = values["technical_skill"] * 0.60 + values["soft_skill"] * 0.40
    feedback_score = values["satisfaction"] * 0.50 + values["faculty_feedback"] * 0.50

    academic_score, attendance_score, lms_score, engagement_score = [round(x, 2) for x in (academic_score, attendance_score, lms_score, engagement_score)]
    placement_score, skills_score, feedback_score = [round(x, 2) for x in (placement_score, skills_score, feedback_score)]
    success_score = round(academic_score * 0.25 + attendance_score * 0.15 + lms_score * 0.15 + engagement_score * 0.10 + placement_score * 0.20 + skills_score * 0.10 + feedback_score * 0.05, 2)

    def success_category(score):
        if score < 40: return "Critical"
        if score < 60: return "At Risk"
        if score < 75: return "Moderate"
        if score < 90: return "Good"
        return "Excellent"

    academic_risk_score = round((100 - academic_score) * 0.60 + (100 - attendance_score) * 0.40, 2)
    placement_risk_score = round((100 - placement_score) * 0.70 + (100 - skills_score) * 0.30, 2)
    engagement_risk_score = round((100 - lms_score) * 0.60 + (100 - engagement_score) * 0.40, 2)

    def risk_level(score):
        if score >= 70: return "High Risk"
        if score >= 40: return "Medium Risk"
        return "Low Risk"

    risk_scores = {"Academic Risk": academic_risk_score, "Placement Risk": placement_risk_score, "Engagement Risk": engagement_risk_score}
    primary_risk_type = max(risk_scores, key=risk_scores.get)
    overall_risk_score = round(academic_risk_score * 0.40 + placement_risk_score * 0.40 + engagement_risk_score * 0.20, 2)
    overall_risk_level = risk_level(overall_risk_score)

    if academic_score >= 70 and placement_score < 55:
        student_segment = "Academic Strong / Placement Unprepared"
    elif academic_score >= 70 and placement_score >= 70:
        student_segment = "High Performer"
    elif academic_score < 55:
        student_segment = "Academic Support Needed"
    elif academic_score >= 55 and placement_score < 55:
        student_segment = "Placement Support Needed"
    elif engagement_score < 50 and skills_score < 50:
        student_segment = "Overall At Risk"
    else:
        student_segment = "Balanced Performer"

    drivers, strengths, actions = [], [], []
    if values["cgpa"] < 6.5:
        drivers.append(f"Low CGPA ({values['cgpa']:.2f})")
        actions.append("Provide academic mentoring and subject support")
    elif values["cgpa"] >= 8.5:
        strengths.append(f"Strong CGPA ({values['cgpa']:.2f})")
    if values["backlogs"] >= 2:
        drivers.append(f"{values['backlogs']} active backlogs")
        actions.append("Provide backlog clearance support")
    if values["attendance_percentage"] < 65:
        drivers.append(f"Low attendance ({values['attendance_percentage']:.1f}%)")
        actions.append("Attendance monitoring and faculty follow-up")
    if values["aptitude_score"] < 50:
        drivers.append(f"Low aptitude score ({values['aptitude_score']:.1f})")
        actions.append("Aptitude training and practice tests")
    if values["coding_score"] < 50:
        drivers.append(f"Low coding score ({values['coding_score']:.1f})")
        actions.append("Structured coding practice")
    if values["mock_interview_score"] < 50:
        drivers.append(f"Low mock interview score ({values['mock_interview_score']:.1f})")
        actions.append("Mock interview and communication practice")
    if values["assignment_completion"] < 60:
        drivers.append(f"Low assignment completion ({values['assignment_completion']:.1f}%)")
        actions.append("Assignment completion monitoring")
    if values["login_frequency"] < 8:
        drivers.append(f"Low LMS activity ({values['login_frequency']} logins)")
        actions.append("Encourage regular LMS participation")
    if values["events"] <= 2 and values["clubs"] == 0 and values["hackathons"] == 0:
        drivers.append("Low extracurricular engagement")
        actions.append("Encourage participation in clubs, events or hackathons")
    if values["technical_skill"] < 50:
        drivers.append(f"Low technical skill score ({values['technical_skill']:.1f})")
        actions.append("Technical skill development program")
    if values["soft_skill"] < 50:
        drivers.append(f"Low soft skill score ({values['soft_skill']:.1f})")
        actions.append("Communication and soft-skill training")
    if not drivers:
        drivers.append("No major weakness detected across monitored indicators")
    if not strengths and values["internal_marks"] >= 75:
        strengths.append(f"Good internal marks ({values['internal_marks']:.1f})")
    if not actions:
        actions.append("Continue current performance and engagement")

    interventions = []
    if primary_risk_type == "Academic Risk": interventions.extend(["Assign academic mentor", "Provide subject-wise remedial support"])
    if primary_risk_type == "Placement Risk": interventions.extend(["Enroll in coding practice program", "Provide aptitude training", "Schedule mock interview"])
    if primary_risk_type == "Engagement Risk": interventions.extend(["Encourage regular LMS usage", "Monitor assignment completion", "Encourage participation in campus activities"])
    if student_segment == "Academic Strong / Placement Unprepared": interventions.extend(["Create personalized placement preparation plan", "Assign placement mentor"])
    elif student_segment == "Placement Support Needed": interventions.append("Increase placement readiness activities")
    elif student_segment == "Academic Support Needed": interventions.extend(["Create academic improvement plan", "Schedule faculty mentoring"])
    elif student_segment == "Overall At Risk": interventions.extend(["Assign high-priority student mentor", "Create comprehensive intervention plan"])
    interventions = list(dict.fromkeys(interventions))

    new_row = {
        "student_id": student_id, "name": name, "department": department, "semester": values["semester"], **values,
        "academic_score": academic_score, "attendance_score": attendance_score, "lms_score": lms_score,
        "engagement_score": engagement_score, "placement_score": placement_score, "skills_score": skills_score,
        "feedback_score": feedback_score, "success_score": success_score, "success_category": success_category(success_score),
        "academic_risk_score": academic_risk_score, "placement_risk_score": placement_risk_score,
        "engagement_risk_score": engagement_risk_score, "academic_risk": risk_level(academic_risk_score),
        "placement_risk": risk_level(placement_risk_score), "engagement_risk": risk_level(engagement_risk_score),
        "primary_risk_type": primary_risk_type, "overall_risk_score": overall_risk_score,
        "overall_risk_level": overall_risk_level, "risk_drivers": " | ".join(drivers), "strengths": " | ".join(strengths),
        "recommended_actions": " | ".join(actions), "student_segment": student_segment,
        "intervention_recommendations": " | ".join(interventions), "intervention_priority": overall_risk_level.split()[0].upper(),
    }

    # Add the source-level record to each CSV used by the integration pipeline.
    raw_updates = {
        "data/raw/students.csv": {"student_id": student_id, "name": name, "department": department, "semester": values["semester"]},
        "data/raw/academics.csv": {"student_id": student_id, **{k: values[k] for k in ("cgpa", "internal_marks", "backlogs")}},
        "data/raw/attendance.csv": {"student_id": student_id, "attendance_percentage": values["attendance_percentage"]},
        "data/raw/lms.csv": {"student_id": student_id, **{k: values[k] for k in ("login_frequency", "assignment_completion")}},
        "data/raw/engagement.csv": {"student_id": student_id, **{k: values[k] for k in ("events", "clubs", "hackathons")}},
        "data/raw/placement.csv": {"student_id": student_id, **{k: values[k] for k in ("aptitude_score", "coding_score", "mock_interview_score")}},
        "data/raw/skills.csv": {"student_id": student_id, **{k: values[k] for k in ("technical_skill", "soft_skill")}},
        "data/raw/feedback.csv": {"student_id": student_id, **{k: values[k] for k in ("satisfaction", "faculty_feedback")}},
        "data/processed/student_360.csv": new_row,
        "data/processed/student_success_scores.csv": new_row,
        "data/processed/student_risk_analysis.csv": new_row,
        "data/processed/student_explanations.csv": new_row,
        "data/processed/student_segments.csv": new_row,
    }

    # Create the login account before writing CSVs so duplicate usernames fail early.
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role, student_id) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(default_password), "student", student_id),
        )
        conn.commit()
        conn.close()
        conn = None

        for relative_path, row_values in raw_updates.items():
            csv_path = os.path.join(PROJECT_ROOT, relative_path)
            if not os.path.exists(csv_path):
                continue
            existing = pd.read_csv(csv_path)
            if "student_id" in existing.columns and (existing["student_id"].astype(str) == student_id).any():
                continue
            record = {column: row_values.get(column, None) for column in existing.columns}
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
            updated.to_csv(csv_path, index=False)

        df = pd.concat([df, pd.DataFrame([{column: new_row.get(column, None) for column in df.columns}])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
    except sqlite3.IntegrityError:
        if conn:
            conn.close()
        app.logger.exception("Unable to create student account")
        return jsonify({"error": "The generated student account already exists. Please submit again."}), 409
    except Exception:
        if conn:
            conn.close()
        app.logger.exception("Unable to create student record")
        return jsonify({"error": "Unable to save the student. Please try again or check the server logs."}), 500

    return jsonify({
        "message": "Student created successfully", "student_id": student_id,
        "username": username, "default_password": default_password,
        "success_score": success_score, "overall_risk_level": overall_risk_level,
        "student_segment": student_segment,
    }), 201


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
