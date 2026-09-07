# send_allure_to_slack.py
import json
import os
import requests
from datetime import datetime
import glob
from dotenv import load_dotenv

load_dotenv()


def get_latest_test_run():
    """Получает информацию о последнем запуске тестов"""
    try:
        result_files = glob.glob('allure-results/*-result.json')
        if not result_files:
            return None
        
        result_files.sort(key=os.path.getctime, reverse=True)
        
        # Берем все файлы за последние 5 минут
        import time
        now = time.time()
        recent_files = [f for f in result_files if now - os.path.getctime(f) < 300]
        
        if not recent_files:
            recent_files = [result_files[0]]
        
        tests = []
        for file in recent_files:
            with open(file, 'r', encoding='utf-8') as f:
                tests.append(json.load(f))
        
        return tests
    except Exception as e:
        print(f"[WARN] {e}")
        return None


def get_summary_from_files(tests):
    """Создает summary из тестов"""
    if not tests:
        return None
    
    total = len(tests)
    passed = 0
    failed = 0
    broken = 0
    
    for test in tests:
        status = test.get('status', 'unknown')
        if status == 'passed':
            passed += 1
        elif status == 'failed':
            failed += 1
        elif status == 'broken':
            broken += 1
    
    return {
        'statistic': {
            'total': total,
            'passed': passed,
            'failed': failed,
            'broken': broken,
            'skipped': 0,
            'unknown': 0
        },
        'time': {
            'duration': 0
        }
    }


def get_failed_tests(tests):
    """Получает упавшие тесты без дубликатов"""
    failed_tests = []
    seen_names = set()
    
    for test in tests:
        if test.get('status') in ['failed', 'broken']:
            name = test.get('name', 'Unknown')
            
            # Убираем дубликаты
            if name in seen_names:
                continue
            seen_names.add(name)
            
            status_details = test.get('statusDetails', {})
            error = status_details.get('message', 'No error message')
            
            # Убираем Stacktrace
            if 'Stacktrace' in error:
                error = error.split('Stacktrace')[0].strip()
            
            # Убираем длинный текст
            if len(error) > 200:
                error = error[:200] + '...'
            
            failed_tests.append({
                'name': name,
                'error': error
            })
    
    return failed_tests


def format_slack_message(summary, failed_tests, allure_url=None):
    """Форматирует сообщение для Slack"""
    
    total = summary['statistic']['total']
    passed = summary['statistic']['passed']
    failed = summary['statistic']['failed']
    broken = summary['statistic']['broken']
    
    # Статус
    if failed > 0 or broken > 0:
        color = "#FF0000"
        status_icon = "❌"
        status_text = "FAILED"
    else:
        color = "#36a64f"
        status_icon = "✅"
        status_text = "PASSED"
    
    # Сообщение
    message = {
        "attachments": [
            {
                "color": color,
                "title": f"{status_icon} *Last Test Run* - *{status_text}*",
                "fields": [
                    {
                        "title": "📊 *Test Results*",
                        "value": f"• *Total:* {total}\n"
                                f"• ✅ *Passed:* {passed}\n"
                                f"• ❌ *Failed:* {failed}\n"
                                f"• ⚠️ *Broken:* {broken}",
                        "short": False
                    },
                    {
                        "title": "🕐 *Time*",
                        "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "short": True
                    }
                ],
                "footer": "UI Auto Tests • Latest Run",
                "footer_icon": "https://allure-framework.github.io/allure-docs/static/img/allure-logo.svg"
            }
        ]
    }
    
    # ✅ Ссылка на Allure отчет
    if allure_url:
        message["attachments"][0]["fields"].append({
            "title": "🔗 *Full Allure Report*",
            "value": f"<{allure_url}|📊 Open detailed report with graphs>",
            "short": False
        })
    
    # ❌ Упавшие тесты
    if failed_tests:
        test_list = ""
        for idx, test in enumerate(failed_tests[:5], 1):
            test_list += f"{idx}. *{test['name']}*\n"
            test_list += f"   ```{test['error']}```\n\n"
        
        if len(failed_tests) > 5:
            test_list += f"• ... и еще {len(failed_tests) - 5} тестов\n"
        
        message["attachments"][0]["fields"].append({
            "title": f"❌ *Failed Tests ({len(failed_tests)})*",
            "value": test_list,
            "short": False
        })
    else:
        message["attachments"][0]["fields"].append({
            "title": "🎉 *All Tests Passed!*",
            "value": "Все автотесты успешно пройдены! 🚀",
            "short": False
        })
    
    return message


def send_to_slack():
    """Отправляет отчет в Slack"""
    
    print("[INFO] Sending latest test report to Slack...")
    
    # Получаем данные
    tests = get_latest_test_run()
    if not tests:
        print("[ERROR] No test results found")
        return False
    
    summary = get_summary_from_files(tests)
    failed_tests = get_failed_tests(tests)
    
    # ✅ URL Allure отчета (добавь в .env)
    allure_url = os.getenv('ALLURE_REPORT_URL')
    
    # Формируем сообщение
    message = format_slack_message(summary, failed_tests, allure_url)
    
    # Отправляем
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("[ERROR] SLACK_WEBHOOK_URL is not set")
        return False
    
    try:
        response = requests.post(webhook_url, json=message)
        if response.status_code == 200:
            print("[OK] Report sent to Slack!")
            return True
        else:
            print(f"[ERROR] {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


if __name__ == "__main__":
    send_to_slack()