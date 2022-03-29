import numpy as np
from models.Buses import Buses
def process_results(v, bus):
    for Buses in bus:
        if Buses.Type == 1:
            V_mag = np.sqrt(np.square(v[Buses.node_Vr]) + np.square(v[Buses.node_Vi]))
            V_ang = np.rad2deg(np.arctan2(v[Buses.node_Vi],v[Buses.node_Vr]))
            print(str(Buses.Bus)+ ' is a PQ bus with' + ' voltage mag=' +str(V_mag) + ' and angle=' + str(V_ang))
        elif Buses.Type == 3:
            V_mag = np.sqrt(np.square(v[Buses.node_Vr]) + np.square(v[Buses.node_Vi]))
            V_ang = np.rad2deg(np.arctan2(v[Buses.node_Vi],v[Buses.node_Vr]))
            print(str(Buses.Bus)+ ' is a slack bus with' + ' voltage mag=' +str(V_mag) + ' and angle=' + str(V_ang))
        else:
            V_mag = np.sqrt(np.square(v[Buses.node_Vr]) + np.square(v[Buses.node_Vi]))
            V_ang = np.rad2deg(np.arctan2(v[Buses.node_Vi],v[Buses.node_Vr]))
            print(str(Buses.Bus)+ ' is a generator bus with' + ' voltage mag=' +str(V_mag) + ' and angle=' + str(V_ang))
        