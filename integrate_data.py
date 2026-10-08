import pandas as pd
import os

# Folder locations
raw_path = "data/raw"
processed_path = "data/processed"

# Make sure processed folder exists
os.makedirs(processed_path, exist_ok=True)

# ---------------------------------------------------
# LOAD ALL DATA SOURCES
# ---------------------------------------------------

students = pd.read_csv(f"{raw_path}/students.csv")
academics = pd.read_csv(f"{raw_path}/academics.csv")
attendance = pd.read_csv(f"{raw_path}/attendance.csv")
lms = pd.read_csv(f"{raw_path}/lms.csv")
engagement = pd.read_csv(f"{raw_path}/engagement.csv")
placement = pd.read_csv(f"{raw_path}/placement.csv")
skills = pd.read_csv(f"{raw_path}/skills.csv")
feedback = pd.read_csv(f"{raw_path}/feedback.csv")

# ---------------------------------------------------
# MERGE ALL DATA USING STUDENT ID
# ---------------------------------------------------

student_360 = students.merge(
    academics, on="student_id", how="left"
)

student_360 = student_360.merge(
    attendance, on="student_id", how="left"
)

student_360 = student_360.merge(
    lms, on="student_id", how="left"
)

student_360 = student_360.merge(
    engagement, on="student_id", how="left"
)

student_360 = student_360.merge(
    placement, on="student_id", how="left"
)

student_360 = student_360.merge(
    skills, on="student_id", how="left"
)

student_360 = student_360.merge(
    feedback, on="student_id", how="left"
)

# ---------------------------------------------------
# SAVE UNIFIED DATASET
# ---------------------------------------------------

output_file = f"{processed_path}/student_360.csv"

student_360.to_csv(
    output_file,
    index=False
)

# ---------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------

print("====================================")
print("Student 360 dataset created!")
print("====================================")

print("Number of students:", len(student_360))
print("Number of features:", len(student_360.columns))

print("\nColumns:")
print(list(student_360.columns))

print("\nMissing values:")
print(student_360.isnull().sum().sum())

print("\nSaved to:")
print(output_file)

print("====================================")