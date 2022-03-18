from __future__ import division
from itertools import count
from models.Buses import Buses

class Shunts:
    _ids = count(0)

    def __init__(self,
                 Bus,
                 G_MW,
                 B_MVAR,
                 shunt_type,
                 Vhi,
                 Vlo,
                 Bmax,
                 Bmin,
                 Binit,
                 controlBus,
                 flag_control_shunt_bus=False,
                 Nsteps=[0],
                 Bstep=[0]):

        """ Initialize a shunt in the power grid.
        Args:
            Bus (int): the bus where the shunt is located
            G_MW (float): the active component of the shunt admittance as MW per unit voltage
            B_MVAR (float): reactive component of the shunt admittance as  MVar per unit voltage
            shunt_type (int): the shunt control mode, if switched shunt
            Vhi (float): if switched shunt, the upper voltage limit
            Vlo (float): if switched shunt, the lower voltage limit
            Bmax (float): the maximum shunt susceptance possible if it is a switched shunt
            Bmin (float): the minimum shunt susceptance possible if it is a switched shunt
            Binit (float): the initial switched shunt susceptance
            controlBus (int): the bus that the shunt controls if applicable
            flag_control_shunt_bus (bool): flag that indicates if the shunt should be controlling another bus
            Nsteps (list): the number of steps by which the switched shunt should adjust itself
            Bstep (list): the admittance increase for each step in Nstep as MVar at unity voltage
        """
        self.Bus = Bus
        self.G_MW = G_MW
        self.B_MVAR = B_MVAR
        self.shunt_type = shunt_type
        self.Vhi = Vhi
        self.Vlo = Vlo
        self.Bmax = Bmax
        self.Bmin = Bmin
        self.Binit = Binit
        self.controlBus = controlBus
        self.flag_control_shunt_bus = flag_control_shunt_bus
        self.Nsteps = Nsteps
        self.Bstep = Bstep
        self.id = self._ids.__next__()#NOT SURE IF THIS SHOULD GO AT BEGINNING OR END
        self.from_sh_r = None
        self.from_sh_i = None
        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
    def assign_nodes(self,bus): #What I currently have is wrong
        self.from_sh_r = bus[Buses.bus_key_[self.bus]].node_Vr#Vnr (a)
        self.from_sh_i = bus[Buses.bus_key_[self.bus]].node_Vi#Vni (c)
        pass

    def sparse_stamp_lin(self, Y_row, Y_col,Y_val, idx_y): #not sure if I need this
        #Real
        Y_row[idx_y]= self.from_sh_r
        Y_col[idx_y]= self.from_sh_r
        Y_val[idx_y] = self.G_MW
        idx_y += 1
        Y_row[idx_y]= self.from_sh_r
        Y_col[idx_y]= self.from_sh_i
        Y_val[idx_y] = -self.B_MVAR
        idx_y += 1
        #imagniary
        Y_row[idx_y]= self.from_sh_i
        Y_col[idx_y]= self.from_sh_r
        Y_val[idx_y] = self.B_MVAR
        idx_y += 1
        Y_row[idx_y]= self.from_sh_i
        Y_col[idx_y]= self.from_sh_i
        Y_val[idx_y] = -self.G_MW
        idx_y += 1
        #return idx_y

    def stamp_non_lin(self): #not sure if I need this
        pass
        
    def initialize(self,Vinit): 
        Vinit[self.from_sh_r] = 0
        Vinit[self.from_sh_i] = 0
        pass