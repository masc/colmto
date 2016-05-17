# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import logging

class Logger(object):

    def __init__(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # create a file handler

        handler = logging.FileHandler('hello.log')
        handler.setLevel(logging.INFO)

        # create a logging format

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger

        logger.addHandler(handler)

        logger.info('Hello baby')