# requires: aiohttp prometheus_client
from .. import loader, utils
from aiohttp import web
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import time

# --- ОПРЕДЕЛЕНИЕ МЕТРИК ---
# Счетчик всех команд
COMMANDS_TOTAL = Counter(
    "userbot_commands_total", 
    "Total number of commands executed", 
    ["command_name", "status"] # Labels: имя команды, статус (success/error)
)

# Время выполнения команд (Гистограмма)
COMMAND_LATENCY = Histogram(
    "userbot_command_duration_seconds",
    "Time spent executing command",
    ["command_name"]
)

# Счетчик входящих сообщений (Watcher)
MESSAGES_TOTAL = Counter(
    "userbot_messages_total",
    "Total incoming messages processed",
    ["chat_type"] # private/group/channel
)

@loader.tds
class GrafanaExporterMod(loader.Module):
    """
    Модуль-экспортер метрик для Prometheus/Grafana.
    Запускает HTTP сервер на порту 9090 и отдает метрики по /metrics.
    """
    
    strings = {"name": "GrafanaExporter"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "port",
                9090,
                "Port for metrics server",
                validator=loader.validators.Integer()
            )
        )
        self.site = None

    async def client_ready(self, client, db):
        self.client = client
        
        # Запуск HTTP сервера
        app = web.Application()
        app.router.add_get("/metrics", self.metrics_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Слушаем на всех интерфейсах
        self.site = web.TCPSite(runner, "0.0.0.0", self.config["port"])
        await self.site.start()
        
        # Логируем старт
        await utils.answer(
            await client.send_message("me", "Grafana Exporter started!"), 
            f"📊 <b>Metrics available at:</b> <code>http://localhost:{self.config['port']}/metrics</code>"
        )

    async def on_unload(self):
        # Обязательно останавливаем сервер при выгрузке модуля
        if self.site:
            await self.site.stop()

    async def metrics_handler(self, request):
        """Отдает метрики в формате Prometheus"""
        data = prometheus_client.generate_latest()
        return web.Response(body=data, content_type="text/plain; version=0.0.4")

    @loader.watcher(only_messages=True)
    async def watcher(self, message):
        """Считаем входящие сообщения"""
        chat_type = "unknown"
        if message.is_private: chat_type = "private"
        elif message.is_group: chat_type = "group"
        elif message.is_channel: chat_type = "channel"
        
        MESSAGES_TOTAL.labels(chat_type=chat_type).inc()

    # Пример обертки для команд
    # (В реальном юзерботе лучше встроить это в ядро лоадера, но можно и так)
    @loader.command()
    async def metricstestcmd(self, message):
        """Тестовая команда для генерации метрик"""
        start = time.time()
        
        try:
            # Эмуляция работы
            await utils.answer(message, "Working...")
            time.sleep(0.5) 
            
            # Успех
            COMMANDS_TOTAL.labels(command_name="test", status="success").inc()
            await utils.answer(message, "Done!")
            
        except Exception:
            COMMANDS_TOTAL.labels(command_name="test", status="error").inc()
            raise
            
        finally:
            duration = time.time() - start
            COMMAND_LATENCY.labels(command_name="test").observe(duration)
