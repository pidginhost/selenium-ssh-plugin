import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.ie.service import Service as IEService
from webdriver_manager.microsoft import IEDriverManager


class DelayedWebDriver:
    def __init__(self, driver):
        self.driver = driver

    def __getattr__(self, attr):
        orig_attr = getattr(self.driver, attr)
        if callable(orig_attr):
            def delayed_method(*args, **kwargs):
                time.sleep(1)  # Add delay before each method call
                return orig_attr(*args, **kwargs)

            return delayed_method
        else:
            return orig_attr


@pytest.fixture(scope="function")
def setup(request, browser, url):
    driver = None
    if browser == "chrome":
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser == "firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    elif browser == "edge":
        driver = webdriver.Ie(service=IEService(IEDriverManager().install()))
    else:
        print("Please provide a valid browser!")

    delayed_driver = DelayedWebDriver(driver)

    driver.get(url)
    driver.maximize_window()
    request.cls.driver = delayed_driver
    yield
    driver.close()
    driver.quit()


def pytest_addoption(parser):
    parser.addoption("--browser")
    parser.addoption("--url")


@pytest.fixture(autouse=True)
def browser(request):
    return request.config.getoption("--browser")


@pytest.fixture(autouse=True)
def url(request):
    return request.config.getoption("--url")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    if report.when == "call":
        driver = item.cls.driver
        extras.append(pytest_html.extras.url(driver.current_url))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            report_directory = os.path.dirname(item.config.getoption("htmlpath"))
            file_name = report.nodeid.replace("::", "_") + ".png"
            destination_file = os.path.join(report_directory, file_name)
            driver.save_screenshot(destination_file)
            if file_name:
                html = f"""
                <div>
                    <img src="{file_name}" alt="screenshot" style="width:300px;height:200px;" onclick="window.open(this.src)" align="right"/>
                </div>
                """
                extras.append(pytest_html.extras.html(html))
        report.extras = extras


def pytest_html_report_title(report):
    report.title = "PidginHost TestFramework"
