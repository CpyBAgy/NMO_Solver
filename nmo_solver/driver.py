"""
Browser driver configuration and utilities.
"""

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver(path_to_profile: str):
    """
    Configure and initialize Chrome WebDriver.

    Args:
        path_to_profile: Path to Chrome user profile directory

    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"--user-data-dir={path_to_profile}")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def get_by(driver: webdriver, by: By, value: str, timeout: int = 10):
    """
    Find an element in the page and wait until it's clickable.

    Args:
        driver: WebDriver instance
        by: Locator type
        value: Locator value
        timeout: Maximum time to wait for the element

    Returns:
        WebElement if found and clickable, None otherwise
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    except TimeoutException:
        return None


def wait_for_url_change(driver: webdriver, current_url: str, timeout: int = 10):
    """
    Wait for the URL to change from the current one.

    Args:
        driver: WebDriver instance
        current_url: Current URL to wait for change
        timeout: Maximum time to wait for URL change

    Returns:
        bool: True if URL changed, False if timeout occurred
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.url_changes(current_url)
        )
        return True
    except TimeoutException:
        return False


def wait_for_new_window(driver: webdriver, current_handles_count: int, timeout: int = 30):
    """
    Wait for a new window or tab to open.

    Args:
        driver: WebDriver instance
        current_handles_count: Current number of window handles
        timeout: Maximum time to wait for new window

    Returns:
        bool: True if new window opened, False if timeout occurred
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.window_handles) > current_handles_count
        )
        return True
    except TimeoutException:
        return False