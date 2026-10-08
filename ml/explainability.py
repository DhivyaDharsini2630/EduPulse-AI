import pandas as pd

# ============================================================
# LOAD RISK ANALYSIS DATA
# ============================================================

input_file = "data/processed/student_risk_analysis.csv"

df = pd.read_csv(input_file)


# ============================================================
# EXPLANATION FUNCTION
# ============================================================

def generate_explanation(row):

    reasons = []
    strengths = []
    recommendations = []

    # --------------------------------------------------------
    # ACADEMIC FACTORS
    # --------------------------------------------------------

    if row["cgpa"] < 6.5:
        reasons.append(
            f"Low CGPA ({row['cgpa']:.2f})"
        )
        recommendations.append(
            "Provide academic mentoring and subject support"
        )

    elif row["cgpa"] >= 8.5:
        strengths.append(
            f"Strong CGPA ({row['cgpa']:.2f})"
        )

    if row["backlogs"] >= 2:
        reasons.append(
            f"{int(row['backlogs'])} active backlogs"
        )
        recommendations.append(
            "Provide backlog clearance support"
        )

    if row["attendance_percentage"] < 65:
        reasons.append(
            f"Low attendance ({row['attendance_percentage']:.1f}%)"
        )
        recommendations.append(
            "Attendance monitoring and faculty follow-up"
        )

    # --------------------------------------------------------
    # PLACEMENT FACTORS
    # --------------------------------------------------------

    if row["aptitude_score"] < 50:
        reasons.append(
            f"Low aptitude score ({row['aptitude_score']:.1f})"
        )
        recommendations.append(
            "Aptitude training and practice tests"
        )

    if row["coding_score"] < 50:
        reasons.append(
            f"Low coding score ({row['coding_score']:.1f})"
        )
        recommendations.append(
            "Structured coding practice"
        )

    if row["mock_interview_score"] < 50:
        reasons.append(
            f"Low mock interview score ({row['mock_interview_score']:.1f})"
        )
        recommendations.append(
            "Mock interview and communication practice"
        )

    # --------------------------------------------------------
    # LMS FACTORS
    # --------------------------------------------------------

    if row["assignment_completion"] < 60:
        reasons.append(
            f"Low assignment completion ({row['assignment_completion']:.1f}%)"
        )
        recommendations.append(
            "Assignment completion monitoring"
        )

    if row["login_frequency"] < 8:
        reasons.append(
            f"Low LMS activity ({int(row['login_frequency'])} logins)"
        )
        recommendations.append(
            "Encourage regular LMS participation"
        )

    # --------------------------------------------------------
    # ENGAGEMENT FACTORS
    # --------------------------------------------------------

    if (
        row["events"] <= 2
        and row["clubs"] == 0
        and row["hackathons"] == 0
    ):
        reasons.append(
            "Low extracurricular engagement"
        )
        recommendations.append(
            "Encourage participation in clubs, events or hackathons"
        )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    if row["technical_skill"] < 50:
        reasons.append(
            f"Low technical skill score ({row['technical_skill']:.1f})"
        )
        recommendations.append(
            "Technical skill development program"
        )

    if row["soft_skill"] < 50:
        reasons.append(
            f"Low soft skill score ({row['soft_skill']:.1f})"
        )
        recommendations.append(
            "Communication and soft-skill training"
        )

    # --------------------------------------------------------
    # IF NO SPECIFIC WEAKNESS IS FOUND
    # --------------------------------------------------------

    if not reasons:
        reasons.append(
            "No major weakness detected across monitored indicators"
        )

    if not strengths:
        if row["internal_marks"] >= 75:
            strengths.append(
                f"Good internal marks ({row['internal_marks']:.1f})"
            )

    if not recommendations:
        recommendations.append(
            "Continue current performance and engagement"
        )

    return (
        " | ".join(reasons),
        " | ".join(strengths),
        " | ".join(recommendations)
    )


# ============================================================
# GENERATE EXPLANATIONS
# ============================================================

results = df.apply(
    generate_explanation,
    axis=1
)

df["risk_drivers"] = results.apply(
    lambda x: x[0]
)

df["strengths"] = results.apply(
    lambda x: x[1]
)

df["recommended_actions"] = results.apply(
    lambda x: x[2]
)


# ============================================================
# SAVE RESULT
# ============================================================

output_file = "data/processed/student_explanations.csv"

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY EXAMPLES
# ============================================================

print("====================================")
print("Explainability Engine created!")
print("====================================")

print("Students:", len(df))

print("\nExample Student Explanations:")

print(
    df[
        [
            "student_id",
            "success_score",
            "primary_risk_type",
            "risk_drivers",
            "strengths",
            "recommended_actions"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nSaved to:")
print(output_file)

print("====================================")