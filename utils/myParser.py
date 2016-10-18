#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import lxml.html as html
# import requests
# import time
# from lxml import etree
# from lxml.html import HTMLParser
#
#
# def get_body(body):
#     tree = etree.fromstring(body, parser=HTMLParser())
#
#     path_name = tree.xpath('html/body')[0].text
#     print(path_name)
#     # for element in tree.xpath(path_name):
#     #     print(element)

#--
# import html5lib
# from html5lib import treebuilders
# from lxml import etree
#
# def get_body(body):
#     f = open('D:\msg_example.html').read()
#     parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('lxml'), namespaceHTMLElements=False)
#     doc = parser.parse(f)
#     val = doc.xpath('/html/body/p[2]/.')
#     for e in val:
#         print(etree.tostring(e))

import sys
import logging
from lxml import etree as ET
from io import StringIO, BytesIO
from datetime import datetime
import locale

logger = logging.getLogger(__name__)


def parse_mail_body(mail_body):
    result = dict.fromkeys(['type', 'is_message', 'date', 'sender', 'text'])
    result['is_message'] = False

    tree = ET.parse(StringIO(mail_body), ET.HTMLParser())
    body = tree.xpath('/html/body/p[contains(text(), "Incoming") and contains(text(), "SMS")]')
    result['type'] = 'SMS' if len(body) == 1 else 'Missed Call'

    body = tree.xpath('/html/body/p[contains(text(), "Received From")]')
    if len(body) > 0:
        data = str(body[0].text).replace('Received From', '').replace(':', '', 1).lstrip()
        result['sender'] = data

    body = tree.xpath('/html/body/p[contains(text(), "Received On")]')
    if len(body) > 0:
        data = str(body[0].text).replace('Received On', '').replace(':', '', 1).strip()

        am_pm = 'am' if ' am' in data.lower() else 'pm' if 'pm ' in data.lower() else None

        cur_locale = locale.getlocale(locale.LC_ALL)
        if cur_locale[0] is None or 'ru' not in cur_locale[0]:
            logger.debug('Changing locale from {}'.format(cur_locale[0]))
            if 'win' in sys.platform:
                locale.setlocale(locale.LC_ALL, 'rus_rus')
            else:
                locale.setlocale(locale.LC_ALL, 'ru_RU')
            logger.debug(locale.getlocale(locale.LC_ALL))

        if am_pm is not None:
            data = data.lower().replace(' ' + am_pm, '')
            rec_date = datetime.strptime(data, '%d-%b.-%y %I:%M:%S')
            new_hour = rec_date.hour
            if am_pm == 'am':
                new_hour = new_hour - 12 if new_hour == 12 else new_hour
            elif 'pm' == am_pm:
                new_hour = new_hour + 12

            rec_date = rec_date.replace(hour=new_hour)
        else:
            rec_date = datetime.strptime(data, '%d-%b.-%y %H:%M:%S')

        result['date'] = rec_date

    body = tree.xpath('/html/body/p[contains(text(), "SMS Text")]')
    if len(body) > 0:
        data = str(body[0].text).replace('SMS Text', '').replace(':', '', 1).strip()
        result['text'] = data
        result['is_message'] = True

    return result

