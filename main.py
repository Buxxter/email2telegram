#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from utils.log import *
from utils.myParser import *
import imaplib
import email
from email.header import Header, decode_header, make_header
import quopri, base64

logger = logging.getLogger()
logger_init(logger, __name__)

mail = imaplib.IMAP4_SSL(host='imap.yandex.ru', port=993)
mail.login(user='home.phone@buxxter.ru', password='***')
mail.select('INBOX')

result, data = mail.search(None, "ALL") #"(UNSEEN)"

ids = data[0]  # data is a list.
id_list = ids.split()  # ids is a space separated string

# for id in id_list:


latest_email_id = id_list[-1]  # get the latest

result, data = mail.fetch(latest_email_id, "(RFC822)")  # fetch the email body (RFC822) for the given ID

raw_email = data[0][1]  # here's the body, which is raw text of the whole email
                        # including headers and alternate payloads

print(raw_email)
f = open('d:\mail.txt', 'w', encoding='ASCII')
f.write(raw_email.decode('ASCII'))
f.close()

email_message = email.message_from_string(raw_email.decode('ASCII'))

# print(email_message)

print('From:    ', str(make_header(decode_header(email_message['From']))))
print('To:      ', str(make_header(decode_header(email_message['To']))))
print('Subject: ', str(make_header(decode_header(email_message['Subject']))))

print('BodyH:')
print(str(make_header(decode_header(email_message.get_payload()))))

html_text = email_message.get_payload()
print('Body:')
print(quopri.decodestring(html_text))


get_body(html_text)

# parser = MyHTMLParser()
# parser.feed(html_text)
#print(parser.get_starttag_text())
