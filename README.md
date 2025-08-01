# Exchange Cthulhu (excthulhu)

Exchange Cthulhu — это консольная утилита для выявления аномалий и поиска прибыльных транзакций между криптовалютными биржами. Проект предоставляет набор команд для работы с биржами, получения данных о доступных валютах, кеширования обменных курсов и поиска циклов арбитража.

## Установка

1. Убедитесь, что установлен Python версии 3.7 или новее.
2. Клонируйте репозиторий и установите зависимости:
   ```bash
   git clone <repo_url>
   cd ExCthulhu
   python -m pip install -r requirements.txt
   ```
   При наличии `poetry` можно использовать `poetry install`.

## Быстрый старт

Все команды запускаются через модуль `cthulhu_src.main`:

```bash
python -m cthulhu_src.main [КОМАНДА] [ПАРАМЕТРЫ]
```

Список доступных команд можно получить через `--help`:

```bash
python -m cthulhu_src.main --help
```

### Команда `find`

Поиск прибыльных циклов обмена.

```bash
python -m cthulhu_src.main find -s <биржа_валюта> [опции]
```

Параметры:
- `-d, --max-depth` – максимальная глубина поиска (по умолчанию 4).
- `-s, --start` – точка входа в формате `биржа_валюта` (например, `binance_BTC`).
- `-a, --amount` – количество исходной валюты (по умолчанию 1.0).
- `-c, --cached` – использовать кеш обменных данных.
- `--cache-dir` – путь к каталогу кеша (по умолчанию `~/.cache/cthulhu`).
- `-e, --exchange-list` – список бирж для анализа (можно указать несколько значений).
- `--current-node` и `--current-amount` – продолжить поиск с промежуточной точки.
- `--algorithm` – выбор алгоритма (`dfs` или `bellman-ford`, по умолчанию `dfs`).
- `--processes` – количество процессов для DFS.
- `--prune-ratio` – коэффициент отсечения нерентабельных веток.
- `--batch-size` – размер батча при загрузке книг ордеров.

Пример:
```bash
python -m cthulhu_src.main find -s binance_BTC -a 0.002 -e binance -e hollaex
```

### Команда `config`

Запуск поиска с использованием конфигурационного файла (JSON или YAML).

```bash
python -m cthulhu_src.main config path/to/config.yaml
```

Пример конфигурации `config.yaml`:
```yaml
max_depth: 4
start: binance_BTC
amount: 0.002
exchange_list:
  - binance
  - hollaex
```

В формате JSON можно дополнительно указать список прокси:
```json
{
  "max_depth": 4,
  "start": "binance_BTC",
  "amount": 0.002,
  "exchange_list": ["binance", "hollaex"],
  "proxy_list": "proxy_list.txt",
  "proxy": ["http://some.proxy/", "http://some.another.proxy/"]
}
```

### Команда `exchanges`

Показать список поддерживаемых библиотекой `ccxt` бирж:
```bash
python -m cthulhu_src.main exchanges
```

### Команда `available-io`

Получить перечень валют, доступных для ввода и вывода на конкретной бирже.
```bash
python -m cthulhu_src.main available-io <exchange>
```

Результаты сохраняются в `~/.cache/cthulhu/available_io`.

### Команда `forecast`

Базовый прогноз цен на основе окна лог-доходностей. Поддерживает несколько методов предикта (mean, median, ema, arima).

```bash
python -m cthulhu_src.main forecast --prices 1,2,4,8 --horizons 1,5 --methods mean,arima
```

### Команда `forecast-backtest`

Проверка, принесла бы прибыль сделка, совершённая в прошлом. По умолчанию
используется временной сдвиг **120 минут**, но его можно задать вручную.

```bash
python -m cthulhu_src.main forecast-backtest --prices 1,2,4,8,16 --horizon 5 \
    --minutes-back 180
```

## Архитектура проекта

```
cthulhu_src/
├── actions/    – реализация команд CLI
├── routes/     – описание CLI-интерфейса (параметры и help)
├── services/   – работа с биржами и обработка данных
├── utils/      – вспомогательные модули (например, логирование)
└── main.py     – точка входа в приложение
```

## Для разработчиков

1. Создайте виртуальное окружение и установите зависимости из `requirements.txt` или через `poetry`.
2. Запуск CLI во время разработки осуществляется командой `python -m cthulhu_src.main ...`.
3. При добавлении новой биржи реализуйте класс в `cthulhu_src/services/exchanges` и зарегистрируйте его в `exchange_manager.py`.
4. Логи выводятся в консоль и зависят от уровня `--debug` при запуске.
5. Примеры конфигураций и прокси находятся в каталоге `configs_examples`.
6. В корне проекта расположен `Makefile` с удобными командами:
   - `make install` – установка зависимостей;
   - `make format` – автоформатирование кода `black`;
   - `make lint` – запуск `flake8`;
   - `make test` – выполнение тестов;
   - `make check` – быстрая проверка запуска CLI.
   - `make all` – последовательный запуск форматтера, линтера, тестов и небольшой проверки.

В проекте присутствуют автотесты. Перед отправкой изменений выполните `make test` и убедитесь в отсутствии ошибок.

## CI

В репозитории настроен workflow `.github/workflows/hourly-test.yml`, который каждый час запускает тесты и отправляет результат в Telegram‑бота. Для работы необходимо в настройках репозитория создать секрет `BOT_TOKEN` и поместить туда токен, полученный от BotFather.

Также добавлен workflow `.github/workflows/lint.yml`, запускающийся на каждое изменение и проверяющий код с помощью `make lint`.

Workflow не требует отдельного chat ID: скрипт `ci/send_telegram.py` сам обращается к методу `getUpdates`, собирает идентификаторы всех пользователей, которые писали боту, и отправляет им сообщение. Поэтому достаточно, чтобы каждый пользователь хотя бы раз написал боту.

## Лицензия

Проект распространяется под лицензией MIT.
