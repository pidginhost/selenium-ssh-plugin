from selenium.webdriver.ie.options import Options as IEOOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.ie.service import Service as IEService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
import os
import time
import logging
import inspect
from typing import Generator, Optional

import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from utilities.utils import Utils

# Constants
REMOTE_URL = "http://selenium-server:4444/wd/hub"


# Configure the root logger


class DelayedWebDriver:
    """
    A wrapper class for Selenium WebDriver that introduces a configurable delay before every method call.

    This can be useful in cases where interactions with the web page need to be delayed,
    for example, to avoid triggering anti-bot measures or to ensure all elements have loaded.

    Attributes:
        driver (WebDriver): The WebDriver instance to be wrapped.
        delay (float): The delay in seconds before each method call.
    """

    def __init__(self, driver: WebDriver, delay: float = 1.0):
        """
        Initialize the DelayedWebDriver with a Selenium WebDriver instance and a delay.

        Args:
            driver (WebDriver): A Selenium WebDriver instance to be wrapped by DelayedWebDriver.
            delay (float, optional): Delay in seconds before each method call. Defaults to 1.0.
        """
        self.driver = driver
        self.delay = delay
        self.logger = self._setup_logger()

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """
        Sets up a logger for the DelayedWebDriver.

        Returns:
            logging.Logger: Configured logger instance.
        """
        caller_name = inspect.stack()[1].function
        logger = logging.getLogger(f"{__name__}.DelayedWebDriver.{caller_name}")
        logger.setLevel(logging.DEBUG)
        return logger

    def __getattr__(self, attr: str):
        """
        Get an attribute of the wrapped WebDriver instance, adding a delay before calling any method.

        Args:
            attr (str): The name of the attribute to retrieve from the wrapped WebDriver.

        Returns:
            Any: The attribute of the WebDriver, wrapped with a delay if it is callable (i.e., a method).
        """
        orig_attr = getattr(self.driver, attr)
        if callable(orig_attr):
            def delayed_method(*args, **kwargs):
                """
                Wrapper function that adds a delay before invoking the original method.

                Args:
                    *args: Positional arguments for the original method.
                    **kwargs: Keyword arguments for the original method.

                Returns:
                    Any: The result of the original method call.
                """
                self.logger.debug(f"Delaying execution of method '{attr}' by {self.delay} seconds.")
                time.sleep(self.delay)  # Add delay before each method call
                result = orig_attr(*args, **kwargs)
                self.logger.debug(f"Method '{attr}' executed.")
                return result

            return delayed_method
        else:
            self.logger.debug(f"Accessing attribute '{attr}' without delay.")
            return orig_attr


@pytest.fixture(scope="function")
def setup(request, browser: str, url: str):
    """
    Pytest fixture for setting up the Selenium WebDriver based on specified browser and URL.

    This fixture initializes the appropriate WebDriver (Chrome, Firefox, Edge, IE) using webdriver-manager,
    navigates to the specified URL, maximizes the browser window, and assigns the driver to the test class.
    After the test function completes, it ensures the driver is properly closed and quit.

    Args:
        request: Pytest's request object for accessing test context.
        browser (str): The name of the browser to use (e.g., "chrome", "firefox", "edge", "ie").
        url (str): The URL to navigate to.

    Yields:
        None
    """
    logger = Utils().logger

    logger.info(f"Initializing WebDriver for browser: '{browser}', navigating to URL: '{url}'.")

    # Map browser names to their corresponding service and driver classes
    browser_drivers = {
        "chrome": (ChromeService, webdriver.Chrome, ChromeDriverManager),
        "firefox": (FirefoxService, webdriver.Firefox, GeckoDriverManager),
        "ie": (IEService, webdriver.Ie, IEDriverManager),
        "internet explorer": (IEService, webdriver.Ie, IEDriverManager),
    }

    # Initialize WebDriver based on the specified browser
    try:
        service_class, driver_class, driver_manager_class = browser_drivers[browser.lower()]
        logger.debug(f"Setting up {browser.capitalize()} WebDriver.")
        service = service_class(driver_manager_class().install())
        driver = driver_class(service=service)
        logger.info(f"{browser.capitalize()} WebDriver initialized successfully.")
    except KeyError:
        logger.error(f"Unsupported browser specified: '{browser}'.")
        raise ValueError("Unsupported browser! Supported browsers: chrome, firefox, edge, ie.")

    # Wrap the WebDriver with DelayedWebDriver if necessary
    delayed_driver = DelayedWebDriver(driver)
    logger.debug("WebDriver wrapped with DelayedWebDriver.")

    # Navigate to the specified URL and maximize the window
    driver.get(url)
    logger.info(f"Navigated to URL: '{url}'.")
    driver.maximize_window()
    logger.info("Browser window maximized.")

    # Assign the WebDriver to the test class for access within tests
    request.cls.driver = delayed_driver
    logger.debug("Assigned DelayedWebDriver to the test class's 'driver' attribute.")

    # Use try-finally to ensure driver.quit() is called
    try:
        yield
    finally:
        logger.debug("Closing and quitting the WebDriver.")
        driver.close()
        driver.quit()
        logger.info("WebDriver closed and quit successfully.")


