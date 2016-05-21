# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib import rc


def colormap(p_values, p_cmap):
    l_jet = plt.get_cmap(p_cmap)
    l_cnorm = colors.Normalize(vmin=min(p_values), vmax=max(p_values))
    return cm.ScalarMappable(norm=l_cnorm, cmap=l_jet)


def boxplot(p_filename, p_data, p_title="", p_xlabel="", p_ylabel=""):
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