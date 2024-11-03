import re
from typing import Optional
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from base.base_driver import BaseDriver


class DetailsPage(BaseDriver):
    """
    DetailsPage class encapsulates functionalities specific to the Details page,
    such as retrieving the cloud IP and user information.
    """

    # Locators
    ACTIVE_BADGE = '//span[contains(@class, "bg-success") and contains(text(), "ACTIVE")]'
    DETAILS_BUTTON = '//a[contains(@href, "/panel/cloud/servers/") and contains(text(), "Details")]'
    USER_SPAN_ITEM = "//span[@data-bs-toggle='popover']"

    # Regex Patterns
    IPV4_REGEX = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    IPV6_REGEX = r'[a-f0-9:]+:[a-f0-9:]+'

    def __init__(self, driver):
        """
        Initializes the DetailsPage with a WebDriver instance and sets up logging.

        Args:
            driver: Selenium WebDriver instance.
        """
        super().__init__(driver)
        # self.utils is already initialized in BaseDriver
        # self.logger is also initialized in BaseDriver

    def get_cloud_ip(self, ipv_type: str = 'IPv4') -> Optional[str]:
        """
        Retrieves the cloud IP address from the Details page.

        Args:
            ipv_type (str): Type of IP to retrieve ('IPv4' or 'IPv6'). Defaults to 'IPv4'.

        Returns:
            Optional[str]: The retrieved IP address if found; otherwise, None.

        Raises:
            pytest.fail: If the IP address cannot be found or any other exception occurs.
        """
        self.logger.debug(f"Attempting to retrieve {ipv_type} address.")

        # Select the appropriate regex based on ipv_type
        if ipv_type.upper() == 'IPv6':
            ip_regex = self.IPV6_REGEX
        else:
            ip_regex = self.IPV4_REGEX

        try:
            # Wait until the ACTIVE_BADGE is visible to ensure the page is loaded
            self.wait_until_element_is_visible(By.XPATH, self.ACTIVE_BADGE)
            self.logger.debug("Active badge is visible. Proceeding to retrieve IP address.")

            # Instead of time.sleep, wait for the element containing the IP to be present
            # Assuming that the IP is within a specific element; adjust the locator as needed
            # Here, using BeautifulSoup as in the original code

            soup = self.return_soup()
            ip_pattern = re.compile(ip_regex)
            p_element = soup.find('span', string=ip_pattern)

            if p_element:
                ip_element_text = p_element.get_text().strip()
                self.logger.info(f"Retrieved {ipv_type} address: {ip_element_text}")
                return ip_element_text
            else:
                self.logger.error(f"No IP element found matching the regex pattern: {ip_regex}")
                pytest.fail(f"No IP element found matching the regex pattern: {ip_regex}")

        except TimeoutException as e:
            self.logger.critical(f"Timeout while waiting for the active badge or IP element: {e}", exc_info=True)
            pytest.fail(f"Timeout while retrieving the cloud IP: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while retrieving the cloud IP: {e}", exc_info=True)
            pytest.fail(f"An unexpected error occurred while retrieving the cloud IP: {e}")

    def get_cloud_user(self) -> Optional[str]:
        """
        Retrieves the cloud user name from the Details page.

        Returns:
            Optional[str]: The retrieved cloud user name if found; otherwise, None.

        Raises:
            pytest.fail: If the cloud user name cannot be found or any other exception occurs.
        """
        self.logger.debug("Attempting to retrieve cloud user name.")
        try:
            # Wait until the USER_SPAN_ITEM is clickable
            user_element = self.wait_until_element_is_clickable(By.XPATH, self.USER_SPAN_ITEM)
            user_name = user_element.text.strip()
            self.logger.info(f"Retrieved cloud user name: {user_name}")

            if user_name:
                # Instead of time.sleep, ensure that any dynamic content is loaded
                # If necessary, implement additional waits here
                return user_name
            else:
                self.logger.error("No cloud user name found.")
                pytest.fail("No cloud user name found.")

        except TimeoutException as e:
            self.logger.critical(f"Timeout while waiting for the cloud user name element: {e}", exc_info=True)
            pytest.fail(f"Timeout while retrieving the cloud user name: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while retrieving the cloud user name: {e}", exc_info=True)
            pytest.fail(f"An unexpected error occurred while retrieving the cloud user name: {e}")
