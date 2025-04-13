"""
Functions for parsing web content from the NMO platform.
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException

from ..driver import get_by


def get_test_name(driver):
    """
    Extract the test name from the current page.

    Args:
        driver: WebDriver instance

    Returns:
        str: Test name
    """
    try:
        test_name_element = get_by(driver, By.XPATH,
                                   "//h1[contains(@class, 'heading') and contains(@class, 'heading_1')]")
        if test_name_element:
            test_name = test_name_element.text
            # Remove year designation from test name if present
            test_name = re.sub(r'\s?-\s?20\d+', '', test_name)
            print(f"Название теста: {test_name}")
            return test_name
    except Exception as e:
        print(f"Error getting test name: {e}")

    return "unknown_test"


def parse_question_details(driver):
    """
    Parse the current question details.

    Args:
        driver: WebDriver instance

    Returns:
        tuple: (question_text, question_type)
    """
    try:
        question_text = get_by(driver, By.CLASS_NAME, "question-title-text").text.strip()
        question_type_element = get_by(driver, By.CLASS_NAME, "mat-card-question__type")

        if question_type_element:
            question_type = question_type_element.text
            question_type = "НЕСК" if "несколько" in question_type.lower() else "ОДИН"
        else:
            question_type = "ОДИН"  # Default to single choice if type not found

        return question_text, question_type
    except Exception as e:
        print(f"Error parsing question details: {e}")
        return None, None


def parse_answer_options(driver, question_type):
    """
    Parse available answer options for the current question.

    Args:
        driver: WebDriver instance
        question_type: Type of question ("ОДИН" or "НЕСК")

    Returns:
        list: Available answer options
    """
    answers = []

    try:
        if "НЕСК" in question_type:
            answer_elements = driver.find_elements(By.XPATH,
                                                   "//mat-checkbox[contains(@class, 'mat-mdc-checkbox')]")
        else:
            answer_elements = driver.find_elements(By.XPATH,
                                                   "//mat-radio-button[contains(@class, 'mat-mdc-radio-button')]")

        for element in answer_elements:
            answer_text = element.find_element(By.XPATH,
                                               ".//span[contains(@class, 'question-inner-html-text')]").text.strip()
            answers.append(answer_text)
    except Exception as e:
        print(f"Error parsing answer options: {e}")

    return answers


def parse_correct_answers_from_results(driver, submitted_answers, existing_correct_answers=None):
    """
    Parse correct answers from test results.

    Args:
        driver: WebDriver instance
        submitted_answers: Dictionary of submitted answers
        existing_correct_answers: Dictionary of already known correct answers

    Returns:
        dict: Updated dictionary with correct answers
    """
    # Инициализируем словарь существующими ответами, если они есть
    if existing_correct_answers is None:
        existing_correct_answers = {}

    # Копируем существующие ответы, чтобы не изменять оригинал
    correct_answers = dict(existing_correct_answers)

    try:
        time.sleep(5)  # Wait for results to load
        questions = driver.find_elements(By.CLASS_NAME, 'questionList-item')

        print("-" * 50)
        for question in questions:
            try:
                number = question.find_element(By.CLASS_NAME, 'questionList-item-number').text
                title = question.find_element(By.CLASS_NAME, 'questionList-item-content-title').text
                status_element = question.find_element(By.CLASS_NAME, "questionList-item-status")

                status = status_element.text

                if status == "Верно" and title in submitted_answers:
                    correct_answers[title] = submitted_answers.get(title)

                print(f"Вопрос {number}: {title}")
                print(f"Статус ответа: {status}")
            except NoSuchElementException:
                continue
        print("-" * 50)
    except Exception as e:
        print(f"Error parsing correct answers: {e}")

    return correct_answers