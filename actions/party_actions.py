# actions/party_actions.py
import time
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from actions.device_actions import DeviceActions
from selenium.common.exceptions import TimeoutException
from utils.error_handler import ErrorCollector, safe_close_party


class PartyActions:

    @staticmethod
    def create_party_with_type(page, release_type: dict):
        """Создание партии с указанным типом"""
        print(f"📋 Создание партии для типа: {release_type['display_name']}")

        fields_from_config = release_type.get('fields', {})
        page.current_fields = fields_from_config
        page.current_unique_field = release_type.get('unique_field', None)
        
        if not page.current_unique_field and fields_from_config:
            page.current_unique_field = list(fields_from_config.keys())[0]
        
        print(f"  📋 Обязательные поля: {list(page.current_fields.keys())}")
        print(f"  📋 Unique field: {page.current_unique_field}")

        try:
            page.select_device_type(release_type["display_name"])
            time.sleep(0.5)
            page.select_device_model(release_type["model"])
            time.sleep(0.5)
            
            party_fields = release_type.get("party_fields", {})
            if party_fields:
                page.fill_party_fields(party_fields)
                time.sleep(0.3)
            
            page.create_party()
            time.sleep(0.5)
            
        except Exception as e:
            ErrorCollector.add_error(f"Ошибка при создании партии: {e}")
            safe_close_party(page, page.driver)
            raise

        return page

    @staticmethod
    def close_party(page):
        """Закрытие партии"""
        safe_close_party(page, page.driver)

    @staticmethod
    def create_party_add_remove_close(page, release_type: dict, devices_count: int = 1) -> list:
        """Полный цикл с обработкой ошибок"""
        added_identifiers = []
        test_failed = False
        error_messages = []
        
        try:
            # Создаем партию
            PartyActions.create_party_with_type(page, release_type)

            devices_to_add = release_type["devices"][:devices_count]
            
            print(f"\n📊 Будет добавлено {len(devices_to_add)} устройств:")
            for idx, device in enumerate(devices_to_add, 1):
                print(f"  {idx}. {device}")
            
            # Добавляем устройства - ПРЕРЫВАЕМ при первой ошибке
            for idx, device_data in enumerate(devices_to_add, 1):
                print(f"\n📱 Добавление устройства {idx}/{len(devices_to_add)}")
                
                # Проверяем обязательные поля
                required_fields = getattr(page, 'current_fields', {})
                missing_fields = []
                for field_name in required_fields.keys():
                    if field_name not in device_data or device_data[field_name] is None or device_data[field_name] == "":
                        field_id = required_fields[field_name].get("id", field_name)
                        missing_fields.append(f"{field_name} (id: {field_id})")
                
                if missing_fields:
                    error_msg = f"❌ ОШИБКА: Отсутствуют обязательные поля в устройстве {idx}: {', '.join(missing_fields)}"
                    print(error_msg)
                    ErrorCollector.add_error(error_msg)
                    error_messages.append(error_msg)
                    test_failed = True
                    break  # ✅ ПРЕРЫВАЕМ добавление устройств
                
                # Если все поля есть - добавляем
                modal = page.open_add_device_modal()
                time.sleep(0.2)
                
                try:
                    DeviceActions._fill_fields_from_config(modal, device_data, required_fields)
                except Exception as e:
                    error_msg = f"❌ Не удалось заполнить поля устройства {idx}: {e}"
                    print(error_msg)
                    ErrorCollector.add_error(error_msg)
                    error_messages.append(error_msg)
                    modal.close_modal()
                    test_failed = True
                    break  # ✅ ПРЕРЫВАЕМ добавление устройств
                
                modal.save_device()
                time.sleep(0.3)
                modal.close_modal()
                time.sleep(0.2)
                
                # Получаем идентификатор
                unique_field = getattr(page, 'current_unique_field', None)
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
                        error_msg = f"❌ Устройство {identifier} не появилось: {e}"
                        print(error_msg)
                        ErrorCollector.add_error(error_msg)
                        error_messages.append(error_msg)
                        test_failed = True
                        break  # ✅ ПРЕРЫВАЕМ добавление устройств
                else:
                    error_msg = f"⚠️ Не удалось определить идентификатор для устройства {idx}"
                    print(error_msg)
                    ErrorCollector.add_warning(error_msg)
            
            # Если были ошибки - удаляем то, что успели добавить
            if test_failed and added_identifiers:
                print(f"\n⚠️ Были ошибки, удаляем {len(added_identifiers)} добавленных устройств...")
                DeviceActions.remove_all_devices(page, added_identifiers)
                time.sleep(0.5)
            
            # Удаляем все устройства (если их добавили без ошибок)
            elif added_identifiers:
                print("\n🗑️ Удаление всех добавленных устройств...")
                DeviceActions.remove_all_devices(page, added_identifiers)
                time.sleep(0.5)
                
                # Проверяем удаление
                print(f"\n✅ Проверяем удаление устройств:")
                for identifier in added_identifiers:
                    exists = DeviceActions._quick_check_exists(page, identifier)
                    if not exists:
                        print(f"  ✅ Устройство '{identifier}' удалено")
                    else:
                        error_msg = f"⚠️ Устройство '{identifier}' не удалилось"
                        print(f"  ❌ {error_msg}")
                        ErrorCollector.add_warning(error_msg)
            
        except Exception as e:
            error_msg = f"❌ Ошибка в тесте: {e}"
            print(error_msg)
            ErrorCollector.add_error(error_msg)
            error_messages.append(error_msg)
            test_failed = True
        
        finally:
            # Всегда закрываем партию
            print("\n🔚 Закрытие партии (финальный блок)...")
            safe_close_party(page, page.driver)
        
        # ✅ В конце теста показываем ошибки, но НЕ ПАДАЕМ
        if test_failed:
            print(f"\n❌ ТЕСТ ПРОВАЛЕН! Причины:")
            for msg in error_messages:
                print(f"  - {msg}")
            
            # Прикрепляем к Allure
            try:
                import allure
                allure.attach(
                    "\n".join(error_messages),
                    name="Ошибки в тесте",
                    attachment_type=allure.attachment_type.TEXT
                )
                # Отмечаем тест как FAILED в Allure
                allure.dynamic.title(f"{release_type['display_name']} - FAILED")
            except:
                pass
            
            # ✅ НЕ ПАДАЕМ, но отмечаем как FAILED через pytest
            # Используем pytest.fail с параметром pytrace=False чтобы не показывать трейсбек
            pytest.fail(f"Тест провален: {len(error_messages)} ошибок", pytrace=False)
        
        return added_identifiers