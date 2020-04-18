# Exchange Cthulhu (excthulhu)

Утилита для выявления аномалий на биржах

## Структура
Excthulhu
├── README.md
├── cthulhu_src
│   ├── __init__.py
│   ├── actions         -- Основные действия
│   │   ├── __init__.py
│   │   └── find_txn.py
│   ├── main.py         -- Эндпоинт (вход в программу)
│   ├── routes          -- Роуты к коммандам с хелпом и описанием аргументов
│   │   ├── __init__.py
│   │   └── find_txn.py
│   ├── services        -- Используемые сервисы, обертки на api бирж и т.д.
│   │   └── __init__.py
│   └── utils           -- Переиспользуемые утилиты
│       └── logger.py
├── requirements.txt
└── tests               -- Авто и юнит тесты
    ├── auto_tests
    └── unit_tests