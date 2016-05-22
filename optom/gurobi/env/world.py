# @package world
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
from gurobipy import *

from optom.optov.sumo.vehicle.vehicle import Vehicle


class World(object):


    def __init__(self, p_optov,
                p_lane_start = 0,
                p_lane_end = 21,
                p_otl_start = 6,
                p_otl_end = 15):

        self._optov = p_optov

        # initial environment parameters
        self._lane_start = p_lane_start
        self._lane_end = p_lane_end
        self._otl_start = p_otl_start
        self._otl_end = p_otl_end

        # vehicle storage by id
        self._vehicles = {}

        # create a new optimization model
        self._model = Model("overtakinglane")

    def addVehicle(self, p_pos, p_desiredspeed):

        l_vid = len(self._vehicles)

        # create optimization model variables
        l_var_ds = self._model.addVar(vtype=GRB.INTEGER, name="var_ds_"+str(l_vid))

        l_var_posx = self._model.addVar(vtype=GRB.INTEGER, name="var_posx"+str(l_vid))
        l_var_posy = self._model.addVar(vtype=GRB.INTEGER, name="var_posy"+str(l_vid))

        # TODO: Create n-1 sets of (y,yt,z,zt)'s to allow the case of each vehicle overtaking every other.
        # TODO: e.g. for vehicle 3 of {1,..,5} create y1,y2,y4,y5,... zt4,zt5.
        # TODO: Add constraints that if vehicle can't overtake or it's not sensible, y > lanel length. => otl_s < y < otl_e || y > lane_len

        l_var_y = self._model.addVar(vtype=GRB.INTEGER, name="var_y"+str(l_vid))
        l_var_yt = self._model.addVar(vtype=GRB.INTEGER, name="var_yt"+str(l_vid))
        l_var_z = self._model.addVar(vtype=GRB.INTEGER, name="var_z"+str(l_vid))
        l_var_zt = self._model.addVar(vtype=GRB.INTEGER, name="var_zt"+str(l_vid))

        # create vehicles object with variables
        l_vehicle = Vehicle(p_id=l_vid, p_desiredspeed=l_var_ds, p_posx=l_var_posx, p_posy=l_var_posy,
                        p_y=l_var_y, p_yt=l_var_yt, p_z=l_var_z, p_zt=l_var_zt)

        self._model.update()
        self._model.addConstr(l_var_ds==p_desiredspeed, name="c_ds"+str(l_vid))
        self._model.update()
        for v in self._model.getVars():
            print v.varName, help(v)
        self._vehicles[l_vid] = l_vehicle

    # calculate distance needed for vehicle A to overtake vehicle B, i.e. for A to reach one cell ahead of B
    # needed_time = (pos_b - pos_a) / (v_a - v_b) => needed_distance = needed_time * v_a
    def getMinOvertakingDistance(self, p_vid_a, p_vid_b):
        l_vehicle_a = self._vehicles[p_vid_a]
        l_vehicle_b = self._vehicles[p_vid_b]
        l_var_ds_a = l_vehicle_a.getDesiredSpeed()
        l_var_ds_b = l_vehicle_b.getDesiredSpeed()






