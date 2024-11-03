import os
import random
import string
from typing import Optional
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from base.base_driver import BaseDriver
from pages.details_page import DetailsPage
from ssh_tests.ssh_tests import SSHConnection


class CloudPage(BaseDriver):
    """
    CloudPage class encapsulates functionalities specific to the Cloud page,
    such as server management, SSH key handling, and interacting with cloud packages.
    """

    # Authentication Methods
    SSH_KEY_AUTHENTICATION = "SSH Key"
    PASSWORD_AUTHENTICATION = "Password"

    # Locators
    PACKAGE_LI = '//li[text()="{}"]'
    INPUT_PACKAGE_OPTION = '//input[@aria-controls="select2-id_product-results"]'
    INPUT_OS_OPTION = '//input[@aria-controls="select2-id_os-results"]'
    PACKAGE_DROPDOWN = '//span[@id="select2-id_product-container"]'
    OS_DROPDOWN = '//span[@id="select2-id_os-container"]'
    CLOUD_BUTTON = '//a[@href="/panel/cloud/"]'
    ADD_NEW_SERVER_BUTTON = '//a[@id="add_server_btn"]'
    PUBLIC_KEY_FIELD = '//textarea[@id="id_ssh_pub_key"]'
    ADVANCED_SERVER_BUTTON = '//button[@data-bs-target="#advanced-options"]'
    SELECT_OS_ELEMENT = '//select[@id="id_os"]'
    SELECT_PACKAGE_ELEMENT = '//select[@id="id_product"]'
    HOSTNAME_INPUT_FIELD = '//input[@id="id_hostname"]'
    SERVER_PASSWORD_INPUT_FIELD = '//input[@id="id_password"]'
    PUBLIC_NETWORK_INTERFACES_INPUT_FIELD = '//input[@id="id_public_interface"]'
    IPV4_LABEL_FIELD = "//label[normalize-space()='IPv4 Address']"
    IPV6_LABEL_FIELD = "//label[normalize-space()='IPv6 Address']"
    ENABLE_EXTRA_VOLUME_INPUT_FIELD = "//input[@id='id_extra_volume']"
    SIZE_VOLUME_FIELD = "//input[@id='sizeInput']"
    EXTRA_VOLUME_GB_FIELD = "//span[@id='sizeValue']"
    ADD_SERVER_BUTTON = '//button[text()="Add server"]'
    SERVER_TABLE_ITEM = '.table.table-striped'
    DESTROY_BUTTON1 = '//a[normalize-space()="Destroy"]'
    DESTROY_BUTTON2 = '//button[normalize-space()="Destroy"]'
    DETAILS_BUTTON = '//a[normalize-space()="Details"]'
    PROVISIONING_ITEM = '//span[normalize-space()="Active"]'

    # Constants
    CLOUD_0 = "CloudV 0"
    SSH_TESTS_INTERFACE = "Debian 12"
    SERVER_PASSWORD = "SdF23!23^sdf"

    # Paths
    CURRENT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
    PRIVATE_KEY_PATH = os.path.join(PROJECT_ROOT, 'ssh_tests', 'private_key.txt')
    PUBLIC_KEY_PATH = os.path.join(PROJECT_ROOT, 'ssh_tests', 'public_key.txt')

    def __init__(
        self,
        driver,
        cloud_package: str,
        operating_system: str,
        ssh_connection_type: str
    ):
        """
        Initializes the CloudPage with a WebDriver instance and necessary configurations.

        Args:
            driver: Selenium WebDriver instance.
            cloud_package (str): The cloud package to be used.
            operating_system (str): The operating system to be selected.
            ssh_connection_type (str): The type of SSH connection (e.g., SSH Key, Password).
        """
        super().__init__(driver)
        self.cloud_package = cloud_package
        self.operating_system = operating_system
        self.ssh_connection_type = ssh_connection_type
        self.details_page = DetailsPage(self.driver)
        self.ssh_connection = SSHConnection(self.PRIVATE_KEY_PATH)
        self.logger = self.utils.custom_logger()

    def read_public_key_file(self) -> str:
        """
        Reads and returns the content of the public SSH key file.

        Returns:
            str: The content of the public SSH key.

        Raises:
            FileNotFoundError: If the public key file does not exist.
            IOError: If an I/O error occurs while reading the file.
        """
        self.logger.info(f"Attempting to read public key from: {self.PUBLIC_KEY_PATH}")
        try:
            with open(self.PUBLIC_KEY_PATH, 'r') as file:
                public_key = file.read().strip()
                self.logger.info("Successfully read public SSH key.")
                return public_key
        except FileNotFoundError as e:
            self.logger.error(f"Public key file not found: {e}")
            raise
        except IOError as e:
            self.logger.error(f"Error reading public key file: {e}")
            raise

    def generate_random_hostname(self, length: int = 15) -> str:
        """
        Generates a random hostname consisting of alphanumeric characters,
        ensuring that it does not start with a digit.

        Args:
            length (int): The total length of the hostname. Must be at least 1.

        Returns:
            str: A randomly generated hostname starting with a letter.

        Raises:
            ValueError: If the specified length is less than 1.
        """
        if length < 1:
            raise ValueError("Hostname length must be at least 1.")

        # First character must be a letter
        first_char = random.choice(string.ascii_letters)
        self.logger.debug(f"First character (letter): {first_char}")

        if length == 1:
            hostname = first_char
        else:
            # Remaining characters can be letters or digits
            remaining_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length - 1))
            self.logger.debug(f"Remaining characters: {remaining_chars}")
            hostname = first_char + remaining_chars

        self.logger.info(f"Generated random hostname: {hostname}")
        return hostname

    def click_and_assert_package(self) -> None:
        """
        Clicks on the 'Add New Server' button, selects the cloud package from the dropdown,
        and asserts that the selected package matches the expected value.

        Raises:
            TimeoutException: If any of the elements are not found within the timeout.
            AssertionError: If the selected package does not match the expected value.
        """
        self.logger.info("Initiating package selection process.")
        try:
            # Click on Add New Server Button
            add_server_btn = self.wait_until_element_is_clickable(By.XPATH, self.ADD_NEW_SERVER_BUTTON)
            add_server_btn.click()
            self.logger.info("Clicked on 'Add New Server' button.")

            # Click on Package Dropdown
            package_dropdown = self.wait_until_element_is_clickable(By.XPATH, self.PACKAGE_DROPDOWN)
            package_dropdown.click()
            self.logger.info("Clicked on package dropdown.")

            # Type Package Name
            input_option = self.wait_until_element_is_clickable(By.XPATH, self.INPUT_PACKAGE_OPTION)
            input_option.send_keys(self.cloud_package)
            self.logger.info(f"Typed package name: {self.cloud_package}")

            # Click on Package Option
            package_option_xpath = self.PACKAGE_LI.format(self.cloud_package)
            package_option = self.wait_until_element_is_clickable(By.XPATH, package_option_xpath)
            package_option_text = package_option.text
            package_option.click()
            self.logger.info(f"Clicked on package option: {self.cloud_package}")

            # Assert Package Selection
            assert package_option_text == self.cloud_package, (
                f"Expected Package: {self.cloud_package}, Actual option: {package_option_text}"
            )
            self.logger.info("Package selection asserted successfully.")

        except TimeoutException as e:
            self.logger.error(f"Timeout while selecting package '{self.cloud_package}': {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")
        except AssertionError as e:
            self.logger.error(f"Assertion failed during package selection: {e}", exc_info=True)
            pytest.fail(f"Assertion failed: {e}")

    def select_operating_system(self) -> None:
        """
        Clicks on the 'Advanced Server' button, selects the operating system from the dropdown,
        and asserts that the selected OS matches the expected value.

        Raises:
            TimeoutException: If any of the elements are not found within the timeout.
            AssertionError: If the selected OS does not match the expected value.
        """
        self.logger.info("Initiating operating system selection process.")
        try:
            # Click on Advanced Server Button
            advanced_server_btn = self.wait_until_element_is_clickable(By.XPATH, self.ADVANCED_SERVER_BUTTON)
            advanced_server_btn.click()
            self.logger.info("Clicked on 'Advanced Server' button.")

            # Click on OS Dropdown
            os_dropdown = self.wait_until_element_is_clickable(By.XPATH, self.OS_DROPDOWN)
            os_dropdown.click()
            self.logger.info("Clicked on OS dropdown.")

            # Type OS Name
            input_option = self.wait_until_element_is_clickable(By.XPATH, self.INPUT_OS_OPTION)
            input_option.send_keys(self.operating_system)
            self.logger.info(f"Typed OS name: {self.operating_system}")

            # Click on OS Option
            os_option_xpath = self.PACKAGE_LI.format(self.operating_system)
            os_option = self.wait_until_element_is_clickable(By.XPATH, os_option_xpath)
            os_option_text = os_option.text
            os_option.click()
            self.logger.info(f"Clicked on OS option: {self.operating_system}")

            # Assert OS Selection
            assert os_option_text == self.operating_system, (
                f"Expected Server OS: {self.operating_system}, Actual option: {os_option_text}"
            )
            self.logger.info("Operating system selection asserted successfully.")

        except TimeoutException as e:
            self.logger.error(f"Timeout while selecting OS '{self.operating_system}': {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")
        except AssertionError as e:
            self.logger.error(f"Assertion failed during OS selection: {e}", exc_info=True)
            pytest.fail(f"Assertion failed: {e}")

    def add_hostname(self) -> str:
        """
        Generates a random hostname and fills it into the hostname input field.

        Returns:
            str: The generated hostname.

        Raises:
            TimeoutException: If the hostname input field is not found within the timeout.
        """
        self.logger.info("Initiating hostname addition process.")
        try:
            hostname = self.generate_random_hostname()
            hostname_input = self.wait_until_element_is_clickable(By.XPATH, self.HOSTNAME_INPUT_FIELD)
            hostname_input.send_keys(hostname)
            self.logger.info(f"Filled hostname field with: {hostname}")
            return hostname
        except TimeoutException as e:
            self.logger.error(f"Timeout while adding hostname: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_password(self) -> str:
        """
        Fills the server password into the password input field.

        Returns:
            str: The server password.

        Raises:
            TimeoutException: If the password input field is not found within the timeout.
        """
        self.logger.info("Initiating password addition process.")
        try:
            password_input = self.wait_until_element_is_clickable(By.XPATH, self.SERVER_PASSWORD_INPUT_FIELD)
            password_input.send_keys(self.SERVER_PASSWORD)
            self.logger.info(f"Filled password field with: {self.SERVER_PASSWORD}")
            return self.SERVER_PASSWORD
        except TimeoutException as e:
            self.logger.error(f"Timeout while adding password: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_public_key(self) -> None:
        """
        Reads the public SSH key from file and fills it into the public key input field.

        Raises:
            TimeoutException: If the public key input field is not found within the timeout.
        """
        self.logger.info("Initiating public key addition process.")
        try:
            public_key = self.read_public_key_file()
            key_input = self.wait_until_element_is_clickable(By.XPATH, self.PUBLIC_KEY_FIELD)
            key_input.send_keys(public_key)
            self.logger.info("Filled public key field successfully.")
        except TimeoutException as e:
            self.logger.error(f"Timeout while adding public key: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")
        except Exception as e:
            self.logger.error(f"Error while adding public key: {e}", exc_info=True)
            pytest.fail(f"Failed due to Exception: {e}")

    def click_public_network_interface_enable(self) -> None:
        """
        Enables the public network interface by clicking the corresponding checkbox.

        Raises:
            TimeoutException: If the public network interface checkbox is not found within the timeout.
        """
        self.logger.info("Initiating public network interface enable process.")
        try:
            enable_button = self.wait_until_element_is_clickable(By.XPATH, self.PUBLIC_NETWORK_INTERFACES_INPUT_FIELD)
            enable_button.click()
            self.logger.info("Enabled public network interface.")
        except TimeoutException as e:
            self.logger.error(f"Timeout while enabling public network interface: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_ipv4_and_ipv6(self) -> None:
        """
        Clicks on the IPv4 and IPv6 address labels to add them to the server configuration.

        Raises:
            TimeoutException: If the IPv4 or IPv6 label elements are not found within the timeout.
        """
        self.logger.info("Initiating IPv4 and IPv6 addition process.")
        try:
            label_fields = {
                "IPv4 Address": self.IPV4_LABEL_FIELD,
                "IPv6 Address": self.IPV6_LABEL_FIELD
            }
            for key, xpath in label_fields.items():
                label_element = self.wait_until_element_is_clickable(By.XPATH, xpath)
                label_element.click()
                self.logger.info(f"Clicked on {key} label.")
        except TimeoutException as e:
            self.logger.error(f"Timeout while adding key: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def check_slider(self) -> str:
        """
        Retrieves the extra volume size from the slider element.

        Returns:
            str: The size of the extra volume in GB.

        Raises:
            Exception: If unable to retrieve the extra volume size.
        """
        self.logger.info("Initiating extra volume size retrieval process.")
        try:
            # Wait for the size volume slider to be clickable
            self.wait_until_element_is_clickable(By.XPATH, self.SIZE_VOLUME_FIELD)
            extra_vol_element = self.wait_until_element_is_clickable(By.XPATH, self.EXTRA_VOLUME_GB_FIELD)
            extra_volume_size = extra_vol_element.text
            self.logger.info(f"Retrieved extra volume size: {extra_volume_size} GB")
            return extra_volume_size
        except TimeoutException as e:
            self.logger.fatal(f"Timeout while retrieving extra volume size: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")
        except Exception as e:
            self.logger.error(f"Error while retrieving extra volume size: {e}", exc_info=True)
            pytest.fail(f"Failed due to Exception: {e}")

    def add_volume(self) -> str:
        """
        Enables the extra volume option, retrieves the volume size, and adds the server.

        Returns:
            str: The size of the extra volume in GB.

        Raises:
            TimeoutException: If any of the elements are not found within the timeout.
        """
        self.logger.info("Initiating extra volume addition process.")
        try:
            # Enable Extra Volume
            enable_extra_volume = self.wait_until_element_is_clickable(By.XPATH, self.ENABLE_EXTRA_VOLUME_INPUT_FIELD)
            enable_extra_volume.click()
            self.logger.info("Enabled extra volume option.")

            # Retrieve Extra Volume Size
            extra_volume_size = self.check_slider()

            # Click on Add Server Button
            add_server_btn = self.wait_until_element_is_clickable(By.XPATH, self.ADD_SERVER_BUTTON)
            add_server_btn.click()
            self.logger.info("Clicked on 'Add Server' button.")

            # Wait for the server to be added (could be improved with explicit waits)
            self.wait_until_element_is_clickable(By.XPATH, self.PROVISIONING_ITEM)
            self.logger.info("Server is provisioning.")

            return extra_volume_size

        except TimeoutException as e:
            self.logger.error(f"Timeout while adding volume: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def check_if_cloud_has_been_created(self, host_name: str) -> None:
        """
        Checks if the cloud server has been successfully created by verifying the hostname.

        Args:
            host_name (str): The expected hostname of the created server.

        Raises:
            AssertionError: If the hostname does not match the expected value.
            TimeoutException: If the server table is not found within the timeout.
        """
        self.logger.info(f"Verifying if cloud server '{host_name}' has been created.")
        try:
            server_table = self.wait_until_presence_of_element_located(By.CSS_SELECTOR, self.SERVER_TABLE_ITEM)
            if server_table:
                soup = self.return_soup()
                hostname_strong = soup.find('strong', string='Hostname')
                if hostname_strong:
                    hostname_td = hostname_strong.find_parent('td')
                    if hostname_td:
                        actual_hostname = hostname_td.get_text(strip=True).split(':')[-1].strip()
                        self.logger.info(f"Retrieved hostname: {actual_hostname}")

                        # Assert Hostname
                        assert host_name == actual_hostname, (
                            f"Expected Hostname: {host_name}, Actual Hostname: {actual_hostname}"
                        )
                        self.logger.info(f"Server '{actual_hostname}' has been created successfully!")
                    else:
                        self.logger.error("Hostname TD element not found.")
                        pytest.fail("Hostname TD element not found.")
                else:
                    self.logger.error("Hostname strong element not found.")
                    pytest.fail("Hostname strong element not found.")
            else:
                self.logger.error("Server table not found.")
                pytest.fail("Server table not found.")

        except TimeoutException as e:
            self.logger.error(f"Timeout while verifying server creation: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")
        except AssertionError as e:
            self.logger.error(f"Assertion failed while verifying server creation: {e}", exc_info=True)
            pytest.fail(f"Assertion failed: {e}")
        except Exception as e:
            self.logger.error(f"Error while verifying server creation: {e}", exc_info=True)
            pytest.fail(f"Failed due to Exception: {e}")

    def destroy_server(self, server_hostname: str) -> None:
        """
        Destroys the specified server by its hostname.

        Args:
            server_hostname (str): The hostname of the server to be destroyed.

        Raises:
            TimeoutException: If any of the elements are not found within the timeout.
        """
        self.logger.info(f"Initiating server destruction for: {server_hostname}")
        try:
            # Wait and click on Cloud Navbar Button
            cloud_navbar_btn = self.wait_until_element_is_clickable(By.XPATH, self.CLOUD_BUTTON)
            cloud_navbar_btn.click()
            self.logger.info("Clicked on 'Cloud' navbar button.")

            # Click on Destroy Button 1
            destroy_btn1 = self.wait_until_element_is_clickable(By.XPATH, self.DESTROY_BUTTON1)
            destroy_btn1.click()
            self.logger.info("Clicked on first 'Destroy' button.")

            # Optional wait before clicking Destroy Button 2
            self.wait_until_element_is_clickable(By.XPATH, self.DESTROY_BUTTON2)
            destroy_btn2 = self.wait_until_element_is_clickable(By.XPATH, self.DESTROY_BUTTON2)
            destroy_btn2.click()
            self.logger.info("Clicked on second 'Destroy' button in confirmation modal.")

            # Wait until the Details Button is no longer visible
            self.wait_invisibility_of_element_located(By.XPATH, self.DETAILS_BUTTON)
            self.logger.info(f"Server '{server_hostname}' has been destroyed successfully!")

        except TimeoutException as e:
            self.logger.error(f"Timeout while destroying server '{server_hostname}': {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")
        except Exception as e:
            self.logger.error(f"Error while destroying server '{server_hostname}': {e}", exc_info=True)
            pytest.fail(f"Failed due to Exception: {e}")

    def click_details_button(self) -> None:
        """
        Clicks on the 'Details' button of the provisioning item.

        Raises:
            TimeoutException: If any of the elements are not found within the timeout.
        """
        self.logger.info("Initiating 'Details' button click process.")
        try:
            # Wait for Provisioning Item to be visible
            provisioning_item = self.wait_until_element_is_clickable(By.XPATH, self.PROVISIONING_ITEM)
            provisioning_item.click()
            self.logger.info("Clicked on 'Provisioning' item.")

            # Click on Details Button
            details_btn = self.wait_until_element_is_clickable(By.XPATH, self.DETAILS_BUTTON)
            details_btn.click()
            self.logger.info("Clicked on 'Details' button.")
        except TimeoutException as e:
            self.logger.error(f"Timeout while clicking 'Details' button: {e}", exc_info=True)
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_server(self) -> None:
        """
        Adds a new server by performing a series of actions:
        - Click and assert package selection
        - Select operating system
        - Add hostname
        - Add SSH key or password
        - Enable public network interface
        - Add IPv4 and IPv6
        - Add volume
        - Verify server creation
        - Click details button
        - Perform SSH functionality test
        - Destroy the server

        Raises:
            AssertionError: If any of the assertions fail during the process.
        """
        self.logger.info("Initiating server addition process.")
        try:
            # Click and assert package
            self.click_and_assert_package()

            # Select operating system
            self.select_operating_system()

            # Add hostname
            host_name = self.add_hostname()

            # Add SSH key or password based on the connection type
            cloud_password: Optional[str] = None
            if self.ssh_connection_type == self.SSH_KEY_AUTHENTICATION:
                self.add_public_key()
            elif self.ssh_connection_type == self.PASSWORD_AUTHENTICATION:
                cloud_password = self.add_password()
            else:
                self.logger.error(f"Unsupported SSH connection type: {self.ssh_connection_type}")
                pytest.fail(f"Unsupported SSH connection type: {self.ssh_connection_type}")

            # Enable public network interface
            self.click_public_network_interface_enable()

            # Add IPv4 and IPv6
            self.add_ipv4_and_ipv6()

            # Add volume and retrieve the size
            extra_volume_size = self.add_volume()

            # Verify if cloud server has been created
            self.check_if_cloud_has_been_created(host_name)

            # Click on Details button
            self.click_details_button()

            # Retrieve IP and user details
            ip_element = self.details_page.get_cloud_ip()
            cloud_user = self.details_page.get_cloud_user()

            # Perform SSH functionality test
            assert_data = self.ssh_connection.test_ssh_functionality(
                cloud_server_ip=ip_element,
                username=cloud_user,
                password=cloud_password,
                cloud_0=self.CLOUD_0,
                ssh_test_interface=self.SSH_TESTS_INTERFACE,
                cloud_package=self.cloud_package,
                operating_system=self.operating_system,
                extra_volume_size=extra_volume_size,
                ssh_connection_type=self.ssh_connection_type,
                ssh_key_authentication=self.SSH_KEY_AUTHENTICATION,
                password_authentication=self.PASSWORD_AUTHENTICATION
            )

            # Destroy the server after testing
            self.destroy_server(host_name)

            # Assert SSH functionality test results
            if assert_data:
                self.logger.error(f"SSH functionality test failed with errors: {assert_data}")
                assert False, f"Bad errors {assert_data}"
            else:
                self.logger.info("SSH functionality test passed successfully.")

        except AssertionError as e:
            self.logger.error(f"Assertion failed during server addition: {e}", exc_info=True)
            pytest.fail(f"Assertion failed: {e}")
        except Exception as e:
            self.logger.error(f"Error during server addition: {e}", exc_info=True)
            pytest.fail(f"Failed due to Exception: {e}")