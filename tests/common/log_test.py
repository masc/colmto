# -*- coding: utf-8 -*-
# @package tests
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of 2+1 Manoeuvres project.          #
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
"""
optom: Test module for optom.common.log.
"""
import logging

import os
import tempfile

from nose.tools import assert_equal
from nose.tools import assert_true
from nose.tools import assert_raises

import optom.common.log


def test_logger():
    """Test logger"""
    assert_equal(
        optom.common.log.LOGLEVEL,
        {
            "NOTSET": logging.NOTSET,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
    )
    f_temp_log = tempfile.NamedTemporaryFile()

    l_logs = [
        optom.common.log.logger(
            name="foo",
            logfile=f_temp_log.name,
            quiet=True,
            loglevel=logging.INFO
        ),
        optom.common.log.logger(
            name="foo",
            logfile=f_temp_log.name,
            quiet=False,
            loglevel=logging.INFO
        )
    ]

    for i_logger in l_logs:
        i_logger.info("foo")

    for i_level in optom.common.log.LOGLEVEL.iterkeys():
        l_log = optom.common.log.logger(
            name="foo{}".format(i_level),
            logfile=f_temp_log.name,
            quiet=True,
            loglevel=i_level
        )
        assert_true(
            os.path.exists(os.path.dirname(f_temp_log.name))
        )
        assert_true(
            l_log.name,
            "foo{}".format(i_level)
        )
        assert_equal(
            l_log.level,
            optom.common.log.LOGLEVEL.get(i_level)
        )
    assert_equal(
        optom.common.log.logger(
            name="bar",
            logfile=f_temp_log.name,
            quiet=True,
            loglevel="this should result in NOTSET"
        ).level,
        logging.NOTSET
    )

    with assert_raises(TypeError):
        optom.common.log.logger(
            name="bar",
            logfile=f_temp_log.name,
            quiet=True,
            loglevel=["this should fail"]
        )

    with assert_raises(TypeError):
        optom.common.log.logger(
            name="barz",
            logfile=f_temp_log.name,
            quiet="foo",
            loglevel="info"
        )
