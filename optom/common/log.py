# -*- coding: utf-8 -*-
import logging
import logging.handlers

s_loglevel = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET
}


def logger(p_args, p_name):
    l_log = logging.getLogger(p_name)
    l_level = s_loglevel.get(p_args.loglevel.upper())
    l_log.setLevel(l_level if l_level is not None else logging.NOTSET)

    # create a file handler
    l_handler = logging.handlers.RotatingFileHandler(p_args.logfile, maxBytes=100*1024*1024, backupCount=16)
    l_handler.setLevel(l_level if l_level is not None else logging.NOTSET)

    # create a logging format
    l_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    l_handler.setFormatter(l_formatter)

    # add the handlers to the logger
    l_log.addHandler(l_handler)

    return l_log
