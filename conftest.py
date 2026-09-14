# conftest.py
import pytest
import subprocess
import shutil
import os
import time
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


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запуск в headless режиме"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox"],
        help="Выбор браузера: chrome или firefox"
    )


def pytest_sessionstart(session):
    print("\n[INFO] Cleaning allure-results before run...")
    try:
        if os.path.exists("allure-results"):
            shutil.rmtree("allure-results")
            print("  [OK] allure-results removed")
        os.makedirs("allure-results", exist_ok=True)
        print("  [OK] allure-results created")
    except Exception as e:
        print(f"  [WARN] Cleanup error: {e}")


@pytest.fixture(scope="function")
def driver(request):
    print("\n[INFO] Starting browser...")
    
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
        
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            print("[INFO] Running in headless mode")
        else:
            print("[INFO] Running with visible browser")
        
        driver = None
        try:
            # ✅ В контейнере используем системный chromedriver
            chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
            if chromedriver_path:
                print(f"[INFO] Using system chromedriver: {chromedriver_path}")
                service = Service(chromedriver_path)
            else:
                print("[INFO] Using webdriver-manager")
                service = Service(ChromeDriverManager().install())
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(Config.IMPLICIT_WAIT)
            driver.set_page_load_timeout(60)
            
            print("[OK] Chrome browser started")
            yield driver
        except Exception as e:
            print(f"[ERROR] Failed to start browser: {e}")
            raise
        finally:
            if driver:
                print("[INFO] Closing browser...")
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
            print("[INFO] Running in headless mode")
        else:
            print("[INFO] Running with visible browser")
        
        driver = None
        try:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.implicitly_wait(Config.IMPLICIT_WAIT)
            driver.set_page_load_timeout(60)
            print("[OK] Firefox browser started")
            yield driver
        except Exception as e:
            print(f"[ERROR] Failed to start browser: {e}")
            raise
        finally:
            if driver:
                print("[INFO] Closing browser...")
                try:
                    driver.quit()
                except:
                    pass


@pytest.fixture(scope="function")
def authenticated_driver(driver):
    ErrorCollector.clear()
    creds = Config.get_credentials()
    
    try:
        auth_page = AuthPage(driver).open()
        auth_page.login(creds["username"], creds["password"])
        assert auth_page.is_login_successful(), "Failed to login"
        print("[OK] Authentication completed")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar, .main-content, nav")))
        time.sleep(1)
        
    except Exception as e:
        print(f"[ERROR] Authentication error: {e}")
        try:
            driver.save_screenshot("auth_error.png")
            print("[INFO] Screenshot saved as auth_error.png")
        except:
            pass
        raise
    
    return driver


@pytest.fixture(scope="function")
def device_page(authenticated_driver):
    try:
        sidebar = SidebarMenu(authenticated_driver)
        device_page = sidebar.click_device_release()
        time.sleep(2)
        
        try:
            close_btn = authenticated_driver.find_element(By.ID, "btnCloseParty")
            if close_btn.is_displayed():
                print("[WARN] Active party found, closing...")
                authenticated_driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(0.5)
                confirm = authenticated_driver.find_element(By.ID, "mainModalPrimary")
                authenticated_driver.execute_script("arguments[0].click();", confirm)
                time.sleep(2)
                authenticated_driver.refresh()
                time.sleep(1)
        except:
            pass
        
        wait = WebDriverWait(authenticated_driver, 15)
        create_party_btn = wait.until(
            EC.element_to_be_clickable(device_page.CREATE_PARTY_BUTTON)
        )
        print("[OK] 'Create party' button available")
        
        authenticated_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_party_btn)
        time.sleep(0.5)
        authenticated_driver.execute_script("arguments[0].click();", create_party_btn)
        time.sleep(1)
        
        wait.until(EC.visibility_of_element_located(device_page.DEVICE_TYPE_SELECT))
        print("[OK] Party creation form opened")
        
        return device_page
        
    except TimeoutException as e:
        print(f"[ERROR] Timeout waiting for elements: {e}")
        try:
            authenticated_driver.save_screenshot("device_page_error.png")
            print("[INFO] Screenshot saved as device_page_error.png")
        except:
            pass
        raise
    except Exception as e:
        print(f"[ERROR] Error opening creation page: {e}")
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
                print(f"\n[INFO] Screenshot saved: {screenshot_path}")
                
                html_path = os.path.join(screenshot_dir, f"{safe_name}.html")
                try:
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"[INFO] HTML saved: {html_path}")
                except:
                    pass
                
            except Exception as e:
                print(f"[WARN] Failed to save screenshot: {e}")


def pytest_configure(config):
    try:
        from slack_plugin import SlackPlugin
        config.pluginmanager.register(SlackPlugin(config), "slack_plugin")
        print("[OK] Slack plugin registered")
    except ImportError:
        pass
    except Exception as e:
        print(f"[WARN] Error registering Slack plugin: {e}")


def pytest_sessionfinish(session, exitstatus):
    if not os.path.exists("allure-results"):
        print("[WARN] allure-results not found, skipping")
        return
    
    print("\n" + "="*60)
    print("[INFO] Generating Allure report...")
    print("="*60)
    
    try:
        allure_path = shutil.which("allure") or "allure"
        
        result = subprocess.run(
            [allure_path, "generate", "allure-results", "-o", "allure-report", "--clean"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("[OK] Allure report generated")
            
            if os.path.exists("allure-report/widgets/summary.json"):
                os.makedirs("allure-results/widgets", exist_ok=True)
                shutil.copy("allure-report/widgets/summary.json", "allure-results/widgets/summary.json")
                print("[OK] summary.json copied to allure-results")
            else:
                print("[WARN] summary.json not found, creating manually...")
                
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
                print("[OK] summary.json created manually")
            
            print("[INFO] Sending to Slack...")
            slack_result = subprocess.run(
                ["python", "send_allure_to_slack.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if slack_result.returncode == 0:
                print("[OK] Report sent to Slack!")
                if slack_result.stdout:
                    print(slack_result.stdout)
            else:
                print(f"[WARN] Error sending to Slack: {slack_result.stderr}")
        else:
            print(f"[WARN] Error generating report: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("[WARN] Timeout generating report")
    except FileNotFoundError as e:
        print(f"[WARN] File not found: {e}")
        print("   Check Allure installation: allure --version")
    except Exception as e:
        print(f"[WARN] Error: {e}")
    
    print("="*60)