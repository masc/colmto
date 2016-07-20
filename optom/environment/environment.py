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

import random
from collections import defaultdict
import itertools

import matplotlib.pyplot as plt
import networkx

import vehicle


class Grid(object):
    def __init__(self):
        """
        Construct a time/space-grid for 3-tuples (x,y,t) -> Occupied,
        with x: {0, ... n} position on lane, y: {0,1} main lane/otl lane, t: {0, ..., T} time step as a defaultdict.
        :return: Returns None if position not occupied, i.e. free, GridElement object otherwise
        """
        self._grid = defaultdict(itertools.repeat(None).next)

    def cell(self, pos):
        if len(pos) != 3:
            raise AssertionError
        return self._grid[pos]

    def put(self, obj, pos):
        if type(obj) is not GridElement:
            raise TypeError
        if len(pos) != 3:
            raise AssertionError
        self._grid[pos] = obj

    def pop(self, pos):
        if len(pos) != 3:
            raise AssertionError
        return self._grid.pop(pos)

    def move(self, pos_from, pos_to):
        if self.cell(pos_from) is not GridElement:
            raise AssertionError
        if self.cell(pos_to) is not None:
            raise AssertionError
        self.put(self.pop(pos_from), pos_to)


class GridElement(object):
    def __init__(self, **p_kwargs):
        if p_kwargs:
            raise TypeError('Unexpected **p_kwargs: %r' % p_kwargs)


class Wall(GridElement):
    def __init__(self, **p_kwargs):
        super(GridElement, self).__init__(p_kwargs)
        if p_kwargs:
            raise TypeError('Unexpected **p_kwargs: %r' % p_kwargs)


class Environment(object):
    def __init__(self, **p_kwargs):
        self._length = p_kwargs.pop("length", (30,))
        self._otl_split_pos = p_kwargs.pop("otl_split_pos", (10,))
        self._otl_join_pos = p_kwargs.pop("otl_join_pos", (20,))
        self._grid = Grid()
        self._graph = self._create_graph()
        self._vehicles = {}

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
        return self._grid.cell(p_position) is None

    def isvehicle(self, p_position):
        return type(self._grid.cell(p_position)) is vehicle.Vehicle

    def isblocked(self, p_position):
        return type(self._grid.cell(p_position)) is Wall

    def _create_graph(self):
        print("Creating DiGraph")
        l_graph = networkx.DiGraph()
        l_graph.add_node("start")
        l_graph.add_node("end")
        l_start_times = [1, 2, 3]
        l_length = 10000

        for i_start_time in l_start_times:

            i_pos_t = i_start_time
            i_pos_x = 1

            # connect start node with node representing pos_x=0 for given start_time
            l_graph.add_edge(
                u="start",
                v=(i_pos_x, 0, i_pos_t),
                attr_dict={
                    "1": 1,
                    "2": 1,
                    "3": 1
                }
            )
            l_velocity = 1

            while i_pos_x < l_length:
                i_pos_x_new = i_pos_x + l_velocity
                l_graph.add_edge(
                    u=(i_pos_x, 0, i_pos_t),
                    v=(i_pos_x_new, 0, i_pos_t+1),
                    attr_dict={
                        "1": 1,
                        "2": 1,
                        "3": 1
                    }
                )
                i_pos_x = i_pos_x_new
                i_pos_t += 1

            # connect to end node
            l_graph.add_edge(
                u=(i_pos_x, 0, i_pos_t),
                v="end",
                attr_dict={
                    "1": 1,
                    "2": 1,
                    "3": 1
                }
            )

            i_pos_t = i_start_time
            i_pos_x = 1
            l_velocity = 2

            while i_pos_x < l_length:
                i_pos_x_new = i_pos_x + l_velocity
                l_graph.add_edge(
                    u=(i_pos_x, 0, i_pos_t),
                    v=(i_pos_x_new, 0, i_pos_t+1),
                    attr_dict={
                        "1": 10**9,
                        "2": 1,
                        "3": 1
                    }
                )
                i_pos_x = i_pos_x_new
                i_pos_t += 1

            # connect to end node
            l_graph.add_edge(
                u=(i_pos_x, 0, i_pos_t),
                v="end",
                attr_dict={
                    "1": 10**9,
                    "2": 1,
                    "3": 1
                }
            )

            i_pos_t = i_start_time
            i_pos_x = 1
            l_velocity = 3

            while i_pos_x < l_length:
                i_pos_x_new = i_pos_x + l_velocity
                l_graph.add_edge(
                    u=(i_pos_x, 0, i_pos_t),
                    v=(i_pos_x_new, 0, i_pos_t+1),
                    attr_dict={
                        "1": 10**9,
                        "2": 10**9,
                        "3": 1
                    }
                )
                i_pos_x = i_pos_x_new
                i_pos_t += 1

            l_graph.add_edge(
                u=(i_pos_x, 0, i_pos_t),
                v="end",
                attr_dict={
                    "1": 10**9,
                    "2": 10**9,
                    "3": 1
                }
            )

        print("edges:", l_graph.number_of_edges(), "nodes:", l_graph.number_of_nodes())
        for i_speed in xrange(1,4):
            l_path = networkx.shortest_path(l_graph, (1, 0, 1), "end", weight=str(i_speed))
            print("shortest path for speed", i_speed, ":", "len", len(l_path))
        return l_graph

    # def _connect_cells(self):
    #     print("connecting cells")
    #     l_pos = {}
    #     for x in xrange(len(self.grid)):
    #         for y in xrange(len(self.grid[x])):
    #
    #             if x < len(self.grid)-1 and self.grid[x][y].state != CELL_TYPE.BLOCKED \
    #                     and self.grid[x+1][y].state != CELL_TYPE.BLOCKED:
    #
    #                 # Join 1-neighbouring cells in driving direction
    #                 self.graph.add_weighted_edges_from(
    #                     [
    #                         (self.grid[x][y], self.grid[x+1][y], random.randint(1, 5))
    #                     ]
    #                 )
    #
    #             if y < len(self.grid[x])-1 \
    #                     and self.grid[x][y].state != CELL_TYPE.BLOCKED \
    #                     and self.grid[x][y+1].state != CELL_TYPE.BLOCKED:
    #
    #                 # Join 1-neighbouring cells in lane-change direction (perpendicular to driving direction)
    #                 self.graph.add_weighted_edges_from(
    #                     [
    #                         (self.grid[x][y], self.grid[x][y+1], 1),
    #                         (self.grid[x][y+1], self.grid[x][y], 1)
    #                     ]
    #                 )
    #
    #             l_pos[self.grid[x][y]] = self.grid[x][y].position
    #
    #     networkx.draw_networkx_edges(self.graph,l_pos,width=1.0,alpha=0.5, edge_color="b")
    #     for node in networkx.astar_path(self.graph, self.grid[0][0], self.grid[29][0]):
    #         print(node.position)
    #
    #     networkx.draw(self.graph, pos=l_pos, node_size=16, alpha=0.4, edge_color="r")
    #     plt.show()

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

