import pandas as pd
import numpy as np

# ============================================================
# LOAD SUCCESS SCORE DATA
# ============================================================

input_file = "data/processed/student_success_scores.csv"

df = pd.read_csv(input_file)


# ============================================================
# 1. ACADEMIC RISK
# ============================================================

academic_risk = (
    (100 - df["academic_score"]) * 0.60
    + (100 - df["attendance_score"]) * 0.40
)

df["academic_risk_score"] = academic_risk.round(2)


# ============================================================
# 2. PLACEMENT RISK
# ============================================================

placement_risk = (
    (100 - df["placement_score"]) * 0.70
    + (100 - df["skills_score"]) * 0.30
)

df["placement_risk_score"] = placement_risk.round(2)


# ============================================================
# 3. ENGAGEMENT RISK
# ============================================================

engagement_risk = (
    (100 - df["lms_score"]) * 0.60
    + (100 - df["engagement_score"]) * 0.40
)

df["engagement_risk_score"] = engagement_risk.round(2)


# ============================================================
# RISK LEVEL FUNCTION
# ============================================================

def risk_level(score):

    if score >= 70:
        return "High Risk"

    elif score >= 40:
        return "Medium Risk"

    else:
        return "Low Risk"


# Apply risk levels

df["academic_risk"] = df["academic_risk_score"].apply(
    risk_level
)

df["placement_risk"] = df["placement_risk_score"].apply(
    risk_level
)

df["engagement_risk"] = df["engagement_risk_score"].apply(
    risk_level
)


# ============================================================
# PRIMARY RISK TYPE
# ============================================================

risk_columns = [
    "academic_risk_score",
    "placement_risk_score",
    "engagement_risk_score"
]

df["primary_risk_type"] = (
    df[risk_columns]
    .idxmax(axis=1)
    .str.replace("_risk_score", "", regex=False)
    .str.title()
    + " Risk"
)


# ============================================================
# OVERALL RISK SCORE
# ============================================================

df["overall_risk_score"] = (
    df["academic_risk_score"] * 0.40
    + df["placement_risk_score"] * 0.40
    + df["engagement_risk_score"] * 0.20
).round(2)


df["overall_risk_level"] = df["overall_risk_score"].apply(
    risk_level
)


# ============================================================
# SAVE RESULT
# ============================================================

output_file = "data/processed/student_risk_analysis.csv"

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("====================================")
print("Student Risk Analysis created!")
print("====================================")

print("Students:", len(df))

print("\nOverall Risk Levels:")
print(
    df["overall_risk_level"].value_counts()
)

print("\nRisk Types:")
print(
    df["primary_risk_type"].value_counts()
)

print("\nSample Risk Analysis:")

print(
    df[
        [
            "student_id",
            "name",
            "success_score",
            "academic_risk",
            "placement_risk",
            "engagement_risk",
            "primary_risk_type",
            "overall_risk_level"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nSaved to:")
print(output_file)

print("====================================")