# utils/error_handler.py
import time
from selenium.webdriver.common.by import By


class ErrorCollector:
    """Сборщик ошибок для тестов"""
    
    _errors = []
    _warnings = []
    _test_failed = False
    
    @classmethod
    def add_error(cls, message, screenshot=None):
        """Добавить ошибку"""
        cls._errors.append({
            "message": message,
            "screenshot": screenshot,
            "time": time.strftime("%H:%M:%S")
        })
        cls._test_failed = True
        print(f"❌ ОШИБКА: {message}")
    
    @classmethod
    def add_warning(cls, message):
        """Добавить предупреждение"""
        cls._warnings.append(message)
        print(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {message}")
    
    @classmethod
    def has_errors(cls):
        """Есть ли ошибки"""
        return len(cls._errors) > 0
    
    @classmethod
    def is_test_failed(cls):
        """Провален ли тест"""
        return cls._test_failed
    
    @classmethod
    def get_errors(cls):
        """Получить все ошибки"""
        return cls._errors
    
    @classmethod
    def get_warnings(cls):
        """Получить все предупреждения"""
        return cls._warnings
    
    @classmethod
    def clear(cls):
        """Очистить ошибки"""
        cls._errors = []
        cls._warnings = []
        cls._test_failed = False
    
    @classmethod
    def report(cls):
        """Отчет об ошибках"""
        if cls._errors:
            print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ ОШИБОК ({len(cls._errors)}):")
            for i, error in enumerate(cls._errors, 1):
                print(f"  {i}. {error['message']} (время: {error['time']})")
        if cls._warnings:
            print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЯ ({len(cls._warnings)}):")
            for warning in cls._warnings:
                print(f"  - {warning}")


def safe_close_party(page, driver):
    """Безопасное закрытие партии"""
    try:
        print("🔚 Попытка закрыть партию...")
        
        try:
            close_btn = driver.find_element(By.ID, "btnCloseParty")
            if close_btn.is_displayed():
                driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(0.5)
                confirm = driver.find_element(By.ID, "mainModalPrimary")
                driver.execute_script("arguments[0].click();", confirm)
                time.sleep(2)
                print("✅ Партия закрыта")
                return True
            else:
                print("ℹ️ Партия уже закрыта")
                return True
        except:
            print("ℹ️ Партия уже закрыта")
            return True
            
    except Exception as e:
        print(f"⚠️ Не удалось закрыть партию: {e}")
        try:
            driver.refresh()
            time.sleep(2)
            print("🔄 Страница обновлена")
        except:
            pass
        return False