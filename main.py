import json
import mailparser
import random
import vk_api, vk
import threading
import time
import logging
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
from imapclient import IMAPClient
from emailClass import Email
from sql import ChatRepository

chatRepository = ChatRepository()

with open("config.json", "r") as f:
    data = json.loads(f.read())
    VK_TOKEN = data["vk_token"]
    VK_GROUP_ID = data["vk_group_id"]
    VK_KEY = data["vk_key"]
    VK_SERVER = data["vk_server"]
    VK_TS = data["vk_ts"]
    HOST = data["host"]
    LOGIN = data["login"]
    PASSWORD = data["password"]
    PRINT_BODY = data["print_body"]
    NEED_FILTER = data["need_filter"]
    INPUT_FILTERS = data["input_filters"]
    FILTERS = data["filters"]

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)
vk = vk_session.get_api()


chats_ids = []

def filterEmails(x):
    result = False
    for i in x.to_email:
        if i[1] in FILTERS:
            result = True 

    for i in x.from_email:
        if i[1] in INPUT_FILTERS:
            result = False
    return result

def get_emails():
    emails = []

    with IMAPClient(HOST) as server:
        server.login(LOGIN, PASSWORD)
        server.select_folder("INBOX", readonly=True)

        messages = server.search(["UNSEEN"])
        
        for uid, message_data in server.fetch(messages, ["RFC822", "BODY[TEXT]"]).items():
            mail = mailparser.parse_from_bytes(message_data[b"RFC822"])

            email = Email(mail)
            emails.append(email)
        
        if len(messages) > 0:
            server.move(messages, "Прочитанные ботом")

    return emails

def update_emails():
    time.sleep(10)
    while True:
        emails = get_emails()

        if NEED_FILTER:
            emails = list(filter(filterEmails, emails))

        for email in emails:
            message = "📌Новое сообщение: \n"
            message += f" - От: {email.from_as_string}\n"
            message += f" - Куда: {email.to_as_string}\n"
            message += f" - Тема: {email.subject}\n"

            if PRINT_BODY:
                message += f"Содержание: \n {email.body}"

            chats_ids = chatRepository.get_all()

            for chat_id in chats_ids:
                vk.messages.send(
                    key = (VK_KEY),
                    server = (VK_SERVER),
                    ts=(VK_TS),
                    random_id = get_random_id(),
                    message=message,
                    chat_id = chat_id
                )

        time.sleep(10)

th = threading.Thread(target=update_emails)
th.start()

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if 'Включить рассылку' in str(event):
            if event.from_chat:
                message = 'Рассылка включена!'
                if not chatRepository.get(event.chat_id):
                    chatRepository.subscribe(event.chat_id)
                else:
                    message = "Рассылка уже была включена!"
                vk.messages.send(
                    key = (VK_KEY),
                    server = (VK_SERVER),
                    ts=(VK_TS),
                    random_id = get_random_id(),
                    message=message,
                    chat_id = event.chat_id
                )
        elif 'Выключить рассылку' in str(event):
            if event.from_chat:
                message = 'Рассылка выключена!'
                if chatRepository.get(event.chat_id):
                    chatRepository.unsubscribe(event.chat_id)
                else:
                    message = "Рассылка уже была выключена!"
                vk.messages.send(
                    key = (VK_KEY),
                    server = (VK_SERVER),
                    ts=(VK_TS),
                    random_id = get_random_id(),
                    message=message,
                    chat_id = event.chat_id
                )