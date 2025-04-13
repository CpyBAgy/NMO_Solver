"""
Configurations for the NMO solver.
"""

from .config_init import ensure_user_config, ensure_answers_folder, ensure_certificates_folder

ensure_user_config()

from .user_config import USERNAME, PASSWORD, EMAIL, PATH_TO_CHROME_PROFILE
from .config import LOGIN_URL, EXPECTED_REDIRECT_URL, SEARCH_BASE_URL, CERTIFICATES_FOLDER, ANSWERS_FOLDER, WAIT_TIMEOUT, PAGE_LOAD_TIMEOUT, ELEMENT_WAIT_TIMEOUT

__all__ = [
    "ensure_user_config",
    "ensure_answers_folder",
    "ensure_certificates_folder",
    "USERNAME",
    "PASSWORD",
    "EMAIL",
    "PATH_TO_CHROME_PROFILE",
    "LOGIN_URL",
    "EXPECTED_REDIRECT_URL",
    "SEARCH_BASE_URL",
    "CERTIFICATES_FOLDER",
    "ANSWERS_FOLDER",
    "WAIT_TIMEOUT",
    "PAGE_LOAD_TIMEOUT",
    "ELEMENT_WAIT_TIMEOUT"
]