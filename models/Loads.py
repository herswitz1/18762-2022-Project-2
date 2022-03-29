from __future__ import division
from itertools import count
from models.Buses import Buses
import numpy as np

####PQ BUS
class Loads:
    _ids = count(0)

    def __init__(self,
                 Bus,
                 P,
                 Q,
                 IP,
                 IQ,
                 ZP,
                 ZQ,
                 area,
                 status):
        """Initialize an instance of a PQ or ZIP load in the power grid.

        Args:
            Bus (int): the bus where the load is located
            P (float): the active power of a constant power (PQ) load.
            Q (float): the reactive power of a constant power (PQ) load.
            IP (float): the active power component of a constant current load.
            IQ (float): the reactive power component of a constant current load.
            ZP (float): the active power component of a constant admittance load.
            ZQ (float): the reactive power component of a constant admittance load.
            area (int): location where the load is assigned to.
            status (bool): indicates if the load is in-service or out-of-service.
        """
        self.Bus = Bus
        self.P = P
        self.Q = Q
        self.IP = IP
        self.IQ = IQ
        self.ZP = ZP
        self.ZQ= ZQ
        self.area = area
        self.status = status
        self.id = Loads._ids.__next__()#NOT SURE IF THIS SHOULD BE AT THE TOP OR END
        self.node_Vrl = None
        self.node_Vil = None
        self.P_base = self.P/100
        self.Q_base = self.Q/100


        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
    def assign_nodes(self,bus): #struggling to figure out how to properly assign the nodes
        self.node_Vrl = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.node_Vil = bus[Buses.bus_key_[self.Bus]].node_Vi
        pass

    def sparse_stamp_non_lin(self,Y_row, Y_col,Y_val,J_vec, idx_y,prev_v): 
        Vrl_il = ((np.square(prev_v[self.node_Vrl]))+(np.square(prev_v[self.node_Vil]))) #this is the sum of the previous real voltage square and imaginary voltage squared
        Irl = ((self.P_base*prev_v[self.node_Vrl]) + (self.Q_base*prev_v[self.node_Vil]))/(Vrl_il) ##current value of real load current
        Iil = ((self.P_base*prev_v[self.node_Vil]) - (self.Q_base*prev_v[self.node_Vrl]))/(Vrl_il) ##current value of imaginary load current
        ##calculating partials
        #real
        dIrl_dvrl = ((Vrl_il)*self.P_base - (self.P_base*prev_v[self.node_Vrl] + self.Q_base*prev_v[self.node_Vil])*(2*prev_v[self.node_Vrl]))/(np.square(Vrl_il)) #dIrl/dVrl
        dIrl_dvil = ((Vrl_il)*self.Q_base - (self.P_base*prev_v[self.node_Vrl] + self.Q_base*prev_v[self.node_Vil])*(2*prev_v[self.node_Vil]))/(np.square(Vrl_il)) #dIrl/dVil
        #imaginary
        dIil_dvrl = ((Vrl_il)*(-self.Q_base) - (self.P_base*prev_v[self.node_Vil] - self.Q_base*prev_v[self.node_Vrl])*(2*prev_v[self.node_Vrl]))/(np.square(Vrl_il)) #dIil/dVrl
        dIil_dvil = ((Vrl_il)*self.P_base - (self.P_base*prev_v[self.node_Vil] - self.Q_base*prev_v[self.node_Vrl])*(2*prev_v[self.node_Vil]))/(np.square(Vrl_il)) #dIil/dVil
        ###
        ##History
       
        
        
        ###Makeing stamps
        #real current row
        ##Y(i,i) 1
        Y_row[idx_y] = self.node_Vrl
        Y_col[idx_y] = self.node_Vrl
        Y_val[idx_y] = dIrl_dvrl
        
        idx_y += 1
        ##Y(i,j) 2
        Y_row[idx_y] = self.node_Vrl
        Y_col[idx_y] = self.node_Vil
        Y_val[idx_y] =  dIrl_dvil
        idx_y +=1
        #J(i)
        J_vec[self.node_Vrl] += -(Irl - (dIrl_dvrl*prev_v[self.node_Vrl]) - (dIrl_dvil*prev_v[self.node_Vil]))#j stamp for real current
        #self.HistR = J_vec[self.node_Vrl]
        ##imaginary current row
        ##Y(j,i) 3
        Y_row[idx_y] = self.node_Vil
        Y_col[idx_y] = self.node_Vrl
        Y_val[idx_y] = dIil_dvrl
        
        idx_y += 1
        ##Y(j,j) 4
        Y_row[idx_y] = self.node_Vil
        Y_col[idx_y] = self.node_Vil
        Y_val[idx_y] = dIil_dvil
        idx_y +=1
        ##J(j)
        J_vec[self.node_Vil] += -(Iil - (dIil_dvrl*prev_v[self.node_Vrl]) - (dIil_dvil*prev_v[self.node_Vil]))#J stamp for imaginary current
        #self.HistI = J_vec[self.node_Vil]

        return idx_y

    def stamp_non_lin(self): #not sure if I need this
        pass
        
    def initialize(self, Vinit): #For liniear components stamp 0(not sure what to give them iniitlaly)
        #Vinit[self.node_Vrl] = self.P#These are wrong
        #Vinit[self.node_Vil] = self.Q
        pass
