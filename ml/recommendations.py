import pandas as pd

# Load datasets
risk_df = pd.read_csv(
    "data/processed/student_risk_analysis.csv"
)

explain_df = pd.read_csv(
    "data/processed/student_explanations.csv"
)

segment_df = pd.read_csv(
    "data/processed/student_segments.csv"
)


# Get explanation information
explain_data = explain_df[
    [
        "student_id",
        "risk_drivers",
        "strengths",
        "recommended_actions"
    ]
]


# Get segmentation information
segment_data = segment_df[
    [
        "student_id",
        "student_segment"
    ]
]


# Merge risk + explanation + segmentation
df = risk_df.merge(
    explain_data,
    on="student_id",
    how="left"
)

df = df.merge(
    segment_data,
    on="student_id",
    how="left"
)


# --------------------------------------------------
# RECOMMENDATION ENGINE
# --------------------------------------------------

def generate_recommendations(row):

    recommendations = []

    primary_risk = row["primary_risk_type"]
    segment = row["student_segment"]


    # Academic Risk
    if primary_risk == "Academic Risk":

        recommendations.append(
            "Assign academic mentor"
        )

        recommendations.append(
            "Provide subject-wise remedial support"
        )


    # Placement Risk
    if primary_risk == "Placement Risk":

        recommendations.append(
            "Enroll in coding practice program"
        )

        recommendations.append(
            "Provide aptitude training"
        )

        recommendations.append(
            "Schedule mock interview"
        )


    # Engagement Risk
    if primary_risk == "Engagement Risk":

        recommendations.append(
            "Encourage regular LMS usage"
        )

        recommendations.append(
            "Monitor assignment completion"
        )

        recommendations.append(
            "Encourage participation in campus activities"
        )


    # --------------------------------------------------
    # SEGMENT-SPECIFIC RECOMMENDATIONS
    # --------------------------------------------------

    if segment == "Academic Strong / Placement Unprepared":

        recommendations.append(
            "Create personalized placement preparation plan"
        )

        recommendations.append(
            "Assign placement mentor"
        )


    elif segment == "Placement Support Needed":

        recommendations.append(
            "Increase placement readiness activities"
        )


    elif segment == "Academic Support Needed":

        recommendations.append(
            "Create academic improvement plan"
        )

        recommendations.append(
            "Schedule faculty mentoring"
        )


    elif segment == "Overall At Risk":

        recommendations.append(
            "Assign high-priority student mentor"
        )

        recommendations.append(
            "Create comprehensive intervention plan"
        )


    # Remove duplicates
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    return " | ".join(recommendations)


# Generate recommendations
df["intervention_recommendations"] = df.apply(
    generate_recommendations,
    axis=1
)


# --------------------------------------------------
# PRIORITY
# --------------------------------------------------

def get_priority(row):

    risk_level = row["overall_risk_level"]

    if risk_level == "High Risk":
        return "HIGH"

    elif risk_level == "Medium Risk":
        return "MEDIUM"

    else:
        return "LOW"


df["intervention_priority"] = df.apply(
    get_priority,
    axis=1
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

output_file = (
    "data/processed/student_interventions.csv"
)

df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

print(
    "Intervention recommendation engine completed!"
)

print(
    f"Students processed: {len(df)}"
)

print(
    f"Saved to: {output_file}"
)

print("\nSample recommendations:")

print(
    df[
        [
            "student_id",
            "primary_risk_type",
            "student_segment",
            "intervention_priority",
            "intervention_recommendations"
        ]
    ]
    .head(10)
    .to_string(index=False)
)