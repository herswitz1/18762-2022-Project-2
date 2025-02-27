from __future__ import division
from itertools import count
import numpy as np
from models.Buses import Buses #SINCE IMPORTS BUSSES MAY BEED TO INCREMENT BUS INDEX COUNTER

####
class Transformers:
    _ids = count(0)

    def __init__(self,
                 from_bus,
                 to_bus,
                 r,
                 x,
                 status,
                 tr,
                 ang,
                 Gsh_raw,
                 Bsh_raw,
                 rating):
        """Initialize a transformer instance

        Args:
            from_bus (int): the primary or sending end bus of the transformer.
            to_bus (int): the secondary or receiving end bus of the transformer
            r (float): the line resitance of the transformer in
            x (float): the line reactance of the transformer
            status (int): indicates if the transformer is active or not
            tr (float): transformer turns ratio
            ang (float): the phase shift angle of the transformer
            Gsh_raw (float): the shunt conductance of the transformer
            Bsh_raw (float): the shunt admittance of the transformer
            rating (float): the rating in MVA of the transformer
        """
        self.from_bus = from_bus
        self.to_bus = to_bus
        self.r = r
        self.x = x
        self.status = status
        self.tr = tr
        self.ang = ang
        self.Gsh_raw = Gsh_raw #not sure how to use this
        self.Bsh_raw = Bsh_raw
        self.rating = rating
        self.id = self._ids.__next__()
        self.V1r = None
        self.V1i = None
        self.I2r = None
        self.I2i = None
        self.from_Bnode_r = None
        self.to_Bnode_r = None
        self.from_Bnode_i = None
        self.to_Bnode_i = None


        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
    def assign_nodes(self,bus): #not sure if I need this
        
        self.from_Bnode_r = bus[Buses.bus_key_[self.from_bus]].node_Vr#Vr1
        self.from_Bnode_i = bus[Buses.bus_key_[self.from_bus]].node_Vi#Vi1 (c)
        self.to_Bnode_r = bus[Buses.bus_key_[self.to_bus]].node_Vr#Vtor (b)
        self.to_Bnode_i = bus[Buses.bus_key_[self.to_bus]].node_Vi#Vtoi(d)
        self.V2r = Buses._node_index.__next__()#V2
        self.V2i = Buses._node_index.__next__()#V
        self.I1r = Buses._node_index.__next__()#
        self.I1i = Buses._node_index.__next__()

    def stamp(self, Y_row_lin, Y_col_lin, Y_val_lin, idx_y, row, col, val):
        Y_row_lin[idx_y] = row
        Y_col_lin[idx_y] = col
        Y_val_lin[idx_y] = val
        idx_y +=1
        return idx_y

    def sparse_stamp_lin(self,Y_row_lin, Y_col_lin, Y_val_lin, idx_y,prev_v): #not sure if I need this
        #all possible values
        G = self.r/(np.square(self.r)+np.square(self.x))
        B = -self.x/(np.square(self.r)+np.square(self.x))
        SH = self.Bsh_raw/2
        T_c = self.tr*np.cos(np.deg2rad(self.ang))
        T_s = self.tr*np.sin(np.deg2rad(self.ang))
        ###all possible indexes
        f_r = self.from_Bnode_r
        f_i = self.from_Bnode_i
        t_r = self.to_Bnode_r
        t_i = self.to_Bnode_i
        e_r = self.V2r
        e_i = self.V2i
        c_r = self.I1r
        c_i = self.I1i
        #row 1
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_r, e_r, -T_c)
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_r, e_i, T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_r, c_r, 1)
        #idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_r, c_i, -1)
        #row 2
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_i, e_r, -T_s)
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_i, e_i, -T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_i, c_i, 1)
        #idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, f_i, c_r, -1)
        #row 3
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, f_r, T_c)
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, f_i, T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, c_r, T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, c_i, T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, e_r, G)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, e_i, -B-SH)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, t_r, -G)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_r, t_i, B)
        #row 4
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, f_r, -T_s)
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, f_i, T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, c_r, -T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, c_i, T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, e_r, B+SH)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, e_i, G)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, t_r, -B)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, e_i, t_i, -G)
         #row 5
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_r, c_r, T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_r, c_i, T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_r, e_r, -G)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_r, e_i, B)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_r, t_r, G)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_r, t_i, -B-SH)
        #row 6
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_i, c_r, -T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_i, c_i, T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_i, e_r, -B)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_i, e_i, -G)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_i, t_r, B+SH)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, t_i, t_i, G)
        #row 7
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_r, t_r, -T_c)
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_r, t_i, -T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_r, e_r, T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_r, e_i, -T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_r, f_r, 1)
        #row 8
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_i, t_r, T_s)
        # idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_i, t_i, -T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_i, e_r, T_s)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_i, e_i, T_c)
        idx_y = self.stamp(Y_row_lin, Y_col_lin, Y_val_lin, idx_y, c_i, f_i, 1)

        return idx_y
        
    def initialize(self): 
        pass