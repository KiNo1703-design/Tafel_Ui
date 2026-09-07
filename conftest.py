# conftest.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from pages.auth_page import AuthPage
from pages.sidebar_menu import SidebarMenu
from pages.device_creation_page import DeviceCreationPage
from config import Config
from utils.error_handler import ErrorCollector, safe_close_party
import os
import time


def pytest_addoption(parser):
    """Добавляем параметр командной строки для headless режима"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запуск в headless режиме (без открытия браузера)"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox"],
        help="Выбор браузера: chrome или firefox"
    )


@pytest.fixture(scope="function")
def driver(request):
    """Создает и закрывает браузер для каждого теста"""
    print("\n🟢 Запуск браузера...")
    
    # Получаем параметры
    headless = request.config.getoption("--headless")
    browser = request.config.getoption("--browser")
    
    if browser == "chrome":
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # ✅ Headless режим
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")
            options.add_argument("--silent")
            print("🧪 Запуск в headless режиме (браузер не отображается)")
        else:
            print("👁️ Запуск с открытым браузером")
        
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(Config.IMPLICIT_WAIT)
            driver.set_page_load_timeout(30)
            print("✅ Браузер Chrome запущен")
            yield driver
        except Exception as e:
            print(f"❌ Ошибка запуска браузера: {e}")
            raise
        finally:
            if driver:
                print("🛑 Закрытие браузера...")
                try:
                    driver.quit()
                except:
                    pass
    
    elif browser == "firefox":
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager
        
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        
        if headless:
            options.add_argument("--headless")
            print("🧪 Запуск в headless режиме (браузер не отображается)")
        else:
            print("👁️ Запуск с открытым браузером")
        
        driver = None
        try:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.implicitly_wait(Config.IMPLICIT_WAIT)
            driver.set_page_load_timeout(30)
            print("✅ Браузер Firefox запущен")
            yield driver
        except Exception as e:
            print(f"❌ Ошибка запуска браузера: {e}")
            raise
        finally:
            if driver:
                print("🛑 Закрытие браузера...")
                try:
                    driver.quit()
                except:
                    pass


@pytest.fixture(scope="function")
def authenticated_driver(driver):
    """Возвращает драйвер с уже выполненной авторизацией"""
    # Очищаем ошибки перед тестом
    ErrorCollector.clear()
    
    creds = Config.get_credentials()
    
    try:
        auth_page = AuthPage(driver).open()
        auth_page.login(creds["username"], creds["password"])
        
        # Проверяем успешность авторизации
        assert auth_page.is_login_successful(), "Не удалось авторизоваться"
        print("✅ Авторизация выполнена")
        
        # Ждем загрузки основного контента
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar, .main-content, nav")))
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ Ошибка при авторизации: {e}")
        try:
            driver.save_screenshot("auth_error.png")
            print("📸 Скриншот сохранен как auth_error.png")
        except:
            pass
        raise
    
    return driver


@pytest.fixture(scope="function")
def device_page(authenticated_driver):
    """Возвращает страницу 'Выпуск устройств' с уже открытой формой"""
    
    try:
        sidebar = SidebarMenu(authenticated_driver)
        device_page = sidebar.click_device_release()
        time.sleep(2)
        
        # Проверяем, есть ли активная партия
        try:
            close_btn = authenticated_driver.find_element(By.ID, "btnCloseParty")
            if close_btn.is_displayed():
                print("⚠️ Найдена активная партия, закрываем...")
                authenticated_driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(0.5)
                confirm = authenticated_driver.find_element(By.ID, "mainModalPrimary")
                authenticated_driver.execute_script("arguments[0].click();", confirm)
                time.sleep(2)
                authenticated_driver.refresh()
                time.sleep(1)
        except:
            pass
        
        # Ожидаем кнопку создания партии
        wait = WebDriverWait(authenticated_driver, 15)
        create_party_btn = wait.until(
            EC.element_to_be_clickable(device_page.CREATE_PARTY_BUTTON)
        )
        print("✅ Кнопка 'Создать партию' доступна")
        
        # Скролл и клик по кнопке
        authenticated_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_party_btn)
        time.sleep(0.5)
        authenticated_driver.execute_script("arguments[0].click();", create_party_btn)
        time.sleep(1)
        
        # Проверяем, что форма открылась
        wait.until(EC.visibility_of_element_located(device_page.DEVICE_TYPE_SELECT))
        print("✅ Форма создания партии открыта")
        
        return device_page
        
    except TimeoutException as e:
        print(f"❌ Таймаут при ожидании элементов: {e}")
        try:
            authenticated_driver.save_screenshot("device_page_error.png")
            print("📸 Скриншот сохранен как device_page_error.png")
        except:
            pass
        raise
    except Exception as e:
        print(f"❌ Ошибка при открытии страницы создания: {e}")
        raise


@pytest.fixture(scope="function")
def clean_device_page(authenticated_driver):
    """Очищает все устройства перед началом теста и возвращает страницу"""
    
    try:
        sidebar = SidebarMenu(authenticated_driver)
        device_page = sidebar.click_device_release()
        time.sleep(2)
        
        # Проверяем, есть ли активная партия
        try:
            close_btn = authenticated_driver.find_element(By.ID, "btnCloseParty")
            if close_btn.is_displayed():
                print("⚠️ Найдена активная партия, закрываем...")
                authenticated_driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(0.5)
                confirm = authenticated_driver.find_element(By.ID, "mainModalPrimary")
                authenticated_driver.execute_script("arguments[0].click();", confirm)
                time.sleep(2)
                authenticated_driver.refresh()
                time.sleep(1)
        except:
            pass
        
        # Ожидаем кнопку создания партии
        wait = WebDriverWait(authenticated_driver, 15)
        create_party_btn = wait.until(
            EC.element_to_be_clickable(device_page.CREATE_PARTY_BUTTON)
        )
        print("✅ Кнопка 'Создать партию' доступна")
        
        # Кликаем для открытия формы
        authenticated_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_party_btn)
        time.sleep(0.5)
        authenticated_driver.execute_script("arguments[0].click();", create_party_btn)
        time.sleep(1)
        
        wait.until(EC.visibility_of_element_located(device_page.DEVICE_TYPE_SELECT))
        print("✅ Форма создания партии открыта")
        
        return device_page
        
    except Exception as e:
        print(f"❌ Ошибка при подготовке страницы: {e}")
        raise


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get('driver')
        if driver:
            try:
                screenshot_dir = "screenshots"
                os.makedirs(screenshot_dir, exist_ok=True)
                safe_name = item.name.replace('[', '_').replace(']', '_').replace('/', '_').replace('\\', '_')
                screenshot_path = os.path.join(screenshot_dir, f"{safe_name}.png")
                driver.save_screenshot(screenshot_path)
                print(f"\n📸 Скриншот сохранен: {screenshot_path}")
                
                html_path = os.path.join(screenshot_dir, f"{safe_name}.html")
                try:
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"📄 HTML сохранен: {html_path}")
                except:
                    pass
                
            except Exception as e:
                print(f"⚠️ Не удалось сохранить скриншот: {e}")


# Опционально: фикстура для очистки после каждого теста
@pytest.fixture(scope="function", autouse=True)
def cleanup_after_test(request):
    """Автоматическая очистка после каждого теста"""
    yield
    # Здесь можно добавить очистку, если нужно
    pass

def pytest_configure(config):
    """Регистрируем плагин для отправки в Slack"""
    try:
        from slack_plugin import SlackPlugin
        config.pluginmanager.register(SlackPlugin(config), "slack_plugin")
        print("✅ Slack плагин зарегистрирован")
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ Ошибка регистрации Slack плагина: {e}")


def pytest_sessionfinish(session, exitstatus):
    """Принудительно генерируем Allure-отчет после тестов"""
    
    import os
    import subprocess
    import shutil
    
    # Проверяем, что есть результаты
    if not os.path.exists("allure-results"):
        return
    
    print("\n" + "="*60)
    print("📊 Генерация Allure-отчета...")
    print("="*60)
    
    try:
        # Путь к Allure
        allure_path = shutil.which("allure") or "allure"
        
        # Генерируем отчет
        result = subprocess.run(
            [allure_path, "generate", "allure-results", "-o", "allure-report", "--clean"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Allure-отчет сгенерирован")
            
            # Проверяем, есть ли summary.json в allure-report
            if os.path.exists("allure-report/widgets/summary.json"):
                # Копируем в allure-results
                os.makedirs("allure-results/widgets", exist_ok=True)
                shutil.copy("allure-report/widgets/summary.json", "allure-results/widgets/summary.json")
                print("✅ summary.json скопирован в allure-results")
            else:
                # Если нет summary.json — создаём вручную
                print("⚠️ summary.json не найден, создаём вручную...")
                
                # Собираем статистику из result-файлов
                import json
                import glob
                
                result_files = glob.glob("allure-results/*-result.json")
                total = len(result_files)
                passed = 0
                failed = 0
                broken = 0
                
                for file in result_files:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        status = data.get('status', 'unknown')
                        if status == 'passed':
                            passed += 1
                        elif status == 'failed':
                            failed += 1
                        elif status == 'broken':
                            broken += 1
                
                summary = {
                    "statistic": {
                        "total": total,
                        "passed": passed,
                        "failed": failed,
                        "broken": broken,
                        "skipped": 0,
                        "unknown": 0
                    },
                    "time": {
                        "duration": 0
                    }
                }
                
                os.makedirs("allure-results/widgets", exist_ok=True)
                with open("allure-results/widgets/summary.json", 'w', encoding='utf-8') as f:
                    json.dump(summary, f)
                print("✅ summary.json создан вручную")
            
            # Отправляем в Slack
            print("📤 Отправка в Slack...")
            slack_result = subprocess.run(
                ["python", "send_allure_to_slack.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if slack_result.returncode == 0:
                print("✅ Отчет отправлен в Slack!")
                if slack_result.stdout:
                    print(slack_result.stdout)
            else:
                print(f"⚠️ Ошибка отправки в Slack: {slack_result.stderr}")
        else:
            print(f"⚠️ Ошибка генерации отчета: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
    
    print("="*60)