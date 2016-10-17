#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from utils.log import *
from utils.myParser import *
import netrc
import imaplib
import email
from email.header import Header, decode_header, make_header
import quopri

logger = logging.getLogger()
logger_init(logger, __name__)


secrets = netrc.netrc()
username, account, password = secrets.authenticators('home_phone_mail')

mail = imaplib.IMAP4_SSL(host='imap.yandex.ru', port=993)
mail.login(user=username, password=password)
mail.select('INBOX')

result, data = mail.search(None, "(UNSEEN)") #"(UNSEEN)"

ids = data[0]  # data is a list.
id_list = ids.split()  # ids is a space separated string

for msg_id in id_list:

    result, data = mail.fetch(msg_id, "(RFC822)")  # fetch the email body (RFC822) for the given ID

    raw_email = data[0][1]  # here's the body, which is raw text of the whole email
                            # including headers and alternate payloads

    email_message = email.message_from_string(raw_email.decode('ASCII'))

    logger.debug('From:    {}'.format(str(make_header(decode_header(email_message['From'])))))
    logger.debug('To:      {}'.format(str(make_header(decode_header(email_message['To'])))))
    logger.debug('Subject: {}'.format(str(make_header(decode_header(email_message['Subject'])))))

    html_text = quopri.decodestring(email_message.get_payload()).decode('utf-8')

    get_body(html_text)

    # mail.store(msg_id, '+FLAGS', '\Seen')

# parser = MyHTMLParser()
# parser.feed(html_text)
#print(parser.get_starttag_text())
