"""
Configuration settings for the NMO Solver application.
"""

# URLs
LOGIN_URL = "https://a.edu.rosminzdrav.ru/idp/login.html?response_type=client-ticket&sp=https%3A%2F%2Fnmfo-vo.edu.rosminzdrav.ru%2F%23%2Flogin%2F"
EXPECTED_REDIRECT_URL = "https://iom-vo.edu.rosminzdrav.ru/#!"

# Search settings
SEARCH_BASE_URL = "https://24forcare.com"

# File paths
CERTIFICATES_FOLDER = "certificates/"
ANSWERS_FOLDER = "answers/"

# Timeouts (in seconds)
WAIT_TIMEOUT = 10
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 3