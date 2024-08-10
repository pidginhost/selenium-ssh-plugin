import pytest
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utilities.utils import Utils
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


class BaseDriver:
    EMAIL_INPUT_FIELD = "//input[@name='email']"
    BUTTON_EMAIL_NEXT = "//button[text()='Log in / Sign up']"
    PASSWORD_INPUT_FIELD = ('//input[contains(@name, "password") and contains(@type, "password") '
                            'and contains(@class, "form-control")]')
    BUTTON_PASSWORD_NEXT = '//button[contains(@type, "submit") and contains(text(), "Login")]'
    WELCOME_MESSAGE_FIELD = '//h2[@class="mb-0"]'
    WELCOME_MESSAGE_TEXT = 'Welcome to your account.'

    def __init__(self, driver):
        self.driver = driver
        self.utils = Utils()

    def login(self, username, password):
        try:
            email_input = self.wait_until_element_is_clickable(By.XPATH, self.EMAIL_INPUT_FIELD)
            email_input.send_keys(username)
            self.utils.custom_logger().info("Type email")
            email_login_button = self.wait_until_element_is_clickable(By.XPATH, self.BUTTON_EMAIL_NEXT)
            email_login_button.click()
            self.utils.custom_logger().info("Click Login button")
            password_input = self.wait_until_element_is_clickable(By.XPATH, self.PASSWORD_INPUT_FIELD)
            password_input.send_keys(password)
            self.utils.custom_logger().info("Type password")
            password_login_button = self.wait_until_element_is_clickable(By.XPATH, self.BUTTON_PASSWORD_NEXT)
            password_login_button.click()
            self.utils.custom_logger().info("Click Login button")
            welcome_message = self.wait_until_element_is_clickable(By.XPATH, self.WELCOME_MESSAGE_FIELD)
            assert welcome_message.text == self.WELCOME_MESSAGE_TEXT
            self.utils.custom_logger().info("Wellcome message displayed")
        except TimeoutException:
            self.utils.custom_logger().critical("Failed to login")
            pytest.fail("Failed to login")

    @staticmethod
    def select_option_by_visible_text(select_element, visible_text):
        try:
            select = Select(select_element)
            select.select_by_visible_text(visible_text)
            selected_option = select.first_selected_option.text
            return selected_option
        except Exception as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def wait_until_element_is_clickable(self, locator_type, locator):
        wait = WebDriverWait(self.driver, 30)
        element = wait.until(EC.element_to_be_clickable((locator_type, locator)))
        return element

    def wait_until_element_is_visible(self, locator_type, locator):
        wait = WebDriverWait(self.driver, 30)
        element = wait.until(EC.visibility_of_element_located((locator_type, locator)))
        return element

    def wait_until_presence_of_element_located(self, locator_type, locator):
        wait = WebDriverWait(self.driver, 30)
        element = wait.until(EC.presence_of_element_located((locator_type, locator)))
        return element

    def wait_invisibility_of_element_located(self, locator_type, locator):
        wait = WebDriverWait(self.driver, 30)
        element = wait.until(EC.invisibility_of_element_located((locator_type, locator)))
        return element

    def return_soup(self):
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup