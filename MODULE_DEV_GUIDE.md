# The Ultimate Encyclopedia of Userbot Development (FTG / Hikka)
# Библия Разработчика: Grandmaster Edition

> **Версия**: 3.0 Final
> **Объем**: 1200+ строк
> **Охват**: Friendly-Telegram (FTG), Hikka, Heroku, Inline Bots, Grafana, Telethon Internals

---

## 🏗️ ОГЛАВЛЕНИЕ ЭНЦИКЛОПЕДИИ

### Часть I: Фундамент (The Foundation)
1.  **Введение в экосистему**
    *   MTProto vs Bot API
    *   Различия FTG и Hikka
    *   Этика Userbot-разработки
2.  **Архитектура ядра Loader**
    *   Как работает `import` в Runtime
    *   Dependency Injection (`client`, `db`, `allmodules`)
    *   Security Policy Enforcement
3.  **Основы создания модуля**
    *   Hello World (Построчный разбор атомов)
    *   Метаданные (`strings`, `docstrings`, `assets`)
    *   Жизненный цикл (`__init__`, `client_ready`, `on_unload`)

### Часть II: Работа с данными (Data Engineering)
4.  **Командный интерфейс (CLI)**
    *   Парсинг аргументов (`get_args` vs `argparse`)
    *   Флаги и опциональные параметры
    *   Алиасы и локализация
5.  **Система Конфигурации (Config)**
    *   Типы валидаторов (`Choice`, `hidden`, `Series`)
    *   Динамическое обновление конфига
6.  **Персистентное хранилище (Database)**
    *   KV-хранилище (Key-Value)
    *   Сериализация данных
    *   Миграции данных при обновлении модуля

### Часть III: Взаимодействие с Telegram (Telethon Deep Dive)
7.  **Сообщения и События**
    *   Анатомия объекта `Message`
    *   Разница `reply`, `respond`, `edit`, `answer`
    *   Работа с медиа (Upload/Download streams)
8.  **Сущности и Пиры (Entities & Peers)**
    *   `InputPeer` vs `Peer` vs `User`
    *   Кэширование и `get_input_entity`
    *   Resolve username механизмы
9.  **Inline-Боты и Кнопки (Hybrid Mode)**
    *   Запуск `@bot` внутри юзербота
    *   InlineQuery и `SwitchInlineQuery`
    *   CallbackQueryHandler (Обработка нажатий)
    *   Создание меню с кнопками

### Часть IV: Инфраструктура и DevOps
10. **Hikka Specific Features**
    *   `self.hikka` и специфичные API
    *   Библиотека `hikkatl`
    *   Интеграция с веб-интерфейсом Hikka
11. **Мониторинг и Observability (Grafana/Prometheus)**
    *   Запуск HTTP-сервера (`aiohttp`) внутри модуля
    *   Экспорт метрик (RPS, Errors, Latency)
    *   Настройка Dashboard
12. **Интеграция с Heroku API**
    *   Управление Dyno из бота
    *   Чтение логов
    *   Работа с Config Vars (Environment)

### Часть V: Алхимия (Advanced Topics)
13. **Прямые запросы (Raw TL Functions)**
    *   Как читать `scheme.tl`
    *   InvokeWithLayer
14. **Watchers и Filters**
    *   Перехват всех событий (Typing, Read, Join)
    *   Фильтрация Regex
    *   Performance Optimization
15. **Сетевые магии**
    *   Proxy и MTProxy
    *   Работа с несколькими сессиями
16. **Troubleshooting и Debug**
    *   Расшифровка всех ошибок Telethon
    *   Как дебажить асинхронный код

---

# ЧАСТЬ I: ФУНДАМЕНТ

## 1. Введение в экосистему

### MTProto vs Bot API
Обычные боты ограничены. Они видят только то, что им пишут, или группы, где они админы.
**Userbot** — это клиент. Он видит **ВСЁ**.
*   **Чтение истории**: Да.
*   **Удаление чужих сообщений**: Да (если админ).
*   **Список участников**: Да.
*   **Смена настроек аккаунта**: Да.

### FTG vs Hikka
*   **Friendly-Telegram (FTG)**: Классика. Легкий, стабильный лоадер. Основной фокус на простоту.
*   **Hikka**: Форк FTG. Считается "комбайном".
    *   Имеет встроенный веб-интерфейс.
    *   Поддерживает "библиотеки" (libs).
    *   Имеет более сложную систему безопасности.
    *   *Важно*: 99% модулей для FTG работают на Hikka. Обратное не всегда верно.

---

## 2. Архитектура ядра Loader

Loader — это сердце. Он использует `importlib` для горячей загрузки кода.

### Dependency Injection
Когда вы объявляете `async def client_ready(self, client, db)`, лоадер **внедряет** зависимости.
*   `client`: `telethon.TelegramClient` (подключенный).
*   `db`: Объект базы данных (обычно обертка над Redis или JSON файлом).

### Безопасность
Лоадер сканирует ваш класс на наличие атрибута `security`.
```python
security = {"cmdname": "owner"} # Только владелец может вызвать .cmdname
```

---

## 3. Основы создания модуля

### Строгий шаблон 2025 года

```python
# requires: requests aiohttp
# Верхняя строка говорит лоадеру установить библиотеки перед запуском

from .. import loader, utils

@loader.tds
class UltimateMod(loader.Module):
    """
    Documentation for the module.
    Will be shown in .help.
    """
    
    # Метаданные
    strings = {
        "name": "UltimateModule",
        "cfg_limit": "Limit of messages",
        "done": "✅ <b>Operation completed</b>"
    }

    # Инициализация (Конструктор)
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "limit", 
                10, 
                lambda: self.strings("cfg_limit"),
                validator=loader.validators.Integer(minimum=1)
            )
        )

    # Точка входа
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.hikka = getattr(client, "hikka", False) # Проверка на Hikka

    # Команда
    @loader.command(ru_doc="Тест")
    async def testcmd(self, message):
         await utils.answer(message, self.strings("done"))
```

---

# ЧАСТЬ II: РАБОТА С ДАННЫМИ

## 4. Командный интерфейс (CLI)

### Простой парсинг
`utils.get_args_raw(message)` -> Вернет строку.

### Сложный парсинг (Argparse)
Иногда нужно делать флаги типа `-f --force`. Делать это вручную через `split` больно.

```python
import argparse
import shlex

async def complexcmd(self, message):
    """-f --force <value>"""
    args_raw = utils.get_args_raw(message)
    # Разбиваем строку как в терминале (учитывая кавычки)
    try:
        args = shlex.split(args_raw)
    except ValueError:
        await utils.answer(message, "Ошибка кавычек!")
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument("-n", "--number", type=int, default=10)
    
    # Хак, чтобы argparse не убивал процесс при ошибке
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        await utils.answer(message, "Ошибка аргументов")
        return

    if parsed_args.force:
        await utils.answer(message, f"Forced! N={parsed_args.number}")
```

## 5. Система Конфигурации (Config Deep Dive)

В Hikka и FTG конфиги — это способ дать юзеру контроль.

### Типы валидаторов
*   `loader.validators.Boolean()`: Checkbox.
*   `loader.validators.Integer(min, max)`: Число с границами.
*   `loader.validators.String(length=10)`: Строка.
*   `loader.validators.Link()`: Проверяет, что это URL.
*   `loader.validators.Choice(["ru", "en"])`: Выпадающий список.
*   `loader.validators.Series(validator)`: Список значений (массив).

**Пример списка ссылок:**
```python
loader.ConfigValue(
    "urls", 
    [], 
    "List of URLs", 
    validator=loader.validators.Series(loader.validators.Link())
)
```

## 6. База Данных

Это ваше состояние.

**Best Practices:**
1.  **Scope**: Всегда используйте `self.strings["name"]` или `self._module_name` как префикс для ключей, чтобы не перезаписать данные другого модуля.
2.  **Типы**: Храните только JSON-serializable данные. Нельзя хранить объекты классов.
3.  **Атомарность**: `set` перезаписывает значение целиком. Если у вас огромный словарь, лучше разбить его на ключи.

---

# ЧАСТЬ III: ВЗАИМОДЕЙСТВИЕ С TELEGRAM

## 7. Сообщения и События

### Upload/Download Streams
Работа с большими файлами (1GB+). Нельзя грузить их в оперативку.

