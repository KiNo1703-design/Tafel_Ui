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
},
 "MercuryUniversal": {
            "display_name": "Универсальный выпуск Меркурий",
            "model": "Меркурий 204",
            "unique_field": "serial",
            "party_fields": {},
            "fields": {
                "serial": {"id": "serial", "required": True}
            },
            "devices": [
                {"serial": "50580248"},
                {"serial": "40580135"},
                {"serial": "30580055"}
            ],
            "scenarios": {
                "add_multiple": {"devices_count": 3},
               
            }
},
"Mercury204Spodes": {
            "display_name": "Меркурий 204 СПОДЕС",
            "model": "Меркурий 204 СПОДЕС",
            "unique_field": "serial",
            "party_fields": {},
            "fields": {
                "serial": {"id": "serial", "required": True}
            },
            "devices": [
                {"serial": "50580248"},
                {"serial": "83400189"},
                {"serial": "30580055"}
            ],
            "scenarios": {
                "add_multiple": {"devices_count": 3},
               
            }
},
"Mercury206TwoCommand": {
                    "display_name": "Меркурий 206 (двумя командами)",
                    "model": "Меркурий 206",
                    "unique_field": "serial", 
                    "party_fields": {},
                    "fields": {
                "serial": {"id": "serial", "required": True},
                "devEui": {"id": "devEui", "required": True}
                    },
                    "devices": [
                        {"devEui": "04:97:90:00:0F:F5:B1:4C","serial": "50580248"},
                        {"devEui": "04:97:90:00:0F:F5:B2:4A","serial": "50580322"},
                        {"devEui": "04:97:90:00:21:F4:7A:56","serial": "30580055"}
                    ],
                    "scenarios": {
                        "add_multiple": {"devices_count": 3},
                    
                    }
         },
