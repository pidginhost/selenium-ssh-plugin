import pytest
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utilities.utils import Utils
from bs4 import BeautifulSoup
from typing import Optional


class BaseDriver:
    """
    BaseDriver class encapsulates common WebDriver functionalities such as logging in,
    selecting options from dropdowns, waiting for elements, and parsing page source.
    """

    # Locators
    EMAIL_INPUT_FIELD = "//input[@name='email']"
    BUTTON_EMAIL_NEXT = "//button[text()='Log in / Sign up']"
    PASSWORD_INPUT_FIELD = (
        '//input[contains(@name, "password") and contains(@type, "password") '
        'and contains(@class, "form-control")]'
    )
    BUTTON_PASSWORD_NEXT = '//button[contains(@type, "submit") and contains(text(), "Login")]'
    WELCOME_MESSAGE_FIELD = '//h2[@class="mb-0"]'
    WELCOME_MESSAGE_TEXT = 'Welcome to your account.'

    def __init__(self, driver):
        """
        Initializes the BaseDriver with a WebDriver instance and sets up logging.

        Args:
            driver: Selenium WebDriver instance.
        """
        self.driver = driver
        self.utils = Utils()
        self.logger = self.utils.custom_logger()
        self.wait_timeout = 30  # Default wait timeout in seconds

    def login(self, username: str, password: str) -> None:
        """
        Performs the login operation using the provided username and password.

        Args:
            username (str): The user's email address.
            password (str): The user's password.

        Raises:
            pytest.fail: If login fails due to a TimeoutException or assertion failure.
        """
        self.logger.debug("Initiating login process.")
        try:
            # Enter Email
            email_input = self.wait_until_element_is_clickable(By.XPATH, self.EMAIL_INPUT_FIELD)
            email_input.send_keys(username)
            self.logger.info("Entered email address.")

            # Click Email Next Button
            email_login_button = self.wait_until_element_is_clickable(By.XPATH, self.BUTTON_EMAIL_NEXT)
            email_login_button.click()
            self.logger.info("Clicked on 'Log in / Sign up' button.")

            # Enter Password
            password_input = self.wait_until_element_is_clickable(By.XPATH, self.PASSWORD_INPUT_FIELD)
            password_input.send_keys(password)
            self.logger.info("Entered password.")

            # Click Password Next Button
            password_login_button = self.wait_until_element_is_clickable(By.XPATH, self.BUTTON_PASSWORD_NEXT)
            password_login_button.click()
            self.logger.info("Clicked on 'Login' button.")

            # Verify Welcome Message
            welcome_message = self.wait_until_element_is_visible(By.XPATH, self.WELCOME_MESSAGE_FIELD)
            actual_welcome_text = welcome_message.text
            self.logger.debug(f"Retrieved welcome message: '{actual_welcome_text}'")
            assert actual_welcome_text == self.WELCOME_MESSAGE_TEXT, (
                f"Expected welcome message '{self.WELCOME_MESSAGE_TEXT}', but got '{actual_welcome_text}'."
            )
            self.logger.info("Login successful. Welcome message displayed.")

        except (TimeoutException, AssertionError) as e:
            self.logger.critical(f"Login failed: {str(e)}", exc_info=True)
            pytest.fail(f"Login failed: {str(e)}")

    def wait_until_element_is_clickable(self, locator_type: str, locator: str) -> Optional[WebElement]:
        """
        Waits until the specified element is clickable.

        Args:
            locator_type (By): The type of locator (e.g., By.XPATH, By.ID).
            locator (str): The locator string to identify the element.

        Returns:
            Optional[WebElement]: The clickable WebElement if found; otherwise, None.

        Raises:
            TimeoutException: If the element is not clickable within the timeout period.
        """
        self.logger.debug(f"Waiting for element to be clickable: {locator_type}='{locator}'")
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            element = wait.until(EC.element_to_be_clickable((locator_type, locator)))
            self.logger.debug(f"Element is clickable: {locator_type}='{locator}'")
            return element
        except TimeoutException as e:
            self.logger.error(f"Element not clickable after {self.wait_timeout} seconds: {locator_type}='{locator}'",
                              exc_info=True)
            raise e

    def wait_until_element_is_visible(self, locator_type: str, locator: str) -> Optional[WebElement]:
        """
        Waits until the specified element is visible on the page.

        Args:
            locator_type (By): The type of locator (e.g., By.XPATH, By.ID).
            locator (str): The locator string to identify the element.

        Returns:
            Optional[WebElement]: The visible WebElement if found; otherwise, None.

        Raises:
            TimeoutException: If the element is not visible within the timeout period.
        """
        self.logger.debug(f"Waiting for element to be visible: {locator_type}='{locator}'")
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            element = wait.until(EC.visibility_of_element_located((locator_type, locator)))
            self.logger.debug(f"Element is visible: {locator_type}='{locator}'")
            return element
        except TimeoutException as e:
            self.logger.error(f"Element not visible after {self.wait_timeout} seconds: {locator_type}='{locator}'", exc_info=True)
            raise e

    def wait_until_presence_of_element_located(self, locator_type: str, locator: str) -> Optional[WebElement]:
        """
        Waits until the specified element is present in the DOM.

        Args:
            locator_type (By): The type of locator (e.g., By.XPATH, By.ID).
            locator (str): The locator string to identify the element.

        Returns:
            Optional[WebElement]: The WebElement if found; otherwise, None.

        Raises:
            TimeoutException: If the element is not present within the timeout period.
        """
        self.logger.debug(f"Waiting for presence of element: {locator_type}='{locator}'")
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            element = wait.until(EC.presence_of_element_located((locator_type, locator)))
            self.logger.debug(f"Element is present: {locator_type}='{locator}'")
            return element
        except TimeoutException as e:
            self.logger.error(f"Element not present after {self.wait_timeout} seconds: {locator_type}='{locator}'", exc_info=True)
            raise e

    def wait_invisibility_of_element_located(self, locator_type: str, locator: str) -> Optional[WebElement]:
        """
        Waits until the specified element is invisible or not present in the DOM.

        Args:
            locator_type (By): The type of locator (e.g., By.XPATH, By.ID).
            locator (str): The locator string to identify the element.

        Returns:
            bool: True if the element is invisible; False otherwise.

        Raises:
            TimeoutException: If the element remains visible after the timeout period.
        """
        self.logger.debug(f"Waiting for invisibility of element: {locator_type}='{locator}'")
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            result = wait.until(EC.invisibility_of_element_located((locator_type, locator)))
            self.logger.debug(f"Element is invisible: {locator_type}='{locator}'")
            return result
        except TimeoutException as e:
            self.logger.error(f"Element still visible after {self.wait_timeout} seconds: {locator_type}='{locator}'", exc_info=True)
            raise e

    def return_soup(self) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object of the current page's HTML source.

        Returns:
            BeautifulSoup: Parsed HTML content of the current page.
        """
        self.logger.debug("Retrieving page source for BeautifulSoup parsing.")
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        self.logger.debug("Successfully parsed page source with BeautifulSoup.")
        return soup
