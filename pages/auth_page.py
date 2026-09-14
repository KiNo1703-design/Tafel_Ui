# pages/auth_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
import time


class AuthPage(BasePage):
    
    USERNAME_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")
    # ✅ Расширенный поиск индикатора успешной авторизации
    SUCCESS_INDICATOR = (
        By.XPATH, 
        "//*[contains(@class, 'sidebar') or "
        "contains(@class, 'main-content') or "
        "contains(@class, 'dashboard') or "
        "contains(@class, 'layout') or "
        "contains(@class, 'app')]"
    )
    
    def open(self):
        from config import Config
        url = Config.BASE_URL + "/auth"
        print(f"🔗 Открываем: {url}")
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.USERNAME_INPUT)
        )
        return self
    
    def login(self, username, password):
        print(f"👤 Ввод логина: {username}")
        username_input = self.find_element(self.USERNAME_INPUT)
        username_input.clear()
        username_input.send_keys(username)
        
        print("🔑 Ввод пароля")
        password_input = self.find_element(self.PASSWORD_INPUT)
        password_input.clear()
        password_input.send_keys(password)
        
        print("🖱️ Клик по кнопке 'Войти'")
        self.click(self.LOGIN_BUTTON)
        time.sleep(3)  # Увеличил ожидание
        return self
    
    def is_login_successful(self) -> bool:
        try:
            # Ждем любой признак, что мы внутри системы
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.SUCCESS_INDICATOR)
            )
            return True
        except:
            # Если не нашли индикатор, проверяем URL
            current_url = self.driver.current_url
            if "/auth" not in current_url:
                print(f"ℹ️ Редирект на: {current_url}")
                return True
            return False