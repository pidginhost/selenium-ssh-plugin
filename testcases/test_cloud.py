import os
from pages.panel_page import PanelPage
import pytest
from utilities.utils import Utils
import softest
from ddt import ddt, data, unpack


@pytest.mark.usefixtures("setup")
@ddt
class TestCloud(softest.TestCase, ):
    CURRENT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
    DATA_FILE_PATH = os.path.join(PROJECT_ROOT, 'testdata', 'testdata.xlsx')

    @pytest.fixture(autouse=True)
    def class_setup(self, setup):
        self.utils = Utils()

    @data(*Utils().read_data_from_excel_file(DATA_FILE_PATH, "Sheet"))
    @unpack
    def test_cloud(self, user, user_password, cloud_package, operating_system):
        PanelPage(self.driver, user, user_password, cloud_package, operating_system).navbar_panel_button()
