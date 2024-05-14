import logging
import re
import paramiko
import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater,CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from psycopg2 import Error

TOKEN = "7028785582:AAFaGnQt9enQNJPZjA3qYCw3Gk2UvX_RkiE"

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding='utf-8', level=logging.INFO
)

logger = logging.getLogger(__name__)

dotenv_path = Path('C:\\devops_bot\\ENV.env')
load_dotenv(dotenv_path=dotenv_path)

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

host_bd = os.getenv('HOST_BD')
port_bd = os.getenv('PORT_BD')
username_bd = os.getenv('USER_BD')
password_bd = os.getenv('PASSWORD_BD')

def execute_ssh_command(host, port, username, password, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=port, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode('utf-8').strip()

        client.close()

        return output
    except Exception as e:
        return str(e)

connection = None

def execute_ssh_command_bd(host_bd, port_bd, username_bd, password_bd, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host_bd, port=port_bd, username=username_bd, password=password_bd)
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode('utf-8').strip()

        client.close()

        return output
    except Exception as e:
        return str(e)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет, {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Справочник команд:\n/get_phone_numbers - Список телефонных номеров\n/get_emails - Список email-адресов\n/find_phone_number - Вывести список телефонных номеров\n/find_email - Вывести список email-адресов\n/get_release - Информация о релизе системы\n/verify_password - Проверка пароля\n/get_uname - Информация об архитектуре процессора, имени хоста системы и версии ядра\n/get_uptime - Информация о времени работы системы\n/get_df - Информация о состоянии файловой системы\n/get_free - Информация о состоянии оперативной памяти\n/get_mpstat - Информация о производительности системы\n/get_w - Информация о работающих в системе пользователях\n/get_auths - Логи о последних 10 входов в систему\n/get_critical - Логи о последних 5 критических событиях\n/get_ps - Информация о запущенных процессах\n/get_ss - Информация об используемых портах\n/get_apt_list - Информация об установленных пакетах\n/get_services - Информация о запущенных сервисах\n/get_repl_logs - Вывод логов о репликации')


def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

def find_emailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')

    return 'find_email'

def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')

    return 'verify_password'

def get_apt_listCommand(update: Update, context):
    keyboard = ([
        [
            InlineKeyboardButton("Все пакеты", callback_data='button_all'),
            InlineKeyboardButton("Выбранный пакет", callback_data='button_selected'),
        ]
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    reply_text = ('Информацию о каких пакетах Вам предоставить?')
    update.message.reply_text(reply_text, reply_markup=reply_markup)
    return 'get_apt_list'

def find_phone_number(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'(?:\+7|8)\s?(?:\(|-)?\d{3}(?:\)|-)?\s?\d{3}(?:(?:-|\s)?\d{2}){2}')
    phoneNumbersList = phoneNumRegex.findall(user_input)

    if not phoneNumbersList:
        update.message.reply_text('Телефонные номера не найдены')
        return
    
    phoneNumbers_text = '' 
    for i, phoneNumber in enumerate(phoneNumbersList, 1):
        phoneNumbers_text += f'{i}. {phoneNumber}\n' 

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Да", callback_data='button_yes'), 
            InlineKeyboardButton("Нет", callback_data='button_no')
        ],
    ])
    reply_text = f'Найдены следующие телефонные номера:\n{phoneNumbers_text}\nХотите записать данные?'  
    update.message.reply_text(reply_text, reply_markup=keyboard)
    context.user_data['phoneNumbersList'] = phoneNumbersList     
    return 'confirm_insert_phone'


def confirm_insert_phone(update: Update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'button_yes':
        phoneNumbersList = context.user_data.get('phoneNumbersList', [])
        try:
            connection = psycopg2.connect(user="postgres",
                                           password="123",
                                           host="172.20.10.6",
                                           port="5432",
                                           database="bot_tg")
            cursor = connection.cursor()
            for phoneNumber in phoneNumbersList:
                cursor.execute("INSERT INTO phone_number_table (phone_number) VALUES (%s);", (phoneNumber,))
            connection.commit()
            query.message.reply_text('Добавление в базу данных прошло успешно!')
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            # Обработка ошибок
            query.message.reply_text(f'Ошибка при работе с PostgreSQL: {error}')
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            # Закрытие соединения
            if connection is not None:
                cursor.close()
                connection.close()

    elif query.data == 'button_no':
        query.message.reply_text('ок')

    return ConversationHandler.END


def find_email(update: Update, context):
    user_input = update.message.text 
    EmailsRegex = re.compile(r'\b[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+)*' \
                r'@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')
    EmailsList = EmailsRegex.findall(user_input) 

    if not EmailsList: 
        update.message.reply_text('email-адреса не найдены')
        return 
    
    Emails = ''
    for i, email in enumerate(EmailsList, 1):
        Emails += f'{i}. {email}\n'

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Да", callback_data='button_yes'),
            InlineKeyboardButton("Нет", callback_data='button_no')
        ]
    ])
    reply_text = f'Найдены следующие email-адреса:\n{Emails}\nХотите записать данные?'
    update.message.reply_text(reply_text, reply_markup=keyboard)
    context.user_data['EmailsList'] = EmailsList
    return 'confirm_insert_email' 

