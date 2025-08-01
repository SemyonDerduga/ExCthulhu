# Exchange Cthulhu (excthulhu)

Exchange Cthulhu — это консольная утилита для поиска арбитража между криптовалютными биржами. 

## Что это такое?

Арбитраж — это возможность купить актив на одной бирже по низкой цене и продать на другой по высокой цене, получив прибыль. Эта утилита автоматически ищет такие возможности между различными криптовалютными биржами.

## Основные возможности:

- 🔍 **Поиск арбитража**: Автоматический поиск прибыльных циклов обмена между биржами
- 📊 **Анализ рынков**: Получение данных о курсах валют с множества бирж
- 💰 **Расчет прибыли**: Учет комиссий и расчет реальной прибыльности сделок
- 📈 **Прогнозирование**: Базовые методы прогнозирования цен
- 🗄️ **Кеширование**: Сохранение данных для ускорения работы
- 🔄 **Множественные алгоритмы**: DFS и Bellman-Ford для поиска циклов

## Поддерживаемые биржи:

Binance, DSX, Exmo, Hollaex, Oceanex, Poloniex, Tidex, Upbit, Yobit и другие через библиотеку CCXT.

## Установка

1. Убедитесь, что установлен Python версии 3.7 или новее.
2. Клонируйте репозиторий и установите зависимости:
   ```bash
   git clone <repo_url>
   cd ExCthulhu
   pip install ./
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

Эта команда проверяет, какие криптовалюты можно пополнить и вывести с указанной биржи.
Результаты сохраняются в файлы:
- `~/.cache/cthulhu/available_io/{exchange}_input.txt` - валюты для ввода
- `~/.cache/cthulhu/available_io/{exchange}_output.txt` - валюты для вывода

**Поддерживаемые биржи:** binance, exmo, hollaex, oceanex, poloniex, upbit, yobit

**Примеры:**
```bash
python -m cthulhu_src.main available-io binance
python -m cthulhu_src.main available-io hollaex
python -m cthulhu_src.main available-io yobit
```

### Команда `forecast`

Базовый прогноз цен на основе исторических данных. Поддерживает несколько методов прогнозирования.

```bash
python -m cthulhu_src.main forecast --prices 100,101,102,103 --horizons 1,5 --methods mean,arima
```

**Методы прогнозирования:**
- **mean**: Среднее значение доходностей за период
- **median**: Медианное значение доходностей за период
- **ema**: Экспоненциальное скользящее среднее доходностей
- **arima**: Авторегрессионная модель (ARIMA) для временных рядов

**Параметры:**
- `--prices`: Список исторических цен через запятую
- `--horizons`: Временные горизонты для прогноза (в минутах)
- `--methods`: Методы прогнозирования через запятую
- `--lookback`: Окно для анализа исторических данных (по умолчанию 60)

**Примеры:**
```bash
# Простой прогноз средним значением
python -m cthulhu_src.main forecast --prices 100,101,102,103 --horizons 1,5

# Прогноз с несколькими методами
python -m cthulhu_src.main forecast --prices 100,101,102,103 --methods mean,ema,arima

# Прогноз с увеличенным окном анализа
python -m cthulhu_src.main forecast --prices 100,101,102,103 --lookback 30
```

### Команда `forecast-backtest`

Проверка прибыльности сделки, совершенной в прошлом. Симулирует торговую стратегию на исторических данных.

```bash
python -m cthulhu_src.main forecast-backtest --prices 100,101,102,103 --horizon 5 --minutes-back 180
```

**Как работает:**
1. Берет данные из прошлого (`minutes-back` минут назад)
2. Делает прогноз на `horizon` минут вперед
3. Симулирует покупку/продажу на основе прогноза
4. Рассчитывает прибыль/убыток

**Параметры:**
- `--prices`: Исторические цены через запятую
- `--horizon`: На сколько минут вперед делать прогноз
- `--lookback`: Сколько исторических точек использовать
- `--minutes-back`: В какой момент прошлого симулировать сделку (по умолчанию 120)

**Примеры:**
```bash
# Проверить сделку 2 часа назад
python -m cthulhu_src.main forecast-backtest --prices 100,101,102,103 --horizon 5

# Проверить сделку 3 часа назад
python -m cthulhu_src.main forecast-backtest --prices 100,101,102,103 --minutes-back 180

# Проверить с увеличенным окном анализа
python -m cthulhu_src.main forecast-backtest --prices 100,101,102,103 --lookback 30
```

### Команда `forecast-arbitrage` ⭐ **НОВАЯ**

Интегрированный поиск арбитража с прогнозированием. Объединяет поиск возможностей с анализом рыночных трендов.

```bash
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC -a 0.001 --historical-prices 50000,50100,50200,50300
```

**Что делает:**
1. Находит арбитражные возможности между биржами
2. Автоматически получает исторические данные с бирж
3. Анализирует данные для прогнозирования
4. Делает прогнозы движения цен
5. Рекомендует действия на основе прогнозов и прибыльности

**Методы прогнозирования:**
- **mean**: Среднее значение доходностей
- **median**: Медианное значение доходностей
- **ema**: Экспоненциальное скользящее среднее
- **arima**: Авторегрессионная модель

**Рекомендации:**
- **buy**: Рекомендуется покупать (ожидается рост + хорошая прибыль)
- **sell**: Рекомендуется продавать (ожидается падение)
- **hold**: Рекомендуется держать (неопределенный тренд)

**Параметры:**
- `-s, --start`: Точка входа в формате 'биржа_валюта'
- `-a, --amount`: Количество исходной валюты
- `--historical-prices`: Исторические цены через запятую для прогнозирования
- `--auto-fetch-history`: Автоматически получить исторические данные с биржи
- `--history-hours`: Количество часов истории для загрузки (по умолчанию 24)
- `--history-symbol`: Торговая пара для исторических данных (например, BTC/USDT)
- `--forecast-method`: Метод прогнозирования (mean, median, ema, arima)
- `--forecast-horizon`: Горизонт прогнозирования (в минутах)
- `--lookback`: Окно для анализа исторических данных

**Примеры:**
```bash
# Базовый поиск без прогнозирования
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC -a 0.001

