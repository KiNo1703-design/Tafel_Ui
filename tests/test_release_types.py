# tests/test_release_types.py
import pytest
import allure
from actions.party_actions import PartyActions
from config import Config


class TestReleaseTypes:

    @pytest.mark.parametrize(
        "release_type_key, scenario_name",
        [
            (rt, scenario)
            for rt in Config.get_all_release_types()
            for scenario in Config.get_scenarios(rt)
        ]
    )
    def test_party_with_devices(self, device_page, release_type_key, scenario_name):
        """Тест с разными сценариями для каждого типа"""
        release_type = Config.get_release_type(release_type_key)
        
        # ✅ Устанавливаем красивое русское название из конфига
        allure.dynamic.title(f"{release_type['display_name']} - {scenario_name}")
        
        scenarios = Config.get_scenarios(release_type_key)
        if scenario_name not in scenarios:
            pytest.skip(f"Сценарий '{scenario_name}' не поддерживается для {release_type_key}")
        
        scenario = scenarios[scenario_name]
        devices_count = scenario.get("devices_count", 1)
        
        # ✅ Добавляем Allure шаги
        with allure.step(f"Создание партии для {release_type['display_name']}"):
            result = PartyActions.create_party_add_remove_close(
                device_page, 
                release_type, 
                devices_count
            )
        
        # ✅ Добавляем информацию в отчет
        allure.attach(
            f"Тип выпуска: {release_type['display_name']}\n"
            f"Сценарий: {scenario_name}\n"
            f"Количество устройств: {devices_count}\n"
            f"Результат: {len(result)} устройств добавлено и удалено",
            name="Информация о тесте",
            attachment_type=allure.attachment_type.TEXT
        )
        
        print(f"✅ Тест для '{release_type['display_name']}' / '{scenario_name}' пройден!")