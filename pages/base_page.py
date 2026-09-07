from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from config import Config
import time

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver, 
            Config.DEFAULT_TIMEOUT, 
            poll_frequency=Config.POLL_FREQUENCY
        )

    def find_element(self, locator) -> WebElement:
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print(f"⚠️ Элемент не найден: {locator}")
            raise

    def click(self, locator):
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
        except TimeoutException:
            print(f"⚠️ Элемент не кликабелен: {locator}")
            raise

    def enter_text(self, locator, text):
        try:
            element = self.find_element(locator)
            element.clear()
            element.send_keys(text)
        except Exception as e:
            print(f"⚠️ Ошибка ввода текста: {e}")
            raise

    def is_element_present(self, locator, timeout=5) -> bool:
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=Config.POLL_FREQUENCY).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False