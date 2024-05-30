import telebot
from decimal import Decimal
from prometheus_client import start_http_server, Counter, Summary

bot = telebot.TeleBot("7080557202:AAHUXlYCck-y5g12Nx7ZTIyCNISFmB7ZxZw")

OPERATIONS_COUNTER = Counter('math_operations_total', 'Total number of math operations performed', ['operation'])
ERRORS_COUNTER = Counter('errors_total', 'Total number of errors encountered')
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

start_http_server(9091)

@bot.message_handler(commands=['show'])
def send_show(message):
    show_message = """
    Розробкою займались:
    Хижняк Валерія Валеріївна
    Костенко Павло Сергійович
    Сидорук Аліна Констянтинівна
    """
    bot.reply_to(message, show_message)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = f"""
    Привіт, {message.from_user.first_name}! Я бот, здатний виконувати прості математичні операції (ТОБТО МНОЖЕННЯ, ДІЛЕННЯ, ДОДАВАННЯ ТА ВІДНІМАННЯ) з двома числами.
    Просто введіть два числа та операцію між ними (наприклад, 2 + 3), 
    і я вам надішлю результат. Не забудьте розділити числа та операцію пробілом.
    Для допомоги напишіть /help
    """
    bot.reply_to(message, welcome_message)


@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = """
    Як використовувати цього бота:

    /start - початок роботи з ботом
    /help - показати цей довідник
    /show - отримати інформацію про розробників
    Для виконання операцій просто напишіть повідомлення з операцією (наприклад, 2 + 3)
    """
    bot.reply_to(message, help_message)


@bot.message_handler(func=lambda message: True)
@REQUEST_TIME.time()
def calculate(message):
    try:
        text = message.text.split()
        num1 = Decimal(text[0])
        num2 = Decimal(text[2])
        operation = text[1]

        if operation == '/' and num2 == 0:
            bot.reply_to(message, 'Ділення на нуль неможливе. ' + message.from_user.first_name + ', хіба Вас в школі не вчили, що на нуль ділити не можна?)')
            ERRORS_COUNTER.inc()
            return

        result = None
        if operation == '+':
            result = num1 + num2
            OPERATIONS_COUNTER.labels(operation='+').inc()
        elif operation == '-':
            result = num1 - num2
            OPERATIONS_COUNTER.labels(operation='-').inc()
        elif operation == '*':
            result = num1 * num2
            OPERATIONS_COUNTER.labels(operation='*').inc()
        elif operation == '/':
            result = num1 / num2
            OPERATIONS_COUNTER.labels(operation='/').inc()
        else:
            bot.reply_to(message, 'Будь ласка, введіть коректну операцію.')
            ERRORS_COUNTER.inc()
            return

        bot.reply_to(message, f'Результат: {result}')
    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так. Схоже такої команди немає, або команду було введено не корректно. Спробуйте ще раз пізніше.')
        ERRORS_COUNTER.inc()


bot.polling()
