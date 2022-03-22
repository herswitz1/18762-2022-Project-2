from __future__ import division
from models.Buses import Buses
import numpy as np

class Slack:

    def __init__(self,
                 Bus,
                 Vset,
                 ang,
                 Pinit,
                 Qinit):
        """Initialize slack bus in the power grid.

        Args:
            Bus (int): the bus number corresponding to the slack bus.
            Vset (float): the voltage setpoint that the slack bus must remain fixed at.
            ang (float): the slack bus voltage angle that it remains fixed at.
            Pinit (float): the initial active power that the slack bus is supplying
            Qinit (float): the initial reactive power that the slack bus is supplying
        """
        # You will need to implement the remainder of the __init__ function yourself.
        self.Bus = Bus
        self.Vset = Vset
        self.ang = ang
        self.Pinit = Pinit
        self.Qinit = Qinit
        # initialize nodes
        self.node_P_Slack = None #SINCE NO VMAG AND ANGLE CAN CALCULATE REAL AND IMAGNIARY SLACK VOLTAGE
        self.node_Q_Slack = None #These should probably be P and Q two be more representative
        self.Vr_index = None
        self.Vi_index = None
    def assign_nodes(self,bus):
        """Assign the additional slack bus nodes for a slack bus.

        Returns:
            None
        """
        self.node_P_Slack = Buses._node_index.__next__()#THIS BOTH ASSIGNS THE SLACK BUS NODES AND MAKES THE BUES NODE_INDEX COUNTER INCEMENT
        self.node_Q_Slack = Buses._node_index.__next__()
        self.Vr_index = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.Vi_index = bus[Buses.bus_key_[self.Bus]].node_Vi

    # You should also add some other class functions you deem necessary for stamping,
    # initializing, and processing results
    def stamp_lin(self): #not sure if I need this
        pass

    def sparse_stamp_non_lin(self,Y_row, Y_col, Y_val, J_vec, idx_y, prev_v): #not sure if I need this
        #Real slack stamp 1
        Y_row[idx_y] = self.node_P_Slack
        Y_col[idx_y] = self.node_P_Slack
        Y_val[idx_y] = 1#abs(self.Vset)*np.cos(self.ang) #maybe this should be 1
        J_vec[self.node_P_Slack] = abs(self.Vset)*np.cos(self.ang)#prev_v[self.node_P_Slack] #may nnot need this node
        idx_y +=1
        
        Y_row[idx_y] = self.Vr_index
        Y_col[idx_y] = self.node_P_Slack
        Y_val[idx_y] = 1 #maybe this should be 1
        #J_vec[self.node_P_Slack] += prev_v[self.node_P_Slack]
        idx_y +=1
        
        #Imaginary slack stamp 2
        Y_row[idx_y] = self.node_Q_Slack
        Y_col[idx_y] = self.node_Q_Slack
        Y_val[idx_y] = 1#abs(self.Vset)*np.sin(self.ang)#maybe this shoud be 1
        J_vec[self.node_Q_Slack] = abs(self.Vset)*np.sin(self.ang)#prev_v[self.node_Q_Slack]
        idx_y +=1

        Y_row[idx_y] = self.Vi_index
        Y_col[idx_y] = self.node_Q_Slack
        Y_val[idx_y] = 1#abs(self.Vset)*np.sin(self.ang)#maybe this shoud be 1
        #J_vec[self.node_Q_Slack] += prev_v[self.node_Q_Slack]
        idx_y +=1
        return idx_y
        
    def initialize(self,Vinit): #not sure if I need this
        ##given voltage magnitude and angel along with intial p and Q we can find and stamp initila Ir and Ii
        Vinit[self.node_P_Slack] = self.Pinit#/(abs(self.Vset)*np.cos(self.ang))
        Vinit[self.node_Q_Slack] = self.Qinit#/(abs(self.Vset)*np.sin(self.ang))
        #return Vinit
