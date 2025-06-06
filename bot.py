import telebot
from telebot import types
from config import TOKEN
from datetime import datetime
import openpyxl
import os

API_TOKEN = 
bot = telebot.TeleBot(API_TOKEN)

language_links = {
    "Python": "https://t.me/pythonvideo",
    "JavaScript": "https://t.me/JS_per_month",
    "Java": "https://t.me/javazavr",
    "C++": "https://t.me/cplusplus_tg"
}
#Этот словарь может использоваться в коде для получения ссылки на соответствующий канал в зависимости от выбранного пользователем языка программирования. Например, если пользователь выберет язык "Python", можно получить ссылку с помощью language_links["Python"], что вернет https://t.me/pythonvideo.
excel_file = 'users_data.xlsx'

if not os.path.exists(excel_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "logs"
    ws.append(["Дата и время", "User id", "Имя", "Действие"])
    wb.save(excel_file)
#этот код создает новый файл Excel с указанными заголовками, если файл с таким именем еще не существует

def log_to_excel(user_id, full_name, action):
    try:
        wb = openpyxl.load_workbook(excel_file)
        ws = wb["logs"]
        ws.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, full_name, action])
        wb.save(excel_file)
    except Exception as e:
        print(f"Ошибка при записи в Excel: {e}")
#функция log_to_excel предназначена для записи информации о действиях пользователей в файл Excel. Она обрабатывает возможные ошибки при работе с файлом и листом, что делает код более надежным. 


questions = [
    ("Что такое переменная в Python?",
     ["a) Команда", "b) Имя, ссылающееся на объект", "c) Оператор"], "b"),
    ("Какой тип переменной используется в Java для хранения целых чисел?",
     ["a) float", "b) int", "c) char"], "b"),
    ("Что означает ++ в C++?",
     ["a) Увеличить значение на 1", "b) Комментарий", "c) Ошибка"], "a"),
    ("Что такое let в JavaScript?",
     ["a) Объявление переменной", "b) Функция", "c) Цикл"], "a")
]

user_quiz_data = {}
#создадим функцию, которая будет проводить викторину, задавая вопросы пользователю и проверяя его ответы

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for lang in language_links:
        markup.add(lang)
    markup.add("Пройти опрос")
    bot.send_message(chat_id,
                     "Выбери язык или начни опрос.",
                     reply_markup=markup)
#код для функции show_main_menu создает меню с кнопками, которое позволяет пользователю выбрать язык или начать опрос

@bot.message_handler(commands=['start']) #@bot.message_handler(commands=['start']), чтобы указать, что функция send_welcome будет вызываться при получении команды /start
def send_welcome(message): #Внутри функции send_welcome вызываем show_main_menu, передавая message.chat.id, чтобы показать пользователю главное меню.
    show_main_menu(message.chat.id)
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    log_to_excel(message.from_user.id, full_name, "Зашёл в бота (/start)")
#Функция log_to_excel записывает информацию о пользователе в Excel, что может быть полезно для отслеживания активности пользователей

@bot.message_handler(commands=['help']) #@bot.message_handler(commands=['help']), чтобы указать, что функция send_help будет вызываться при получении команды /help
def send_help(message):
    help_text = ("Я помогаю находить обучающие Telegram-каналы по языкам программирования.\n"
                 "Также ты можешь пройти мини-опрос.\n"
                 "Доступные команды:\n"
                 "/start — начать\n"
                 "/help — справка") #кортеж
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(func=lambda message: message.text == "Пройти опрос")
def start_quiz(message):
    user_quiz_data[message.chat.id] = {"score": 0, "q_index": 0}
    ask_next_question(message) #опрос и очки за него


def ask_next_question(message):
    data = user_quiz_data[message.chat.id]
    index = data["q_index"]
    if index < len(questions):
        q_text, options, _ = questions[index]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in options:
            markup.add(option)
        bot.send_message(message.chat.id, q_text, reply_markup=markup)
    else:
        score = data["score"]
        bot.send_message(message.chat.id,
                         f"Опрос завершён! Ваш результат: {score} из {len(questions)}.")
        del user_quiz_data[message.chat.id]
        show_main_menu(message.chat.id) #опрос и очки за него


@bot.message_handler(func=lambda message: message.chat.id in user_quiz_data)
def handle_quiz_answer(message):
    data = user_quiz_data[message.chat.id]
    index = data["q_index"]
    q_text, options, correct_letter = questions[index] №код для обработки ответов на вопросы в опросе

    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    user_input = message.text.strip()
    user_answer_letter = user_input.lower()[0] if user_input else ""
    correct_option = next((opt for opt in options if opt.startswith(correct_letter)), None) #для обработки ответов пользователей

    is_correct = user_answer_letter == correct_letter

    selected_option = next((opt for opt in options if opt.startswith(user_answer_letter)), "Некорректный ответ")

    if is_correct:
        bot.send_message(message.chat.id, " Верно!")
        data["score"] += 1
    else:
        bot.send_message(message.chat.id, f" Неверно. Правильный ответ: {correct_option}")

    action = (f"Вопрос: '{q_text}' | Ответил: '{selected_option}' | "
              f"{'Верно' if is_correct else 'Неверно'}")
    log_to_excel(message.from_user.id, full_name, action) #для обработки ответов пользователей

    data["q_index"] += 1
    ask_next_question(message)


@bot.message_handler(func=lambda message: True)
def handle_language_selection(message):
    lang = message.text.strip()
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()

    if lang in language_links:
        bot.send_message(message.chat.id, f"Вот канал по {lang}: {language_links[lang]}")
        log_to_excel(message.from_user.id, full_name, f"Перешёл в канал {lang}")
    else:
        bot.send_message(message.chat.id, "Я не понял. Пожалуйста, выбери язык из списка или используй меню.") #если написано что-то непонятное


bot.infinity_polling()
