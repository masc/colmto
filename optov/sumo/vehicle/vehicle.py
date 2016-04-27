class Vehicle(object):

    def __init__(self, p_id, p_vtype, p_starttime):
        self._id = p_id
        self._vtype = p_vtype
        self._starttime = 0

    def get(self, p_value):
        return self._vtype.get(p_value)

    def getID(self):
        return self._id

    def getStartTime(self):
        return self._starttime

    def __str__(self):
        return "{}({})".format(self._id, self._maxspeed)

    def __repr__(self):
        return "{}({})".format(self._id, self._maxspeed)
