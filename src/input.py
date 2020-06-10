import sys
import json
import os
import numpy
import math

from collections import defaultdict
from point import Point, SensorNode, RelayNode, distance

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

from config.constant import Constants

class Input:
    def __init__(self, _W=500, _H=500, _depth=1., _height=10., _num_of_relays=10, _num_of_sensors=50,
                 _sensor_radius=25, _communicate_radius=50, _sensors=None, _relays=None, _sensor_coverage=None,
                 _comm_loss_matrix=None):
        self.W = _W
        self.H = _H
        self.depth = _depth
        self.height = _height
        self.num_of_relays = _num_of_relays
        self.num_of_sensors = _num_of_sensors
        self.sensor_radius = _sensor_radius
        self.communicate_radius = _communicate_radius
        self.relays = _relays
        self.sensors = _sensors
        self.sensor_coverage = _sensor_coverage
        self.comm_loss_matrix = _comm_loss_matrix

        if _sensor_coverage == None:
            self.cal_sensor_coverage()
        if _comm_loss_matrix == None:
            self.cal_comm_loss_matrix()

    def cal_comm_loss_matrix(self):
        comm_loss_matrix = numpy.zeros(
            (self.num_of_sensors, self.num_of_sensors))

        for sn in range(self.num_of_sensors):
            for ss in range(sn+1, self.num_of_sensors):
                d = distance(self.sensors[sn], self.sensors[ss])
                loss = 6.4 + 20 * math.log(10, d) + 20 * math.log(10, Constants.get_beta()
                                                                  ) + 8.69 * Constants.get_anpha() * d
                comm_loss_matrix[sn][ss] = loss
                comm_loss_matrix[ss][sn] = loss

        self.comm_loss_matrix = comm_loss_matrix

    def cal_sensor_coverage(self):
        sensor_coverage = numpy.zeros(
            (self.num_of_relays, self.num_of_sensors))
        R = self.sensor_radius
        print(self.num_of_relays, self.num_of_sensors)

        for rn in range(self.num_of_relays):
            for sn in range(self.num_of_sensors):
                d = distance(self.sensors[sn], self.relays[rn])
                if (self.relays[rn].x - self.sensors[sn].x) == 0:
                    x_atan = 0
                else:
                    x_atan = numpy.arctan(
                        (self.relays[rn].y-self.sensors[sn].y)/(self.relays[rn].x - self.sensors[sn].x))
                
                if d == 0:
                    z_atan = 0
                else:
                    z_atan = numpy.arctan(
                        (self.relays[rn].z - self.sensors[sn].z)/d)

                if (d <= 2*R) and (x_atan >= 0 and x_atan <= 1.57) and (z_atan >= 0 and z_atan <= 1.57):
                    sensor_coverage[rn][sn] = 1
                    # sensor_coverage[sn][rn] = 1
                else:
                    sensor_coverage[rn][sn] = 0
                    # sensor_coverage[sn][rn] = 0

        self.sensor_coverage = sensor_coverage

    @classmethod
    def from_file(cls, path):
        f = open(path)
        d = json.load(f)
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d):
        W = d['W']
        H = d['H']
        depth = d['depth']
        height = d['height']
        num_of_relays = d['num_of_relays']
        num_of_sensors = d['num_of_sensors']
        relays = []
        sensors = []
        sensor_radius = d["radius"]
        communicate_radius = 50

        for i in range(num_of_sensors):
            d['sensors'][i]['index'] = i
            sensors.append(SensorNode.from_dict(d['sensors'][i]))
        for i in range(num_of_relays):
            d['relays'][i]['index'] = i
            relays.append(RelayNode.from_dict(d['relays'][i]))

        return cls(W, H, depth, height, num_of_relays, num_of_sensors, sensor_radius, communicate_radius, sensors, relays)


if __name__ == "__main__":
    inp = Input.from_file('../data/small_data/no-dem1_r25_1.in')
    print(numpy.count_nonzero(inp.sensor_coverage > 0))