"Mercury208SpodesWithRemote": {
    "display_name": "Меркурий 208 СПОДЕС с дисплеем",
    "model": "Меркурий 208 СПОДЕС",
    "unique_field": "serial", 
    "party_fields": {},
    "fields": {
        "serial": {"id": "serial", "required": True},
        "serialRemote": {"id": "serialRemote", "required": True}
    },
    "devices": [
        {"serial": "50580357", "serialRemote": "0000016043600000"},
        {"serial": "50580348", "serialRemote": "0000016043800000"},
        {"serial": "50580213", "serialRemote": "0000016045800000"}
    ],
    "scenarios": {
        "add_multiple": {"devices_count": 3},
    }
         },

         "MercurySpodesWithLabelForRC": {
    "display_name": "Меркурий СПОДЭС с этикеткой, пульт + GSM",
    "model": "Меркурий 238 СПОДЭС",
    "unique_field": "serial", 
    "party_fields": {},
    "fields": {
        "serial": {"id": "serial", "required": True},
        "serialRemote": {"id": "serialRemote", "required": True},
        "devEui": {"id": "devEui", "required": True} 
    },
    "devices": [
        {"devEui": "04:97:90:00:0F:33:22:00","serial": "50580357", "serialRemote": "0000016043600000"},
        {"devEui": "04:97:90:00:0F:43:11:3A","serial": "50580348", "serialRemote": "0000016043800000"},
        {"devEui": "04:97:90:00:0F:F5:B1:5F","serial": "50580213", "serialRemote": "0000016045800000"}
    ],
    "scenarios": {
        "add_multiple": {"devices_count": 3},
    }
         },
    "MercurySpodesInputControl": {
            "display_name": "Входной контроль СПОДЭС",
            "model": "Меркурий 204 СПОДЕС",
            "unique_field": "serial",
            "party_fields": {},
            "fields": {
                "serial": {"id": "serial", "required": True}
            },
            "devices": [
                {"serial": "50580248"},
                {"serial": "83400189"},
                {"serial": "30580055"}
            ],
            "scenarios": {
                "add_multiple": {"devices_count": 3},
               
            }
},
"Mercury234SpodesTest": {
                    "display_name": "Меркурий 234 СПОДЭС с этикеткой",
                    "model": "Меркурий 234 СПОДЕС",
                    "unique_field": "serial", 
                    "party_fields": {},
                    "fields": {
                "serial": {"id": "serial", "required": True},
                "devEui": {"id": "devEui", "required": True}
                    },
                    "devices": [
                        {"devEui": "04:97:90:00:0F:F5:B1:4C","serial": "50580248"},
                        {"devEui": "04:97:90:00:0F:00:B2:4A","serial": "50280312"},
                        {"devEui": "04:97:90:00:21:AA:7A:56","serial": "30580055"}
                    ],
                    "scenarios": {
                        "add_multiple": {"devices_count": 3},
                    
                    }
         },
          "Mercury238SpodesWithRemote": {
             "display_name": "Меркурий 238 СПОДЕС с дисплеем",
             "model": "Меркурий 238 СПОДЭС",
             "unique_field": "serial", 
             "party_fields": {},
             "fields": {
                 "serial": {"id": "serial", "required": True},
                 "serialRemote": {"id": "serialRemote", "required": True}
             },
             "devices": [
                 {"serial": "50580357", "serialRemote": "0000016043600000"},
                 {"serial": "50580348", "serialRemote": "0000016043800000"},
                 {"serial": "50580213", "serialRemote": "0000016045800000"}
             ],
             "scenarios": {
                 "add_multiple": {"devices_count": 3},
             }
                  },
    "NartisSplit": {
                    "display_name": "Нартис Сплит",
                    "model": "Нартис-102",
                    "unique_field": "serial", 
                    "party_fields": {},
                    "fields": {
                "serial": {"id": "serial", "required": True},
                "devEui": {"id": "devEui", "required": True}
                    },
                    "devices": [
                        {"devEui": "04:97:90:01:E0:10:A3:61","serial": "021242003572"},
                        {"devEui": "04:97:90:01:E0:10:A4:62","serial": "021244003521"},
                        {"devEui": "04:97:90:00:21:AA:7F:53","serial": "021243003500"}
                    ],
                    "scenarios": {
                        "add_multiple": {"devices_count": 3},
                    
                    }
         },
    "NartisShaph": {
                        "display_name": "Нартис Шкафной",
                        "model": "Нартис-100",
                        "unique_field": "serial", 
                        "party_fields": {},
                        "fields": {
                    "serial": {"id": "serial", "required": True},
                    "devEui": {"id": "devEui", "required": True}
                        },
                        "devices": [
                            {"devEui": "04:97:90:01:E0:10:A3:61","serial": "021242003578"},
                            {"devEui": "04:97:90:01:E0:10:A4:62","serial": "021244003526"},
                            {"devEui": "04:97:90:00:21:AA:7F:53","serial": "021243003502"}
                        ],
                        "scenarios": {
                            "add_multiple": {"devices_count": 3},
                        
                        }
             },
    "ZIP272XWORemote": {
                            "display_name": "ЦЭ272x без дисплея",
                            "model": "ЦЭ2727А",
                            "unique_field": "serial", 
                            "party_fields": {},
                            "fields": {
                        "serial": {"id": "serial", "required": True},
                        "devEui": {"id": "devEui", "required": True}
                            },
                            "devices": [
                                {"devEui": "04:97:90:01:E0:10:A3:61","serial": "4091130"},
                                {"devEui": "04:97:90:01:E0:10:A4:62","serial": "4091126"},
                                {"devEui": "04:97:90:00:21:AA:7F:53","serial": "4091178"}
                            ],
                            "scenarios": {
                                "add_multiple": {"devices_count": 3},
                            
                            }
                 },

    "NevaWithPasswords": {
    "display_name": "Нева с паролями",
    "model": "NEVASP311",
    "unique_field": "serial",
    "party_fields": {  
        "llsPwd": {"id": "llsPwd", "value": "00000000"},
        "hlsPwd": {"id": "hlsPwd", "value": "2022674818082022"}
    },
    "fields": {
        "serial": {"id": "serial", "required": True},
        "devEui": {"id": "devEui", "required": True}
    },
    "devices": [
        {"devEui": "04:97:90:01:E0:10:A3:61","serial": "88500012"},
        {"devEui": "04:97:90:01:F0:00:A4:98","serial": "88500022"},
        {"devEui": "04:97:90:00:0F:F0:35:67","serial": "88500034"}
    ],
    "scenarios": {
        "add_multiple": {"devices_count": 3},
    }
},

