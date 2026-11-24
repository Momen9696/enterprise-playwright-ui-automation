"""Limits and labels shared by the demo application and the tests."""

PAGE_SIZE = 5
TITLE_MAX = 120
DESCRIPTION_MAX = 500
NAME_MAX = 80
PASSWORD_MIN = 8
PASSWORD_MAX = 128

STATUSES = ("open", "in_progress", "done")
PRIORITIES = ("low", "medium", "high")

STATUS_LABELS = {
    "open": "Open",
    "in_progress": "In progress",
    "done": "Done",
}
PRIORITY_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
}

EMAIL_REQUIRED = "Email is required."
EMAIL_INVALID = "Enter a valid email address."
PASSWORD_REQUIRED = "Password is required."
PASSWORD_RULE = "Password must be at least 8 characters and include a letter and a digit."
PASSWORD_MISMATCH = "Passwords do not match."
CREDENTIALS = "Email or password is incorrect."
NAME_REQUIRED = "Name is required."
NAME_LONG = "Name must be at most 80 characters."
TITLE_REQUIRED = "Title is required."
TITLE_LONG = "Title must be at most 120 characters."
DESCRIPTION_LONG = "Description must be at most 500 characters."
STATUS_INVALID = "Choose a valid status."
PRIORITY_INVALID = "Choose a valid priority."
EMAIL_TAKEN = "An account with this email already exists."
CSRF_FAIL = "The form expired. Refresh the page and try again."
FORBIDDEN_TEXT = "You do not have access to this page."

NOTICES = {
    "auth_required": "Sign in to continue.",
    "session_expired": "Your session expired. Sign in again.",
    "logged_out": "You have logged out.",
    "welcome": "Account created.",
    "created": "Item created.",
    "saved": "Changes saved.",
    "deleted": "Item deleted.",
    "profile_saved": "Profile saved.",
}