# Поиск с автоматическим получением исторических данных
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --auto-fetch-history

# Поиск с 48 часами истории
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --auto-fetch-history --history-hours 48

# Поиск с ручными историческими данными
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --historical-prices 50000,50100,50200,50300

# Поиск с ARIMA прогнозированием
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --forecast-method arima --forecast-horizon 10

# Поиск с несколькими биржами
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC -e binance -e hollaex
```

## Интеграция прогнозирования с арбитражем

### 🚀 **Новая интегрированная команда `forecast-arbitrage`**

Теперь прогнозирование полностью интегрировано в поиск арбитража! Вместо отдельных команд используйте одну команду:

```bash
# Интегрированный поиск с прогнозированием
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC -a 0.001 --historical-prices 50000,50100,50200,50300
```

### Как работает интеграция:

1. **Поиск арбитража**: Находит все возможные арбитражные циклы
2. **Анализ данных**: Использует исторические цены для прогнозирования
3. **Прогнозирование**: Делает прогнозы движения цен различными методами
4. **Рекомендации**: Выдает рекомендации на основе прогнозов и прибыльности

### Стратегии использования:

**Консервативная стратегия:**
- Используйте только проверенные арбитражные возможности
- Прогнозы для подтверждения направления движения
- Бэктестинг для валидации стратегий

**Агрессивная стратегия:**
- Прогнозы для определения моментов входа
- Комбинирование нескольких методов прогнозирования
- Динамическое управление рисками

### Примеры использования:

```bash
# 1. Базовый поиск без прогнозирования
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC -a 0.001

# 2. Поиск с прогнозированием
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --historical-prices 50000,50100,50200,50300

# 3. Поиск с ARIMA прогнозированием
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --forecast-method arima --forecast-horizon 10

# 4. Поиск с несколькими биржами
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC -e binance -e hollaex

# 5. Полный анализ с бэктестингом
python -m cthulhu_src.main forecast-arbitrage -s binance_BTC --historical-prices 50000,50100,50200,50300 --forecast-method arima
```

### Команда `historical-data` ⭐ **НОВАЯ**

Получить исторические данные с бирж для анализа и прогнозирования.

```bash
python -m cthulhu_src.main historical-data binance BTC/USDT
```

**Форматы вывода:**
- **prices**: Только цены закрытия (для прогнозирования)
- **ohlcv**: Полные OHLCV данные (Open, High, Low, Close, Volume)
- **info**: Информация о рынке (текущие цены, объемы, изменения)

**Параметры:**
- `EXCHANGE`: Название биржи (например, binance)
- `SYMBOL`: Торговая пара (например, BTC/USDT)
- `--hours`: Количество часов истории (по умолчанию 24)
- `--count`: Количество последних записей (по умолчанию 100)
- `--format`: Формат вывода (prices, ohlcv, info)

**Примеры:**
```bash
# Получить цены для прогнозирования
python -m cthulhu_src.main historical-data binance BTC/USDT

# Получить 48 часов истории
python -m cthulhu_src.main historical-data binance BTC/USDT --hours 48

# Получить полные OHLCV данные
python -m cthulhu_src.main historical-data binance BTC/USDT --format ohlcv

# Получить информацию о рынке
python -m cthulhu_src.main historical-data binance BTC/USDT --format info
```

### Команда `web` ⭐ **НОВАЯ**

Запустить веб-интерфейс с интерактивными графиками и визуализацией.

```bash
python -m cthulhu_src.main web
```

**Возможности веб-интерфейса:**
- 🎯 **Интерактивные графики** с Plotly для визуализации цен и прогнозов
- 📊 **Дашборд** с статистикой и быстрым анализом
- 🔍 **Поиск арбитража** с визуализацией результатов
- 📈 **Прогнозирование** с графиками движения цен
- 📋 **Исторические данные** с различными форматами
- 🚀 **Интегрированный анализ** объединяющий арбитраж и прогнозирование

**Параметры:**
- `--host`: Хост для запуска сервера (по умолчанию 0.0.0.0)
- `--port`: Порт для запуска сервера (по умолчанию 8000)
- `--no-reload`: Отключить автоматическую перезагрузку

**Примеры:**
```bash
# Запустить на стандартном порту
python -m cthulhu_src.main web

# Запустить на другом порту
python -m cthulhu_src.main web --port 8080

# Запустить только для локального доступа
python -m cthulhu_src.main web --host 127.0.0.1 --port 3000
```

**После запуска откройте браузер и перейдите по адресу:**
- http://localhost:8000 - главная страница
- http://localhost:8000/dashboard - дашборд
- http://localhost:8000/integrated - интегрированный анализ

### Отдельные команды (для детального анализа):

Если нужен более детальный анализ, можно использовать отдельные команды:

```bash
# 1. Найти арбитражные возможности
python -m cthulhu_src.main find -s binance_BTC -a 0.001

# 2. Получить исторические данные
python -m cthulhu_src.main historical-data binance BTC/USDT

# 3. Сделать прогноз
python -m cthulhu_src.main forecast --prices 50000,50100,50200,50300 --methods arima

# 4. Проверить стратегию на исторических данных
python -m cthulhu_src.main forecast-backtest --prices 50000,50100,50200,50300 --horizon 5
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
