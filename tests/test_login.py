import pytest
from pages.auth_page import AuthPage
from config import Config

class TestLogin:

    def test_successful_login(self, driver):
        """Тест успешного входа (без фикстур)"""
        print("\n🧪 Запуск теста успешного входа")
        
        creds = Config.get_credentials()
        
        auth_page = AuthPage(driver).open()
        auth_page.login(creds["username"], creds["password"])
        
        assert auth_page.is_login_successful(), "Не удалось авторизоваться"
        print("✅ Вход выполнен")
        
        user_name = auth_page.get_user_name()
        print(f"👤 Имя пользователя: {user_name}")
        assert user_name != "Имя не найдено", "Имя пользователя не получено"
    
    # === НОВЫЙ ТЕСТ: использует готовую фикстуру ===
    def test_authenticated_user(self, authenticated_driver):
        """
        Тест, который использует уже авторизованного пользователя
        Не нужно писать логику авторизации!
        """
        print("\n🧪 Тест с авторизованным пользователем")
        
        # Драйвер уже авторизован, можно сразу проверять
        auth_page = AuthPage(authenticated_driver)
        user_name = auth_page.get_user_name()
        
        print(f"👤 Имя пользователя: {user_name}")
        assert user_name != "Имя не найдено", "Имя пользователя не получено"