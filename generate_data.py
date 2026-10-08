import pandas as pd
import numpy as np
import os

# Reproducible dataset
np.random.seed(42)

# Number of students
NUM_STUDENTS = 500

# Create folders
os.makedirs("data/raw", exist_ok=True)

# Student IDs
student_ids = [f"STU{i:03d}" for i in range(1, NUM_STUDENTS + 1)]

# ============================================================
# 1. STUDENTS
# ============================================================

names = [f"Student_{i:03d}" for i in range(1, NUM_STUDENTS + 1)]

departments = np.random.choice(
    ["AIML", "CSE", "ECE", "EEE", "IT"],
    NUM_STUDENTS
)

semesters = np.random.choice(
    [3, 4, 5, 6, 7, 8],
    NUM_STUDENTS
)

students = pd.DataFrame({
    "student_id": student_ids,
    "name": names,
    "department": departments,
    "semester": semesters
})

students.to_csv("data/raw/students.csv", index=False)


# ============================================================
# 2. BASE STUDENT PROFILE
# ============================================================

# A latent overall performance factor creates realistic
# relationships between different campus indicators.

profile = np.random.normal(0, 1, NUM_STUDENTS)

# Keep values in a reasonable range
profile = np.clip(profile, -2.5, 2.5)

# Convert profile into a 0-100 base performance
base = 70 + (profile * 12) + np.random.normal(0, 5, NUM_STUDENTS)
base = np.clip(base, 35, 98)


# ============================================================
# 3. ACADEMICS
# ============================================================

cgpa = np.clip(
    5.5 + (base - 35) / 63 * 4.2 + np.random.normal(0, 0.35, NUM_STUDENTS),
    5.0,
    10.0
)

cgpa = np.round(cgpa, 2)

internal_marks = np.clip(
    base + np.random.normal(0, 7, NUM_STUDENTS),
    40,
    100
)

internal_marks = np.round(internal_marks, 2)

# Backlogs are more likely when academic performance is low
backlog_probability = np.clip(
    (75 - base) / 35,
    0,
    0.85
)

backlogs = np.random.binomial(4, backlog_probability)

academics = pd.DataFrame({
    "student_id": student_ids,
    "cgpa": cgpa,
    "internal_marks": internal_marks,
    "backlogs": backlogs
})

academics.to_csv("data/raw/academics.csv", index=False)


# ============================================================
# 4. ATTENDANCE
# ============================================================

attendance_percentage = np.clip(
    base + np.random.normal(0, 9, NUM_STUDENTS),
    50,
    100
)

attendance_percentage = np.round(
    attendance_percentage,
    2
)

attendance = pd.DataFrame({
    "student_id": student_ids,
    "attendance_percentage": attendance_percentage
})

attendance.to_csv(
    "data/raw/attendance.csv",
    index=False
)


# ============================================================
# 5. LMS
# ============================================================

login_frequency = np.clip(
    (base / 3) + np.random.normal(0, 5, NUM_STUDENTS),
    1,
    30
)

login_frequency = np.round(login_frequency).astype(int)

assignment_completion = np.clip(
    base + np.random.normal(0, 10, NUM_STUDENTS),
    30,
    100
)

assignment_completion = np.round(
    assignment_completion,
    2
)

lms = pd.DataFrame({
    "student_id": student_ids,
    "login_frequency": login_frequency,
    "assignment_completion": assignment_completion
})

lms.to_csv(
    "data/raw/lms.csv",
    index=False
)


# ============================================================
# 6. ENGAGEMENT
# ============================================================

events = np.clip(
    np.round((base - 30) / 5 + np.random.normal(0, 2.5, NUM_STUDENTS)),
    0,
    14
).astype(int)

clubs = np.clip(
    np.round((base - 45) / 15 + np.random.normal(0, 1, NUM_STUDENTS)),
    0,
    4
).astype(int)

hackathons = np.clip(
    np.round((base - 50) / 12 + np.random.normal(0, 1.2, NUM_STUDENTS)),
    0,
    5
).astype(int)

