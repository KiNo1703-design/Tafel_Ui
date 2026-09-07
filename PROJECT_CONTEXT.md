# КОНТЕКСТ ПРОЕКТА: UI-тесты выпуска устройств
Путь: C:\Users\k.novikov\Desktop\QA\Задачи\UI тест
(Создан 2026-09-04. Обновлять этот файл при каждом изменении кода, чтобы не перечитывать исходники.)

## ЧТО ЭТО
Selenium + pytest (Page Object Model) e2e-тесты для https://qa-manufacture.lar.tech — системы выпуска устройств ("Выпуск устройств"):
полный цикл: логин → создать партию (выбрать тип выпуска и модель) → добавить устройства в модалке → проверить в списке → удалить → закрыть партию.

## ОКРУЖЕНИЕ ЗАПУСКА (важно!)
- Рабочий интерпретатор: C:/Users/k.novikov/AppData/Local/Programs/Python/Python312/python.exe — Python 3.12.3, pytest 9.1.1, selenium 4.44.0.
- python в PATH терминала = venv Hermes (3.11.16), pytest ТАМ НЕТ. Тесты запускать ТОЛЬКО явным путём Python312.
- requirements.txt УСТАРЕЛ (пины pytest==7.4.3, selenium==4.15.2) — фактически стоят 9.1.1 / 4.44.0. webdriver-manager указан, но НЕ используется.
- chromedriver.exe (42 МБ) лежит в корне проекта; conftest: Service("chromedriver.exe") — относительный путь → запуск строго из корня проекта.
- .env пустой (0 байт). Креды берутся из config.py: TEST_USERNAME/TEST_PASSWORD = qa/qa (env-переменные перекрывают, но не заданы).
- Браузер НЕ headless (строка закомментирована в conftest), window-size 1920x1080, implicit wait 2 c.
- При падении теста хук conftest сохраняет скриншот: screenshots/<имя_теста>.png (у параметризованных — с [param] в имени).
- Запуск: cd "C:/Users/k.novikov/Desktop/QA/Задачи/UI тест" && "C:/Users/k.novikov/AppData/Local/Programs/Python/Python312/python.exe" -m pytest tests/ -v -s
  Фильтр по типу: -k "twin" или -k "lora_lte". Один тест: tests/test_release_types.py::TestReleaseTypes::test_create_party_with_devices
- ОГРАНИЧЕНИЕ: у используемой модели (deepseek) НЕТ vision — скриншоты глазами не прочитать (vision_analyze возвращает Unsupported Image). Разбирать падения по HTML/тексту, логам или просить пользователя описать скриншот.

## СТРУКТУРА
- config.py — Config: BASE_URL, креды, RELEASE_TYPES (данные и конфиг полей для типов выпуска).
- conftest.py — фикстура driver (scope=function, Chrome), фикстура auth_page, хук скриншотов при падении.
- pages/base_page.py — BasePage: wait = WebDriverWait(driver, 15, poll 0.5). find_element (visibility), click (clickable), enter_text (clear+send_keys), is_element_present (timeout 5).
- pages/auth_page.py — страница входа.
- pages/sidebar_menu.py — боковое меню, переход к DeviceCreationPage.
- pages/device_creation_page.py — создание партии + список устройств.
- pages/add_device_modal.py — универсальная модалка добавления устройства (input + select2).
- tests/test_login.py — тест успешного входа.
- tests/test_release_types.py — основной параметризованный e2e-тест (lora_lte, twin).
- screenshots/ — артефакты падений. test_full_party_cycle.png и test_create_party_with_devices[twin].png — БИТОВО ИДЕНТИЧНЫ (один md5) — мусор от удалённых/старых тестов.

## config.py: РЕЛИЗ-ТИПЫ (данные-движок тестов)
Config.RELEASE_TYPES = {ключ: {...}}, каждый:
  display_name — как пункт в select2 "тип устройства"
  model — как пункт в select2 "модель"
  fields — {имя_поля: {"id": DOM-id, "required": bool, "type": "input"|"select2"}} — форма модалки
  devices — [{имя_поля: значение, ...}] — тестовые устройства
  unique_field — по какому полю искать/удалять в списке

1) lora_lte: display "Выходной контроль Термоманометра LRPC (LORA+LTE)", model "Термоманометр LRPC исполнение 2".
   Поля: devEui, imei (оба input). 3 устройства (devEui 04:97:90:00:21:3A:7B:73..75, imei 866234070577892..894). unique_field=imei.
2) twin: display "Twin-комплект", model "Для двух приборов учета".
   Поля (9): devEui(input), serialTwinFirst, modelTwinFirst(select2), indicationTwinFirst, serialTwinSecond, modelTwinSecond(select2), indicationTwinSecond, partAmount(select2: "1 литр"/"10 литров"), scheduler(select2: "Оставить без изменений"/"1 раз в день 24 часовых показания"). 2 устройства (devEui ...7B:80/81). unique_field=devEui.
   Значения select2 в devices — ВИДИМЫЙ ТЕКСТ опции (например "WFK26"), клик идёт по contains(text()).

