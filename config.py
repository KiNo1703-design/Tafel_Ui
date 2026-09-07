# config.py
class Config:
    # ===== Базовые настройки =====
    BASE_URL = "https://qa-manufacture.lar.tech"
    TEST_USERNAME = "qa"
    TEST_PASSWORD = "qa"
    
    # ===== Таймауты =====
    DEFAULT_TIMEOUT = 15
    IMPLICIT_WAIT = 3
    POLL_FREQUENCY = 0.5
    
    # ===== Данные для тестов =====
    
    RELEASE_TYPES = {
        "lora_lte": {
            "display_name": "Выходной контроль Термоманометра LRPC (LORA+LTE)",
            "model": "Термоманометр LRPC исполнение 2",
            "unique_field": "imei",
            "party_fields": {
                "pressure": {"id": "pressure", "value": "5"},
                "temperature": {"id": "temperature", "value": "25.5"}
            },
            "fields": {
                "devEui": {"id": "devEui", "required": True},
                "imei": {"id": "imei", "required": True}
            },
            "devices": [
                {"devEui": "04:97:90:00:21:3A:7B:73", "imei": "866234070577892"},
                {"devEui": "04:97:90:00:21:3A:7B:74", "imei": "866234070577893"},
                {"devEui": "04:97:90:00:21:3A:7B:75", "imei": "866234070577894"}
            ],
            "scenarios": {
                "add_multiple": {"devices_count": 3},
                # "add_single": {"devices_count": 1}
            }
        },
        "twin": {
            "display_name": "Twin-комплект",
            "model": "Для двух приборов учета",
            "unique_field": "devEui",
            "party_fields": {},
            "fields": {
                "devEui": {"id": "devEui", "required": True},
                "serialTwinFirst": {"id": "serialTwinFirst", "required": True},
                "modelTwinFirst": {"id": "modelTwinFirst", "required": True, "type": "select2"},
                "indicationTwinFirst": {"id": "indicationTwinFirst", "required": True},
                "serialTwinSecond": {"id": "serialTwinSecond", "required": True},
                "modelTwinSecond": {"id": "modelTwinSecond", "required": True, "type": "select2"},
                "indicationTwinSecond": {"id": "indicationTwinSecond", "required": True},
                "partAmount": {"id": "partAmount", "required": True, "type": "select2"},
                "scheduler": {"id": "scheduler", "required": True, "type": "select2"}
            },
            "devices": [
                {
                    "devEui": "04:97:90:00:21:3A:7B:80",
                    "serialTwinFirst": "12-345678",
                    "modelTwinFirst": "WFK26",
                    "indicationTwinFirst": "12345.678",
                    "serialTwinSecond": "12-345679",
                    "modelTwinSecond": "WFK25",
                    "indicationTwinSecond": "12345.679",
                    "partAmount": "1 литр",
                    "scheduler": "Оставить без изменений"
                },
                {
                    "devEui": "04:97:90:00:21:3A:7B:81",
                    "serialTwinFirst": "12-345680",
                    "modelTwinFirst": "WFK27",
                    "indicationTwinFirst": "12345.680",
                    "serialTwinSecond": "12-345681",
                    "modelTwinSecond": "WFK24",
                    "indicationTwinSecond": "12345.681",
                    "partAmount": "10 литров",
                    "scheduler": "1 раз в день 24 часовых показания"
                }
            ],
            "scenarios": {
                "add_multiple": {"devices_count": 2},
               #  "add_single": {"devices_count": 1}
            }
        },
        "energo": {
            "display_name": "Энергомера CEx08 СПОДЕС без этикетки",
            "model": "CE310 СПОДЭС",
            "unique_field": "serial",
            "party_fields": {},
            "fields": {
                "serial": {"id": "serial", "required": True}
            },
            "devices": [
                {"serial": "012465184133208"},
                {"serial": "012465184133209"},
                {"serial": "012465184133210"}
            ],
            "scenarios": {
                "add_multiple": {"devices_count": 3},
                # "add_single": {"devices_count": 1}
            }
        },
        "Mercury_with_label": {
                    "display_name": "Меркурий СПОДЭС с этикеткой",
                    "model": "Меркурий 208 СПОДЕС",
                    "unique_field": "serial", 
                    "party_fields": {},
                    "fields": {
                "serial": {"id": "serial", "required": True},
                "devEui": {"id": "devEui", "required": True}
                    },
                    "devices": [
                        {"devEui": "04:97:90:00:21:3A:7B:73","serial": "50580357"},
                        {"devEui": "04:97:90:00:21:3A:7B:71","serial": "50580322"},
                        {"devEui": "04:97:90:00:21:3A:7B:56","serial": "50580357"}
                    ],
                    "scenarios": {
                        "add_multiple": {"devices_count": 3},
                        # "add_single": {"devices_count": 1}
                    }
         },
        "Mercury_with_remote": {
    "display_name": "Универсальный выпуск Меркурий с блоком индикации",
    "model": "Меркурий 204",
    "unique_field": "serial", 
    "party_fields": {},
    "fields": {
        "serial": {"id": "serial", "required": True},
        "serialRemote": {"id": "serialRemote", "required": True}  # ✅ Исправлено!
    },
    "devices": [
        {"serial": "50580357", "serialRemote": "0000016043600000"},
        {"serial": "50580348", "serialRemote": "0000016043800000"},
        {"serial": "50580213", "serialRemote": "0000016045800000"}
    ],
    "scenarios": {
        "add_multiple": {"devices_count": 3},
    }
}
    }
    
    # ===== Данные для авторизации =====
    @classmethod
    def get_credentials(cls):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        return {
            "username": os.getenv("TEST_USERNAME", cls.TEST_USERNAME),
            "password": os.getenv("TEST_PASSWORD", cls.TEST_PASSWORD)
        }
    
    @classmethod
    def get_all_release_types(cls):
        return list(cls.RELEASE_TYPES.keys())
    
    @classmethod
    def get_release_type(cls, key):
        return cls.RELEASE_TYPES.get(key)
    
    @classmethod
    def get_scenarios(cls, release_type_key):
        release_type = cls.RELEASE_TYPES.get(release_type_key, {})
        return release_type.get("scenarios", {})