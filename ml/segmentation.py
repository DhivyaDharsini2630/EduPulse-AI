import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ============================================================
# LOAD DATA
# ============================================================

input_file = "data/processed/student_explanations.csv"

df = pd.read_csv(input_file)


# ============================================================
# FEATURES USED FOR SEGMENTATION
# ============================================================

features = [
    "academic_score",
    "placement_score",
    "engagement_score",
    "lms_score",
    "skills_score"
]

X = df[features]


# ============================================================
# STANDARDIZE FEATURES
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ============================================================
# K-MEANS CLUSTERING
# ============================================================

kmeans = KMeans(
    n_clusters=5,
    random_state=42,
    n_init=10
)

df["cluster"] = kmeans.fit_predict(X_scaled)


# ============================================================
# ANALYZE CLUSTERS
# ============================================================

cluster_summary = (
    df.groupby("cluster")[features]
    .mean()
    .round(2)
)

print("====================================")
print("Cluster Analysis")
print("====================================")

print(cluster_summary)


# ============================================================
# AUTOMATIC SEGMENT LABELING
# ============================================================

def assign_segment(row):

    academic = row["academic_score"]
    placement = row["placement_score"]
    engagement = row["engagement_score"]
    skills = row["skills_score"]

    # Strong academic performance but weak placement
    if academic >= 70 and placement < 55:
        return "Academic Strong / Placement Unprepared"

    # Strong academics and strong placement
    elif academic >= 70 and placement >= 70:
        return "High Performer"

    # Weak academics
    elif academic < 55:
        return "Academic Support Needed"

    # Adequate academics but weak placement
    elif academic >= 55 and placement < 55:
        return "Placement Support Needed"

    # Low engagement and skills
    elif engagement < 50 and skills < 50:
        return "Overall At Risk"

    else:
        return "Balanced Performer"


df["student_segment"] = df.apply(
    assign_segment,
    axis=1
)


# ============================================================
# SAVE RESULT
# ============================================================

output_file = "data/processed/student_segments.csv"

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n====================================")
print("Student Segmentation created!")
print("====================================")

print("Students:", len(df))

print("\nStudent Segments:")

print(
    df["student_segment"]
    .value_counts()
)


print("\nExample Segment Assignments:")

print(
    df[
        [
            "student_id",
            "name",
            "academic_score",
            "placement_score",
            "skills_score",
            "student_segment"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


print("\nSaved to:")
print(output_file)

print("====================================")