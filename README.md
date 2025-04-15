# Бот для управления паролями

Это Telegram-бот, который помогает пользователям управлять своими паролями. Он позволяет:

- Генерировать безопасные пароли с настраиваемой длиной и сложностью.
- Сохранять и получать пароли с использованием шифрования и дешифрования.
- Шифровать и дешифровать пароли вручную.

Бот использует SQLite для хранения зашифрованных паролей и применяет шифрование с использованием библиотеки `cryptography`.

## Возможности

- **Генерация паролей**: Генерация безопасных паролей с различной длиной и уровнем сложности.
- **Шифрование паролей**: Шифрование паролей с использованием уникального ключа для каждого пользователя.
- **Дешифрование паролей**: Дешифровка сохранённых паролей.
- **Сохранение паролей**: Надёжное хранение зашифрованных паролей в базе данных SQLite.
- **Просмотр паролей**: Просмотр сохранённых паролей в зашифрованном виде.

## Установка

1. Клонируйте репозиторий на свой локальный компьютер.

    ```bash
    git clone https://github.com/yourusername/password-bot.git
    cd password-bot
    ```

2. Установите необходимые зависимости.

    ```bash
    pip install -r requirements.txt
    ```

3. Настройте бота, получив токен от [BotFather](https://core.telegram.org/bots#botfather) в Telegram и добавив его в конфигурационный файл (`config.py`).

    ```python
    BOT_TOKEN = "your-telegram-bot-token"
    ```

4. Запустите бота.

    ```bash
    python bot.py
    ```

## База данных

Бот использует SQLite для хранения зашифрованных паролей пользователей. Файл базы данных — `passwords.db`, он создаётся автоматически в корневом каталоге.

## Команды и функции

- `/start`: Начать работу с ботом и получить главное меню.
- **Генерация паролей**:
    - Выбор длины пароля (8, 12, 16 или 20 символов).
    - Выбор сложности пароля (Простой, Средний, Сложный).
    - Указание количества паролей для генерации.
- **Мои пароли**: Просмотр сохранённых паролей.
- **Шифрование пароля**: Шифрование пароля с получением зашифрованной строки.
- **Дешифрование пароля**: Дешифровка зашифрованного пароля.

## Вклад в проект

Не стесняйтесь форкать репозиторий и отправлять пулл-реквесты. Если вы столкнулись с ошибками или проблемами, откройте issue, и я постараюсь их решить.

## Лицензия

Этот проект лицензирован на условиях MIT License — смотрите файл [LICENSE](LICENSE) для подробностей.
