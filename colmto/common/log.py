# -*- coding: utf-8 -*-
# @package tests
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Cooperative Lane Management and Traffic flow     #
# # Optimisation project.                                                     #
# # Copyright (c) 2017, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
# # This program is free software: you can redistribute it and/or modify      #
# # it under the terms of the GNU Lesser General Public License as            #
# # published by the Free Software Foundation, either version 3 of the        #
# # License, or (at your option) any later version.                           #
# #                                                                           #
# # This program is distributed in the hope that it will be useful,           #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# # GNU Lesser General Public License for more details.                       #
# #                                                                           #
# # You should have received a copy of the GNU Lesser General Public License  #
# # along with this program. If not, see http://www.gnu.org/licenses/         #
# #############################################################################
# @endcond
"""Logging module"""
import logging
import logging.handlers
import os
import sys

LOGLEVEL = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET
}


def logger(name, loglevel=logging.NOTSET, quiet=False,
           logfile=os.path.expanduser(u"~/.colmto/colmto.log")):
    """Create a logger instance."""

    if os.path.dirname(logfile) != "" and not os.path.exists(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))  # pragma: no cover

    l_log = logging.getLogger(name)
    if isinstance(loglevel, int):
        l_level = loglevel
    elif isinstance(loglevel, str):
        l_level = LOGLEVEL.get(str(loglevel).upper()) \
            if LOGLEVEL.get(str(loglevel).upper()) is not None else logging.NOTSET
    else:
        raise TypeError("loglevel argument {} is not a valid logging log level.".format(loglevel))

    l_log.setLevel(l_level if l_level is not None else logging.NOTSET)

    # create a logging format
    l_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create a file/stream handler if not already done
    l_add_fhandler = True
    l_add_qhandler = True
    for i_handler in l_log.handlers:
        if isinstance(i_handler, logging.handlers.RotatingFileHandler):
            i_handler.setLevel(l_level if l_level is not None else logging.NOTSET)
            i_handler.setFormatter(l_formatter)
            l_add_fhandler = False
        if isinstance(i_handler, logging.StreamHandler):
            i_handler.setLevel(l_level)
            i_handler.setFormatter(l_formatter)
            l_add_qhandler = False

    if l_add_fhandler:
        l_fhandler = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=100 * 1024 * 1024, backupCount=16
        )
        l_fhandler.setLevel(l_level if l_level is not None else logging.NOTSET)
        l_fhandler.setFormatter(l_formatter)

        # add the handlers to the logger
        l_log.addHandler(l_fhandler)

    if l_add_qhandler:
        # create a stdout handler if not set to quiet
        if not isinstance(quiet, bool):
            raise TypeError("quiet ({}) is {}, but bool expected.".format(quiet, type(quiet)))

        if not quiet:
            l_shandler = logging.StreamHandler(sys.stdout)
            l_shandler.setLevel(l_level)
            l_shandler.setFormatter(l_formatter)
            l_log.addHandler(l_shandler)

    return l_log
