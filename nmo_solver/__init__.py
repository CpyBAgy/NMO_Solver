"""
NMO Solver - Automated solution for NMO tests on Rosminzdrav portal
"""

__version__ = "1.0.0"
__author__ = "Ivan Bashkatov - CpyBAgy"
__email__ = "ibaskatov9@gmail.com"

from .configs import ensure_user_config, ensure_answers_folder, ensure_certificates_folder

# Create necessary folders
ANSWERS_FOLDER = ensure_answers_folder()
CERTIFICATES_FOLDER = ensure_certificates_folder()

# Initialize config file if needed
ensure_user_config()

# Import main components for easier access
from .parser import NmoParser
from .main import main

__all__ = ["NmoParser", "main"]
