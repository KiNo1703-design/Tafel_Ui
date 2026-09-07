# actions/device_actions.py
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from utils.error_handler import ErrorCollector


class DeviceActions:
    
    @staticmethod
    def add_multiple_devices(page, devices: list) -> list:
        """Добавление нескольких устройств с обработкой ошибок"""
        added_identifiers = []
        
        required_fields = getattr(page, 'current_fields', {})
        unique_field = getattr(page, 'current_unique_field', None)
        
        print(f"\n🔍 ДИАГНОСТИКА:")
        print(f"  current_fields: {list(required_fields.keys())}")
        print(f"  unique_field: {unique_field}")
        
        if not unique_field and required_fields:
            unique_field = list(required_fields.keys())[0]
            print(f"  unique_field (взят из fields): {unique_field}")
        
        for idx, device_data in enumerate(devices, 1):
            print(f"\n📱 Добавление устройства {idx}/{len(devices)}")
            
            # Проверяем поля с обработкой ошибок
            if required_fields:
                print(f"  🔍 Проверка обязательных полей из конфига: {list(required_fields.keys())}")
                
                missing_fields = []
                for field_name, field_config in required_fields.items():
                    field_id = field_config.get("id", field_name)
                    if field_name not in device_data or device_data[field_name] is None or device_data[field_name] == "":
                        missing_fields.append(f"{field_name} (id: {field_id})")
                
                if missing_fields:
                    error_msg = f"❌ ОШИБКА: В данных отсутствуют обязательные поля: {', '.join(missing_fields)}"
                    print(error_msg)
                    ErrorCollector.add_error(error_msg)
                    continue
            
            # Открываем модальное окно
            try:
                modal = page.open_add_device_modal()
                time.sleep(0.2)
            except Exception as e:
                ErrorCollector.add_error(f"Не удалось открыть модальное окно для устройства {idx}: {e}")
                continue
            
            # Заполняем поля
            try:
                DeviceActions._fill_fields_from_config(modal, device_data, required_fields)
            except Exception as e:
                ErrorCollector.add_error(f"Не удалось заполнить поля устройства {idx}: {e}")
                modal.close_modal()
                continue
            
            # Сохраняем
            try:
                modal.save_device()
                time.sleep(0.3)
            except Exception as e:
                ErrorCollector.add_error(f"Не удалось сохранить устройство {idx}: {e}")
                modal.close_modal()
                continue
            
            # Закрываем модальное окно
            modal.close_modal()
            time.sleep(0.2)
            
            # Получаем идентификатор
            identifier = None
            if unique_field:
                identifier = device_data.get(unique_field)
            
            if not identifier:
                for field_name in required_fields.keys():
                    if field_name in device_data and device_data[field_name]:
                        identifier = device_data[field_name]
                        break
            
            if identifier:
                added_identifiers.append(identifier)
                print(f"📌 Идентификатор: {identifier}")
                
                # Проверяем появление
                try:
                    DeviceActions._quick_check_device(page, identifier)
                except Exception as e:
                    ErrorCollector.add_error(f"Устройство {identifier} не появилось: {e}")
            else:
                ErrorCollector.add_warning(f"Не удалось определить идентификатор для устройства {idx}")
            
            time.sleep(0.1)
        
        return added_identifiers
    
    @staticmethod
    def _fill_fields_from_config(modal, device_data: dict, required_fields: dict):
        """Заполнение ТОЛЬКО полей из конфига"""
        print("📝 Заполнение полей устройства...")
        
        for field_name, field_config in required_fields.items():
            field_id = field_config.get("id")
            field_value = device_data.get(field_name)
            
            if not field_id:
                print(f"  ⚠️ Нет ID для поля '{field_name}'")
                continue
            
            if field_value is None or field_value == "":
                print(f"  ⚠️ Поле '{field_name}' пустое, пропускаем")
                continue
            
            try:
                if field_config.get("type") == "select2":
                    DeviceActions._select2_select(modal.driver, field_id, field_value)
                else:
                    locator = (By.ID, field_id)
                    element = modal.find_element(locator)
                    element.clear()
                    element.send_keys(field_value)
                
                print(f"  ✅ Поле '{field_name}' (id: {field_id}) = '{field_value}'")
                time.sleep(0.1)
                
            except Exception as e:
                error_msg = f"❌ ОШИБКА: Не удалось заполнить поле '{field_name}': {e}"
                print(error_msg)
                raise Exception(error_msg)
    
    @staticmethod
    def _select2_select(driver, field_id: str, value: str):
        """Выбор значения в select2"""
        try:
            select_container = (By.ID, f"select2-{field_id}-container")
            driver.find_element(*select_container).click()
            time.sleep(0.1)
            
            option_locator = (By.XPATH, f"//li[contains(@class, 'select2-results__option') and contains(text(), '{value}')]")
            driver.find_element(*option_locator).click()
            time.sleep(0.1)
            
        except Exception as e:
            raise Exception(f"Не удалось выбрать значение '{value}' в select2 поле '{field_id}': {e}")
    
    @staticmethod
    def _quick_check_device(page, identifier: str, timeout: int = 5):
        """Быстрая проверка появления устройства"""
        if not identifier:
            return
        
        print(f"⏳ Проверка устройства '{identifier}'...")
        locator = (By.XPATH, f"//*[contains(text(), '{identifier}')]")
        
        try:
            wait = WebDriverWait(page.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            print(f"✅ Устройство '{identifier}' появилось")
        except TimeoutException:
            error_msg = f"❌ ОШИБКА: Устройство '{identifier}' не появилось в списке!"
            print(error_msg)
            page.driver.refresh()
            time.sleep(1)
            try:
                wait.until(EC.visibility_of_element_located(locator))
                print(f"✅ Устройство '{identifier}' появилось после обновления")
            except:
                ErrorCollector.add_error(f"Устройство {identifier} не появилось после обновления")
                raise Exception(error_msg)
    
    @staticmethod
    def remove_all_devices(page, identifiers: list):
        """Удаление всех устройств"""
        if not identifiers:
            print("ℹ️ Нет устройств для удаления")
            return
        
        print(f"🗑️ Удаление {len(identifiers)} устройств...")
        
        for idx, identifier in enumerate(identifiers, 1):
            print(f"\n  Удаление {idx}/{len(identifiers)}: {identifier}")
            
            if not DeviceActions._quick_check_exists(page, identifier):
                print(f"  ℹ️ Устройство '{identifier}' уже удалено")
                continue
            
            try:
                DeviceActions._delete_by_js_fast(page, identifier)
                time.sleep(0.3)
            except Exception as e:
                ErrorCollector.add_error(f"Не удалось удалить устройство {identifier}: {e}")
    
    @staticmethod
    def _delete_by_js_fast(page, identifier: str):
        """Быстрое удаление через JavaScript"""
        try:
            js_script = f"""
                var rows = document.querySelectorAll('tr');
                for (var i = 0; i < rows.length; i++) {{
                    if (rows[i].textContent.includes('{identifier}')) {{
                        var btn = rows[i].querySelector('button.delete');
                        if (!btn) {{
                            btn = rows[i].querySelector('i.material-icons');
                            if (btn && btn.textContent === 'clear') {{
                                btn = btn.parentElement;
                            }}
                        }}
                        if (btn) {{
                            btn.click();
                            setTimeout(function() {{
                                var confirm = document.getElementById('mainModalPrimary');
                                if (confirm) confirm.click();
                            }}, 300);
                            return true;
                        }}
                    }}
                }}
                return false;
            """
            result = page.driver.execute_script(js_script)
            if result:
                time.sleep(0.5)
                if not DeviceActions._quick_check_exists(page, identifier):
                    print(f"  ✅ Устройство '{identifier}' удалено")
                else:
                    print(f"  ⚠️ Устройство '{identifier}' не удалилось")
            else:
                print(f"  ❌ Не найдено устройство '{identifier}'")
        except Exception as e:
            print(f"  ⚠️ Ошибка удаления: {e}")
            raise
    
    @staticmethod
    def _quick_check_exists(page, identifier: str) -> bool:
        if not identifier:
            return False
        
        locator = (By.XPATH, f"//*[contains(text(), '{identifier}')]")
        try:
            page.driver.find_element(*locator)
            return True
        except:
            return False
    
    @staticmethod
    def get_device_identifier(device_data: dict, unique_field: str) -> str:
        return device_data.get(unique_field) or device_data.get('devEui') or device_data.get('serial') or device_data.get('imei')