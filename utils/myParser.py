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

from lxml import etree as ET
from io import StringIO, BytesIO
import quopri

def get_body(mail_body):
    result = dict.fromkeys(['type', 'date', 'sender', 'text'])

    tree = ET.parse(StringIO(mail_body), ET.HTMLParser())
    body = tree.xpath('/html/body/p[contains(text(), "Incoming") and contains(text(), "SMS")]')
    result['type'] = 'SMS' if len(body) == 1 else 'Missed Call'

    body = tree.xpath('/html/body/p[contains(text(), "Received From")]')
    if len(body) > 0:
        sender = str(body[0].text).replace('Received From', '').replace(':', '', 1).lstrip()
        result['sender'] = quopri.decodestring(sender)

    body = tree.xpath('/html/body/p[contains(text(), "Received On")]')
    if len(body) > 0:
        sender = str(body[0].text).replace('Received On', '').replace(':', '', 1).lstrip()
        result['date'] = quopri.decodestring(sender)

    body = tree.xpath('/html/body/p[contains(text(), "SMS Text")]')
    if len(body) > 0:
        sender = str(body[0].text).replace('SMS Text', '').replace(':', '', 1).lstrip()
        result['text'] = quopri.decodestring(sender)

    print(result)

