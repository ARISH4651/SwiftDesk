import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./swiftdesk.db")

# SLA Thresholds (in hours)
SLA_HOURS = {
    "High": 2,
    "Medium": 4,
    "Low": 8
}

# AI Confidence Threshold
AI_CONFIDENCE_THRESHOLD = 0.80

# Priority Map
PRIORITY_TO_LEVEL = {
    "Low": "L1",
    "Medium": "L2",
    "High": "L3"
}

# Eligibility Matrix
LEVEL_ELIGIBILITY = {
    "L1": ["Low"],
    "L2": ["Low", "Medium"],
    "L3": ["Low", "Medium", "High"]
}
