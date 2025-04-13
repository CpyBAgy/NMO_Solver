"""
Core NMO Parser implementation.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .driver import setup_driver, get_by, wait_for_url_change, wait_for_new_window
from .utils import select_answers, generate_answer_combinations, save_failed_tests
from .models.question import Question

try:
    from .user_config import USERNAME, PASSWORD, EMAIL, PATH_TO_CHROME_PROFILE
except ImportError:
    from .configs import USERNAME, PASSWORD, EMAIL, PATH_TO_CHROME_PROFILE

from .configs import LOGIN_URL, EXPECTED_REDIRECT_URL

from .parsers.answer_parser import parse_answers, read_correct_answers, save_correct_answers
from .parsers.web_parser import get_test_name, parse_answer_options, parse_correct_answers_from_results


class NmoParser:
    """
    Main class for interacting with the NMO platform.
    """

    def __init__(self, username=None, email=None, password=None, path_to_profile=None):
        """
        Initialize the NMO parser.

        Args:
            username: SNILS or username for login
            email: Email for login (if used)
            password: Password for login
            path_to_profile: Path to Chrome profile directory
        """
        self.login_url = LOGIN_URL
        self.expected_redirect_url = EXPECTED_REDIRECT_URL
        self.username = username or USERNAME
        self.email = email or EMAIL
        self.password = password or PASSWORD
        self.path_to_profile = path_to_profile or PATH_TO_CHROME_PROFILE

        self.driver = setup_driver(self.path_to_profile)

        use_email = self.email != "" and self.email is not None
        self.__login(use_email=use_email)

    def __login(self, use_email=False):
        """
        Log in to the NMO platform.

        Args:
            use_email: Whether to use email for login instead of SNILS

        Returns:
            bool: True if login successful, False otherwise
        """
        self.driver.get(self.login_url)

        while "login" in self.driver.current_url.lower():
            self.driver.refresh()

            def send_keys(element, keys):
                if element:
                    element.clear()
                    element.send_keys(keys)

            try:
                if use_email:
                    get_by(self.driver, By.XPATH, "//li[@id='liEmail']//a").click()
                    time.sleep(3)
                    username_field = get_by(self.driver, By.ID, "usernameEmail")
                    send_keys(username_field, self.email)
                else:
                    username_field = get_by(self.driver, By.ID, "username")
                    send_keys(username_field, self.username)

                password_field = get_by(self.driver, By.ID, "password")
                send_keys(password_field, self.password)
                password_field.send_keys(Keys.RETURN)

                if wait_for_url_change(self.driver, self.login_url):
                    print("Авторизация успешна")
                    return True
            except Exception as e:
                print(f"Ошибка при авторизации: {e}")
                continue

        return True

    def __ready_to_solve(self):
        """
        Check if the test is ready to be solved.

        Returns:
            bool: True if test is ready, False otherwise
        """
        try:
            button = get_by(self.driver, By.XPATH, "//button[contains(., 'Включить в план')]")

            if button:
                button.click()
                print("Тест включен в план")
                return True

            return get_by(self.driver, By.XPATH, "//button[contains(., 'Исключить из плана')]") is not None
        except Exception as e:
            print(f"Ошибка при проверке готовности теста: {e}")
            return False

    def __machination(self):
        """
        Method for correct pressing button 'Перейти к обучению'
        Handles the test setup process.

        Returns:
            None
        """
        try:
            # Click on "Перейти к обучению" button
            get_by(self.driver, By.XPATH, "//button[contains(., 'Перейти к обучению')]").click()
            time.sleep(3)

            # Execute JS to check the checkbox and enable the "Далее" button
            js_code = """
                var checkbox = document.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = true;
                    var event = new Event('change', { bubbles: true });
                    checkbox.dispatchEvent(event);
                }
                var nextButton = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === 'Далее');
                if (nextButton) {
                    nextButton.disabled = false;
                }
            """
            self.driver.execute_script(js_code)

            # Click on "Далее" button
            get_by(self.driver, By.XPATH, "//button[contains(., 'Далее')]").click()
            time.sleep(3)

            # Wait for new tab to open
            wait_for_new_window(self.driver, 1)
            self.driver.switch_to.window(self.driver.window_handles[-1])

            # Wait for page to load
            WebDriverWait(self.driver, 30).until(EC.url_contains("https://iom-vo.edu.rosminzdrav.ru/"))
            print(f"Текущий URL: {self.driver.current_url}")
        except Exception as e:
            print(f"Ошибка при настройке теста: {e}")

    def __skip_preliminary(self):
        """
        Skip preliminary testing if present.

        Returns:
            bool: True if preliminary test was skipped, False if no preliminary test
        """
        try:
            # Check if preliminary test exists
            self.driver.find_element(By.XPATH,
                                     "//span[contains(@class, 'c-groupbox-caption-text') and contains(text(), 'Предварительное тестирование')]")

            # Click on variant
            get_by(self.driver, By.XPATH,
                   "//span[contains(@class, 'c-table-clickable-cell') and contains(text(), 'Вариант №')]").click()
            print("Нажата кнопка 'Вариант №'")

            # Start testing
            start_button = get_by(self.driver, By.XPATH,
                                  "//button[contains(@class, 'quiz-buttons-primary') and contains(., 'Начать тестирование')]")
            if start_button:
                start_button.click()
                print("Нажата кнопка 'Начать тестирование'")
                time.sleep(3)

            # End testing
            get_by(self.driver, By.XPATH, "//button[contains(., 'Завершить тестирование')]").click()
            get_by(self.driver, By.XPATH, "//button[contains(., 'Да')]").click()
            self.__close_variant()
            return True
        except NoSuchElementException:
            print("Предварительное тестирование отсутствует")
            return False

    def __get_variant(self):
        """
        Get a new test variant.

        Returns:
            int: Variant number
        """
        # JavaScript for clicking "Получить новый вариант" button
        js_code_new_variant = """
            var buttons = document.querySelectorAll('div[role="button"]');
            for (var i = 0; i < buttons.length; i++) {
                if (buttons[i].textContent.trim() === 'Получить новый вариант') {
                    buttons[i].click();
                    return true;
                }
            }
            return false;
        """

        # JavaScript for clicking "Вперед" button
        js_code_forward = """
            var buttons = document.querySelectorAll('div[role="button"].blue-button');
            for (var i = 0; i < buttons.length; i++) {
                if (buttons[i].textContent.trim().includes('Вперед')) {
                    buttons[i].click();
                    return true;
                }
            }
            return false;
        """

        # Check for existing unfinished variant
        new_variant = get_by(self.driver, By.XPATH,
                             "//span[contains(@class, 'c-table-clickable-cell') and contains(text(), 'не завершен')]")
        if new_variant:
            # Extract variant number from format "Вариант №7289 - не завершен"
            variant_text = new_variant.text.split()
            if len(variant_text) > 1:
                variant_number = variant_text[1].replace("№", "")
                return int(variant_number)

        # Try to get new variant
        while not self.driver.execute_script(js_code_new_variant):
            self.driver.execute_script(js_code_forward)
            time.sleep(3)

        time.sleep(10)

        # Check for newly created variant
        new_variant = get_by(self.driver, By.XPATH,
                             "//span[contains(@class, 'c-table-clickable-cell') and contains(text(), 'не завершен')]")
        if new_variant:
            variant_text = new_variant.text.split()
            if len(variant_text) > 1:
                variant_number = variant_text[1].replace("№", "")
                return int(variant_number)

        # If still not found, try one more time
        self.driver.execute_script(js_code_forward)
        return self.__get_variant()

    def __solve_variant(self, answers):
        """
        Solve a test variant with provided answers.

        Args:
            answers: Dictionary of questions mapped to their Question objects

        Returns:
            dict: Dictionary of unsolved questions
        """
        # Click on variant
        get_by(self.driver, By.XPATH,
               "//span[contains(@class, 'c-table-clickable-cell') and contains(text(), 'Вариант №')]").click()
        print("Нажата кнопка 'Вариант №'")

        # Start testing
        try:
            start_button = get_by(self.driver, By.XPATH,
                                  "//button[contains(@class, 'quiz-buttons-primary') and contains(., 'Начать тестирование')]")
            if start_button:
                start_button.click()
                print("Нажата кнопка 'Начать тестирование'")
                time.sleep(3)
        except Exception:
            pass

        # Process questions one by one
        unsolved_questions = dict()
        while True:
            try:
                # Get current question text
                current_question = get_by(self.driver, By.CLASS_NAME, "question-title-text").text.strip()
                print("Вопрос:", current_question)

                # Get question type
                question_type_element = get_by(self.driver, By.CLASS_NAME, "mat-card-question__type")
                question_type = question_type_element.text if question_type_element else "ОДИН"
                question_type = "НЕСК" if "несколько" in question_type.lower() else "ОДИН"

                # Get answers for current question
                current_answers = answers[current_question].answers if current_question in answers else None
                print("Ответ:", current_answers)

                if not current_answers:
                    print(f"Ответы на вопрос '{current_question}' не найдены")

                    # Save unsolved question details
                    unsolved_answers = parse_answer_options(self.driver, question_type)
                    unsolved_questions[current_question] = Question(current_question, question_type, unsolved_answers)
                else:
                    # Select answers for the question
                    select_answers(self.driver, current_answers, question_type)

                # Go to next question or finish
                next_button = get_by(self.driver, By.XPATH, "//button[contains(., 'Следующий вопрос')]")
                if next_button:
                    next_button.click()
                    print("Нажата кнопка 'Следующий вопрос'")
                    time.sleep(2)
                    continue

                # Finish testing
                get_by(self.driver, By.XPATH, "//button[contains(., 'Завершить тестирование')]").click()
                get_by(self.driver, By.XPATH, "//button[contains(., 'Да')]").click()

                return unsolved_questions
            except StaleElementReferenceException:
                # Idk why, but this error occurs sometimes when peeking multiple choice questions
                #print("Игнорируем ошибку устаревшего элемента, продолжаем...")
                continue
            except Exception as e:
                print(f"Ошибка при решении варианта: {e}")
                continue

    def __close_variant(self):
        """
        Close the current test variant.

        Returns:
            None
        """
        try:
            get_by(self.driver, By.XPATH, "//button[contains(., 'Вернуться к обучению')]").click()
            time.sleep(1)

            try:
                # Click on "Да" button in confirmation dialog if present
                self.driver.execute_script("""
                                            var buttons = document.querySelectorAll('.v-button-caption');
                                            for(var i = 0; i < buttons.length; i++) {
                                                if(buttons[i].textContent === 'Да') {
                                                    buttons[i].closest('.v-button').click();
                                                    return true;
                                                }
                                            }
                                            return false;
                                        """)
                time.sleep(2)
            except Exception as e:
                pass

            close_button = get_by(self.driver, By.CLASS_NAME, "v-window-closebox")
            if close_button:
                close_button.click()
        except Exception as e:
            print(f"Ошибка при закрытии варианта: {e}")

    def __passing_score(self, variant_number):
        """
        Check if the test has been passed with a passing score.

        Args:
            variant_number: Current test variant number

        Returns:
            bool: True if passed, False otherwise
        """
        try:
            time.sleep(5)
            score_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//span[contains(@class, 'quiz-info-col-indicators-item')]//div[contains(@class, 'text_label') and contains(text(), 'Оценка')]/following-sibling::div[contains(@class, 'text_value')]")
                )
            )

            score_text = score_element.text.strip()
            score = int(score_text)

            print(f"Вариант №{variant_number} завершен. Оценка: {score}")
            return score >= 3
        except Exception as e:
            print(f"Ошибка при получении оценки: {e}")
            return False

    def __solve_variant_hard(self, test_name, total_questions):
        """
        Solve a test variant using the "hard" method (trial and error).

        Args:
            test_name: Name of the test
            total_questions: Dictionary of unsolved questions

        Returns:
            None
        """
        # Read known correct answers
        correct_answers = read_correct_answers(test_name)
        current_answers = dict()

        passed = False
        iteration = 0

        while not passed:
            self.__close_variant()

            current_answers.clear()
            for question in total_questions:
                q_type = total_questions[question].type
                q_text = total_questions[question].text
                q_iteration = total_questions[question].iteration
                q_answers = total_questions[question].answers

                # Use known correct answers if available
                try:
                    current_answers[q_text] = correct_answers[q_text]
                    continue
                except KeyError:
                    pass

                # Otherwise, try new combinations of answers
                current_answers[q_text] = Question(q_text, q_type, [], q_iteration)
                q_amount = len(total_questions[q_text].answers)

                # Generate answer combinations based on question type
                if q_type == "НЕСК":
                    combo_indices = generate_answer_combinations(total_questions, q_text, q_iteration)
                    for i in combo_indices:
                        idx = i % q_amount  # Ensure index is within bounds
                        current_answers[q_text].answers.append(total_questions[q_text].answers[idx])
                else:
                    # For single choice, cycle through options
                    idx = q_iteration % q_amount
                    current_answers[q_text].answers = [total_questions[q_text].answers[idx]]

                total_questions[q_text].iteration += 1

            print(f"Попытка {iteration + 1}. Текущие ответы: ", current_answers)

            # Get a new variant and solve it
            self.__get_variant()
            new_questions = self.__solve_variant(current_answers)

            # Update unsolved questions list
            total_questions.update(new_questions)

            # Parse correct answers from results
            correct_answers = parse_correct_answers_from_results(self.driver, current_answers, correct_answers)
            print("Полученные правильные ответы: ", correct_answers)

            iteration += 1
            passed = self.__passing_score(iteration)

            # Limit the number of attempts to prevent blocking
            if iteration >= 50:
                return False

        # Save correct answers for future use
        save_correct_answers(test_name, correct_answers)
        return True

    def __download_certificate(self, test_name):
        """
        Download the certificate for the completed test.

        Args:
            test_name: Name of the test

        Returns:
            None
        """
        try:
            # Close the variant and go forward
            self.__close_variant()

            js_code_forward = """
                var buttons = document.querySelectorAll('div[role="button"].blue-button');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.trim().includes('Вперед')) {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
            """
            self.driver.execute_script(js_code_forward)

            print("Все решено успешно, можно и сертификат скачать")

            # TODO: Implement certificate download logic

        except Exception as e:
            print(f"Ошибка при скачивании сертификата: {e}")

    def solve(self, url):
        """
        Main method to solve a test.

        Args:
            url: URL of the test to solve

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.driver.get(url)
            time.sleep(3)

            # Ensure logged in
            if "login" in self.driver.current_url.lower():
                use_email = self.email != "" and self.email is not None
                self.__login(use_email=use_email)

            test_name = get_test_name(self.driver)

            if not self.__ready_to_solve():
                print("Тест не доступен для решения или уже решен")
                return False

            # Start test
            self.__machination()

            variant_number = self.__get_variant()

            if self.__skip_preliminary():
                variant_number = self.__get_variant()

            # Get answers for the test
            answers = parse_answers(test_name)

            # Solve the variant
            unsolved_questions = self.__solve_variant(answers)
            print("Нерешенные вопросы: ", unsolved_questions)

            # Check if passed
            if self.__passing_score(variant_number):
                print(f"Тест '{test_name}' успешно пройден")
                self.__download_certificate(test_name)
                return True

            # If not passed, use hard method
            print(f"Тест '{test_name}' не пройден. Приступаем к решению методом перебора, это может занять время...")
            passed = self.__solve_variant_hard(test_name, unsolved_questions)

            if not passed:
                print("Достигнут лимит попыток. Этот тест лучше решить лично. Завершение...")
                save_failed_tests(test_name, url)
                return False

            self.__download_certificate(test_name)
            return True
        except Exception as e:
            print(f"Ошибка при решении теста: {e}")
            return False

    def close(self):
        """
        Close the browser and clean up.

        Returns:
            None
        """
        if self.driver:
            self.driver.quit()