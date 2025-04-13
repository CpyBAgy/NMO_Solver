"""
Helper functions for the NMO solver.
"""

import os
import time
import itertools
from selenium.webdriver.common.by import By


def wait_for_redirect(driver, expected_url, timeout=30):
    """
    Wait for page to redirect to an expected URL.

    Args:
        driver: WebDriver instance
        expected_url: Expected URL or URL part
        timeout: Timeout in seconds

    Returns:
        bool: True if redirected to expected URL, False otherwise
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if expected_url in driver.current_url:
            return True
        time.sleep(0.5)
    return False


def select_answers(driver, answers, question_type):
    """
    Select answers for the current question.

    Args:
        driver: WebDriver instance
        answers: List of answers to select
        question_type: Type of question ("ОДИН" or "НЕСК")

    Returns:
        bool: True if answers were selected, False otherwise
    """
    if "НЕСК" in question_type:
        answer_options = driver.find_elements(By.XPATH,
                                              "//mat-checkbox[contains(@class, 'mat-mdc-checkbox')]")
        for option in answer_options:
            answer_text = option.find_element(By.XPATH,
                                              ".//span[contains(@class, 'question-inner-html-text')]").text.strip()
            if answer_text in answers:
                driver.execute_script("arguments[0].scrollIntoView(true);", option)
                time.sleep(0.5)
                checkbox = option.find_element(By.XPATH, ".//input[@type='checkbox']")
                if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.5)
    else:
        answer_options = driver.find_elements(By.XPATH,
                                              "//mat-radio-button[contains(@class, 'mat-mdc-radio-button')]")
        for option in answer_options:
            answer_text = option.find_element(By.XPATH,
                                              ".//span[contains(@class, 'question-inner-html-text')]").text.strip()
            if answer_text in answers:
                driver.execute_script("arguments[0].scrollIntoView(true);", option)
                time.sleep(0.5)
                radio_button = option.find_element(By.XPATH, ".//input[@type='radio']")
                driver.execute_script("arguments[0].click();", radio_button)
                time.sleep(0.5)
                break


def generate_answer_combinations(total_questions, question_key, iteration, max_combinations=None):
    """
    Generate combinations of answers for a question.

    Args:
        total_questions: Dictionary of all questions
        question_key: Key of the question to generate combinations for
        iteration: Current iteration number
        max_combinations: Maximum number of combinations to generate

    Returns:
        list: Selected answer indices
    """
    question = total_questions[question_key]
    q_answers = question.answers
    q_amount = len(q_answers)

    # Generate combinations
    all_combinations = []
    if question.type == "НЕСК":
        # For multiple choice questions, generate combinations of 2 to n answers
        for r in range(2, q_amount + 1):
            for combo in itertools.combinations(range(q_amount), r):
                all_combinations.append(list(combo))
    else:
        # For single choice questions, just iterate through all answers
        all_combinations = [[i] for i in range(q_amount)]

    # If max_combinations is specified, limit the number of combinations
    if max_combinations and len(all_combinations) > max_combinations:
        all_combinations = all_combinations[:max_combinations]

    # Return the combination for the current iteration, cycling if needed
    if all_combinations:
        return all_combinations[iteration % len(all_combinations)]
    return []


def save_failed_tests(test_name, url):
        """
        Update the list of failed tests in a user-friendly Markdown format.

        Args:
            test_name: Name of the test
            url: URL of the test

        Returns:
            None
        """
        try:
            failed_tests_file = "failed_tests.md"

            # Create file with header if it doesn't exist
            if not os.path.exists(failed_tests_file):
                with open(failed_tests_file, "w", encoding="utf-8") as f:
                    f.write("# Failed Tests\n\n")
                    f.write("Tests that need manual attention:\n\n")

            with open(failed_tests_file, "r", encoding="utf-8") as f:
                content = f.readlines()

            test_entry = f"- [ ] [{test_name}]({url})\n"
            if test_entry not in content:
                # Add the new test
                with open(failed_tests_file, "a", encoding="utf-8") as f:
                    f.write(test_entry)

            print(f"Test added to {failed_tests_file}")
        except Exception as e:
            print(f"Error updating failed tests file: {e}")