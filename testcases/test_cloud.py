import os
import pytest
import softest
from ddt import ddt, data, unpack

from pages.panel_page import PanelPage
from utilities.utils import Utils


@ddt
@pytest.mark.usefixtures("setup")
class TestCloud(softest.TestCase):
    """
    TestCloud class contains test cases for the Cloud functionalities,
    including server creation and SSH connectivity.
    """

    # Constants for file paths
    CURRENT_DIR: str = os.path.dirname(__file__)
    PROJECT_ROOT: str = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
    DATA_FILE_PATH: str = os.path.join(PROJECT_ROOT, 'testdata', 'testdata.xlsx')

    @pytest.fixture(autouse=True)
    def class_setup(self, setup):
        """
        Fixture to set up utilities before each test case.

        Args:
            setup: The WebDriver instance provided by the setup fixture.
        """
        self.utils: Utils = Utils()
        self.logger = self.utils.custom_logger()
        self.logger.info("Initialized TestCloud test case.")

    @data(*Utils().read_data_from_excel_file(DATA_FILE_PATH, "Sheet"))
    @unpack
    def test_cloud(
        self,
        user: str,
        user_password: str,
        cloud_package: str,
        operating_system: str,
        ssh_connection_type: str,
    ) -> None:
        """
        Test case for adding a new cloud server and verifying its functionality.

        Args:
            user (str): Username for login.
            user_password (str): Password for login.
            cloud_package (str): The cloud package to be used.
            operating_system (str): The operating system to be selected.
            ssh_connection_type (str): The type of SSH connection (e.g., SSH Key, Password).
        """
        self.logger.info("Starting test_cloud with parameters:")
        self.logger.info(f"User: {user}, Cloud Package: {cloud_package}, "
                         f"Operating System: {operating_system}, SSH Connection Type: {ssh_connection_type}")

        try:
            # Initialize PanelPage with provided parameters
            panel_page = PanelPage(
                driver=self.driver,
                user=user,
                user_password=user_password,
                cloud_package=cloud_package,
                operating_system=operating_system,
                ssh_connection_type=ssh_connection_type
            )
            self.logger.info("Initialized PanelPage object.")

            # Navigate to Cloud section and add server
            panel_page.navbar_panel_button()
            self.logger.info("Successfully navigated to Cloud section and initiated server addition.")

        except AssertionError as e:
            self.logger.error(f"Assertion failed during test_cloud: {e}", exc_info=True)
            self.soft_assert(self.assertFalse, True, f"Assertion failed: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during test_cloud: {e}", exc_info=True)
            self.soft_assert(self.assertFalse, True, f"Unexpected error: {e}")

        # Perform soft assertions
        self.assert_all()

