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
"""Configuration super class."""
from __future__ import division
from __future__ import print_function

import h5py
f_destination = h5py.File("Scenarios_baseline_time_loss.hdf5", "a", libver="latest")
f_src_NWB1 = h5py.File("Scenarios_baseline_time_loss_NW-B1.hdf5","r")
f_src_HEB62 = h5py.File("Scenarios_baseline_time_loss_HE-B62.hdf5","r")
f_src_NIB210 = h5py.File("Scenarios_baseline_time_loss_NI-B210.hdf5","r")
f_src_BYB20 = h5py.File("Scenarios_baseline_time_loss_BY-B20.hdf5","r")
f_src_BYB471 = h5py.File("Scenarios_baseline_time_loss_BY-B471.hdf5","r")
f_src_HEB49 = h5py.File("Scenarios_baseline_time_loss_HE-B49.hdf5","r")
f_src_NWB1.copy(source="NW-B1", dest=f_destination)
f_src_HEB62.copy(source="HE-B62", dest=f_destination)
f_src_NIB210.copy(source="NI-B210", dest=f_destination)
f_src_HEB49.copy(source="HE-B49", dest=f_destination)
f_src_BYB471.copy(source="BY-B471", dest=f_destination)
f_src_BYB20.copy(source="BY-B20", dest=f_destination)
f_destination.close()
f_src_BYB20.close()
f_src_BYB471.close()
f_src_HEB49.close()
f_src_HEB62.close()
f_src_NIB210.close()
f_src_NWB1.close()
