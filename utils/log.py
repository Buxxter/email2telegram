#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger()

def logger_init(logger, module_name):
    module_name = module_name if module_name is not None else __name__
    formatter = logging.Formatter('%(asctime)s - %(module)s[%(lineno)d] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    fh = logging.FileHandler('./log/{0}_log.txt'.format(module_name))
    fh.setLevel(logging.WARNING)
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)