import logging
import os
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Установлюємо логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Змінна для збереження попереднього стану
previous_status = None

# Функція для перевірки доступності IP-адреси
def is_router_reachable(ip_address):
    try:
        # Створюємо сокет
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip_address, 80))
        s.close()
        return True
    except Exception:
        return False

# Функція для відправки повідомлень у Telegram канал
async def send_message(context, message):
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    await context.bot.send_message(chat_id=channel_id, text=message)

# Функція для перевірки стану роутера та відправки повідомлень
async def check_router_status(context: ContextTypes.DEFAULT_TYPE) -> None:
    global previous_status
    ip_address = os.getenv('ROUTER_IP')
    current_status = is_router_reachable(ip_address)

    if current_status != previous_status:
        if current_status:
            await send_message(context, "Є світло")
        else:
            await send_message(context, "Нема світла")
        
        # Оновлюємо попередній стан
        previous_status = current_status

def main() -> None:
    # Отримуємо токен з змінних середовища
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    # Створюємо ApplicationBuilder та передаємо йому токен вашого бота
    application = ApplicationBuilder().token(token).build()

    # Встановлюємо JobQueue
    job_queue = application.job_queue
    job_queue.run_repeating(check_router_status, interval=60, first=10)

    # Запускаємо бота
    application.run_polling()

if __name__ == '__main__':
    main()
