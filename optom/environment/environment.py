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

import time
import math
from collections import defaultdict
import itertools

import matplotlib.pyplot as plt
import networkx
from networkx.readwrite import graphml, nx_yaml, json_graph
import optom.common.io

from progressbar import Percentage, Bar, Counter, ProgressBar, AdaptiveETA, Timer
import os

import vehicle


class Grid(object):
    def __init__(self, p_dimension=(64,2), p_blocked_ranges=(((i,0) for i in xrange(0,16)), ((i,0) for i in xrange(48,64)))):
        """
        Construct a time/space-grid for 3-tuples (x,y,t) -> Occupied,
        with x: {0, ... n} position on lane, y: {0,1} main lane/otl lane, t: {0, ..., T} time step as a defaultdict.
        :return: Returns None if position not occupied, i.e. free, GridElement object otherwise
        """
        self._grid = defaultdict(itertools.repeat(None).next)
        for i_blocked_range in p_blocked_ranges:
            for i_block in i_blocked_range:
                self._grid[i_block] = Wall()
        print(self._grid)

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
        super(GridElement, self).__init__()
        if p_kwargs:
            raise TypeError('Unexpected **p_kwargs: %r' % p_kwargs)


class Environment(object):
    def __init__(self, p_configuration, **p_kwargs):
        self._writer = optom.common.io.Writer(p_configuration.args)
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

    def vehicle(self, p_vid):
        return self._vehicles.get(p_vid)

    def isfree(self, p_position):
        return self._grid.cell(p_position) is None

    def isvehicle(self, p_position):
        return type(self._grid.cell(p_position)) is vehicle.Vehicle

    def isblocked(self, p_position):
        return type(self._grid.cell(p_position)) is Wall

    @staticmethod
    def _add_links(p_graph, p_node, p_velocities, p_length):

        for i_velocity in p_velocities:
            l_x, l_y, l_t = p_node
            l_destination = (l_x+i_velocity, 0, l_t+1)
            if not p_graph.has_edge(p_node,l_destination):
                l_attr_dict = dict(
                    (
                        (str(s), 10**12 if i_velocity > s else 1) for s in p_velocities
                    )
                )
                if l_x+i_velocity <= p_length:
                    p_graph.add_edge(
                        u=p_node,
                        v=l_destination,
                        attr_dict=l_attr_dict
                    )
                elif l_x == p_length:
                    l_attr_dict = dict(
                        (
                            (str(s), 1) for s in p_velocities
                        )
                    )
                    p_graph.add_edge(
                        u=p_node,
                        v="end",
                        attr_dict=l_attr_dict
                    )
                else:
                    p_graph.add_edge(
                        u=p_node,
                        v="end",
                        attr_dict=l_attr_dict
                    )

    def _write_graph(self, p_graph, p_velocities, p_start_times, p_length):
        # print("writing graphml")
        # t_start = time.time()
        # graphml.write_graphml(
        #     p_graph,
        #     "{}{}-v{}-st{}-len{}.graphml".format(
        #         os.path.expanduser(u"~/.optom"), "/cse", len(p_velocities), len(p_start_times), p_length
        #     )
        # )
        # print("graphml writing took", time.time()-t_start)
        # print("writing yaml")
        # t_start = time.time()
        # nx_yaml.write_yaml(
        #     p_graph,
        #     "{}{}-v{}-st{}-len{}.yaml".format(
        #         os.path.expanduser(u"~/.optom"), "/cse", len(p_velocities), len(p_start_times), p_length
        #     )
        # )
        # print("yaml writing took", time.time()-t_start)
        print("writing json adjacency_data via", optom.common.io.Writer)
        t_start = time.time()
        l_json = json_graph.adjacency_data(p_graph)

        self._writer.write_json(
            l_json,
            "{}{}-v{}-st{}-len{}.adj.json.gz".format(
                os.path.expanduser(u"~/.optom"), "/cse", len(p_velocities), len(p_start_times), p_length
            )
        )
        print("json adjacency_data writing took", time.time()-t_start)
        print("writing json node_link_data via", optom.common.io.Writer)
        t_start = time.time()
        l_json = json_graph.node_link_data(p_graph)

        self._writer.write_json(
            l_json,
            "{}{}-v{}-st{}-len{}.nodelink.json.gz".format(
                os.path.expanduser(u"~/.optom"), "/cse", len(p_velocities), len(p_start_times), p_length
            )
        )
        print("json node_link_data writing took", time.time()-t_start)



    @staticmethod
    def _draw_graph(p_graph, p_velocities, p_start_times, p_length):
        print("drawing graph")
        t_start = time.time()
        l_node_positions = dict(
            (
                (node, node[0::2] if node != "end" else (p_length+1, 10)) for node in p_graph.nodes()
            )
        )

        networkx.draw_networkx_nodes(p_graph,
                                     pos=l_node_positions,
                                     node_size=2,
                                     alpha=1.0
                                     )

        networkx.draw_networkx_edges(p_graph,
                                     l_node_positions,
                                     edgelist=p_graph.edges(),
                                     width=1,
                                     alpha=0.5,
                                     edge_color="gray"
                                     )
        print("drawing took", time.time()-t_start)
        l_path_colors = ["red", "green", "blue", "purple", "orange"] * int(math.ceil(len(p_start_times)/5+1))

        l_paths = []

        for i_start_time in p_start_times:
            t_start = time.time()
            l_path = networkx.astar_path(
                p_graph,
                (0, 0, i_start_time),
                "end",
                weight=str(
                    p_velocities[i_start_time % len(p_velocities)]
                )
            )
            print(
                (0, 0, i_start_time),
                "->",
                "end",
                time.time()-t_start
            )
            l_edges = map(lambda v1, v2: (v1, v2), l_path[:-1], l_path[1:])
            l_paths.append(l_edges)
            networkx.draw_networkx_edges(
                p_graph, l_node_positions, edgelist=l_edges, width=2, alpha=1.0, edge_color=l_path_colors[i_start_time]
            )

        plt.show()

    def _create_graph(self, p_start_times=xrange(20), p_velocities=(1, 2, 3, 4, 5), p_length=512):

        l_pbar_widgets = [
            "Generating Search Space Graph: ",
            Counter(),
            "/",
            str(p_length-1),
            " (", Percentage(), ")",
            Bar(),
            " ",
            AdaptiveETA(),
            " | ",
            Timer()
        ]
        l_length_pbar = ProgressBar(
            widgets=l_pbar_widgets,
            maxval=p_length-1,
        )
        l_length_pbar.start()

        l_graph = networkx.DiGraph()
        l_graph.add_node("end")

        t_start = time.time()
        for i_x in range(p_length):

            for i_start_time in p_start_times:
                l_node = (i_x, 0, i_x+i_start_time)
                l_graph.add_node(l_node)

            # add links to nodes
            for i_nb, i_node in enumerate(l_graph.nodes()):
                if type(i_node) is tuple:
                    self._add_links(l_graph, i_node, p_velocities, p_length)

            l_length_pbar.update(i_x)

        print()
        print("graph gen took", time.time()-t_start)

        self._write_graph(l_graph, p_velocities, p_start_times, p_length)

        return l_graph

    # def _create_graph(self, p_start_times=[0, 1, 2], p_velocities=[1, 2, 3], p_length=12):
    #     print("Creating DiGraph")
    #     l_graph = networkx.DiGraph()
    #     l_graph.add_node("end")
    #
    #     for i_start_time in p_start_times:
    #
    #         for i_velocity in p_velocities:
    #
    #             i_pos_t = i_start_time
    #             i_pos_x = 0
    #             l_attr_dict = dict(
    #                 (
    #                     (str(s), 10**9 if i_velocity > s else 1) for s in p_velocities
    #                 )
    #             )
    #
    #             while i_pos_x < p_length:
    #                 i_pos_x_new = i_pos_x + i_velocity
    #                 l_graph.add_edge(
    #                     u=(i_pos_x, 0, i_pos_t),
    #                     v=(i_pos_x_new, 0, i_pos_t+1),
    #                     attr_dict=l_attr_dict
    #                 )
    #                 i_pos_x = i_pos_x_new
    #                 i_pos_t += 1
    #
    #             # connect to end node
    #             l_graph.add_edge(
    #                 u=(i_pos_x, 0, i_pos_t),
    #                 v="end",
    #                 attr_dict=l_attr_dict
    #             )
    #
    #     print("edges:", l_graph.number_of_edges(), "nodes:", l_graph.number_of_nodes())
    #
    #     l_paths = []
    #     l_pos = dict(
    #         ((node, node[0::2] if node != "end" else (30, 10)) for node in l_graph.nodes())
    #     )
    #
    #     networkx.draw_networkx_nodes(l_graph, pos=l_pos, node_size=12, alpha=0.5)
    #     networkx.draw_networkx_edges(l_graph, l_pos, edgelist=l_graph.edges(), width=1, alpha=0.5, edge_color="gray")
    #
    #     for i_speed in p_velocities:
    #         t_now = time.time()
    #         l_path = networkx.astar_path(l_graph, (0, 0, i_speed-1), "end", weight=str(i_speed))
    #         l_edges = map(lambda v1, v2: (v1, v2), l_path[:-1], l_path[1:])
    #         l_paths.append(
    #             l_edges
    #         )
    #         t_duration = time.time() - t_now
    #         print("shortest path for speed", i_speed, ":", "paths", list(l_path), "duration", t_duration)
    #         networkx.draw_networkx_edges(l_graph, l_pos, edgelist=l_edges, width=1, alpha=0.5, edge_color="r")
    #
    #     # networkx.draw_networkx_edges(l_graph, pos=l_pos, width=.5, alpha=0.5, edge_color="b")
    #
    #     plt.show()
    #
    #     return l_graph

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

