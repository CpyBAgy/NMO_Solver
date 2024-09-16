import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class NmoParser:
    def __init__(self):
        self.login_url = "https://a.edu.rosminzdrav.ru/idp/login.html?response_type=client-ticket&sp=https%3A%2F%2Fnmfo-vo.edu.rosminzdrav.ru%2F%23%2Flogin%2F"
        self.expected_redirect_url = "https://iom-vo.edu.rosminzdrav.ru/#!"
        self.username = "062-376-571 68"  # default = 000-000-000 00
        self.email = ""  # default not in use
        self.password = "97hoTSWWdihx2Uyl"  # default = password
        self.driver = self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def login(self, use_email=False):
        self.driver.get(self.login_url)

        if use_email:
            email_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//li[@id='liEmail']//a"))
            )
            email_button.click()
            time.sleep(3)
            username_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "usernameEmail"))
            )
            username_field.clear()
            username_field.send_keys(self.email)
        else:
            username_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
        password_field = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        password_field.clear()
        password_field.send_keys(self.password)
        password_field.send_keys(Keys.RETURN)

        WebDriverWait(self.driver, 30).until(
            EC.url_changes(self.login_url)
        )
        print("Авторизация успешна")
        time.sleep(5)

    def navigate_to_test(self, target_url):
        self.driver.get(target_url)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        while "login" in self.driver.current_url.lower():
            self.login()  # Warning: use  self.login(True) to login with email
            self.driver.get(target_url)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

    def get_test_name(self):
        test_name_element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(@class, 'heading') and contains(@class, 'heading_1')]"))
        )
        test_name = test_name_element.text
        test_name = re.sub(r'\s?\-\s?20\d+', '', test_name)
        print(f"Название теста: {test_name}")
        return test_name

    def start_test(self):
        button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Перейти к обучению')]"))
        )
        button.click()
        time.sleep(3)
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
        next_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Далее')]"))
        )
        next_button.click()
        time.sleep(3)
        WebDriverWait(self.driver, 30).until(lambda d: len(d.window_handles) > 1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        WebDriverWait(self.driver, 30).until(EC.url_contains("https://iom-vo.edu.rosminzdrav.ru/"))
        print(f"Текущий URL: {self.driver.current_url}")

    def clicking_forward_until_new_variant(self):
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
        while True:
            try:
                variant_element = self.driver.find_element(By.XPATH,
                                                           "//span[contains(@class, 'c-table-clickable-cell') and contains(text(), 'Вариант №')]")
                if "не завершен" in variant_element.text:
                    print("Найден незавершенный вариант, завершаем выполнение функции")
                    return
                self.driver.execute_script(js_code_forward)
                print("Найден завершенный вариант, нажимаем 'Вперед' и продолжаем")
            except NoSuchElementException:
                if self.driver.execute_script(js_code_new_variant):
                    print("Получен новый вариант")
                    return
                if not self.driver.execute_script(js_code_forward):
                    print("Не удалось найти кнопку 'Вперед', завершаем выполнение функции")
                    return
                print("Нажата кнопка вперед, ожидание нового варианта")
            time.sleep(3)

    def find_answers(self, query):
        answers = dict()
        base_url = "https://24forcare.com"
        search_url = f"{base_url}/search/?query={requests.utils.quote(query)}"
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
            else:
                continue
        return answers

    def select_answers(self, question_type, correct_answers):
        if "НЕСКОЛЬКО" in question_type:
            answer_options = self.driver.find_elements(By.XPATH,
                                                       "//mat-checkbox[contains(@class, 'mat-mdc-checkbox')]")
            for option in answer_options:
                answer_text = option.find_element(By.XPATH,
                                                  ".//span[contains(@class, 'question-inner-html-text')]").text.strip()
                if answer_text in correct_answers:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
                    time.sleep(0.5)
                    checkbox = option.find_element(By.XPATH, ".//input[@type='checkbox']")
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        print(f"Выбран ответ: {answer_text}")
                        time.sleep(0.5)
        else:
            answer_options = self.driver.find_elements(By.XPATH,
                                                       "//mat-radio-button[contains(@class, 'mat-mdc-radio-button')]")
            for option in answer_options:
                answer_text = option.find_element(By.XPATH,
                                                  ".//span[contains(@class, 'question-inner-html-text')]").text.strip()
                if answer_text in correct_answers:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
                    time.sleep(0.5)
                    radio_button = option.find_element(By.XPATH, ".//input[@type='radio']")
                    self.driver.execute_script("arguments[0].click();", radio_button)
                    print(f"Выбран ответ: {answer_text}")
                    time.sleep(0.5)
                    break

    def variant_solving(self, test_name):
        answers = self.find_answers(test_name)
        while True:
            try:
                question_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "question-title-text"))
                )
                question_text = question_element.text.strip()
                print("Вопрос: ", question_text)
                correct_answers = answers.get(question_text, [])
                if not correct_answers:
                    print(f"Внимание: Не найдены ответы для вопроса: {question_text}")
                question_type = self.driver.find_element(By.CLASS_NAME, "mat-card-question__type").text
                self.select_answers(question_type, correct_answers)
                next_button = self.driver.find_elements(By.XPATH,
                                                        "//button[contains(@class, 'question-buttons-primary') and contains(., 'Следующий вопрос')]")
                if not next_button:
                    finish_button = self.driver.find_element(By.XPATH,
                                                             "//button[contains(@class, 'question-buttons-primary') and contains(., 'Завершить тестирование')]")
                    self.driver.execute_script("arguments[0].click();", finish_button)
                    print("Нажата кнопка 'Завершить тестирование'")
                    time.sleep(3)
                    yes_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(@class, 'mat-primary') and contains(., 'Да')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", yes_button)
                    print("Нажата кнопка 'Да' во всплывающем окне")
                    time.sleep(3)
                    return_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    "//button[contains(@class, 'quiz-buttons-primary') and contains(., 'Вернуться к обучению')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", return_button)
                    print("Нажата кнопка 'Вернуться к обучению'")
                    time.sleep(3)
                    try:
                        yes_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH,
                                                        "//div[contains(@class, 'v-button') and contains(@class, 'icon')]//span[contains(@class, 'v-button-caption') and text()='Да']"))
                        )
                        self.driver.execute_script("arguments[0].click();", yes_button)
                        print("Нажата кнопка 'Да'")
                        time.sleep(1)
                    except TimeoutException:
                        print("Кнопка 'Да' не найдена или не кликабельна")
                    except Exception as e:
                        # print(f"Произошла ошибка при нажатии кнопки 'Да': {str(e)}")
                        pass
                    close_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "v-window-closebox"))
                    )
                    self.driver.execute_script("arguments[0].click();", close_button)
                    print("Нажат крестик во всплывающем окне")
                    time.sleep(3)
                    print("Решение варианта теста завершено")
                    return
                self.driver.execute_script("arguments[0].click();", next_button[0])
                print("Нажата кнопка 'Следующий вопрос'")
                time.sleep(3)
            except TimeoutException:
                print("Тест завершен или произошла ошибка при ожидании элементов")
                break
            except NoSuchElementException:
                print("Элемент не найден, возможно, тест завершен")
                break
            except Exception as e:
                # print(f"Произошла ошибка: {str(e)}")
                continue

        print(f"Завершен вариант теста {test_name}")

    def check_preliminary_testing(self, test_name):
        try:
            self.driver.find_element(By.XPATH,
                                     "//span[contains(@class, 'c-groupbox-caption-text') and contains(text(), 'Предварительное тестирование')]")
            forward_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'blue-button') and contains(., 'Вперед')]"))
            )
            self.driver.execute_script("arguments[0].click();", forward_button)
            print("Нажата кнопка 'Вперед' после предварительного тестирования")
            time.sleep(3)
            self.clicking_forward_until_new_variant()
            variant_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(@class, 'c-table-clickable-cell') and contains(text(), 'Вариант №')]")))
            variant_element.click()
            time.sleep(3)
            print("Нажата кнопка варианта")
            try:
                start_test_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//button[contains(@class, 'quiz-buttons-primary') and contains(., 'Начать тестирование')]"))
                )
                self.driver.execute_script("arguments[0].click();", start_test_button)
                print("Нажата кнопка 'Начать тестирование'")
                time.sleep(3)
            except TimeoutException:
                print("Кнопки начать тестирования нет, решаем тест")
            self.variant_solving(test_name)
        except NoSuchElementException:
            print("Предварительное тестирование не обнаружено")

    def solve_test(self, target_url):
        self.navigate_to_test(target_url)
        test_name = self.get_test_name()
        self.start_test()
        self.clicking_forward_until_new_variant()
        variant_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'c-table-clickable-cell') and contains(text(), 'Вариант №')]")))
        variant_element.click()
        time.sleep(3)
        print("Нажата кнопка варианта")
        try:
            start_test_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[contains(@class, 'quiz-buttons-primary') and contains(., 'Начать тестирование')]"))
            )
            self.driver.execute_script("arguments[0].click();", start_test_button)
            print("Нажата кнопка 'Начать тестирование'")
            time.sleep(3)
        except TimeoutException:
            print("Кнопки начать тестирования нет, решаем тест")
        self.variant_solving(test_name)
        self.check_preliminary_testing(test_name)
        print(f"Решение теста {test_name} завершено")

    def run_many(self):
        urls = []
        while True:
            target_url = input("Введите URL теста (или 'q' для начала решения тестов): ")
            if target_url.lower() == 'q' or target_url.lower() == 'й':
                break
            urls.append(target_url)
        for i in range(len(urls)):
            self.solve_test(urls[i])
        self.driver.quit()

    def run(self):
        while True:
            target_url = input("Введите URL теста (или 'q' для выхода): ")
            if target_url.lower() == 'q' or target_url.lower() == 'й':
                break
            self.solve_test(target_url)
        self.driver.quit()


if __name__ == "__main__":
    parser = NmoParser()
    parser.run()
