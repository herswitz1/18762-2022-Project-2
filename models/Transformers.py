from __future__ import division
from itertools import count
import numpy as np
from models.Buses import Buses #SINCE IMPORTS BUSSES MAY BEED TO INCREMENT BUS INDEX COUNTER

####90% OF THIS IS ALL WRONG
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
        
        # self.I2r = Buses._node_index.__next__()#
        # self.I2i = Buses._node_index.__next__()
        self.from_Bnode_r = bus[Buses.bus_key_[self.from_bus]].node_Vr#Vr2
        self.from_Bnode_i = bus[Buses.bus_key_[self.from_bus]].node_Vi#Vi2 (c)
        self.to_Bnode_r = bus[Buses.bus_key_[self.to_bus]].node_Vr#Vr2 (b)
        self.to_Bnode_i = bus[Buses.bus_key_[self.to_bus]].node_Vi#Vmi (d)
        self.V1r = Buses._node_index.__next__()#not sure where to use these
        self.V1i = Buses._node_index.__next__()#V

    def sparse_stamp_lin(self,Y_row_lin, Y_col_lin, Y_val_lin, idx_y,prev_v): #not sure if I need this
        G = self.r/(np.square(self.r)+np.square(self.x))
        B = -self.x/(np.square(self.r)+np.square(self.x))
        
        
        #Real primary real (row 1)(a,a)
        Y_row_lin[idx_y] = self.from_Bnode_r
        Y_col_lin[idx_y] = self.from_Bnode_r
        Y_val_lin[idx_y] = self.tr*np.cos(self.ang)#(prev_v[self.from_Bnode_r]*np.cos(self.ang))
        idx_y +=1
        #real primary imaganiary (row 1)(a,b)
        Y_row_lin[idx_y] = self.from_Bnode_r
        Y_col_lin[idx_y] = self.from_Bnode_i
        Y_val_lin[idx_y] = -self.tr*np.sin(self.ang)#(-prev_v[self.from_Bnode_i]*np.sin(self.ang))
        idx_y +=1

        #imaginary primary real(row 2)(b,a)
        Y_row_lin[idx_y] = self.from_Bnode_i
        Y_col_lin[idx_y] = self.from_Bnode_r
        Y_val_lin[idx_y] = self.tr*np.sin(self.ang)#(prev_v[self.from_Bnode_r]*np.sin(self.ang))
        idx_y +=1
        #imaginary primary imaganiary (row 2)(b,b)
        Y_row_lin[idx_y] = self.from_Bnode_i
        Y_col_lin[idx_y] = self.from_Bnode_i
        Y_val_lin[idx_y] = self.tr*np.cos(self.ang)#(prev_v[self.from_Bnode_i]*np.cos(self.ang))
        idx_y +=1

        ###FEEL LIKE J VECTOR SHOULD BE STAMPED WITH SELF.VIR AND THE OTHER EX

        #SECONDAY
        ##real loses (row 3) (c,a)
        Y_row_lin[idx_y] = self.to_Bnode_r
        Y_col_lin[idx_y] = self.from_Bnode_r
        Y_val_lin[idx_y] = G
        idx_y +=1
        #row3 (c,b)
        Y_row_lin[idx_y] = self.to_Bnode_r
        Y_col_lin[idx_y] = self.from_Bnode_i
        Y_val_lin[idx_y] = -B
        idx_y +=1
        #Real secondary real(row 3) (c,c)
        Y_row_lin[idx_y] = self.to_Bnode_r
        Y_col_lin[idx_y] = self.to_Bnode_r
        Y_val_lin[idx_y] = -self.tr*np.cos(self.ang)#(prev_v[self.to_Bnode_r]*np.cos(self.ang))
        idx_y +=1
        #real secondary imaganiary (row 3)(c,d)
        Y_row_lin[idx_y] = self.to_Bnode_r
        Y_col_lin[idx_y] = self.to_Bnode_i
        Y_val_lin[idx_y] = -self.tr*np.sin(self.ang)#(prev_v[self.to_Bnode_i]*np.sin(self.ang))
        idx_y +=1
         #row 3 (c,e)
        Y_row_lin[idx_y] = self.to_Bnode_r
        Y_col_lin[idx_y] = self.V1r
        Y_val_lin[idx_y] = -G
        idx_y +=1
        #row 3 (c,f)
        Y_row_lin[idx_y] = self.to_Bnode_r
        Y_col_lin[idx_y] = self.V1i
        Y_val_lin[idx_y] = B
        idx_y +=1


        ##imaginary losses (row 4) (d,a)
        Y_row_lin[idx_y] = self.to_Bnode_i
        Y_col_lin[idx_y] = self.from_Bnode_r
        Y_val_lin[idx_y] = B
        idx_y +=1
        #row 4 (d,b)
        Y_row_lin[idx_y] = self.to_Bnode_i
        Y_col_lin[idx_y] = self.from_Bnode_i
        Y_val_lin[idx_y] = G
        idx_y +=1
        #imaginary secondary real (row 4)(d,c)
        Y_row_lin[idx_y] = self.to_Bnode_i
        Y_col_lin[idx_y] = self.to_Bnode_r
        Y_val_lin[idx_y] = self.tr*np.sin(self.ang)#(prev_v[self.to_Bnode_r]*np.sin(self.ang))
        idx_y +=1
        #imaginary secondary imaganiary (row 4) (d,d)
        Y_row_lin[idx_y] = self.to_Bnode_i
        Y_col_lin[idx_y] = self.to_Bnode_i
        Y_val_lin[idx_y] = -self.tr*np.cos(self.ang)#(prev_v[self.to_Bnode_i]*np.cos(self.ang))
        idx_y +=1
        ###loss in secondary
        #row 4 (d,e)
        Y_row_lin[idx_y] = self.to_Bnode_i
        Y_col_lin[idx_y] = self.V1r
        Y_val_lin[idx_y] = -B
        idx_y +=1
        #row 4 (d,f)
        Y_row_lin[idx_y] = self.to_Bnode_i
        Y_col_lin[idx_y] = self.V1i
        Y_val_lin[idx_y] = -G
        idx_y +=1

        # ####voltage sources row(5) (e,e)
        # Y_row_lin[idx_y] = self.V1r
        # Y_col_lin[idx_y] = self.V1r#self.to_Bnode_r
        # Y_val_lin[idx_y] = 1
        # idx_y +=1
        # ##row 6 (f,f)
        # Y_row_lin[idx_y] = self.V1i
        # Y_col_lin[idx_y] = self.V1i#self.to_Bnode_i
        # Y_val_lin[idx_y] = 1
        # idx_y +=1

        ###IF I DO NOT USE THE STUFF BELOW IT SEEMS TO CONVERGE FAIRLY QUICKLY BUT THE ANGLES ARE OFF
        ###
        #row 5 (e,a)
        Y_row_lin[idx_y] = self.V1r
        Y_col_lin[idx_y] = self.from_Bnode_r
        Y_val_lin[idx_y] = -G
        idx_y +=1
        #row 5 (e,b)
        Y_row_lin[idx_y] = self.V1r
        Y_col_lin[idx_y] = self.from_Bnode_i
        Y_val_lin[idx_y] = B
        idx_y +=1
        # #row5 (e,c)
        Y_row_lin[idx_y] = self.V1r
        Y_col_lin[idx_y] = self.to_Bnode_r#self.to_Bnode_r
        Y_val_lin[idx_y] = 1
        idx_y +=1
        #row 5 (e,e)
        Y_row_lin[idx_y] = self.V1r
        Y_col_lin[idx_y] = self.V1r
        Y_val_lin[idx_y] = G
        idx_y +=1
        #row 5 (e,f)
        Y_row_lin[idx_y] = self.V1r
        Y_col_lin[idx_y] = self.V1i
        Y_val_lin[idx_y] = -B
        idx_y +=1
        
        ####ROW 6
        #row 6 (f,a)
        Y_row_lin[idx_y] = self.V1i
        Y_col_lin[idx_y] = self.from_Bnode_r
        Y_val_lin[idx_y] = -B
        idx_y +=1
        #row 6 (f,b)
        Y_row_lin[idx_y] = self.V1i
        Y_col_lin[idx_y] = self.from_Bnode_i
        Y_val_lin[idx_y] = -G
        idx_y +=1
        #row6 (f,d)
        Y_row_lin[idx_y] = self.V1i
        Y_col_lin[idx_y] = self.to_Bnode_i#self.to_Bnode_r
        Y_val_lin[idx_y] = 1
        idx_y +=1
        #row 6 (f,e)
        Y_row_lin[idx_y] = self.V1i
        Y_col_lin[idx_y] = self.V1r
        Y_val_lin[idx_y] = B
        idx_y +=1
        #row 6 (f,f)
        Y_row_lin[idx_y] = self.V1i
        Y_col_lin[idx_y] = self.V1i
        Y_val_lin[idx_y] = G
        idx_y +=1

        return idx_y#NEED TO ACCOUNT FOR THE LOSSES
        
    def initialize(self): #not sure if I need this
        pass