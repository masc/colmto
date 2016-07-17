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
from __future__ import print_function
import networkx
import matplotlib.pyplot as plt
from optom.common.enum import Enum
import vehicle
import random

CELL_TYPE = Enum(["FREE", "BLOCKED", "VEHICLE"])


class Cell(object):
    def __init__(self, p_position, p_state=CELL_TYPE.FREE, p_vehicle=None):
        self._position = p_position
        self._state = p_state
        self._vehicle = p_vehicle

    @property
    def position(self):
        return self._position

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, p_state):
        self._state = CELL_TYPE.VEHICLE
        return self

    @property
    def vehicle(self):
        return self._vehicle

    @vehicle.setter
    def vehicle(self, p_vehicle):
        if self._state == CELL_TYPE.FREE:
            self._state = CELL_TYPE.VEHICLE
            self._vehicle = p_vehicle
        else:
            print("Crash into ", __name__, self._state)
        return self


class Environment(object):
    def __init__(self):
        self._grid = [[Cell((x, 0)), Cell((x, 1), CELL_TYPE.BLOCKED)] for x in xrange(10)] \
                   + [[Cell((x, 0)), Cell((x, 1))] for x in xrange(10, 20)] \
                   + [[Cell((x, 0)), Cell((x, 1), CELL_TYPE.BLOCKED)] for x in xrange(20, 30)]
        self._graph = networkx.DiGraph()
        for i_cells in self.grid:
            l_xcell = i_cells[0]
            l_ycell = i_cells[1]
            self.graph.add_node(l_xcell, position=l_xcell.position)
            self.graph.add_node(l_ycell, position=l_ycell.position)
        self._vehicles = {}
        print(self.graph)
        self.connect_cells()

    @property
    def graph(self):
        return self._graph

    @property
    def grid(self):
        return self._grid

    @property
    def vehicles(self):
        return self._vehicles

    @property
    def vehicle(self, p_vid):
        return self._vehicles.get(p_vid)

    def isfree(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.FREE

    def isvehicle(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.VEHICLE

    def isblocked(self, p_position):
        return self._grid[p_position[0]][p_position[1]].state == CELL_TYPE.BLOCKED

    def connect_cells(self):
        print("connecting cells")
        l_pos = {}
        for x in xrange(len(self.grid)):
            for y in xrange(len(self.grid[x])):

                if x < len(self.grid)-1 and self.grid[x][y].state != CELL_TYPE.BLOCKED \
                        and self.grid[x+1][y].state != CELL_TYPE.BLOCKED:

                    # Join 1-neighbouring cells in driving direction
                    self.graph.add_weighted_edges_from(
                        [
                            (self.grid[x][y], self.grid[x+1][y], random.randint(1, 5))
                        ]
                    )

                if y < len(self.grid[x])-1 \
                        and self.grid[x][y].state != CELL_TYPE.BLOCKED \
                        and self.grid[x][y+1].state != CELL_TYPE.BLOCKED:

                    # Join 1-neighbouring cells in lane-change direction (perpendicular to driving direction)
                    self.graph.add_weighted_edges_from(
                        [
                            (self.grid[x][y], self.grid[x][y+1], 1),
                            (self.grid[x][y+1], self.grid[x][y], 1)
                        ]
                    )

                l_pos[self.grid[x][y]] = self.grid[x][y].position

        networkx.draw_networkx_edges(self.graph,l_pos,width=1.0,alpha=0.5, edge_color="b")
        for node in networkx.astar_path(self.graph, self.grid[0][0], self.grid[29][0]):
            print(node.position)

        networkx.draw(self.graph, pos=l_pos, node_size=16, alpha=0.4, edge_color="r")
        plt.show()

    def add_vehicle(self, p_vehicle_id, p_position):
        if self.isfree(p_position) and p_vehicle_id not in self.vehicles:
            self.vehicles[p_vehicle_id] = vehicle.Vehicle(id=p_vehicle_id,
                                                          environment=self,
                                                          position=p_position
                                                          )
        return self

    def vehicles_on_edge(self, p_edgeid):
        return filter(
            lambda v: v.get("edgeid") == p_edgeid,
            self._vehicles.items()
        )

