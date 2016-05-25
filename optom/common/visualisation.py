# -*- coding: utf-8 -*-
# @package visualisation
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
from __future__ import print_function
from __future__ import division

import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib import rc
import log

s_log = log.logger(__name__)


def colormap(p_values, p_cmap):
    l_jet = plt.get_cmap(p_cmap)
    l_cnorm = colors.Normalize(vmin=min(p_values), vmax=max(p_values))
    return cm.ScalarMappable(norm=l_cnorm, cmap=l_jet)


def boxplot(p_filename, p_data, p_title="", p_xlabel="", p_ylabel=""):
    s_log.info("Creating boxplot %s", p_filename)
    rc("text", usetex=True)
    rc("font", **{"family": "sans-serif", "sans-serif": ["Helvetica"], "size" :10})
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