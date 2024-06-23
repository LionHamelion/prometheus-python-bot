import logging
import os
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from ping_server import start_ping_server
import time

# Установлюємо логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Змінна для збереження попереднього стану
previous_status = None

# Лічильник невдалих запитів
failed_attempts = 0

# Час останньої зміни на "Є світло"
last_light_on_time = 0

# Функція визначає, чи пройшов проміжок часу (у секундах) з останнього увімкнення світла
def hasTimePassed(seconds):
    global last_light_on_time
    if time.time() - last_light_on_time >= seconds:
        return True
    else:
        return False

# Функція для перевірки доступності порту за IP-адресою
def is_port_open(ip_address, port):
    for _ in range(3):  # Пробуємо 3 рази
        try:
            # Створюємо сокет
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip_address, port))
            s.close()
            return True
        except Exception:
            time.sleep(3)
    return False

# Функція для відправки повідомлень у Telegram канал
async def send_message(context, message):
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    await context.bot.send_message(chat_id=channel_id, text=message)

# Функція для перевірки стану порту та відправки повідомлень
async def check_port_status(context: ContextTypes.DEFAULT_TYPE) -> None:
    global previous_status, failed_attempts, last_light_on_time
    ip_address = os.getenv('ROUTER_IP')
    port = int(os.getenv('ROUTER_PORT', 80))
    current_status = is_port_open(ip_address, port)

    # Якщо поточний статус змінився на "Є світло"
    if current_status and previous_status != current_status:
        last_light_on_time = time.time()
        await send_message(context, "⚡Є світло")
        previous_status = current_status
        failed_attempts = 0

    # Якщо поточний статус "Нема світла"
    elif not current_status and previous_status != current_status:
        if hasTimePassed(900) or failed_attempts >= 3:
            await send_message(context, "🌚 Нема світла")
            previous_status = current_status
            failed_attempts = 0
        else:
            failed_attempts += 1

# Простий HTTP сервер для підтримки відкритого порту
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world')

def run_http_server():
    port = int(os.getenv('PORT', 8000))
    httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    httpd.serve_forever()

def main() -> None:
    # Запускаємо HTTP сервер у окремому потоці
    threading.Thread(target=run_http_server, daemon=True).start()

    # Запускаємо пінгування сервера у окремому потоці
    start_ping_server()

    # Отримуємо токен з змінних середовища
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    # Створюємо ApplicationBuilder та передаємо йому токен вашого бота
    application = ApplicationBuilder().token(token).build()

    # Встановлюємо JobQueue
    job_queue = application.job_queue
    job_queue.run_repeating(check_port_status, interval=60, first=10)

    # Запускаємо бота
    application.run_polling()

if __name__ == '__main__':
    main()
