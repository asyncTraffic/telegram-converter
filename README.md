# AsyncTraffic Converter

![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**AsyncTraffic Converter** — простой и удобный инструмент для конвертации файлов `.session` Telegram в формат `tdata`, совместимый с Telegram Desktop. Программа предлагает графический интерфейс (GUI) и интерфейс командной строки (CLI) для максимальной гибкости, а также поддержку различных типов прокси.

## Возможности

- **Графический интерфейс (GUI)**: Минималистичный интерфейс на PyQt6:
  - Удобный выбор файла `.session` через диалоговое окно.
  - Поля для ввода `api_id` и `api_hash` с автоматическим сохранением для последующих запусков.
  - Выбор типа прокси (http, https, socks5, socks4) и ввод в формате `login:password@ip:port` или `ip:port`.
  - Уведомления об успехе или ошибке (✅/❌).
  - Результаты сохраняются в папку `data`.
- **Интерфейс командной строки (CLI)**: Лёгкая альтернатива для работы в терминале:
  - Конвертация через аргументы командной строки.
  - Обязательный параметр: `--session`.
  - Параметры `api_id` и `api_hash` сохраняются после первого ввода и необязательны для последующих запусков.
  - Опциональные параметры прокси: `--proxy-type` (http, https, socks5, socks4) и `--proxy` (в формате `login:password@ip:port` или `ip:port`).
  - Вывод пути к папке `tdata` при успешной конвертации.
- **Поддержка прокси**: Настройка прокси типов http, https, socks5, socks4 для безопасной работы.
- **Кроссплатформенность**: Поддержка Windows, Linux и macOS.
- **Логирование**: Запись логов в файл `converter.log` и терминал без чувствительных данных.
- **Обработка ошибок**: Чёткие сообщения об ошибках для некорректных данных или сбоев.

## Скриншот

![AsyncTraffic Converter GUI](https://github.com/user-attachments/assets/65937374-f295-4cc7-894c-5c72fbdc60b8)

## Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/asyncTraffic/telegram-converter.git
   cd asynctraffic-converter
   ```

2. **Установите зависимости**:
   Убедитесь, что у вас установлен Python 3.10+, затем установите необходимые пакеты:
   ```bash
   pip install -r requirements.txt
   ```
   Примечание: PyQt6 требуется только для GUI-версии.

## Использование

### Графический интерфейс (GUI)

1. Запустите приложение:
   ```bash
   python converter.py
   ```
2. Выберите файл `.session`, нажав кнопку "📂 Browse".
3. Введите `api_id` и `api_hash` (получить можно на [my.telegram.org](https://my.telegram.org)). Они сохранятся для следующих запусков.
4. (Опционально) Выберите тип прокси (http, https, socks5, socks4) и укажите прокси в формате `login:password@ip:port` или `ip:port`.
5. Нажмите "Convert ▶️".
6. Результат сохранится в `data/[имя_файла]_tdata`, а уведомление покажет путь или ошибку.

### Интерфейс командной строки (CLI)

1. Запустите CLI-версию с параметрами:
   ```bash
   python converter_cli.py --session path/to/my.session --api-id 123456 --api-hash abcdef1234567890
   ```
   После первого запуска `api_id` и `api_hash` сохраняются, и можно запускать так:
   ```bash
   python converter_cli.py --session path/to/my.session
   ```
   С прокси:
   ```bash
   python converter_cli.py --session path/to/my.session --proxy-type socks5 --proxy user:pass@192.168.1.1:8080
   ```
2. Вывод:
   - Успех: `Success: tdata saved to /path/to/data/my_tdata`
   - Ошибка: `Error: <описание ошибки, например, "Invalid proxy format">`

3. Для справки:
   ```bash
   python converter_cli.py --help
   ```


## Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

## Контакты

Если у вас есть вопросы или предложения, обратитесь в наш телеграм чат: https://t.me/+q8QT8dzyDwdiZTky
