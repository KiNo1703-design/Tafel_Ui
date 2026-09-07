# slack_plugin.py
import pytest
import subprocess
import os


class SlackPlugin:
    """Плагин для отправки Allure отчета в Slack"""

    def __init__(self, config):
        self.config = config

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session, exitstatus):
        """Отправка отчета после завершения тестов"""
        
        # Проверяем, что использовался флаг --alluredir
        args = session.config.invocation_params.args
        if "--alluredir" not in args:
            return
        
        # Проверяем, что есть результаты
        if not os.path.exists("allure-results"):
            return
        
        print("\n📤 Автоматическая отправка в Slack...")
        
        try:
            # Запускаем скрипт отправки
            result = subprocess.run(
                ["python", "send_allure_to_slack.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Отчет отправлен в Slack!")
            else:
                print(f"⚠️ Ошибка отправки: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⚠️ Таймаут отправки в Slack")
        except Exception as e:
            print(f"⚠️ Не удалось отправить отчет: {e}")


def pytest_configure(config):
    """Регистрируем плагин"""
    config.pluginmanager.register(SlackPlugin(config), "slack_plugin")