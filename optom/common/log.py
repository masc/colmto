# -*- coding: utf-8 -*-
import logging


def logger(p_args, p_name):
    l_log = logging.getLogger(p_name)
    l_log.setLevel(p_args.loglevel)

    # create a file handler
    l_handler = logging.FileHandler(p_args.logfile)
    l_handler.setLevel(p_args.loglevel)

    # create a logging format
    l_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    l_handler.setFormatter(l_formatter)

    # add the handlers to the logger
    l_log.addHandler(l_handler)

    return l_log