def pytest_addoption(parser):
    """
    Add command line options for pytest to specify browser and URL.

    This function adds two command line options:
    --browser: Specify the browser to use for testing (e.g., "chrome", "firefox", "edge").
    --url: Specify the URL to be opened in the browser.

    Args:
        parser: The pytest parser object used to add custom command line options.
    """
    parser.addoption("--browser", action="store", default="chrome",
                     help="Browser to use for tests: chrome, firefox, edge")
    parser.addoption("--url", action="store", default="https://www.pidginhost.com/panel/account/login",
                     help="URL to open for tests")
    Utils().logger.debug("Added pytest command line options '--browser' and '--url'.")


@pytest.fixture(scope="session")
def browser(request) -> str:
    """
    Fixture to get the browser specified in the command line options.

    This fixture retrieves the value of the --browser command line option, which is used
    to determine which browser to use for testing.

    Args:
        request: The pytest request object to access configuration options.

    Returns:
        str: The name of the browser specified in the command line options.
    """
    browser_choice = request.config.getoption("--browser")
    Utils().logger.debug(f"Browser selected: {browser_choice}")
    return browser_choice


@pytest.fixture(scope="session")
def url(request) -> str:
    """
    Fixture to get the URL specified in the command line options.

    This fixture retrieves the value of the --url command line option, which is used to
    determine the URL to open in the browser for testing.

    Args:
        request: The pytest request object to access configuration options.

    Returns:
        str: The URL specified in the command line options.
    """
    test_url = request.config.getoption("--url")
    Utils().logger.debug(f"URL selected for testing: {test_url}")
    return test_url


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
        Hook to modify the test report after each test run.

        This hook appends the current URL to the test report and captures a screenshot if the test fails
        or is an expected failure. The screenshot is saved in the report directory and embedded into the
        HTML report.

        Args:
            item: The test item.

        Yields:
            The test report.
        """
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    logger = Utils().logger
    if report.when == "call":
        driver = item.cls.driver
        if not driver:
            logger.warning(f"Test class '{item.cls.__name__}' does not have a 'driver' attribute.")
            return
        extras.append(pytest_html.extras.url(driver.current_url))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            report_directory = os.path.dirname(item.config.getoption("htmlpath"))
            file_name = report.nodeid.replace("::", "_") + ".png"
            destination_file = os.path.join(report_directory, file_name)
            driver.save_screenshot(destination_file)
            logger.info(f"Saved screenshot for test '{item.nodeid}' at '{destination_file}'")
            if file_name:
                html = f"""
                <div>
                    <img src="{file_name}" alt="screenshot" style="width:300px;height:200px;" onclick="window.open(this.src)" align="right"/>
                </div>
                """
                extras.append(pytest_html.extras.html(html))
        report.extras = extras
