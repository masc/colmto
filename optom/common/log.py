# -*- coding: utf-8 -*-
# @package optom
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of Overtaking Manoeuvres project.   #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
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


def logger(p_name, p_loglevel=logging.NOTSET, p_quiet=False,
           p_logfile=os.path.expanduser(u"~/.optom/optom.log")):
    """Create a logger instance."""

    if not os.path.exists(os.path.dirname(p_logfile)):
        os.makedirs(os.path.dirname(p_logfile))

    l_log = logging.getLogger(p_name)
    if isinstance(p_loglevel, int):
        l_level = p_loglevel
    elif isinstance(p_loglevel, str):
        l_level = LOGLEVEL.get(str(p_loglevel).upper()) \
            if LOGLEVEL.get(str(p_loglevel).upper()) is not None else logging.NOTSET
    else:
        l_level = logging.NOTSET

    l_log.setLevel(l_level if l_level is not None else logging.NOTSET)

    # create a file handler
    l_fhandler = logging.handlers.RotatingFileHandler(
        p_logfile, maxBytes=100*1024*1024, backupCount=16
    )
    l_fhandler.setLevel(l_level if l_level is not None else logging.NOTSET)

    # create a logging format
    l_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    l_fhandler.setFormatter(l_formatter)

    # add the handlers to the logger
    l_log.addHandler(l_fhandler)

    # create a stdout handler if not set to quiet
    if not p_quiet:
        l_shandler = logging.StreamHandler(sys.stdout)
        l_shandler.setLevel(l_level)
        l_shandler.setFormatter(l_formatter)
        l_log.addHandler(l_shandler)

    return l_log
