from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException
from config import Config

class AuthPage(BasePage):
    USERNAME_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger, .invalid-feedback, .alert")
    SUCCESS_INDICATOR = (By.ID, "userProfile")
    USER_NAME_SPANS = (By.CSS_SELECTOR, "#userProfile span")

    def open(self):
        url = f"{Config.BASE_URL}/auth"
        print(f"🔗 Открываем: {url}")
        self.driver.get(url)
        self.driver.maximize_window()
        return self

    def login(self, username, password):
        print(f"👤 Ввод логина: {username}")
        self.enter_text(self.USERNAME_INPUT, username)
        
        print("🔑 Ввод пароля")
        self.enter_text(self.PASSWORD_INPUT, password)
        
        print("🖱️ Клик по кнопке 'Войти'")
        self.click(self.LOGIN_BUTTON)
        
        try:
            self.wait.until(
                lambda d: d.current_url != f"{Config.BASE_URL}/auth"
            )
        except TimeoutException:
            pass
        
        return self

    def get_error_text(self) -> str:
        try:
            error_element = self.wait.until(
                EC.visibility_of_element_located(self.ERROR_MESSAGE)
            )
            return error_element.text.strip()
        except TimeoutException:
            return ""

    def is_login_successful(self) -> bool:
        try:
            element = self.wait.until(
                EC.visibility_of_element_located(self.SUCCESS_INDICATOR)
            )
            return element.is_displayed()
        except TimeoutException:
            return False

    def get_user_name(self) -> str:
        try:
            elements = self.driver.find_elements(*self.USER_NAME_SPANS)
            if len(elements) >= 2:
                return f"{elements[0].text} {elements[1].text}".strip()
            return "Имя не найдено"
        except Exception as e:
            print(f"⚠️ Ошибка получения имени: {e}")
            return "Ошибка"

    def get_current_url(self) -> str:
        return self.driver.current_url