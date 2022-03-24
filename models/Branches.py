from __future__ import division
from itertools import count

from sklearn.utils import resample
from models.Buses import Buses
import numpy as np

class Branches:
    _ids = count(0)

    def __init__(self,
                 from_bus,
                 to_bus,
                 r,
                 x,
                 b,
                 status,
                 rateA,
                 rateB,
                 rateC):
        """Initialize a branch in the power grid.

        Args:
            from_bus (int): the bus number at the sending end of the branch.
            to_bus (int): the bus number at the receiving end of the branch.
            r (float): the branch resistance
            x (float): the branch reactance
            b (float): the branch susceptance
            status (bool): indicates if the branch is online or offline
            rateA (float): The 1st rating of the line.
            rateB (float): The 2nd rating of the line
            rateC (float): The 3rd rating of the line.
        """
        self.from_bus = from_bus
        self.to_bus = to_bus
        self.r = r
        self.x = x
        self.b = b
        self.status = status
        self.rateA = rateA
        self.rateB = rateB
        self.rateC = rateC
        self.id = self._ids.__next__()#not sure if this should be first or last
        self.from_Bnode_r = None
        self.to_Bnode_r = None
        self.from_Bnode_i = None
        self.to_Bnode_i = None

        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
        
    def assign_nodes(self,bus): #we shoud have 4 node indeces, 2 for real and 2 for imaginary
        #know these are not correct
        self.from_Bnode_r = bus[Buses.bus_key_[self.from_bus]].node_Vr#Vnr (a)
        self.from_Bnode_i = bus[Buses.bus_key_[self.from_bus]].node_Vi#Vni (c)
        self.to_Bnode_r = bus[Buses.bus_key_[self.to_bus]].node_Vr#Vmr (b)
        self.to_Bnode_i = bus[Buses.bus_key_[self.to_bus]].node_Vi#Vmi (d)

        

    def sparse_stamp_lin(self, Y_row, Y_col,Y_val, idx_y): #not sure if I need this
        G = self.r/(np.square(self.r)+np.square(self.x))
        B = self.x/(np.square(self.r)+np.square(self.x))
        SH = self.b/2
        
        #Real
        #I1r
        #Y(a,a)
        Y_row[idx_y] = self.from_Bnode_r #i
        Y_col[idx_y] = self.from_Bnode_r #j
        Y_val[idx_y] = G#real resistance from node (noteice that there may be some sign error)
        idx_y +=1
        #Y(a,c)
        Y_row[idx_y] = self.from_Bnode_r
        Y_col[idx_y] = self.to_Bnode_r
        Y_val[idx_y] = -G#real resistance to node
        idx_y +=1
        #Y(a,b)
        Y_row[idx_y] = self.from_Bnode_r
        Y_col[idx_y] = self.from_Bnode_i
        Y_val[idx_y] = -B-SH
        idx_y +=1
        #Y(a,d)
        Y_row[idx_y] = self.from_Bnode_r
        Y_col[idx_y] = self.to_Bnode_i
        Y_val[idx_y] = B
        idx_y +=1
        # #Y(a,a) shunt real at from node
        # Y_row[idx_y] = self.from_Bnode_r
        # Y_col[idx_y] = self.from_Bnode_i
        # Y_val[idx_y] = SH
        # idx_y +=1

        #I2r
        #Y(c,a)
        Y_row[idx_y] = self.to_Bnode_r
        Y_col[idx_y] = self.from_Bnode_r
        Y_val[idx_y] = -G
        idx_y +=1
        #Y(c,c)
        Y_row[idx_y] = self.to_Bnode_r
        Y_col[idx_y] = self.to_Bnode_r
        Y_val[idx_y] = G#-SH
        idx_y +=1
        #Y(c,b)
        Y_row[idx_y] = self.to_Bnode_r
        Y_col[idx_y] = self.from_Bnode_i
        Y_val[idx_y] = B
        idx_y +=1
        #Y(c,d)
        Y_row[idx_y] = self.to_Bnode_r
        Y_col[idx_y] = self.to_Bnode_i
        Y_val[idx_y] = -B+SH
        idx_y +=1
        # #Y(b,b) real shunt at to node
        # Y_row[idx_y] = self.to_Bnode_r
        # Y_col[idx_y] = self.to_Bnode_i
        # Y_val[idx_y] = -SH
        # idx_y +=1

        #Imaginary
        #Ii1 (feel likere this is some error here)
        #Y(b,a)
        Y_row[idx_y] = self.from_Bnode_i
        Y_col[idx_y] = self.from_Bnode_r
        Y_val[idx_y] = B+SH #
        idx_y +=1
        #Y(b,c)
        Y_row[idx_y] = self.from_Bnode_i
        Y_col[idx_y] = self.to_Bnode_r
        Y_val[idx_y] = -B
        idx_y +=1
        #Y(b,b)
        Y_row[idx_y] = self.from_Bnode_i
        Y_col[idx_y] = self.from_Bnode_i
        Y_val[idx_y] = G#+SH
        idx_y +=1
        #Y(b,d)
        Y_row[idx_y] = self.from_Bnode_i
        Y_col[idx_y] = self.to_Bnode_i
        Y_val[idx_y] = -G
        idx_y +=1
        #Y(c,c)shunt for imaginary from node
        # Y_row[idx_y] = self.from_Bnode_i
        # Y_col[idx_y] = self.from_Bnode_i
        # Y_val[idx_y] = -SH
        # idx_y +=1

        #I2i
        #Y(d,a)
        Y_row[idx_y] = self.to_Bnode_i
        Y_col[idx_y] = self.from_Bnode_r
        Y_val[idx_y] = -B #this may be negative
        idx_y +=1
        #Y(d,c)
        Y_row[idx_y] = self.to_Bnode_i
        Y_col[idx_y] = self.to_Bnode_r
        Y_val[idx_y] = B-SH
        idx_y +=1
        #Y(d,b)
        Y_row[idx_y] = self.to_Bnode_i
        Y_col[idx_y] = self.from_Bnode_i
        Y_val[idx_y] = -G
        idx_y +=1
        #Y(d,d)
        Y_row[idx_y] = self.to_Bnode_i
        Y_col[idx_y] = self.to_Bnode_i
        Y_val[idx_y] = G#+SH
        idx_y +=1
        # #Y(d,d) shunt for imagainary to node
        # Y_row[idx_y] = self.to_Bnode_i
        # Y_col[idx_y] = self.to_Bnode_i
        # Y_val[idx_y] = -SH
        # idx_y +=1

        return idx_y

    def initialize(self,Vinit): #not sure if I need this
        Vinit[self.from_Bnode_r]=0.00001
        Vinit[self.from_Bnode_i] = 0.00001
        Vinit[self.to_Bnode_r]=0.00001
        Vinit[self.to_Bnode_i]=0.00001
        pass