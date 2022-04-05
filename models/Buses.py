from __future__ import division
from itertools import count
import numpy as np


class Buses:
    _idsActiveBuses = count(1)
    _idsAllBuses = count(1)

    _node_index = count(0)#THIS ESSENTIALLY COUNTS THE NUMBER OF NODES(LIKE OUR NODES IN PROJECT1)
    bus_key_ = {}#THIS MAKES A DICTIONARY FOR EACH BUS(where do we call this?)
    all_bus_key_ = {}#THIS IS THE OVERALL LIST OF DICTIONARIES FOR THE BUSES

    def __init__(self,
                 Bus,
                 Type,
                 Vm_init,
                 Va_init,
                 Area):
        """Initialize an instance of the Buses class.

        Args:
            Bus (int): The bus number.
            Type (int): The type of bus (e.g., PV, PQ, of Slack)
            Vm_init (float): The initial voltage magnitude at the bus.
            Va_init (float): The initial voltage angle at the bus.
            Area (int): The zone that the bus is in.
        """

        self.Bus = Bus
        self.Type = Type
        self.Vm_init = Vm_init
        self.Va_init = Va_init
        self.Area = Area

        # initialize all nodes(indexes looking below we see that these nodes get assigned indexes)
        self.node_Vr = None  
        self.node_Vi = None  
        self.node_Q = None  

        # initialize the bus key
        self.idAllBuses = self._idsAllBuses.__next__()###NOT SURE HOW THIS FUNCTIONS
        Buses.all_bus_key_[self.Bus] = self.idAllBuses - 1

    def __str__(self):
        return_string = 'The bus number is : {} with Vr node as: {} and Vi node as {} '.format(self.Bus,
                                                                                               self.node_Vr,
                                                                                               self.node_Vi)
        return return_string

    def assign_nodes(self):
        """Assign nodes based on the bus type.

        Returns:
            None
        """
        # If Slack or PQ Bus
        if self.Type == 1 or self.Type == 3:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()
            if self.Type == 3:
                pass
                #print('Bus='+str(self.Bus) +' ' + str(self.node_Vr) + '_real voltage slack index ' +  str(self.node_Vi) + '_imganary voltage slack index')
            else:
                #print('Bus='+str(self.Bus) +' ' + str(self.node_Vr) + '_real voltage PQ index ' +  str(self.node_Vi) + '_imganary voltage PQ index')
                pass
        # If PV Bus
        elif self.Type == 2:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()
            self.node_Q = self._node_index.__next__()
            #print('Bus='+str(self.Bus) +' ' +str(self.node_Vr) + '_real voltage PV ' +  str(self.node_Vi) + '_imganary voltage PV ' + str(self.node_Q) + '_q')
    
    def initialize(self, v_init):
        if self.Type == 1 or self.Type == 3:
            v_init[self.node_Vr] += self.Vm_init*np.cos(np.deg2rad(self.Va_init))
            v_init[self.node_Vi] += self.Vm_init*np.sin(np.deg2rad(self.Va_init))
        elif self.Type == 2:
            v_init[self.node_Vr] += self.Vm_init*np.cos(np.deg2rad(self.Va_init))
            v_init[self.node_Vi] += self.Vm_init*np.sin(np.deg2rad(self.Va_init))
    
    def apply_lim(self, v_sol,v):
        max_step = .1
        V_max = 1.07
        V_min = .93
        delt_r = v_sol[self.node_Vr]-v[self.node_Vr]
        de_s_r = np.sign(delt_r)
        delt_i = v_sol[self.node_Vi]-v[self.node_Vi]
        de_s_i = np.sign(delt_i)
        x_r = v[self.node_Vr] + de_s_r*np.min([np.abs(delt_r),max_step])
        x_i = v[self.node_Vi] + de_s_i*np.min([np.abs(delt_i),max_step])
        if x_r > V_max:
            v_sol[self.node_Vr] = V_max
        elif x_r <V_min:
            v_sol[self.node_Vr] = V_min
        else:
            v_sol[self.node_Vr] = x_r
        if x_i > V_max:
            v_sol[self.node_Vi] = V_max
        elif x_i <V_min:
            v_sol[self.node_Vi] = V_min
        else:
            v_sol[self.node_Vi] = x_i

        pass

        

    
