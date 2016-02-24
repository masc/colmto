from world import World
from gurobipy import *

class Optov(object):

    def __init__(self):
        # init world
        self._world = World(self)
        self._world.addVehicle((6,0), 30)
        self._world.addVehicle((0,0), 50)

    def solveexample(self):


        try:
            # Create a new model
            m = Model("test")

            # Create variables
            # vehicle individual vars
            vv = {}

            for i in xrange(2):

                vv["ix"+str(i)] = m.addVar(vtype=GRB.INTEGER, name="ix"+str(i))
                vv["iy"+str(i)] = m.addVar(vtype=GRB.INTEGER, name="iy"+str(i))

                # traveltime
                vv["t"+str(i)] = m.addVar(vtype=GRB.INTEGER, name="t"+str(i))

                # desired speeds
                vv["ds"+str(i)] = m.addVar(vtype=GRB.INTEGER, name="ds"+str(i))

                # pull-outs
                vv["y"+str(i)] = m.addVar(vtype=GRB.INTEGER, name="y"+str(i))

                # pull-ins
                vv["z"+str(i)] = m.addVar(vtype=GRB.INTEGER, name="z"+str(i))

            # Integrate new variables
            m.update()

            # Set objective
            #m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)
            m.setObjective(vv["y0"]+vv["y1"], GRB.MINIMIZE)

            # Add constraint: x + 2 y + 3 z <= 4
            m.addConstr(vv["ix0"]==6, "c_ix0")
            m.addConstr(vv["iy0"]==0, "c_iy0")
            m.addConstr(vv["ds0"]==30, "c_ds0")
            m.addConstr(vv["t0"]*vv["ds0"]==21, "c_t0")

            m.addConstr(vv["ix1"]==6, "c_ix1")
            m.addConstr(vv["iy1"]==0, "c_iy1")
            m.addConstr(vv["ds1"]==30, "c_ds1")
            m.addConstr(vv["t1"]*vv["ds1"]==21, "c_t1")

            # possible pull outs between otl_start and otl_end
            m.addConstr(vv["y0"] >= 6, "c_y0_start")
            m.addConstr(vv["y0"] <= 15-self.minOTSpace(0,1), "c_y0_end") # this needs to be added for each pairwise vehicle combination

            m.addConstr(vv["y1"] >= 6, "c_y1_start")
            m.addConstr(vv["y1"] <= 15-self.minOTSpace(1,0), "c_y1_end")

            # Add constraint: x + y >= 1
            #m.addConstr(x + y >= 1, "c1")

            m.optimize()

            for v in m.getVars():
                print v.varName, v.x

            print 'Obj:', m.objVal

        except GurobiError:
            print 'Error reported'

    def minOTSpace(self, vpreceding, vfollowing):
        return 3


if __name__ == "__main__":
    optov = Optov()
