import pandas as pd
import numpy as np

# ============================================================
# LOAD DATA
# ============================================================

input_file = "data/processed/student_360.csv"

df = pd.read_csv(input_file)


# ============================================================
# NORMALIZATION FUNCTIONS
# ============================================================

def normalize(value, minimum, maximum):
    """
    Convert a value into a 0-100 scale.
    """
    score = ((value - minimum) / (maximum - minimum)) * 100
    return score.clip(0, 100)


def reverse_normalize(value, minimum, maximum):
    """
    Higher original value = lower score.
    Used for negative indicators such as backlogs.
    """
    score = ((maximum - value) / (maximum - minimum)) * 100
    return score.clip(0, 100)


# ============================================================
# 1. ACADEMIC PERFORMANCE
# ============================================================

cgpa_score = normalize(
    df["cgpa"],
    5,
    10
)

internal_score = normalize(
    df["internal_marks"],
    40,
    100
)

backlog_score = reverse_normalize(
    df["backlogs"],
    0,
    4
)

df["academic_score"] = (
    cgpa_score * 0.50 +
    internal_score * 0.30 +
    backlog_score * 0.20
)


# ============================================================
# 2. ATTENDANCE
# ============================================================

df["attendance_score"] = normalize(
    df["attendance_percentage"],
    50,
    100
)


# ============================================================
# 3. LMS ENGAGEMENT
# ============================================================

login_score = normalize(
    df["login_frequency"],
    1,
    30
)

assignment_score = normalize(
    df["assignment_completion"],
    30,
    100
)

df["lms_score"] = (
    login_score * 0.40 +
    assignment_score * 0.60
)


# ============================================================
# 4. STUDENT ENGAGEMENT
# ============================================================

events_score = normalize(
    df["events"],
    0,
    14
)

clubs_score = normalize(
    df["clubs"],
    0,
    4
)

hackathon_score = normalize(
    df["hackathons"],
    0,
    5
)

df["engagement_score"] = (
    events_score * 0.30 +
    clubs_score * 0.30 +
    hackathon_score * 0.40
)


# ============================================================
# 5. PLACEMENT READINESS
# ============================================================

df["placement_score"] = (
    df["aptitude_score"] * 0.30 +
    df["coding_score"] * 0.40 +
    df["mock_interview_score"] * 0.30
)


# ============================================================
# 6. SKILLS
# ============================================================

df["skills_score"] = (
    df["technical_skill"] * 0.60 +
    df["soft_skill"] * 0.40
)


# ============================================================
# 7. FEEDBACK
# ============================================================

df["feedback_score"] = (
    df["satisfaction"] * 0.50 +
    df["faculty_feedback"] * 0.50
)


# ============================================================
# FINAL STUDENT SUCCESS SCORE
# ============================================================

df["success_score"] = (
    df["academic_score"] * 0.25 +
    df["attendance_score"] * 0.15 +
    df["lms_score"] * 0.15 +
    df["engagement_score"] * 0.10 +
    df["placement_score"] * 0.20 +
    df["skills_score"] * 0.10 +
    df["feedback_score"] * 0.05
)


# Round score
df["success_score"] = df["success_score"].round(2)


# ============================================================
# SUCCESS CATEGORY
# ============================================================

def classify_success(score):

    if score < 40:
        return "Critical"

    elif score < 60:
        return "At Risk"

    elif score < 75:
        return "Moderate"

    elif score < 90:
        return "Good"

    else:
        return "Excellent"


df["success_category"] = df["success_score"].apply(
    classify_success
)


# ============================================================
# SAVE RESULT
# ============================================================

output_file = "data/processed/student_success_scores.csv"

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("====================================")
print("Student Success Score created!")
print("====================================")

print("Students:", len(df))

print("\nAverage Success Score:")
print(round(df["success_score"].mean(), 2))

print("\nSuccess Categories:")
print(df["success_category"].value_counts())

print("\nTop 5 Students:")
print(
    df[
        [
            "student_id",
            "name",
            "success_score",
            "success_category"
        ]
    ]
    .sort_values(
        "success_score",
        ascending=False
    )
    .head(5)
    .to_string(index=False)
)

print("\nSaved to:")
print(output_file)

print("====================================")