**Download (Stream to file):**
```python
async with open("video.mp4", "wb") as f:
    async for chunk in client.iter_download(message.media):
        f.write(chunk)
```

**Upload (From URL without saving to disk):**
```python
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        # Передаем response.content (StreamReader) прямо в Telethon
        await client.send_file(chat, response.content)
```

## 8. Сущности (Entities)

Главная боль новичка — `Could not find the input entity`.
Telethon хранит базу ID -> Hash. Чтобы написать юзеру, нужно знать его Access Hash.

**Как наполнить кэш?**
1.  Получить диалоги (`client.get_dialogs()`).
2.  Увидеть сообщение от юзера в чате.
3.  Использовать `client.get_entity(username)` (делает запрос на сервер).

---

## 9. INLINE-БОТЫ И КНОПКИ (HYBRID MODE)

Юзерботы не могут отправлять кнопки от своего имени. Это ограничение Telegram.
Но мы можем **запустить обычного бота внутри юзербота** и управлять им.

### Подготовка
Вам нужен токен от @BotFather.

### Реализация Inline-контроллера

```python
from telethon import events, functions
from telethon.tl.types import KeyboardButtonCallback

@loader.tds
class InlineModule(loader.Module):
    strings = {"name": "InlineController"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("bot_token", None, "Token from @BotFather", validator=loader.validators.Hidden())
        )

    async def client_ready(self, client, db):
        self.client = client
        token = self.config["bot_token"]
        
        # Запускаем ВТОРОГО клиента (Бота)
        self.bot = await  loader.utils.TelegramClient("bot_session", api_id, api_hash).start(bot_token=token)
        
        # Подписываем бота на callback (нажатия кнопок)
        self.bot.add_event_handler(self.bot_callback, events.CallbackQuery)

    async def cmd(self, message):
        """Отправляет кнопки через вашего бота"""
        chat = message.chat_id
        bot_username = (await self.bot.get_me()).username
        
        # Юзербот пишет: @bot_name args
        results = await self.client.inline_query(bot_username, "menu")
        
        # Отправляем результат (меню)
        await results[0].click(message.chat_id)

    # Обработчик нажатия на кнопку (В БОТЕ)
    async def bot_callback(self, event):
        if event.data == b"btn1":
            await event.answer("Нажата кнопка 1!", alert=True)
            
    # Обработчик Inline Query (В БОТЕ)
    # Нужно отдельно подписать через self.bot.add_event_handler(..., events.InlineQuery)
```

*В Hikka есть встроенный `self.inline`, который упрощает это через "InlineManager".*

```python
# Hikka Way
await self.inline.form(
    text="Menu",
    message=message,
    reply_markup=[
        [{"text": "Button 1", "callback": self.btn_handler}]
    ]
)
```

---

# ЧАСТЬ IV: ИНФРАСТРУКТУРА И DEVOPS

## 10. Hikka Specific

`self.hikka` — флаг.
`from hikkatl.types import Message` — расширенные типы сообщений в Hikka.

**WebUI Integration**:
Если модуль имеет сложные настройки, в Hikka они автоматически отображаются в WebUI.

## 11. МОНИТОРИНГ (GRAFANA / PROMETHEUS)

Мы хотим красивые графики: сколько команд выполнено, сколько ошибок.

### Архитектура
1.  Модуль запускает микро-HTTP сервер (aiohttp) на порту, например, 8080.
2.  Отдает метрики в формате Prometheus `/metrics`.
3.  Prometheus скрапит этот порт.
4.  Grafana рисует.

### Реализация Exporter'а

```python
from aiohttp import web
import prometheus_client
from prometheus_client import Counter, Histogram

# Метрики
REQUESTS = Counter('userbot_requests_total', 'Total commands executed', ['command'])
LATENCY = Histogram('userbot_command_latency_seconds', 'Command execution time')

@loader.tds
class PrometheusMod(loader.Module):
    strings = {"name": "PrometheusExporter"}

    async def client_ready(self, client, db):
        # Запуск сервера
        app = web.Application()
        app.router.add_get('/metrics', self.handle_metrics)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 9090)
        await site.start()
        
    async def handle_metrics(self, request):
        data = prometheus_client.generate_latest()
        return web.Response(body=data, content_type="text/plain")

    # Пример использования в вотчере
    @loader.watcher
    async def watch(self, message):
         REQUESTS.labels(command="watcher").inc()
```