"WaterDeviceWFW": {
                            "display_name": "Счетчик горячей воды (WFW)",
                            "model": "WFW20",
                            "unique_field": "serial", 
                            "party_fields": {},
                            "fields": {
                        "serial": {"id": "serial", "required": True},
                        "devEui": {"id": "devEui", "required": True},
                        "indication": {"id": "indication", "required": True}
                            },
                            "devices": [
                                {"devEui": "04:97:90:01:E0:10:A3:61","serial": "24-257321","indication": "1.000"},
                                {"devEui": "04:97:90:01:E0:10:A4:62","serial": "23-257123","indication": "52.000"},
                                {"devEui": "04:97:90:00:21:AA:7F:53","serial": "22-257697","indication": "0.001"}
                            ],
                            "scenarios": {
                                "add_multiple": {"devices_count": 3},
                            
                            }
                 },
"WaterDeviceWFK": {
                            "display_name": "Счетчик холодной воды (WFK)",
                            "model": "WFK27",
                            "unique_field": "serial", 
                            "party_fields": {},
                            "fields": {
                        "serial": {"id": "serial", "required": True},
                        "devEui": {"id": "devEui", "required": True},
                        "indication": {"id": "indication", "required": True}
                            },
                            "devices": [
                                {"devEui": "04:97:90:01:E0:10:A3:61","serial": "24-257321","indication": "1.000"},
                                {"devEui": "04:97:90:01:E0:10:A4:62","serial": "23-257123","indication": "52.000"},
                                {"devEui": "04:97:90:00:21:AA:7A:53","serial": "22-257697","indication": "0.001"}
                            ],
                            "scenarios": {
                                "add_multiple": {"devices_count": 3},
                            
                            }
                 },
    "GasDevice": {
                            "display_name": "Счетчик газа",
                            "model": "СГБМ-1.6",
                            "unique_field": "serial", 
                            "party_fields": {},
                            "fields": {
                        "serial": {"id": "serial", "required": True},
                        "devEui": {"id": "devEui", "required": True},
                        "indication": {"id": "indication", "required": True}
                            },
                            "devices": [
                                {"devEui": "04:97:90:01:E0:10:A3:61","serial": "46123724","indication": "1.000"},
                                {"devEui": "04:97:90:01:E0:10:A4:62","serial": "46833224","indication": "52.000"},
                                {"devEui": "04:97:90:00:21:AA:7A:53","serial": "46833713","indication": "0.001"}
                            ],
                            "scenarios": {
                                "add_multiple": {"devices_count": 3},
                            
                            }
                 },
    "HeatDevice": {
                                "display_name": "Счетчик тепла",
                                "model": "Берилл СТЭУ 41",
                                "unique_field": "serial", 
                                "party_fields": {},
                                "fields": {
                            "serial": {"id": "serial", "required": True},
                            "devEui": {"id": "devEui", "required": True}
                                },
                                "devices": [
                                    {"devEui": "04:97:90:01:E0:10:A3:61","serial": "23030356"},
                                    {"devEui": "04:97:90:01:E0:10:A4:62","serial": "23030468"},
                                    {"devEui": "04:97:90:00:21:AA:7F:53","serial": "23030216"}
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