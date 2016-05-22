# -*- coding: utf-8 -*-
# @package log
# @cond LICENSE
# ######################################################################################
# # LGPL License                                                                       #
# #                                                                                    #
# # This file is part of the Optimisation of Overtaking Manoeuvres (OPTOM) project.                     #
# # Copyright (c) 2016, Malte Aschermann (malte.aschermann@tu-clausthal.de)            #
# # This program is free software: you can redistribute it and/or modify               #
# # it under the terms of the GNU Lesser General Public License as                     #
# # published by the Free Software Foundation, either version 3 of the                 #
# # License, or (at your option) any later version.                                    #
# #                                                                                    #
# # This program is distributed in the hope that it will be useful,                    #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of                     #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                      #
# # GNU Lesser General Public License for more details.                                #
# #                                                                                    #
# # You should have received a copy of the GNU Lesser General Public License           #
# # along with this program. If not, see http://www.gnu.org/licenses/                  #
# ######################################################################################
# @endcond
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
