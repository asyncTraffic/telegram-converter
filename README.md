# AsyncTraffic Converter

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)

**AsyncTraffic Converter** — простой и удобный инструмент для конвертации файлов `.session` Telegram в формат `tdata`, совместимый с Telegram Desktop. Программа предлагает графический интерфейс (GUI) и интерфейс командной строки (CLI) для гибкости, а также поддержку SOCKS5 прокси для продвинутых пользователей.

## Возможности

- **Графический интерфейс (GUI)**: Минималистичный интерфейс на PyQt6:
  - Удобный выбор файла `.session` через диалоговое окно.
  - Поля для ввода `api_id`, `api_hash` и опциональных данных прокси (IP, порт, логин, пароль).
  - Уведомления об успехе или ошибке (✅/❌).
  - Результаты сохраняются в папку `data`.
- **Интерфейс командной строки (CLI)**: Лёгкая альтернатива для работы в терминале:
  - Конвертация через аргументы командной строки.
  - Обязательные параметры: `--session`, `--api-id`, `--api-hash`.
  - Опциональные параметры прокси: `--proxy-ip`, `--proxy-port`, `--proxy-login`, `--proxy-password`.
  - Вывод пути к папке `tdata` при успешной конвертации.
- **Поддержка прокси**: Настройка SOCKS5-прокси для безопасной работы.
- **Кроссплатформенность**: Поддержка Windows, Linux и macOS.

## Скриншот

![изображение](https://github.com/user-attachments/assets/e2ec19d6-0255-4411-81b5-0cd7dac240b7)


## Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/asyncTraffic/telegram-converter.git
   cd telegram-converter
   ```

2. **Установите зависимости**:
   Убедитесь, что у вас установлен Python 3.8+, затем установите необходимые пакеты:
   ```bash
   pip install -r requirements.txt
   ```

## Использование

### Графический интерфейс (GUI)

1. Запустите приложение:
   ```bash
   python converter.py
   ```
2. Выберите файл `.session`, нажав кнопку "📂 Browse".
3. Введите `api_id` и `api_hash` (получить можно на [my.telegram.org](https://my.telegram.org)).
4. (Опционально) Укажите данные прокси (IP, порт, логин, пароль).
5. Нажмите "Convert ▶️".
6. Результат сохранится в `data/[имя_файла]_tdata`, а уведомление покажет путь или ошибку.

### Интерфейс командной строки (CLI)

1. Запустите CLI-версию с параметрами:
   ```bash
   python converter_cli.py --session path/to/my.session --api-id 123456 --api-hash abcdef1234567890
   ```
   С прокси:
   ```bash
   python converter_cli.py --session path/to/my.session --api-id 123456 --api-hash abcdef1234567890 --proxy-ip 192.168.1.1 --proxy-port 8080 --proxy-login user --proxy-password pass
   ```
2. Вывод:
   - Успех: `/path/to/data/my_tdata`
   - Ошибка: `Error: <описание ошибки>`

3. Для справки:
   ```bash
   python converter_cli.py --help
   ```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

## Контакты

Если у вас есть вопросы или предложения, создайте issue или свяжитесь через [ваш email или Telegram].