engagement = pd.DataFrame({
    "student_id": student_ids,
    "events": events,
    "clubs": clubs,
    "hackathons": hackathons
})

engagement.to_csv(
    "data/raw/engagement.csv",
    index=False
)


# ============================================================
# 7. PLACEMENT
# ============================================================

aptitude_score = np.clip(
    base + np.random.normal(0, 12, NUM_STUDENTS),
    20,
    100
)

coding_score = np.clip(
    base + np.random.normal(0, 15, NUM_STUDENTS),
    20,
    100
)

mock_interview_score = np.clip(
    base + np.random.normal(0, 14, NUM_STUDENTS),
    20,
    100
)

aptitude_score = np.round(aptitude_score, 2)
coding_score = np.round(coding_score, 2)
mock_interview_score = np.round(mock_interview_score, 2)


# ============================================================
# SPECIAL DEMO GROUP
# ============================================================
# Create students who are academically strong but
# placement-unprepared.
#
# This is an important EduPulse AI demonstration scenario.

demo_ids = np.arange(0, 30)

cgpa[demo_ids] = np.round(
    np.random.uniform(8.5, 9.8, len(demo_ids)),
    2
)

internal_marks[demo_ids] = np.round(
    np.random.uniform(78, 98, len(demo_ids)),
    2
)

backlogs[demo_ids] = np.random.choice(
    [0, 0, 0, 1],
    len(demo_ids)
)

attendance_percentage[demo_ids] = np.round(
    np.random.uniform(80, 98, len(demo_ids)),
    2
)

aptitude_score[demo_ids] = np.round(
    np.random.uniform(25, 50, len(demo_ids)),
    2
)

coding_score[demo_ids] = np.round(
    np.random.uniform(20, 48, len(demo_ids)),
    2
)

mock_interview_score[demo_ids] = np.round(
    np.random.uniform(25, 50, len(demo_ids)),
    2
)


placement = pd.DataFrame({
    "student_id": student_ids,
    "aptitude_score": aptitude_score,
    "coding_score": coding_score,
    "mock_interview_score": mock_interview_score
})

placement.to_csv(
    "data/raw/placement.csv",
    index=False
)


# ============================================================
# 8. SKILLS
# ============================================================

technical_skill = np.clip(
    base + np.random.normal(0, 14, NUM_STUDENTS),
    30,
    100
)

soft_skill = np.clip(
    base + np.random.normal(0, 12, NUM_STUDENTS),
    30,
    100
)

technical_skill = np.round(
    technical_skill,
    2
)

soft_skill = np.round(
    soft_skill,
    2
)

# Make demo group technically less placement-ready
technical_skill[demo_ids] = np.round(
    np.random.uniform(35, 55, len(demo_ids)),
    2
)

soft_skill[demo_ids] = np.round(
    np.random.uniform(45, 70, len(demo_ids)),
    2
)

skills = pd.DataFrame({
    "student_id": student_ids,
    "technical_skill": technical_skill,
    "soft_skill": soft_skill
})

skills.to_csv(
    "data/raw/skills.csv",
    index=False
)


# ============================================================
# 9. FEEDBACK
# ============================================================

satisfaction = np.clip(
    base + np.random.normal(0, 10, NUM_STUDENTS),
    40,
    100
)

faculty_feedback = np.clip(
    base + np.random.normal(0, 10, NUM_STUDENTS),
    40,
    100
)

satisfaction = np.round(
    satisfaction,
    2
)

faculty_feedback = np.round(
    faculty_feedback,
    2
)

feedback = pd.DataFrame({
    "student_id": student_ids,
    "satisfaction": satisfaction,
    "faculty_feedback": faculty_feedback
})

feedback.to_csv(
    "data/raw/feedback.csv",
    index=False
)


# ============================================================
# FINISHED
# ============================================================

print("====================================")
print("EduPulse AI dataset created!")
print("Students:", NUM_STUDENTS)
print("====================================")