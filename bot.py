import logging
import os
import socket
import time
from telegram.ext import ApplicationBuilder, ContextTypes

# Налаштування логування виключно в stdout/stderr
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

previous_status = None
failed_attempts = 0
last_light_on_time = 0

def hasTimePassed(seconds):
    global last_light_on_time
    return (time.time() - last_light_on_time) >= seconds

def is_port_open(ip_address, port, retries=5, delay=3, timeout=2):
    for attempt in range(retries):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip_address, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            if attempt < retries - 1:
                time.sleep(delay)
        finally:
            if s:
                s.close()
    return False

async def send_message(context: ContextTypes.DEFAULT_TYPE, message: str):
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    await context.bot.send_message(chat_id=channel_id, text=message)

async def check_port_status(context: ContextTypes.DEFAULT_TYPE) -> None:
    global previous_status, failed_attempts, last_light_on_time
    ip_address = os.getenv('ROUTER_IP')
    port = int(os.getenv('ROUTER_PORT', 80))
    current_status = is_port_open(ip_address, port)

    if current_status and previous_status != current_status:
        last_light_on_time = time.time()
        await send_message(context, "⚡Є світло")
        previous_status = current_status
        failed_attempts = 0

    elif not current_status and previous_status != current_status:
        if hasTimePassed(900) or failed_attempts >= 3:
            await send_message(context, "🌚 Нема світла")
            previous_status = current_status
            failed_attempts = 0
        else:
            failed_attempts += 1

def main() -> None:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()

    job_queue = application.job_queue
    job_queue.run_repeating(check_port_status, interval=60, first=10)

    application.run_polling()

if __name__ == '__main__':
    main()
