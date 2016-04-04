class Vehicle(object):

    def __init__(self, p_id, p_desiredspeed, p_posx, p_posy, p_y, p_yt, p_z, p_zt):
        self._id = p_id
        self._desiredspeed = p_desiredspeed
        self._posx = p_posx
        self._posy = p_posy
        self._y = p_y
        self._yt = p_yt
        self._z = p_z
        self._zt = p_zt

        self._speed = 0

    def __str__(self):
        return "V" + str(self._id) + "/" + str(self._desiredspeed.varName)

    def __repr__(self):
        return "V" + str(self._id) + "/" + str(self._desiredspeed.varName)

