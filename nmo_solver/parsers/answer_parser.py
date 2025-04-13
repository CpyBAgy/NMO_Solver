"""
Functions for parsing and managing question answers.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from ..models import Question
from ..configs import SEARCH_BASE_URL, ANSWERS_FOLDER


def parse_answers(query):
    """
    Search for and parse answers for a given test from an external source.

    Args:
        query (str): Test name or search query

    Returns:
        dict: Dictionary of questions mapped to their Question objects
    """
    answers = dict()
    base_url = SEARCH_BASE_URL
    search_url = f"{base_url}/search/?query={requests.utils.quote(query)}"

    try:
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        result_link = soup.find('a', class_='item-name')

        if not result_link:
            print("Результаты не найдены")
            return answers

        url = base_url + '/' + result_link['href']
        print(f"Найденный URL: {url}\nНазвание теста:", result_link['title'])

        response = requests.get(url)
        html = BeautifulSoup(response.text, 'html.parser')
        questions = html.find_all({'h3', 'strong'})

        q = 0
        current_a = []
        pattern_q = r'\d+\.\s'
        pattern_a = r'\d+\)\s'

        for question in questions:
            text = question.text
            if re.match(pattern_q, text):
                answers[q] = current_a
                q = re.sub(pattern_q, '', text)
                current_a = []
            elif re.match(pattern_a, text):
                a = re.sub(pattern_a, '', text)[:-2]
                current_a.append(a)

        return dict_to_questions(answers)
    except Exception as e:
        print(f"Error parsing answers: {e}")
        return answers


def dict_to_questions(answers_dict):
    """
    Convert a dictionary of answers to Question objects.

    Args:
        answers_dict (dict): Dictionary with question text as keys and answers as values

    Returns:
        dict: Dictionary of questions mapped to their Question objects
    """
    questions = dict()

    for q in answers_dict:
        if not q or q == 0:  # Skip empty keys or zero key which is used temporarily
            continue

        q_type = "НЕСК" if isinstance(answers_dict[q], list) and len(answers_dict[q]) > 1 else "ОДИН"
        text = q
        answers_list = answers_dict[q]

        question = Question(text, q_type, answers_list)
        questions[text] = question

    return questions


def questions_to_dict(questions):
    """
    Convert Question objects to a dictionary.

    Args:
        questions (dict): Dictionary of questions mapped to their Question objects

    Returns:
        dict: Dictionary with question text as keys and answers as values
    """
    answers = dict()

    for q in questions:
        answers[q] = questions[q].answers

    return answers


def read_correct_answers(test_name):
    """
    Read saved correct answers from a file.

    Args:
        test_name (str): Name of the test

    Returns:
        dict: Dictionary of questions mapped to their Question objects
    """
    correct_answers = dict()

    try:
        os.makedirs(ANSWERS_FOLDER, exist_ok=True)
        filename = os.path.join(ANSWERS_FOLDER, f"{test_name}.txt")

        if not os.path.exists(filename):
            return correct_answers

        with open(filename, "r") as f:
            for line in f.readlines():
                if ":" not in line:
                    continue

                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue

                question, answer_text = parts

                answer_text = answer_text.strip()
                if answer_text.startswith("[") and answer_text.endswith("]"):
                    answers = [a.strip() for a in answer_text[1:-1].split(",")]
                else:
                    answers = [answer_text]

                correct_answers[question.strip()] = answers
    except Exception as e:
        print(f"Error reading answers file: {e}")

    return dict_to_questions(correct_answers)


def save_correct_answers(test_name, correct_answers):
    """
    Save correct answers to a file.

    Args:
        test_name (str): Name of the test
        correct_answers (dict): Dictionary of questions mapped to their Question objects

    Returns:
        None
    """
    answers = questions_to_dict(correct_answers)

    try:
        os.makedirs(ANSWERS_FOLDER, exist_ok=True)
        filename = os.path.join(ANSWERS_FOLDER, f"{test_name}.txt")

        with open(filename, "w") as f:
            for question in answers:
                answer_text = answers[question]
                if isinstance(answer_text, list):
                    answer_str = ", ".join(answer_text)
                    f.write(f"{question}: [{answer_str}]\n")
                else:
                    f.write(f"{question}: {answer_text}\n")

        print(f"Answers saved to {filename}")
    except Exception as e:
        print(f"Error saving answers file: {e}")