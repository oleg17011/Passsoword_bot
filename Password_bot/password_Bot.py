import os
import sqlite3
import telebot
from telebot import types
from cryptography.fernet import Fernet
import random
import string
import config

BASE_PATH = r"C:\Users\Anastasia\Desktop\Bots\Password_bot"
bot = telebot.TeleBot(config.BOT_TOKEN)
user_states = {}

def get_db_connection():
    db_file = os.path.join(BASE_PATH, "passwords.db")
    conn = sqlite3.connect(db_file, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def execute_db_query(query, params=(), fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return result

def init_db():
    execute_db_query('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        encryption_key TEXT
    )''')
    execute_db_query('''CREATE TABLE IF NOT EXISTS passwords (
        user_id INTEGER,
        encrypted_password TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )''')

def get_or_create_key(user_id):
    row = execute_db_query("SELECT encryption_key FROM users WHERE user_id = ?", (user_id,), fetch=True)
    if row:
        return Fernet(row[0]['encryption_key'])
    key = Fernet.generate_key()
    execute_db_query("INSERT INTO users (user_id, encryption_key) VALUES (?, ?)", (user_id, key))
    return Fernet(key)

def encrypt_password(user_id, password):
    try:
        return get_or_create_key(user_id).encrypt(password.encode()).decode()
    except:
        return None

def decrypt_password(user_id, encrypted_password):
    try:
        return get_or_create_key(user_id).decrypt(encrypted_password.encode()).decode()
    except:
        return None

def save_password(user_id, password):
    encrypted = encrypt_password(user_id, password)
    if encrypted:
        execute_db_query("INSERT INTO passwords (user_id, encrypted_password) VALUES (?, ?)", (user_id, encrypted))

def show_passwords(user_id):
    rows = execute_db_query("SELECT encrypted_password FROM passwords WHERE user_id = ?", (user_id,), fetch=True)
    if not rows:
        bot.send_message(user_id, "У вас нет сохранённых паролей.")
        return
    decrypted = [decrypt_password(user_id, row['encrypted_password']) for row in rows]
    text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(decrypted)])
    bot.send_message(user_id, f"Ваши сохранённые пароли:\n{text}")

def generate_password(length, exclude_numbers, exclude_special_chars):
    chars = string.ascii_letters
    if not exclude_numbers:
        chars += string.digits
    if not exclude_special_chars:
        chars += string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def send_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["🔑 Генерация пароля", "🗂️ Мои пароли", "🔐 Шифрование пароля", "🔓 Дешифрование пароля"]
    markup.add(*[types.KeyboardButton(text) for text in buttons])
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(commands=["start"])
def start_command(message):
    send_main_menu(message)

@bot.message_handler(func=lambda m: m.text == "Назад")
def back_to_main_menu(message):
    user_states.pop(message.chat.id, None)
    send_main_menu(message)

@bot.message_handler(func=lambda m: m.text == "🗂️ Мои пароли")
def my_passwords(message):
    show_passwords(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🔑 Генерация пароля")
def generate_password_command(message):
    user_id = message.chat.id
    user_states[user_id] = "password_generation"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[types.KeyboardButton(text) for text in ["8", "12", "16", "20", "Назад"]])
    msg = bot.send_message(user_id, "Выберите длину пароля:", reply_markup=markup)
    bot.register_next_step_handler(msg, handle_generate_password_length, user_id)

def handle_generate_password_length(message, user_id):
    if message.text == "Назад":
        back_to_main_menu(message)
        return
    try:
        length = int(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(text) for text in ["1 - Простой", "2 - Средний", "3 - Сложный", "Назад"]])
        msg = bot.send_message(user_id, "Выберите сложность пароля:", reply_markup=markup)
        bot.register_next_step_handler(msg, handle_generate_password_complexity, user_id, length)
    except:
        bot.send_message(user_id, "Введите корректную длину из списка.")

def handle_generate_password_complexity(message, user_id, length):
    if message.text == "Назад":
        back_to_main_menu(message)
        return
    try:
        level = int(message.text.split()[0])
        exclude_numbers = exclude_special_chars = True if level == 1 else False
        if level == 2:
            exclude_numbers = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(text) for text in ["1", "2", "3", "4", "5", "Назад"]])
        msg = bot.send_message(user_id, "Сколько паролей сгенерировать?", reply_markup=markup)
        bot.register_next_step_handler(msg, handle_generate_password_count, user_id, length, exclude_numbers, exclude_special_chars)
    except:
        bot.send_message(user_id, "Выберите сложность из списка.")

def handle_generate_password_count(message, user_id, length, exclude_numbers, exclude_special_chars):
    if message.text == "Назад":
        back_to_main_menu(message)
        return
    try:
        count = int(message.text)
        passwords = [generate_password(length, exclude_numbers, exclude_special_chars) for _ in range(count)]
        for p in passwords:
            save_password(user_id, p)
        text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(passwords)])
        bot.send_message(user_id, f"Готово! Вот ваши пароли:\n{text}")
        send_main_menu(message)
    except:
        bot.send_message(user_id, "Введите корректное количество.")

@bot.message_handler(func=lambda m: m.text == "🔐 Шифрование пароля")
def encrypt_password_command(message):
    msg = bot.send_message(message.chat.id, "Введите пароль для шифрования:")
    bot.register_next_step_handler(msg, handle_encryption_step, message.chat.id)

def handle_encryption_step(message, user_id):
    if message.text == "Назад":
        back_to_main_menu(message)
        return
    encrypted = encrypt_password(user_id, message.text)
    bot.send_message(user_id, f"Зашифрованный пароль:\n{encrypted}" if encrypted else "Ошибка шифрования.")
    send_main_menu(message)

@bot.message_handler(func=lambda m: m.text == "🔓 Дешифрование пароля")
def decrypt_password_command(message):
    msg = bot.send_message(message.chat.id, "Введите зашифрованный пароль:")
    bot.register_next_step_handler(msg, handle_decryption_step, message.chat.id)

def handle_decryption_step(message, user_id):
    if message.text == "Назад":
        back_to_main_menu(message)
        return
    decrypted = decrypt_password(user_id, message.text)
    bot.send_message(user_id, f"Пароль: {decrypted}" if decrypted else "Ошибка дешифровки.")
    send_main_menu(message)

if __name__ == "__main__":
    init_db()
    bot.polling(none_stop=True)
