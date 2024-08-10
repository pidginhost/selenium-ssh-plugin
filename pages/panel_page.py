from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from base.base_driver import BaseDriver
from utilities.utils import Utils
from pages.cloud_page import CloudPage
import pytest


class PanelPage(BaseDriver):
    CLOUD_BUTTON = '//a[@href="/panel/cloud/"]'
    WELCOME_CLOUD_FIELD = ('//h2[contains(@class, "mb-0") '
                           'and contains(@class, "ms-3")]')
    WELCOME_CLOUD_TEXT = 'Cloud'

    def __init__(self, driver, user, user_password, cloud_package, operating_system):
        super().__init__(driver)
        self.driver = driver
        self.utils = Utils()
        self.username = user
        self.password = user_password
        self.cloud_page = CloudPage(self.driver, cloud_package, operating_system)

    def navbar_panel_button(self):
        self.login(self.username, self.password)
        try:
            cloud_navbar_button = self.wait_until_element_is_clickable(By.XPATH, self.CLOUD_BUTTON)
            cloud_navbar_button.click()
            self.utils.custom_logger().info("Click Cloud navbar button")
            welcome_message = self.wait_until_element_is_visible(By.XPATH, self.WELCOME_CLOUD_FIELD)
            assert welcome_message.text == self.WELCOME_CLOUD_TEXT
            self.utils.custom_logger().info("Wellcome Cloud displayed")
            self.cloud_page.add_server()
        except TimeoutException:
            pytest.fail("Fail to navigate")
