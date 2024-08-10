import time

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from base.base_driver import BaseDriver
from utilities.utils import Utils
import pytest
import random
import string
from pages.details_page import DetailsPage
from ssh_tests.ssh_tests import SSHConnection
import os


class CloudPage(BaseDriver):
    PACKAGE_LI = '//li[text()="{}"]'
    INPUT_PACKAGE_OPTION = '//input[@aria-controls="select2-id_product-results"]'
    INPUT_OS_OPTION = '//input[@aria-controls="select2-id_os-results"]'
    PACKAGE_DROPDOWN = '//span[@id="select2-id_product-container"]'
    OS_DROPDOWN = '//span[@id="select2-id_os-container"]'
    CLOUD_BUTTON = '//a[@href="/panel/cloud/"]'
    CLOUD_0 = "CloudV 0"
    SSH_TESTS_INTERFACE = "Debian 12"
    CURRENT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
    PRIVATE_KEY_PATH = os.path.join(PROJECT_ROOT, 'ssh_tests', 'private_key.txt')
    PUBLIC_KEY_PATH = os.path.join(PROJECT_ROOT, 'ssh_tests', 'public_key.txt')
    ADD_NEW_SERVER_BUTTON = '//a[@id="add_server_btn"]'
    SERVER_PASSWORD = "SdF23!23^sdf"
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

    def __init__(self, driver, cloud_package, operating_system):
        super().__init__(driver)
        self.driver = driver
        self.utils = Utils()
        self.cloud_package = cloud_package
        self.operating_system = operating_system
        self.dp = DetailsPage(self.driver)
        self.sshc = SSHConnection(self.PRIVATE_KEY_PATH)

    def read_public_key_file(self):
        with open(self.PUBLIC_KEY_PATH, 'r') as file:
            return file.read()

    @staticmethod
    def generate_random_hostname():
        letters_digits = string.ascii_letters
        return ''.join(random.choice(letters_digits) for _ in range(15))

    def click_and_assert_package(self):
        try:
            new_server_add_button = self.wait_until_element_is_clickable(By.XPATH, self.ADD_NEW_SERVER_BUTTON)
            new_server_add_button.click()
            self.utils.custom_logger().info("Click Add New Server")
            package_dropdown = self.wait_until_element_is_clickable(By.XPATH, self.PACKAGE_DROPDOWN)
            package_dropdown.click()
            self.utils.custom_logger().info(f"Click package dropdown")
            input_option = self.wait_until_element_is_clickable(By.XPATH, self.INPUT_PACKAGE_OPTION)
            input_option.send_keys(self.cloud_package)
            self.utils.custom_logger().info(f"Type package name")
            package_option = self.wait_until_element_is_clickable(By.XPATH,
                                                                  self.PACKAGE_LI.replace("{}", self.cloud_package))
            package_option_text = package_option.text
            package_option.click()
            self.utils.custom_logger().info(f"Click package: {self.cloud_package}")
            assert package_option_text == self.cloud_package, (f"Expected Package: {self.cloud_package}, "
                                                               f"Actual option: {package_option_text}")
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def select_operation_system(self):
        try:
            advanced_server = self.wait_until_element_is_clickable(By.XPATH, self.ADVANCED_SERVER_BUTTON)
            advanced_server.click()
            self.utils.custom_logger().info("Click Advanced Server")
            os_dropdown = self.wait_until_element_is_clickable(By.XPATH, self.OS_DROPDOWN)
            os_dropdown.click()

            self.utils.custom_logger().info(f"Click OS dropdown")
            input_option = self.wait_until_element_is_clickable(By.XPATH, self.INPUT_OS_OPTION)
            input_option.send_keys(self.operating_system)
            self.utils.custom_logger().info(f"Type OS name")
            os_option = self.wait_until_element_is_clickable(By.XPATH,
                                                             self.PACKAGE_LI.replace("{}", self.operating_system))
            os_option_text = os_option.text
            os_option.click()
            self.utils.custom_logger().info(f"Click OS: {self.operating_system}")

            assert os_option_text == self.operating_system, (f"Expected Server OS: {self.operating_system}, "
                                                             f"Actual option: {os_option_text}")
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_hostname(self):
        try:
            host_name = self.generate_random_hostname()
            hostname_input = self.wait_until_element_is_clickable(By.XPATH, self.HOSTNAME_INPUT_FIELD)
            hostname_input.send_keys(host_name)
            self.utils.custom_logger().info(f"Fill hostname field with : {host_name}")
            return host_name
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_password(self):
        try:
            password_input = self.wait_until_element_is_clickable(By.XPATH, self.PASSWORD_INPUT_FIELD)
            password_input.send_keys(self.SERVER_PASSWORD)
            self.utils.custom_logger().info(f"Fill password field with : {self.SERVER_PASSWORD}")
            return self.SERVER_PASSWORD
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_public_key(self):
        try:
            public_key = self.read_public_key_file()
            key_input = self.wait_until_element_is_clickable(By.XPATH, self.PUBLIC_KEY_FIELD)
            key_input.send_keys(public_key)
            self.utils.custom_logger().info(f"Fill public key field with : {self.SERVER_PASSWORD}")
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def click_public_network_interface_enable(self):
        try:
            enable_button = self.wait_until_element_is_clickable(By.XPATH, self.PUBLIC_NETWORK_INTERFACES_INPUT_FIELD)
            enable_button.click()
            self.utils.custom_logger().info(f"Enable Public network interface ")
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_ipv4_and_ipv6(self):
        try:
            label_fields = {
                "IPv4 Address": self.IPV4_LABEL_FIELD,
                "IPv6 Address": self.IPV6_LABEL_FIELD
            }
            for key, value in label_fields.items():
                label_option = self.wait_until_element_is_clickable(By.XPATH, value)
                label_option.click()
                self.utils.custom_logger().info(f"Click {key} label.")
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def drag_volume_slider(self, slider):
        try:
            actions = ActionChains(self.driver)
            # Perform sliding action
            actions.move_to_element(slider).click_and_hold().move_by_offset(-240, 0).release().perform()
            time.sleep(2)
            extra_vol = self.wait_until_element_is_clickable(By.XPATH, self.EXTRA_VOLUME_GB_FIELD)
            self.utils.custom_logger().info(f"Add Extra Volume {extra_vol.text} GB")
            return extra_vol.text
        except Exception as e:
            self.utils.custom_logger().fatal(f"Can't add Extra Volume with error: {e}")
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_volume(self):
        try:
            enable_extra_volume = self.wait_until_element_is_clickable(By.XPATH, self.ENABLE_EXTRA_VOLUME_INPUT_FIELD)
            enable_extra_volume.click()
            self.utils.custom_logger().info(f"Click enable Add Extra Volume")
            slider = self.wait_until_element_is_clickable(By.XPATH, self.SIZE_VOLUME_FIELD)
            extra_volume_size = self.drag_volume_slider(slider)
            button_add_server = self.wait_until_element_is_clickable(By.XPATH, self.ADD_SERVER_BUTTON)
            button_add_server.click()
            self.utils.custom_logger().info(f"Click Add Server button")
            time.sleep(3)
            return extra_volume_size
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def check_if_cloud_have_been_created(self, host_name):
        try:
            hostname = None
            server_table = self.wait_until_presence_of_element_located(By.CSS_SELECTOR, self.SERVER_TABLE_ITEM)
            if server_table:
                soup = self.return_soup()
                hostname_strong = soup.find('strong', string='Hostname')
                if hostname_strong:
                    hostname_td = hostname_strong.find_parent('td')
                    if hostname_td:
                        hostname = hostname_td.get_text(strip=True).split(':')[-1].strip()
                        self.utils.custom_logger().info(f"Hostname: {hostname}")

                assert host_name == hostname, (f"Expected Hostname: {host_name}, "
                                               f"Actual Hostname: {hostname}")
                self.utils.custom_logger().info(f"Server Name: {hostname} have been created Successfully!")
        except Exception as e:
            pytest.fail(f"Failed due to Exception: {e}")

    def destroy_server(self, server_hostname):
        try:
            time.sleep(2)
            cloud_navbar_button = self.wait_until_element_is_clickable(By.XPATH, self.CLOUD_BUTTON)
            cloud_navbar_button.click()
            self.utils.custom_logger().info("Click Cloud navbar button")
            destroy_server_button1 = self.wait_until_element_is_clickable(By.XPATH, self.DESTROY_BUTTON1)
            destroy_server_button1.click()
            self.utils.custom_logger().info(f"Click Destroy Server Button1!")
            time.sleep(3)
            destroy_server_button2 = self.wait_until_element_is_clickable(By.XPATH, self.DESTROY_BUTTON2)
            destroy_server_button2.click()
            self.utils.custom_logger().info(f"Click Destroy Server Button2!")
            self.wait_invisibility_of_element_located(By.XPATH, self.DETAILS_BUTTON)
            self.utils.custom_logger().info(f"Server {server_hostname} have been destroyed!")
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def click_details_button(self):
        try:
            self.wait_until_element_is_clickable(By.XPATH, self.PROVISIONING_ITEM)
            details = self.wait_until_element_is_clickable(By.XPATH, self.DETAILS_BUTTON)
            details.click()
            self.utils.custom_logger().info(f"Click Details Button!")
        except TimeoutException as e:
            pytest.fail(f"Failed due to TimeoutException: {e}")

    def add_server(self):
        self.click_and_assert_package()
        self.select_operation_system()
        host_name = self.add_hostname()
        self.add_public_key()
        cloud_password = self.add_password()
        self.click_public_network_interface_enable()
        self.add_ipv4_and_ipv6()
        extra_volume_size = self.add_volume()
        self.check_if_cloud_have_been_created(host_name)
        self.click_details_button()
        ip_element = self.dp.get_cloud_ip()
        cloud_user = self.dp.get_cloud_user()
        assert_data = self.sshc.test_ssh_functionality(ip_element, cloud_user, cloud_password, self.CLOUD_0,
                                                       self.SSH_TESTS_INTERFACE, self.cloud_package,
                                                       self.operating_system, extra_volume_size)
        self.destroy_server(host_name)
        if assert_data:
            assert False, f"Bad errors {assert_data}"
