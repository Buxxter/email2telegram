#!/usr/bin/python3
# -*- coding: utf-8 -*-

import email
import errno
import imaplib
import netrc
import os
import quopri
import time
import traceback
import logging.config
from email.header import decode_header, make_header
from socket import error as SocketError

import telegram

logging.config.fileConfig('log.conf')
logger = logging.getLogger(__name__)

from utils.myParser import *

secrets = netrc.netrc(
    file=os.path.join(os.environ['USERPROFILE'], "_netrc")) if 'win' in sys.platform else netrc.netrc()

master, none_account, TOKEN = secrets.authenticators('personal_sms_resender_bot')
logging.debug(TOKEN)
bot = telegram.TelegramBot(TOKEN)
bot.master = master
bot.message_loop(relax=60)

mail_username, account, mail_password = secrets.authenticators('home_phone_mail')


def mail_state_check_before_select(box):
    if 'NONAUTH' == box.state:
        box.login(user=mail_username, password=mail_password)

    box.noop()


def mail_get_unseen_count(box):
    mail_state_check_before_select(box)
    result, data = mail.status('SMS', '(UNSEEN)')
    res = data[0].decode('ASCII')
    res = res.replace('SMS (UNSEEN', '').replace(')', '').strip()
    res = int(res)
    logger.debug('Unseen count: {}'.format(res))
    if res > 0:
        logging.info('Have unread mail ({})'.format(res))
    return res


def mail_check():

    mail_state_check_before_select(mail)

    mail.select('SMS')

    result, data = mail.search(None, '(UNSEEN FROM "buxxter.phone")')  # "(UNSEEN)"

    ids = data[0]  # data is a list.
    id_list = ids.split()  # ids is a space separated string

    for msg_id in id_list:

        result, data = mail.fetch(msg_id,
                                  '(BODY.PEEK[HEADER])')  # "(RFC822.PEEK)", )  # fetch the email body (RFC822) for the given ID
        if 'OK' not in result:
            logging.warning('Headers read error ({}) on msg_id={}'.format(result, msg_id))
            continue

        raw_email = data[0][1]  # here's the body, which is raw text of the whole email
        # including headers and alternate payloads

        email_message = email.message_from_string(raw_email.decode('ASCII'))

        logger.debug('From:    {}'.format(str(make_header(decode_header(email_message['From'])))))
        logger.debug('To:      {}'.format(str(make_header(decode_header(email_message['To'])))))
        subject = str(make_header(decode_header(email_message['Subject'])))
        logger.debug('Subject: {}'.format(subject))

        if 'SMS@Email' not in subject:
            logger.debug('Message {} not from SMS@Email'.format(msg_id))
            continue

        result, data = mail.fetch(msg_id,
                                  '(BODY.PEEK[TEXT])')  # "(RFC822.PEEK)", )  # fetch the email body (RFC822) for the given ID
        if 'OK' not in result:
            logging.warning('Body read error ({}) on msg_id={}'.format(result, msg_id))
            continue

        html_text = quopri.decodestring(data[0][1]).decode('utf-8')
        parsed_message = parse_mail_body(html_text)

        bot_message = '{} {}  ({})'.format("\u2709" if parsed_message['is_message'] else "\u260E",
                                            parsed_message['sender'],
                                            parsed_message['date'].strftime('%Y-%m-%d %H:%M:%S')
                                            )
        if parsed_message['is_message']:
            bot_message = bot_message + ':\r\n' + parsed_message['text']

        bot.sendMessage(chat_id=bot.master, text=bot_message)
        mail.store(msg_id, '+FLAGS', '\Seen')


mail = None
sleep_time = 1
connected = False

logger.info('Listening...')
while 1:
    try:
        if mail is None:
            mail = imaplib.IMAP4_SSL(host='imap.yandex.ru', port=993)

        if mail_get_unseen_count(mail) == 0:
            mail.noop()
        else:
            mail_check()
            counter = 0
        sleep_time = 1
        if not connected:
            logger.info('Connected')
            connected = True
    except OSError as ex:   # Network problem
        connected = False
        logger.info(str(ex))
        sleep_time = min(sleep_time + 10, 100)
        pass
    except imaplib.IMAP4.abort as ex:
        logger.debug(str(ex))
        logger.debug(traceback.format_exc())
        mail = None
    except SocketError as er:
        logger.debug('{}: {}'.format('SE', traceback.format_exc()))
        if er.errno != errno.ECONNRESET:
            raise
        pass
    except:
        logging.warning(traceback.format_exc())
        bot.sendMessage(chat_id=bot.master, text=traceback.format_exc())
        mail = None
        sleep_time = min(sleep_time * 10, 7200)

    time.sleep(sleep_time)

mail.close()
mail.logout()
mail = None