## ПОТОК СТРАНИЦ И КЛЮЧЕВЫЕ ЛОКАТОРЫ
AuthPage (/auth): поля id=email, id=password; кнопка button[type='submit']; успех = видим #userProfile; ошибка = .alert-danger, .invalid-feedback, .alert. login() ждёт ухода с /auth. get_user_name() — первые 2 span внутри #userProfile.
SidebarMenu: пункт //span[@class='sidebar__text' and text()='Выпуск устройств'] → возвращает DeviceCreationPage.
DeviceCreationPage:
  Кнопка "Создать партию" id=createParty (экран после закрытия партии).
  select2 типа: id=select2-deviceType-container; модели: id=select2-deviceModel-container; дропдаун .select2-results__options; опция ищется //li[contains(@class,'select2-results__option') and contains(text(),'...')].
  "Создать" (создать партию) id=execParty; успех = видим //span[contains(text(),'Партия №')].
  "Добавить устройство" id=add → AddDeviceModal.
  "Завершить выпуск и сохранить отчет" id=btnCloseParty → модалка h3#mainModalTitle содержит 'Закрытие партии' → подтверждение id=mainModalPrimary → ждём видимость createParty.
AddDeviceModal:
  Сохранить id=saveDevice; закрыть окно id=closeForm; сообщение об успехе id=resultMessage.
  fill_device_fields(fields): для каждого поля ищет конфиг ЛИНЕЙНЫМ поиском по всем RELEASE_TYPES (по имени поля); select2 → клик по id=select2-<field_id>-container → опция //li[contains(@class,'select2-results__option') and contains(text(),'значение')] (fallback: точный text()); input → id=<field_id>, clear+send_keys. Пропускает None/"".
  Удаление: крестик //*[contains(text(),'<id>')]/ancestor::tr//i[contains(@class,'text-danger')] → модалка 'Удаление устройства' → mainModalPrimary → ждём исчезновения id.
  Проверки: is_device_in_list / is_device_deleted — contains(text()) по ВСЕЙ странице (хрупко!).
  Счётчик: //td[contains(@class,'pl-3')]//span[contains(@class,'imei')], fallback //table//tbody//tr.

## ТЕСТЫ
test_login.py::TestLogin::test_successful_login — открыть /auth, login(qa/qa), ждёт #userProfile, имя ≠ "Имя не найдено".

test_release_types.py::TestReleaseTypes — fixture setup(autouse): логин + assert успеха → SidebarMenu → DeviceCreationPage → click_create_party() (ждёт появления select2-deviceType-container).
  test_create_party_with_devices[release_type_key] для lora_lte и twin:
    1. select_device_type(display_name)  2. select_device_model(model)  3. create_party() (execParty, ждёт 'Партия №')
    4. Для каждого устройства: open_add_device_modal → fill_device_fields → save_device → assert is_device_added_successfully (resultMessage) → close_modal → assert is_device_in_list(unique_id)
    5. assert get_device_count_in_list() >= len(devices)
    6. Удалить ВСЕ устройства в обратном порядке через delete_device_by_identifier
    7. close_party() → assert кнопка createParty видна

## ХРУПКИЕ МЕСТА / КАНДИДАТЫ НА УЛУЧШЕНИЕ (чеклист для работы)
1. requirements.txt расходится с реальным окружением (pytest 9.1.1 / selenium 4.44.0 vs пины 7.4.3/4.15.2); webdriver-manager не используется — chromedriver локальный, риск рассинхрона версий с Chrome.
2. Service("chromedriver.exe") — относительный путь: запуск только из корня проекта.
3. Креды qa/qa хардкодом в config.py; .env пуст (задумка с dotenv не работает).
4. Много time.sleep (0.3–2 c) вместо WebDriverWait/EC — основной источник флаков.
5. fill_device_fields ищет конфиг поля перебором всех RELEASE_TYPES по имени поля — сломается при пересечении имён полей между типами.
6. Локаторы contains(text()) по всей странице (поиск в списке, select2-опции) — могут цеплять не тот элемент.
7. Данные устройств статичны в config.py: повторный прогон/падение середины теста может конфликтовать (те же EUI/imei); cleanup зависит от успеха теста.
8. get_device_count_in_list заточен под конкретную вёрстку (span.imei в td.pl-3).
9. Скриншоты от удалённых тестов (test_full_party_cycle, test_required_fields_validation) висят в screenshots/ — устаревшие артефакты, тестов в tests/ нет. Два файла — дубликаты.
10. Русские emoji-логи в print — ок для -s, но в отчётах pytest кодировка может падать (Windows cp1251/utf-8).

## ПРИМЕЧАНИЯ
- Все импорты вида "pages.X", "config" — pytest должен стартовать из корня проекта.
- Версии chromedriver/Chrome проверять: chromedriver.exe --version vs chrome://version.
- screenshots/test_required_fields_validation[twin].png (99 КБ) — единственный уникальный скриншот; показывает форму twin-модалки (если понадобится разбор — только глазами пользователя или OCR).
