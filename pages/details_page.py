import time

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from base.base_driver import BaseDriver
from utilities.utils import Utils
import pytest
import re


class DetailsPage(BaseDriver):
    ACTIVE_BADGE = ('//span[contains(@class, "bg-success") '
                    'and contains(text(), "ACTIVE")]')
    DETAILS_BUTTON = ('//a[contains(@href, "/panel/cloud/servers/") '
                      'and contains(text(), "Details")]')
    USER_SPAN_ITEM = "//span[@data-bs-toggle='popover']"
    IPV4_REGEX = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    IPV6_REGEX = r'[a-f0-9:]+:[a-f0-9:]+'

    def __init__(self, driver, ):
        super().__init__(driver)
        self.driver = driver
        self.utils = Utils()

    def get_cloud_ip(self):
        try:
            time.sleep(15)
            ip_regex = self.IPV4_REGEX
            soup = self.return_soup()
            ip_pattern = re.compile(ip_regex)
            p_element = soup.find('span', string=ip_pattern)
            ip_element_text = p_element.get_text()
            assert ip_element_text is not None, (f"No IP element found with the regex pattern: {ip_regex},"
                                                 f" result is {ip_element_text}")
            return ip_element_text
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def get_cloud_user(self):
        try:
            user_name = self.wait_until_element_is_clickable(By.XPATH, self.USER_SPAN_ITEM)
            user_name = user_name.text.strip()
            self.utils.custom_logger().info(f"Find Cloud user name {user_name}")
            assert user_name, f"No Cloud User Name found"
            time.sleep(15)
            return user_name
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")
