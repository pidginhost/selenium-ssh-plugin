from typing import Optional

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from base.base_driver import BaseDriver
from pages.cloud_page import CloudPage
from utilities.utils import Utils


class PanelPage(BaseDriver):
    """
    PanelPage class encapsulates functionalities specific to the user panel,
    such as navigating to the Cloud section and initiating server creation.
    """

    # Locators
    CLOUD_BUTTON = '//a[@href="/panel/cloud/"]'
    WELCOME_CLOUD_FIELD = '//h2[contains(@class, "mb-0") and contains(@class, "ms-3")]'
    WELCOME_CLOUD_TEXT = 'Cloud'

    def __init__(
        self,
        driver,
        user: str,
        user_password: str,
        cloud_package: str,
        operating_system: str,
        ssh_connection_type: str
    ):
        """
        Initializes the PanelPage with a WebDriver instance and user credentials.

        Args:
            driver: Selenium WebDriver instance.
            user (str): Username for login.
            user_password (str): Password for login.
            cloud_package (str): The cloud package to be used.
            operating_system (str): The operating system to be selected.
            ssh_connection_type (str): The type of SSH connection (e.g., SSH Key, Password).
        """
        super().__init__(driver)
        self.user = user
        self.user_password = user_password
        self.cloud_page = CloudPage(driver, cloud_package, operating_system, ssh_connection_type)
        self.logger = Utils().custom_logger()

    def navbar_panel_button(self) -> None:
        """
        Navigates to the Cloud section via the navbar and initiates the server addition process.

        Raises:
            TimeoutException: If navigation elements are not found within the timeout.
            AssertionError: If the welcome message does not match the expected text.
        """
        self.logger.debug("Starting navigation to Cloud section via navbar.")
        try:
            # Perform login
            self.login(self.user, self.user_password)
            self.logger.info(f"Logged in as user: {self.user}")

            # Click on Cloud Navbar Button
            cloud_navbar_button = self.wait_until_element_is_clickable(By.XPATH, self.CLOUD_BUTTON)
            cloud_navbar_button.click()
            self.logger.info("Clicked on 'Cloud' navbar button.")

            # Verify Welcome Message
            welcome_message_element = self.wait_until_element_is_visible(By.XPATH, self.WELCOME_CLOUD_FIELD)
            actual_welcome_text = welcome_message_element.text.strip()
            assert actual_welcome_text == self.WELCOME_CLOUD_TEXT, (
                f"Expected welcome text '{self.WELCOME_CLOUD_TEXT}', but got '{actual_welcome_text}'."
            )
            self.logger.info("Welcome Cloud message displayed correctly.")

            # Initiate server addition
            self.cloud_page.add_server()
            self.logger.info("Initiated server addition process.")

        except TimeoutException as e:
            self.logger.error(f"Timeout while navigating to Cloud section: {e}", exc_info=True)
            pytest.fail("Failed to navigate to Cloud section due to TimeoutException.")
        except AssertionError as e:
            self.logger.error(f"Assertion failed: {e}", exc_info=True)
            pytest.fail(f"Assertion failed: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during navigation: {e}", exc_info=True)
            pytest.fail(f"Failed due to an unexpected exception: {e}")