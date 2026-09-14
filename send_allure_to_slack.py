# send_allure_to_slack.py
import json
import os
import requests
import subprocess
import zipfile
import shutil
from datetime import datetime
import glob
from dotenv import load_dotenv

load_dotenv()


def get_all_tests():
    """Получает ВСЕ тесты из allure-results"""
    try:
        result_files = glob.glob('allure-results/*-result.json')
        if not result_files:
            return None
        
        tests = []
        for file in result_files:
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
            
            if name in seen_names:
                continue
            seen_names.add(name)
            
            status_details = test.get('statusDetails', {})
            error = status_details.get('message', 'No error message')
            
            if 'Stacktrace' in error:
                error = error.split('Stacktrace')[0].strip()
            
            if len(error) > 200:
                error = error[:200] + '...'
            
            failed_tests.append({
                'name': name,
                'error': error
            })
    
    return failed_tests


def generate_allure_report():
    """Генерирует Allure отчет (всегда)"""
    try:
        allure_path = shutil.which("allure") or "allure"
        
        if not os.path.exists("allure-results"):
            print("[ERROR] allure-results not found")
            return False
        
        result = subprocess.run(
            [allure_path, "generate", "allure-results", "-o", "allure-report", "--clean"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("[OK] Allure report generated")
            return True
        else:
            print(f"[ERROR] Failed to generate report: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def zip_allure_report():
    """Создает zip архив с Allure отчетом"""
    try:
        if not os.path.exists("allure-report"):
            print("[ERROR] allure-report not found")
            return None
        
        zip_path = "allure-report.zip"
        
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("allure-report"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, "allure-report")
                    zipf.write(file_path, arcname)
        
        print(f"[OK] Report zipped: {zip_path}")
        return zip_path
    except Exception as e:
        print(f"[ERROR] Failed to zip report: {e}")
        return None


def send_file_to_slack(file_path, filename="allure-report.zip"):
    """Отправляет файл в Slack ТОЛЬКО если есть ошибки"""
    
    # Проверяем статус тестов
    tests = get_all_tests()
    if not tests:
        return False
    
    summary = get_summary_from_files(tests)
    failed = summary['statistic']['failed']
    broken = summary['statistic']['broken']
    
    # Если все тесты прошли — НЕ отправляем
    if failed == 0 and broken == 0:
        print("[INFO] All tests passed, skipping file upload")
        return True
    
    # Проверяем токен
    slack_token = os.getenv('SLACK_TOKEN')
    if not slack_token:
        print("[WARN] SLACK_TOKEN not set, skipping file upload")
        return False
    
    try:
        channel = os.getenv('SLACK_CHANNEL', '#general')
        status_text = f"FAILED (Failed: {failed}, Broken: {broken})"
        
        url = "https://slack.com/api/files.upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/zip')}
            data = {
                'channels': channel,
                'initial_comment': f'Allure Test Report - {status_text}\n\nRun: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'filename': filename
            }
            headers = {
                'Authorization': f'Bearer {slack_token}'
            }
            
            response = requests.post(url, data=data, files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("[OK] Report file sent to Slack!")
                return True
            else:
                print(f"[ERROR] Slack API error: {result.get('error')}")
                return False
        else:
            print(f"[ERROR] HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def format_slack_message(summary, failed_tests, allure_url=None):
    """Форматирует текстовое сообщение для Slack (БЕЗ ЭМОДЗИ)"""
    
    total = summary['statistic']['total']
    passed = summary['statistic']['passed']
    failed = summary['statistic']['failed']
    broken = summary['statistic']['broken']
    
    # Всегда FAILED, потому что отправляем только при ошибках
    color = "#FF0000"
    status_text = "FAILED"
    
    message = {
        "attachments": [
            {
                "color": color,
                "title": f"Test Run - {status_text}",
                "fields": [
                    {
                        "title": "Test Results",
                        "value": f"* Total: {total}\n"
                                f"* Passed: {passed}\n"
                                f"* Failed: {failed}\n"
                                f"* Broken: {broken}",
                        "short": False
                    },
                    {
                        "title": "Time",
                        "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "short": True
                    }
                ],
                "footer": "UI Auto Tests",
                "footer_icon": "https://allure-framework.github.io/allure-docs/static/img/allure-logo.svg"
            }
        ]
    }
    
    # Ссылка на Allure отчёт
    if allure_url:
        message["attachments"][0]["fields"].append({
            "title": "Allure Report",
            "value": f"<{allure_url}|Open Full Report>",
            "short": False
        })
    
    # Упавшие тесты
    if failed_tests:
        test_list = ""
        for idx, test in enumerate(failed_tests[:5], 1):
            test_list += f"{idx}. {test['name']}\n"
            test_list += f"   {test['error']}\n\n"
        
        if len(failed_tests) > 5:
            test_list += f"... and {len(failed_tests) - 5} more tests\n"
        
        message["attachments"][0]["fields"].append({
            "title": f"Failed Tests ({len(failed_tests)})",
            "value": test_list,
            "short": False
        })
    
    return message


def send_text_to_slack():
    """Отправляет текстовый отчет в Slack ТОЛЬКО если есть ошибки"""
    
    tests = get_all_tests()
    if not tests:
        print("[ERROR] No test results found")
        return False
    
    summary = get_summary_from_files(tests)
    failed = summary['statistic']['failed']
    broken = summary['statistic']['broken']
    
    # ✅ Если все тесты прошли — НЕ отправляем
    if failed == 0 and broken == 0:
        print("[INFO] All tests passed, skipping Slack notification")
        return True
    
    # Есть ошибки — отправляем
    failed_tests = get_failed_tests(tests)
    allure_url = os.getenv('ALLURE_REPORT_URL')
    
    message = format_slack_message(summary, failed_tests, allure_url)
    
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("[ERROR] SLACK_WEBHOOK_URL is not set")
        return False
    
    try:
        response = requests.post(webhook_url, json=message)
        if response.status_code == 200:
            print("[OK] Text report sent to Slack!")
            return True
        else:
            print(f"[ERROR] {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def send_to_slack():
    """Основная функция"""
    
    print("[INFO] Processing test report...")
    
    # 1. Генерируем отчет (ВСЕГДА)
    generate_allure_report()
    
    # 2. Проверяем статус тестов
    tests = get_all_tests()
    if not tests:
        print("[ERROR] No test results found")
        return
    
    summary = get_summary_from_files(tests)
    failed = summary['statistic']['failed']
    broken = summary['statistic']['broken']
    passed = summary['statistic']['passed']
    
    # 3. Если всё прошло — только логируем
    if failed == 0 and broken == 0:
        print(f"[OK] All {passed} tests passed. Skipping Slack notification.")
        return
    
    # 4. Если есть ошибки — отправляем в Slack
    print(f"[WARN] Found {failed} failed and {broken} broken tests. Sending to Slack...")
    send_text_to_slack()
    
    # 5. Отправляем zip-файл (только если есть ошибки)
    if os.path.exists("allure-report"):
        zip_path = zip_allure_report()
        if zip_path:
            send_file_to_slack(zip_path)
            try:
                os.remove(zip_path)
            except:
                pass
    
    print("[OK] Done!")


if __name__ == "__main__":
    send_to_slack()
