# pages/add_device_modal.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException
import time

class AddDeviceModal(BasePage):
    
    DEV_EUI_INPUT = (By.ID, "devEui")
    IMEI_INPUT = (By.ID, "imei")
    SERIAL_INPUT = (By.ID, "serial")
    SAVE_BUTTON = (By.ID, "saveDevice")
    CLOSE_BUTTON = (By.ID, "closeForm")
    SUCCESS_MESSAGE = (By.ID, "resultMessage")
    MODAL_WINDOW = (By.ID, "addDevice")
    
    DELETE_MODAL_TITLE = (By.XPATH, "//h3[@id='mainModalTitle' and contains(text(), 'Удаление устройства')]")
    DELETE_CONFIRM_BUTTON = (By.ID, "mainModalPrimary")
    
    def fill_device_fields(self, device_data: dict, required_fields: dict = None):
        """
        Заполнение полей устройства ТОЛЬКО из required_fields
        Если required_fields не передан - заполняем все поля из device_data
        """
        print("📝 Заполнение полей устройства...")
        
        # Если required_fields не указаны - берем все поля из device_data
        if required_fields is None:
            fields_to_fill = {field_name: {"id": field_name} for field_name in device_data.keys()}
        else:
            fields_to_fill = required_fields
        
        for field_name, field_config in fields_to_fill.items():
            # Берем значение из device_data
            field_value = device_data.get(field_name)
            
            if field_value is None or field_value == "":
                print(f"  ⚠️ Поле '{field_name}' пустое, пропускаем")
                continue
            
            try:
                field_id = field_config.get("id") if isinstance(field_config, dict) else field_config
                
                # Проверяем, является ли поле select2
                is_select2 = False
                if isinstance(field_config, dict) and field_config.get("type") == "select2":
                    is_select2 = True
                
                if is_select2:
                    self._select2_select(field_id, field_value)
                else:
                    locator = (By.ID, field_id)
                    element = self.find_element(locator)
                    element.clear()
                    element.send_keys(field_value)
                
                print(f"  ✅ Поле '{field_name}' = '{field_value}'")
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  ❌ Ошибка при заполнении поля '{field_name}': {e}")
                raise Exception(f"Не удалось заполнить поле '{field_name}': {e}")
        
        return self
    
    def _select2_select(self, field_id: str, value: str):
        """Выбор значения в select2"""
        try:
            select_container = (By.ID, f"select2-{field_id}-container")
            self.click(select_container)
            time.sleep(0.1)
            
            option_locator = (By.XPATH, f"//li[contains(@class, 'select2-results__option') and contains(text(), '{value}')]")
            self.click(option_locator)
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ⚠️ Ошибка при выборе select2 для {field_id}: {e}")
            raise
    
    def save_device(self):
        print("🖱️ Нажатие кнопки 'Сохранить'")
        self.click(self.SAVE_BUTTON)
        time.sleep(0.5)
        return self
    
    def close_modal(self):
        """Закрытие модального окна"""
        print("🖱️ Закрытие модального окна")
        
        try:
            close_btn = self.find_element(self.CLOSE_BUTTON)
            self.driver.execute_script("arguments[0].click();", close_btn)
            time.sleep(0.3)
            
            try:
                wait = WebDriverWait(self.driver, 2)
                wait.until(EC.invisibility_of_element_located(self.MODAL_WINDOW))
                print("✅ Модальное окно закрыто")
            except TimeoutException:
                self.driver.execute_script("""
                    var modal = document.getElementById('addDevice');
                    if (modal) {
                        modal.style.display = 'none';
                        modal.classList.remove('show');
                        document.body.classList.remove('modal-open');
                    }
                """)
                print("✅ Модальное окно закрыто (через JS)")
            
        except Exception as e:
            print(f"⚠️ Ошибка при закрытии модального окна: {e}")
            self.driver.execute_script("""
                var modal = document.getElementById('addDevice');
                if (modal) {
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                }
            """)
        
        time.sleep(0.2)
        return self
    
    def is_device_added_successfully(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 3)
            element = wait.until(EC.visibility_of_element_located(self.SUCCESS_MESSAGE))
            text = element.text
            print(f"✅ Найдено сообщение: '{text}'")
            return True
        except TimeoutException:
            print("ℹ️ Сообщение об успехе не найдено")
            return False
    
    def is_device_in_list(self, unique_identifier: str) -> bool:
        locator = (By.XPATH, f"//*[contains(text(), '{unique_identifier}')]")
        try:
            wait = WebDriverWait(self.driver, 3)
            wait.until(EC.visibility_of_element_located(locator))
            print(f"✅ Устройство '{unique_identifier}' найдено в списке")
            return True
        except TimeoutException:
            print(f"❌ Устройство '{unique_identifier}' НЕ найдено в списке")
            return False
    
    def is_device_deleted(self, unique_identifier: str) -> bool:
        locator = (By.XPATH, f"//*[contains(text(), '{unique_identifier}')]")
        try:
            wait = WebDriverWait(self.driver, 3)
            wait.until(EC.invisibility_of_element_located(locator))
            print(f"✅ Устройство '{unique_identifier}' удалено из списка")
            return True
        except TimeoutException:
            print(f"❌ Устройство '{unique_identifier}' всё ещё в списке")
            return False
    
    def get_device_count_in_list(self) -> int:
        try:
            locators = [
                (By.XPATH, "//span[contains(@class, 'imei')]"),
                (By.XPATH, "//span[contains(@class, 'devEui')]"),
                (By.XPATH, "//span[contains(@class, 'serial')]"),
                (By.XPATH, "//table//tbody//tr"),
            ]
            
            for locator in locators:
                try:
                    elements = self.driver.find_elements(*locator)
                    if elements:
                        count = len(elements)
                        if locator == (By.XPATH, "//table//tbody//tr"):
                            headers = self.driver.find_elements(By.XPATH, "//table//thead//tr")
                            if headers and count > 0:
                                count = count - 1
                        return count
                except:
                    continue
            
            return 0
        except:
            return 0
    
    def delete_device_by_identifier(self, unique_identifier: str):
        print(f"🗑️ Удаление устройства: {unique_identifier}")
        
        delete_button = (By.XPATH, f"//*[contains(text(), '{unique_identifier}')]/ancestor::tr//i[contains(@class, 'text-danger')]")
        
        try:
            self.click(delete_button)
            time.sleep(0.3)
            
            wait = WebDriverWait(self.driver, 3)
            wait.until(EC.visibility_of_element_located(self.DELETE_MODAL_TITLE))
            print(f"✅ Модальное окно удаления для '{unique_identifier}' открыто")
            
            self.click(self.DELETE_CONFIRM_BUTTON)
            time.sleep(0.5)
            
            assert self.is_device_deleted(unique_identifier), f"Устройство {unique_identifier} не удалилось!"
            print(f"✅ Устройство '{unique_identifier}' успешно удалено")
            return True
        except Exception as e:
            print(f"❌ Ошибка при удалении {unique_identifier}: {e}")
            return False