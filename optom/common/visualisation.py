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
"""Visualisation of simulation results."""
from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
from matplotlib import rc

import optom.common.log

_LOG = optom.common.log.logger(__name__)


def boxplot(p_filename, p_data, p_title="", p_xlabel="", p_ylabel=""):
    """
    Draw a boxplot of provided data and write result to file.


    :param p_filename filename with path
    :param p_data data as dictionary, key (box) -> [values]
    :param p_title figure title
    :param p_xlabel x label
    :param p_ylabel y label
    """

    _LOG.info("Creating boxplot %s", p_filename)
    rc("text", usetex=True)
    rc("font", **{"family": "sans-serif", "sans-serif": ["Helvetica"], "size": 10})
    rc("text.latex", preamble=r"\usepackage{cmbright}")
    rc("mathtext", fontset="stixsans")

    plt.figure(1)

    l_datakeys = sorted(p_data.keys())
    l_data = [p_data.get(i_key) for i_key in l_datakeys]

    plt.grid(axis='y')
    plt.title(p_title, fontsize=12)
    plt.xlabel(p_xlabel, fontsize=12)
    plt.ylabel(p_ylabel, fontsize=12)
    plt.boxplot(l_data, vert=True, notch=False, labels=l_datakeys)
    plt.savefig(p_filename, bbox_inches="tight")
    plt.close()
