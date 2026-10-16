from enum import Enum


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    SELECTED = "selected"
    REJECTED = "rejected"
