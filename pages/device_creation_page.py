# pages/device_creation_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
from pages.add_device_modal import AddDeviceModal
from selenium.common.exceptions import TimeoutException
import time


class DeviceCreationPage(BasePage):
    
    # ===== Кнопки и основные элементы =====
    CREATE_PARTY_BUTTON = (By.ID, "createParty")
    DEVICE_TYPE_SELECT = (By.ID, "select2-deviceType-container")
    DEVICE_TYPE_DROPDOWN = (By.CSS_SELECTOR, ".select2-results__options")
    DEVICE_MODEL_SELECT = (By.ID, "select2-deviceModel-container")
    CREATE_BUTTON = (By.ID, "execParty")
    PARTY_SUCCESS_INDICATOR = (By.XPATH, "//span[contains(text(), 'Партия №')]")
    ADD_DEVICE_BUTTON = (By.ID, "add")
    CLOSE_PARTY_BUTTON = (By.ID, "btnCloseParty")
    CLOSE_PARTY_MODAL_TITLE = (By.XPATH, "//h3[@id='mainModalTitle' and contains(text(), 'Закрытие партии')]")
    CLOSE_PARTY_CONFIRM_BUTTON = (By.ID, "mainModalPrimary")
    
    # ===== Поля партии =====
    PRESSURE_INPUT = (By.ID, "pressure")
    TEMPERATURE_INPUT = (By.ID, "temperature")
    
    # ===== Универсальные локаторы для устройств в списке =====
    DEVICE_ROWS = (By.XPATH, "//table//tbody//tr")
    DEVICE_IMEI = (By.XPATH, "//span[contains(@class, 'imei')]")
    DEVICE_DEVEUI = (By.XPATH, "//span[contains(@class, 'devEui')]")
    DEVICE_SERIAL = (By.XPATH, "//span[contains(@class, 'serial')]")
    DEVICE_ITEMS = (By.XPATH, "//div[contains(@class, 'device-list')]//div[contains(@class, 'device-item')]")
    
    # ===== Модальное окно добавления устройства =====
    ADD_DEVICE_MODAL = (By.ID, "addDevice")
    
    def __init__(self, driver):
        super().__init__(driver)
        # Значения будут установлены из конфига в create_party_with_type
        self.current_unique_field = None
        self.current_fields = {}
    
    def select_device_type(self, type_name: str):
        """Выбор типа устройства"""
        print(f"📋 Выбор типа устройства: {type_name}")
        try:
            self.click(self.DEVICE_TYPE_SELECT)
            time.sleep(0.5)
            self.wait.until(EC.visibility_of_element_located(self.DEVICE_TYPE_DROPDOWN))
            
            option_locator = (By.XPATH, f"//li[contains(@class, 'select2-results__option') and contains(text(), '{type_name}')]")
            self.click(option_locator)
            time.sleep(1)
            print(f"✅ Тип устройства '{type_name}' выбран")
        except Exception as e:
            print(f"❌ Ошибка при выборе типа устройства: {e}")
            raise
        return self
    
    def select_device_model(self, model_name: str):
        """Выбор модели устройства"""
        print(f"📋 Выбор модели устройства: {model_name}")
        try:
            self.click(self.DEVICE_MODEL_SELECT)
            time.sleep(0.5)
            self.wait.until(EC.visibility_of_element_located(self.DEVICE_TYPE_DROPDOWN))
            
            option_locator = (By.XPATH, f"//li[contains(@class, 'select2-results__option') and contains(text(), '{model_name}')]")
            self.click(option_locator)
            time.sleep(1)
            print(f"✅ Модель устройства '{model_name}' выбрана")
        except Exception as e:
            print(f"❌ Ошибка при выборе модели устройства: {e}")
            raise
        return self
    
    def fill_party_fields(self, party_fields: dict):
        """Заполнение полей партии (давление, температура и т.д.)"""
        if not party_fields:
            return self
        
        print("📝 Заполнение полей партии...")
        for field_name, field_config in party_fields.items():
            field_id = field_config.get("id")
            field_value = field_config.get("value", "")
            
            if field_id:
                try:
                    print(f"  📝 Ввод '{field_name}': {field_value}")
                    locator = (By.ID, field_id)
                    element = self.find_element(locator)
                    element.clear()
                    element.send_keys(field_value)
                    time.sleep(0.3)
                except Exception as e:
                    print(f"  ⚠️ Ошибка при заполнении поля '{field_name}': {e}")
                    raise Exception(f"Не удалось заполнить поле '{field_name}': {e}")
        
        return self
    
    def create_party(self):
        """Создание партии"""
        print("🖱️ Нажатие кнопки 'Создать'")
        try:
            self.click(self.CREATE_BUTTON)
            
            try:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.visibility_of_element_located(self.PARTY_SUCCESS_INDICATOR))
                print("✅ Партия успешно создана")
            except TimeoutException:
                if self.is_element_visible(self.PARTY_SUCCESS_INDICATOR):
                    print("✅ Партия уже создана")
                else:
                    print("❌ Партия не создана!")
                    raise
            
            time.sleep(1)
        except Exception as e:
            print(f"❌ Ошибка при создании партии: {e}")
            raise
        return self
    
    def open_add_device_modal(self):
        """Открытие модального окна добавления устройства"""
        print("🖱️ Нажатие кнопки 'Добавить устройство'")
        
        try:
            modal = self.driver.find_element(*self.ADD_DEVICE_MODAL)
            if modal.is_displayed():
                print("ℹ️ Модальное окно уже открыто")
                return AddDeviceModal(self.driver)
        except:
            pass
        
        for attempt in range(3):
            try:
                add_button = self.find_element(self.ADD_DEVICE_BUTTON)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
                time.sleep(0.3)
                
                self.driver.execute_script("arguments[0].click();", add_button)
                time.sleep(0.5)
                
                self.wait.until(EC.visibility_of_element_located(self.ADD_DEVICE_MODAL))
                print("✅ Модальное окно открыто")
                break
            except Exception as e:
                print(f"⚠️ Попытка {attempt + 1} открыть модальное окно: {e}")
                time.sleep(1)
        else:
            print("❌ Не удалось открыть модальное окно после 3 попыток")
            raise Exception("Не удалось открыть модальное окно")
        
        return AddDeviceModal(self.driver)
    
    def close_party(self):
        """Закрытие партии"""
        print("🖱️ Нажатие кнопки 'Завершить выпуск и сохранить отчет'")
        
        try:
            close_button = self.find_element(self.CLOSE_PARTY_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", close_button)
            time.sleep(0.5)
            
            self.driver.execute_script("arguments[0].click();", close_button)
            time.sleep(1)
            
            self.wait.until(EC.visibility_of_element_located(self.CLOSE_PARTY_MODAL_TITLE))
            print("✅ Модальное окно закрытия партии открыто")
            
            confirm_button = self.find_element(self.CLOSE_PARTY_CONFIRM_BUTTON)
            self.driver.execute_script("arguments[0].click();", confirm_button)
            time.sleep(2)
            
            try:
                self.wait.until(EC.visibility_of_element_located(self.CREATE_PARTY_BUTTON))
                print("✅ Партия успешно закрыта")
            except TimeoutException:
                print("⚠️ Кнопка 'Создать партию' не появилась, обновляем страницу...")
                self.driver.refresh()
                time.sleep(2)
                self.wait.until(EC.visibility_of_element_located(self.CREATE_PARTY_BUTTON))
                print("✅ После обновления кнопка появилась")
            
        except Exception as e:
            print(f"❌ Ошибка при закрытии партии: {e}")
            raise
        
        return self
    
    def click_create_party(self):
        """Нажатие кнопки 'Создать партию' с ожиданием"""
        print("🖱️ Нажатие кнопки 'Создать партию'")
        try:
            create_btn = self.wait.until(
                EC.element_to_be_clickable(self.CREATE_PARTY_BUTTON)
            )
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_btn)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", create_btn)
            
            self.wait.until(EC.visibility_of_element_located(self.DEVICE_TYPE_SELECT))
            print("✅ Форма открыта")
            time.sleep(0.5)
        except TimeoutException:
            print("❌ Не удалось найти кнопку 'Создать партию'")
            self.driver.refresh()
            time.sleep(2)
            create_btn = self.wait.until(
                EC.element_to_be_clickable(self.CREATE_PARTY_BUTTON)
            )
            self.driver.execute_script("arguments[0].click();", create_btn)
            self.wait.until(EC.visibility_of_element_located(self.DEVICE_TYPE_SELECT))
            print("✅ Форма открыта после обновления")
        except Exception as e:
            print(f"❌ Ошибка при открытии формы: {e}")
            raise
        return self
    
    def is_create_party_button_visible(self) -> bool:
        """Проверка видимости кнопки 'Создать партию'"""
        try:
            self.wait.until(EC.visibility_of_element_located(self.CREATE_PARTY_BUTTON))
            return True
        except:
            return False
    
    def is_element_visible(self, locator) -> bool:
        """Проверка видимости элемента"""
        try:
            wait = WebDriverWait(self.driver, 2)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except:
            return False
    
    def get_device_count(self) -> int:
        """Получение количества устройств в списке"""
        try:
            locators = [
                self.DEVICE_ROWS,
                self.DEVICE_IMEI,
                self.DEVICE_DEVEUI,
                self.DEVICE_SERIAL,
                self.DEVICE_ITEMS,
                (By.XPATH, "//table//tbody//tr[contains(@class, 'device-row')]"),
                (By.XPATH, "//div[contains(@class, 'device-list')]//tr"),
            ]
            
            for locator in locators:
                try:
                    elements = self.driver.find_elements(*locator)
                    if elements and len(elements) > 0:
                        if locator == self.DEVICE_ROWS:
                            headers = self.driver.find_elements(By.XPATH, "//table//thead//tr")
                            if headers:
                                count = len(elements) - 1
                                if count > 0:
                                    print(f"📊 Найдено устройств в списке: {count}")
                                    return count
                            if len(elements) > 0:
                                print(f"📊 Найдено устройств в списке: {len(elements)}")
                                return len(elements)
                        
                        count = len(elements)
                        print(f"📊 Найдено устройств в списке: {count}")
                        return count
                except:
                    continue
            
            print("⚠️ Не удалось найти устройства в списке")
            return 0
            
        except Exception as e:
            print(f"⚠️ Ошибка при подсчете устройств: {e}")
            return 0
    
    def find_device_in_list(self, identifier: str) -> bool:
        """Поиск устройства в списке по идентификатору"""
        if not identifier:
            return False
        
        locator = (By.XPATH, f"//*[contains(text(), '{identifier}')]")
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except:
            return False