def confirm_insert_email(update: Update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'button_yes':
        EmailsList = context.user_data.get('EmailsList', [])
        try:
            connection = psycopg2.connect(user="postgres",
                                password="123",
                                host="172.20.10.6",
                                port="5432", 
                                database="bot_tg")
            cursor = connection.cursor()
            
            for email in EmailsList:
                cursor.execute("INSERT INTO emails_table (email) VALUES (%s);", (email,))
            connection.commit()
            query.message.reply_text('Добавление в базу данных прошло успешно!')
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            query.message.reply_text('Ошибка при работе с PostgreSQL: %s', error)
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
             cursor.close()
             connection.close()  
    elif query.data == 'button_no':
        query.message.reply_text('ок')

    return ConversationHandler.END 

def verify_password (update: Update, context):
    user_input = update.message.text
    if re.match(r'[A-Za-z\d!@#$%^&*()]{8,}', user_input):
        update.message.reply_text('Пароль сложный!')
    else:
        update.message.reply_text('Пароль простой.')
    return ConversationHandler.END # Завершаем работу обработчика диалога

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def get_release(update: Update, context):
    command ='lsb_release -a'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация  о релизе:\n' + result)

def get_uname(update: Update, context):
    command ='uname -nrm'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация об архитектуре процессора, имени хоста системы и версии ядра:\n' + result)

def get_uptime(update: Update, context):
    command ='uptime -p'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о времени работы:\n' + result) 

def get_df(update: Update, context):
    command ='df'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о состоянии файловой системы:\n' + result)       

def get_free(update: Update, context):
    command ='free'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о состоянии оперативной памяти:\n' + result)             

def get_mpstat(update: Update, context):
    command ='mpstat'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о производительности системы:\n' + result)         

def get_w(update: Update, context):
    command ='w'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о последних 10 входов в систему:\n' + result) 

def get_auths(update: Update, context):
    command ='last -n 10'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о работающих в данной системе пользователях:\n' + result) 
    
def get_critical(update: Update, context):
    command ='journalctl -p crit -n 5'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о последних 5 критический событиях:\n' + result) 

def get_ps(update: Update, context):
    command ='ps'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о запущенных процессах:\n' + result)     

def get_ss(update: Update, context):
    command ='ss -tulp'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация об используемых портах:\n' + result)   

def get_apt_list(update: Update, context):
    query = update.callback_query
    query.answer()
    command = 'apt list | head -n 20'
    result = execute_ssh_command(host, port, username, password, command)
    if query.data == 'button_selected':
        query.message.reply_text('Введите интересующий Вас пакет:')  
        return 'selected_package' 
    elif query.data == 'button_all':
        command = 'apt list | head -n 20'
        result = execute_ssh_command(host, port, username, password, command)
        query.message.reply_text('Информация об установленных пакетах:\n' + result)     
        return ConversationHandler.END 

    return ConversationHandler.END

def selected_package(update: Update, context):
    user_input = update.message.text
    command = 'apt list ' + user_input
    result = execute_ssh_command(host, port, username, password, command)
    count_result = (len(result.split('\n')))
    if count_result==1:
            update.message.reply_text('Нет установленных пакетов.')
            return ConversationHandler.END
    else:
        update.message.reply_text('Информация об указанном пакете:\n' + result)
        return ConversationHandler.END

def get_services(update: Update, context):
    command ='systemctl list-units --state=running '
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text('Информация о запущенных сервисах:\n' + result)  

def get_repl_logs(update: Update, context):
    command ='cat /var/log/postgresql/postgresql-14-main.log | grep "replic" | tail -n 20'
    result = execute_ssh_command_bd(host_bd, port_bd, username_bd, password_bd, command)
    update.message.reply_text('Логи о репликации:\n' + result) 

def get_emails(update: Update, context):
    try:
        connection = psycopg2.connect(user="postgres",
                                password="123",
                                host="172.20.10.6",
                                port="5432", 
                                database="bot_tg")

        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails_table;")
        data = cursor.fetchall()
        Emails = ''
        for i in range(len(data)):
            Emails += f'{i+1}. {"".join(data[i])}\n'
        update.message.reply_text('Найденные email-адреса:\n' + Emails)  
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()  

def get_phone_numbers(update: Update, context):
    try:
        connection = psycopg2.connect(user="postgres",
                                password="123",
                                host="172.20.10.6",
                                port="5432", 
                                database="bot_tg")

        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phone_number_table;")
        data = cursor.fetchall()
        Phones = ''
        for i in range(len(data)):
            Phones += f'{i+1}. {"".join(data[i])}\n'
        update.message.reply_text('Найденные телефонные номера:\n' + Phones)  
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()  

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'confirm_insert_phone': [CallbackQueryHandler(confirm_insert_phone)],
        },
        fallbacks=[]
    )

    convHandlerfind_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'confirm_insert_email': [CallbackQueryHandler(confirm_insert_email)],
        },
        fallbacks=[]
    )   
    convHandlerverify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerget_apt_list = ConversationHandler(
    entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
    states={
        'get_apt_list': [CallbackQueryHandler(get_apt_list)],
        'selected_package': [MessageHandler(Filters.text & ~Filters.command, selected_package)],
    },
    fallbacks=[] 
)  

# Регистрация всех ConversationHandler
    dp.add_handler(convHandlerfind_phone_number)
    dp.add_handler(convHandlerfind_email)
    dp.add_handler(convHandlerverify_password)
    dp.add_handler(convHandlerget_apt_list)

# Отдельная регистрация обработчиков команд и колбэков
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
