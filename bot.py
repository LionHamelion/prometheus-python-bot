import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Установлюємо логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Функція, яка відповідає на команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привіт! Я твій новий бот.')

def main() -> None:
    # Отримуємо токен з змінних середовища
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    # Створюємо ApplicationBuilder та передаємо йому токен вашого бота
    application = ApplicationBuilder().token(token).build()

    # Реєструємо обробник для команди /start
    application.add_handler(CommandHandler("start", start))

    # Запускаємо бота
    application.run_polling()

if __name__ == '__main__':
    main()
