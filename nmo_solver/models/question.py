"""
Question model for representing test questions and answers.
"""


class Question:
    """
    Represents a test question with its type and possible answers.

    Attributes:
        text (str): The text of the question
        type (str): Type of question ("ОДИН" for single choice, "НЕСК" for multiple choice)
        answers (list): List of answer options or correct answers
        iteration (int): Current iteration number for answer combinations
    """

    def __init__(self, text: str, q_type: str, answers: list, iteration: int = 0):
        """
        Initialize a Question object.

        Args:
            text: The text of the question
            q_type: Type of question ("ОДИН" for single choice, "НЕСК" for multiple choice)
            answers: List of answer options or correct answers
            iteration: Current iteration number for answer combinations
        """
        self.text = text
        self.type = q_type
        self.answers = answers
        self.iteration = iteration

    def __str__(self):
        """String representation of the Question object."""
        return f"Question: {self.text}\nType: {self.type}\nAnswers: {self.answers}"

    def __repr__(self):
        """Representation of the Question object."""
        return f"Question(text='{self.text}', type='{self.type}', answers={self.answers}, iteration={self.iteration})"