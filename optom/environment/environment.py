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

import itertools
import math
import os
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx
from networkx.readwrite import json_graph
from progressbar import Percentage, Bar, Counter, ProgressBar, AdaptiveETA, Timer
import numpy as np

import optom.common.io
import optom.common.log
import vehicle


class Grid(object):
    def __init__(self,
                 p_dimension=(64, 2),
                 p_blocked_ranges=(((i, 0) for i in xrange(0, 16)), ((i, 0) for i in xrange(48, 64)))):
        """
        Construct a time/space-grid for 3-tuples (x,y,t) -> Occupied,
        with x: {0, ... n} position on lane, y: {0,1} main lane/otl lane, t: {0, ..., T} time step as a defaultdict.
        :return: Returns None if position not occupied, i.e. free, GridElement object otherwise
        """
        self._grid = defaultdict(itertools.repeat(None).next)
        for i_blocked_range in p_blocked_ranges:
            for i_block in i_blocked_range:
                self._grid[i_block] = Wall()

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
        l_cell = self._grid.cell(pos)
        self._grid[pos] = None
        return l_cell

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
        self._log = optom.common.log.logger(
            __name__,
            p_configuration.args.loglevel,
            p_configuration.args.quiet,
            p_configuration.args.logfile
        )
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
    def _add_links(p_graph, p_node, p_velocities, p_length, p_otl):
        for i_velocity in p_velocities:
            l_x, l_y, l_t = p_node
            l_destination_mainlane = (l_x+i_velocity, 0, l_t+1)
            l_destination_otl = (l_x+i_velocity, 1, l_t+1)

            # edge weights for A* routing:
            # each key corresponds to a vehicle's maximum velocity
            l_attr_dict = dict(
                (
                    (str(s), 10**12 if i_velocity > s else 1) for s in p_velocities
                )
            )
            l_attr_dict["label"] = ", ".join(filter(lambda k: l_attr_dict[k] < 10**12, l_attr_dict.iterkeys()))
            if not p_graph.has_edge(p_node, l_destination_mainlane) and l_y == 0:

                if l_x+i_velocity < p_length:
                    p_graph.add_edge(
                        u=p_node,
                        v=l_destination_mainlane,
                        attr_dict=l_attr_dict
                    )
                elif l_x+i_velocity == p_length:
                    l_attr_dict["color"] = "gray"
                    p_graph.add_edge(
                        u=p_node,
                        v="end",
                        attr_dict=l_attr_dict
                    )
                elif l_x == p_length-1:
                    l_attr_dict = dict(
                        (
                            (str(s), 1) for s in p_velocities
                        )
                    )
                    l_attr_dict["label"] = ", ".join(filter(lambda k: l_attr_dict[k] < 10**12, l_attr_dict.iterkeys()))
                    l_attr_dict["color"] = "gray"
                    p_graph.add_edge(
                        u=p_node,
                        v="end",
                        attr_dict=l_attr_dict
                    )

                # main lane -> otl connections
                # strategy: pulling out later is more expensive
                if p_otl[0] <= l_x < p_otl[1]:
                    l_attr_dict = dict(
                        (
                            (str(s), 0) for s in p_velocities
                        )
                    )
                    l_attr_dict["label"] = ", ".join(filter(lambda k: l_attr_dict[k] < 10**12, l_attr_dict.iterkeys()))
                    l_attr_dict["style"] = "tapered"
                    l_attr_dict["color"] = "gray"
                    p_graph.add_edge(
                        u=(l_x, 0, l_t),
                        v=(l_x, 1, l_t),
                        attr_dict=l_attr_dict
                    )

            # OTL connections
            if not p_graph.has_edge(p_node, l_destination_otl) and l_y == 1:
                if l_x+i_velocity <= p_otl[1]:
                    l_attr_dict = dict(
                        (
                            (str(s), 10**12 if i_velocity > s else 1) for s in p_velocities
                        )
                    )
                    l_attr_dict["label"] = ", ".join(filter(lambda k: l_attr_dict[k] < 10**12, l_attr_dict.iterkeys()))
                    p_graph.add_edge(
                        u=p_node,
                        v=l_destination_otl,
                        attr_dict=l_attr_dict
                    )

                    # otl -> main lane connections
                    l_attr_dict = dict(
                        (
                            (str(s), 0) for s in p_velocities
                        )
                    )
                    l_attr_dict["label"] = ", ".join(filter(lambda k: l_attr_dict[k] < 10**12, l_attr_dict.iterkeys()))
                    l_attr_dict["style"] = "tapered"
                    l_attr_dict["color"] = "gray"
                    p_graph.add_edge(
                        u=l_destination_otl,
                        v=l_destination_mainlane,
                        attr_dict=l_attr_dict
                    )

    def _write_graph(self, p_graph, p_velocities, p_start_times, p_length):
        self._log.info("writing json adjacency_data via {}".format(optom.common.io.Writer))
        t_start = time.time()
        l_json = json_graph.adjacency_data(p_graph)

        self._writer.write_json_pretty(
            l_json,
            "{}{}-v{}-st{}-len{}.adj.json".format(
                os.path.expanduser(u"~/.optom"), "/cse", len(p_velocities), len(p_start_times), p_length
            )
        )
        self._log.info("json adjacency_data writing took {} seconds".format(round(time.time()-t_start, 1)))

    @staticmethod
    def __position_node(p_node, p_length, p_factor=100):
        if p_node[1] == 0:
            return "{},{}".format(
                p_factor * p_node[0],
                p_factor * p_node[2]
            )
        elif p_node[1] == 1:
            return "{},{}".format(
                p_factor * (p_node[0] + 0.5),
                p_factor * (p_node[2] - p_length/1.2)
            )
        elif p_node == "end":
            return "{},{}".format(
                p_factor * 1.2 * p_length,
                p_factor * p_length
            )
        else:
            return "0,0"

    @staticmethod
    def __edges_cross(p_edge_p, p_edge_q):
        p = np.array(p_edge_p[0][0::2], dtype=float)
        q = np.array(p_edge_q[0][0::2], dtype=float)
        r = np.array(p_edge_p[1][0::2], dtype=float) - p
        s = np.array(p_edge_q[1][0::2], dtype=float) - q
        rxs = np.cross(r, s)
        q_p = np.subtract(q, p)
        q_pxr = np.cross(q_p, r)
        if rxs == 0.0 and q_pxr == 0.0:
            # p_edge_p and p_edge_q are collinear
            return False

        if rxs == 0.0 and q_pxr != 0.0:
            # p_edge_p and p_edge_q are parallel and non-intersecting
            return False

        if rxs != 0.0:
            t = np.divide(
                np.cross(q_p, s),
                rxs
            )
            u = np.divide(
                q_pxr,
                rxs
            )
            if 0 <= t <= 1 and 0 <= u <= 1:
                # p_edge_p and p_edge_q intersect
                return True

            # p_edge_p and p_edge_q are not parallel but do not intersect
            return False

        return False

    @staticmethod
    def _block_nodes(p_graph, p_edges, p_path, p_velocities, p_length):
        l_attr_dict = dict(
            (
                (str(s), 10**12) for s in p_velocities
            )
        )
        l_attr_dict["label"] = ", ".join(filter(lambda k: l_attr_dict[k] < 10**12, l_attr_dict.iterkeys()))
        l_attr_dict["style"] = "invis" if ", ".join(filter(lambda k: l_attr_dict[k] < 10**12, l_attr_dict.iterkeys())) == "" else ""
        for i_edge in p_edges:
            for i_from in p_graph.predecessors(i_edge[0]):
                if i_from not in p_path:
                    # p_graph.edge[i_from][i_edge[0]].update(l_attr_dict)
                    p_graph.remove_edge(i_from, i_edge[0])
            # for i_from in p_graph.predecessors_iter(i_edge[1]):
            #     p_graph.edge[i_from][i_edge[1]].update(l_attr_dict)
            # for i_to in p_graph.successors_iter(i_edge[0]):
            #     p_graph.edge[i_edge[0]][i_to].update(l_attr_dict)
            # for i_to in p_graph.successors_iter(i_edge[1]):
            #     p_graph.edge[i_edge[1]][i_to].update(l_attr_dict)

            for i_x in xrange(p_length):
                l_neighbour_node = (i_x, i_edge[0][1], i_edge[0][2])
                if p_graph.has_node(l_neighbour_node):
                    for i_neighbour_node_successor in p_graph.successors(l_neighbour_node):
                        if i_neighbour_node_successor != "end" != i_edge[1] and Environment.__edges_cross((l_neighbour_node, i_neighbour_node_successor), i_edge):
                            # p_graph.edge[l_neighbour_node][i_neighbour_node_successor].update(l_attr_dict)
                            p_graph.remove_edge(l_neighbour_node, i_neighbour_node_successor)

    def _draw_graph(self, p_graph, p_velocities, p_start_times, p_length):
        self._log.info("drawing graph")
        t_start = time.time()

        # test some routes
        l_path_colors = ["red", "green", "blue", "purple", "orange"] * int(math.ceil(len(p_start_times)/5+1))
        l_paths = []
        l_vehicle_velocities = (1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4)
        for i_start_time in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11):
            t_start = time.time()
            l_path = networkx.astar_path(
                p_graph,
                (0, 0, i_start_time),
                "end",
                weight=str(
                    l_vehicle_velocities[i_start_time]
                )
            )
            l_edges = map(lambda v1, v2: (v1, v2), l_path[:-1], l_path[1:])

            for i_edge in l_edges:
                l_from, l_to = i_edge
                p_graph.edge[l_from][l_to]["color"] = l_path_colors[i_start_time]
                p_graph.edge[l_from][l_to]["style"] = "bold"
                p_graph.edge[l_from][l_to]["penwidth"] = 10
                p_graph.edge[l_from][l_to]["arrowsize"] = 0.75
                p_graph.node[l_from]["fillcolor"] = l_path_colors[i_start_time]
                p_graph.node[l_from]["style"] = "filled"

            self._block_nodes(p_graph, l_edges, l_path, p_velocities, p_length)

            self._log.info(
                "{} -> {}: {} seconds".format(
                    (0, 0, i_start_time),
                    "end",
                    round(time.time()-t_start, 1)
                )
            )
            l_paths.append(l_edges)

            l_agraph = networkx.nx_agraph.to_agraph(p_graph)
            l_fname = "{}{}-v{}-st{}-len{}-vehicle{}.jpg".format(
                os.path.expanduser(u"~/.optom"), "/cse", len(p_velocities), len(p_start_times), p_length, i_start_time if i_start_time >= 10 else "0"+str(i_start_time)
            )
            #l_agraph.draw("test.pdf", prog='neato', args='-n2')
            l_agraph.draw(l_fname, prog='neato', args='-n2')
        self._log.info("drawing took {} seconds".format(round(time.time()-t_start, 1)))

    def _create_graph(self, p_start_times=xrange(12), p_velocities=xrange(1, 5), p_length=30, p_otl=(5, 25)):
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
        l_pbar = ProgressBar(
            widgets=l_pbar_widgets,
            maxval=p_length-1,
        )
        l_pbar.start()

        l_graph = networkx.DiGraph()
        l_graph.add_node("end")

        t_start = time.time()
        for i_x in xrange(p_length):

            for i_start_time in p_start_times:
                # right lane
                l_graph.add_node(
                    (i_x, 0, i_x + i_start_time),
                )
                # overtaking lane
                if p_otl[0] <= i_x <= p_otl[1]:
                    l_graph.add_node(
                        (i_x, 1, i_x + i_start_time),
                    )

            # add links to nodes
            for i_nb, i_node in enumerate(l_graph.nodes()):
                if type(i_node) is tuple:
                    self._add_links(l_graph, i_node, p_velocities, p_length, p_otl)

            l_pbar.update(i_x)

        # one last round to fix missing links and set position attributes
        for i_nb, i_node in enumerate(l_graph.nodes()):
            if type(i_node) is tuple:
                self._add_links(l_graph, i_node, p_velocities, p_length, p_otl)
            l_graph.node[i_node]["pos"] = self.__position_node(i_node, p_length)

        print()
        self._log.info("Generating Search Space Graph took {} seconds".format(round(time.time()-t_start, 1)))

        self._write_graph(l_graph, p_velocities, p_start_times, p_length)
        self._draw_graph(l_graph, p_velocities, p_start_times, p_length)

        return l_graph

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
