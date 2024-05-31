import re
import sqlite3
import nest_asyncio
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests

nest_asyncio.apply()
# Создаем или подключаемся к базе данных
conn = sqlite3.connect('telegram_bot.db', check_same_thread=False)
c = conn.cursor()

# Создаем таблицу для хранения ID пользователей и чатов, если её нет
c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY,
                 chat_id INTEGER
             )''')
c.execute('''CREATE TABLE IF NOT EXISTS pending_users (
                 user_id INTEGER PRIMARY KEY,
                 number TEXT(8)
             )''')
conn.commit()

# Инициализация Flask-приложения
app = Flask(__name__)

loop = asyncio.get_event_loop()

# Инициализация бота
TOKEN = "7080952580:AAEY0Wkfb9NxfJbUQ3a3pUhqrX-wIKPkeFY"
bot = Bot(token=TOKEN)
app_bot = ApplicationBuilder().token(TOKEN).build()

def is_safe_input(value: str) -> bool:
    # Регулярное выражение для поиска опасных символов и конструкций
    injection_pattern = re.compile(
        r"(\'|\"|;|--|\b(OR|AND)\b\s*=\s*\b(OR|AND)\b|\b(SELECT|INSERT|DELETE|UPDATE|DROP|UNION|ALTER)\b)",
        re.IGNORECASE
    )
    if injection_pattern.search(value):
        return False
    return True

# Функция для старта бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    c.execute("SELECT 1 FROM users WHERE chat_id = ?", (chat_id,))
    exists = c.fetchone()

    if exists:
        await update.message.reply_text(f'С возвращением!')
    else:
        await update.message.reply_text('Привет! Введите ваш код командой /auth <номер>')

# Функция для аутентификации пользователя
async def authenticate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    c.execute("SELECT 1 FROM users WHERE chat_id = ?", (chat_id,))
    exists = c.fetchone()
    if exists:
        return await update.message.reply_text(f'Вы уже привязали аккаунт!')

    if len(context.args) != 1:
        await update.message.reply_text('Пожалуйста, введите ваш код в формате: /auth <номер>')
        return

    unique_number = context.args[0]

    if len(unique_number) > 8:
        await update.message.reply_text('Код должен быть не более 8 символов.')
        return

    # Проверка наличия SQL инъекций
    if not is_safe_input(unique_number):
        await update.message.reply_text('Некорректный ввод данных.')
        return
    
    # Проверка наличия пользователя в таблице pending_users по unique_number
    c.execute("SELECT user_id FROM pending_users WHERE number=?", (unique_number,))
    pending_result = c.fetchone()

    if pending_result:
        # Удаляем пользователя из таблицы pending_users
        pending_user_id = pending_result[0]
        c.execute("DELETE FROM pending_users WHERE number=?", (unique_number,))
        # Добавляем пользователя в таблицу users
        c.execute("INSERT INTO users (user_id, chat_id) VALUES (?, ?)", (pending_user_id, chat_id))
        conn.commit()
        await update.message.reply_text(f'Ваш аккаунт успешно привязан')
        
        server_url = " http://localhost:8000/login/local-only/" 
        requests.post(server_url, json={'user_id': pending_user_id})


# Определение асинхронной функции отправки сообщения
async def async_send_message(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

@app.route('/send_message', methods=['POST'])
def send_message_route():
    data = request.json
    user_id = data.get('user_id')
    number = data.get('number')

    if not user_id or not number:
        return jsonify({'error': 'Недостаточно данных. Требуется user_id и number'}), 400

    # Проверка наличия пользователя в базе данных по user_id
    c.execute("SELECT chat_id FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()

    if result:
        chat_id = result[0]
        message = f'Ваш код: {number}'
        try:
            # Используем loop.create_task для планирования асинхронной задачи
            loop.create_task(async_send_message(chat_id, message))
            return jsonify({'status': 'Сообщение отправлено'}), 200
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            return jsonify({'error': f'Ошибка при отправке сообщения: {e}'}), 500
    else:
        try:
            c.execute("INSERT INTO pending_users (user_id, number) VALUES (?, ?)", (user_id, number))
            conn.commit()
            return jsonify({'status': 'Пользователь добавлен в pending_users'}), 200
        except sqlite3.IntegrityError:
            c.execute("UPDATE pending_users SET number = ? WHERE user_id = ?", (number, user_id))
            conn.commit()
            return jsonify({'status': 'Пользователь обновлен в pending_users'}), 200
        except Exception as e:
            return jsonify({'error': f'Ошибка при обработке базы данных: {e}'}), 500
    
async def block_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Доступны только команды /start и /auth.')

def main() -> None:
    # Регистрируем обработчики команд
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("auth", authenticate))

    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_text_messages))

    # Запускаем Flask в отдельном потоке
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(port=5000, debug=True, use_reloader=False))
    flask_thread.start()

    # Запускаем бота
    app_bot.run_polling()

if __name__ == '__main__':
    main()