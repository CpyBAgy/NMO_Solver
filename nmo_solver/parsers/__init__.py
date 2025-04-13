"""
Parser modules for extracting information from various sources.
"""

from .answer_parser import parse_answers, read_correct_answers, save_correct_answers
from .web_parser import get_test_name, parse_answer_options, parse_correct_answers_from_results

__all__ = [
    'parse_answers',
    'read_correct_answers',
    'save_correct_answers',
    'get_test_name',
    'parse_answer_options',
    'parse_correct_answers_from_results'
]