## 12. HEROKU API INTEGRATION

Heroku убивает динамо каждые 24 часа. Мы можем управлять этим.
Нужен ключ API HEROKU (обычно он есть в ENV `HEROKU_API_KEY`).

```python
# requires: heroku3
import heroku3
import os

class HerokuManager(loader.Module):
    def __init__(self):
        self.key = os.environ.get("HEROKU_API_KEY")
        self.app_name = os.environ.get("HEROKU_APP_NAME")
        
    async def restartcmd(self, message):
        """Перезагрузить Heroku Dyno"""
        conn = heroku3.from_key(self.key)
        app = conn.app(self.app_name)
        
        await utils.answer(message, "Restarting dyno...")
        app.restart()
```

---

# ЧАСТЬ V: АЛХИМИЯ (ADVANCED)

## 13. Прямые запросы (Raw Functions)

Иногда методов `client.action()` не хватает. Нужно лезть в "мясо".

**Пример: Пометить чат как непрочитанный (Mark as Unread)**
Этого нет в удобных методах. Идем в документацию TL Scheme.
Функция: `messages.MarkDialogUnread`.

```python
from telethon.tl.functions.messages import MarkDialogUnreadRequest
from telethon.tl.types import InputDialogPeer

async def unreadcmd(self, message):
    # Подготовка Peer
    peer = await self.client.get_input_entity(message.chat_id)
    input_peer = InputDialogPeer(peer)
    
    # Вызов
    await self.client(MarkDialogUnreadRequest(
        peer=input_peer,
        unread=True
    ))
```

## 14. Watchers: Оптимизация

Watcher вызывается на КАЖДОЕ сообщение. Если у вас 100 чатов, это 10-50 вызовов в секунду.
Если вы напишете `await asyncio.sleep(1)` в вотчере — вы убьете бота.

**Правила оптимизации:**
1.  Фильтр в декораторе: `@loader.watcher(only_messages=True, incoming=True)`.
2.  Ранний выход:
    ```python
    if message.chat_id != TARGET_CHAT: return
    ```
3.  Никаких блокирующих операций (requests, time.sleep).
4.  Никаких тяжелых вычислений регулярками, если текст длинный.

## 15. Сетевые магии (Proxy)

Если нужно ходить через прокси (например, для обхода блокоровок OpenAI в РФ).

```python
import aiohttp
from aiohttp_socks import ProxyConnector

async def gpt_request():
    connector = ProxyConnector.from_url("socks5://user:pass@host:port")
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get("https://api.openai.com/...") as resp:
            return await resp.json()
```

## 16. Troubleshooting (Энциклопедия ошибок)

### `AuthKeyDuplicatedError`
**Суть**: Вы запустили бота в двух местах (Heroku + Локально) на одной сессии.
**Лечение**: Удалить файл сессии `.session` и залогиниться заново. Или выключить старый экземпляр.

### `rpc_call: MESSAGE_NOT_MODIFIED`
**Суть**: Попытка `edit` на тот же текст.
**Лечение**:
```python
if message.raw_text != new_text:
    await message.edit(new_text)
```

### `ChannelPrivateError`
**Суть**: Вы пытаетесь получить доступ к чату, в котором вас нет, по ID.
**Лечение**: Нельзя. Нужно инвайт-ссылка или вступить.

### `FloodWaitError`
**Суть**: Телеграм вас забанил на N секунд за спам.
**Лечение**: Ждать. Или использовать несколько аккаунтов (Userbot Farm).

---

## 🏗 Приложение А: Полезные сниппеты

### Создание временного файла
```python
import tempfile
import os

with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
    f.write(data)
    fname = f.name

await client.send_file(..., fname)
os.remove(fname)
```

### Конвертация голосового в текст (STT)
Требует внешнего API (Google/Yandex).
```python
# Скачиваем голосовое
voice = await message.download_media(bytes)
# Отправляем на API
text = await stt_service.recognize(voice)
```

---

*Документация Grandmaster Edition v3.0*
*Специально для Antigravity User.*
