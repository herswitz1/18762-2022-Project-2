from __future__ import division
from itertools import count
from scripts.global_vars import global_vars
import numpy as np
from models.Buses import Buses

##PV BUS
##SOMETHING FEELS OFF ABOUT HOW I AM STAMPING MY J VECTOR
class Generators:
    _ids = count(0)
    RemoteBusGens = dict()
    RemoteBusRMPCT = dict()
    gen_bus_key_ = {}
    total_P = 0

    def __init__(self,
                 Bus,
                 P,
                 Vset,
                 Qmax,
                 Qmin,
                 Pmax,
                 Pmin,
                 Qinit,
                 RemoteBus,
                 RMPCT,
                 gen_type):
        """Initialize an instance of a generator in the power grid.

        Args:
            Bus (int): the bus number where the generator is located.
            P (float): the current amount of active power the generator is providing.
            Vset (float): the voltage setpoint that the generator must remain fixed at.
            Qmax (float): maximum reactive power
            Qmin (float): minimum reactive power
            Pmax (float): maximum active power
            Pmin (float): minimum active power
            Qinit (float): the initial amount of reactive power that the generator is supplying or absorbing.
            RemoteBus (int): the remote bus that the generator is controlling
            RMPCT (float): the percent of total MVAR required to hand the voltage at the controlled bus
            gen_type (str): the type of generator
        """
        self.Bus = Bus
        self.P = P
        self.Vset = Vset
        self.Qmax = Qmax
        self.Qmin = Qmin
        self.Pmax = Pmax
        self.Pmin = Pmin
        self. Qinit = Qinit
        self.RemoteBus = RemoteBus
        self.RMPCT = RMPCT
        self.gen_type = gen_type

        self.id = self._ids.__next__() #not sure if this should go before or after all my initializing
        self.node_Vrg = None
        self.node_Vig = None
        self.node_Qg = None
        ##THINK WE WILL HAVE TO ASSIGN 

        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
    def assign_nodes(self,bus): #struggling to figure out what to do here
        self.node_Vrg = bus[Buses.bus_key_[self.Bus]].node_Vr #trying to go inot buss find the correspdonding bus and then assiging nodes
        self.node_Vig = bus[Buses.bus_key_[self.Bus]].node_Vi
        self.node_Qg = bus[Buses.bus_key_[self.Bus]].node_Q   
            

    def sparse_stamp_non_lin(self,Y_row,Y_col, Y_val,J_vec, idx_y, prev_v): 
        Vrg_ig = ((np.square(prev_v[self.node_Vrg]))+(np.square(prev_v[self.node_Vig]))) #this is the sum of the previous real voltage square and imaginary voltage squared
        Irg = ((-self.P*prev_v[self.node_Vrg]) - (prev_v[self.node_Qg]*prev_v[self.node_Vig]))/(Vrg_ig) ##current value of real generator current
        Iig = ((-self.P*prev_v[self.node_Vig]) + (prev_v[self.node_Qg]*prev_v[self.node_Vrg]))/(Vrg_ig) ##current value of imaginary generator current
        ##calculating partials
        #real
        dIrg_dQg = -(prev_v[self.node_Vig])/(Vrg_ig)
        dIrg_dVrg = ((Vrg_ig)*-self.P - (-self.P*prev_v[self.node_Vrg] - prev_v[self.node_Qg]*prev_v[self.node_Vig])*(2*prev_v[self.node_Vrg]))/(np.square(Vrg_ig)) #dIrg/dVrg
        dIrg_dVig = ((Vrg_ig)*-prev_v[self.node_Qg] - (-self.P*prev_v[self.node_Vrg] - prev_v[self.node_Qg]*prev_v[self.node_Vig])*(2*prev_v[self.node_Vig]))/(np.square(Vrg_ig)) #dIrg/dVig
        #imaginary
        dIig_dQg = (prev_v[self.node_Vrg])/(Vrg_ig)
        dIig_dVrg = ((Vrg_ig)*(prev_v[self.node_Qg]) - (-self.P*prev_v[self.node_Vig] + prev_v[self.node_Qg]*prev_v[self.node_Vrg])*(2*prev_v[self.node_Vrg]))/(np.square(Vrg_ig)) #dIig/dVrg
        dIig_dVig = ((Vrg_ig)*-self.P - (-self.P*prev_v[self.node_Vig] + prev_v[self.node_Qg]*prev_v[self.node_Vrg])*(2*prev_v[self.node_Vig]))/(np.square(Vrg_ig)) #dIig/dVig
        
        ###Makeing stamps
        #real current row
        ##Y(i,i) 1
        Y_row[idx_y] = self.node_Vrg
        Y_col[idx_y] = self.node_Vrg
        Y_val[idx_y] = dIrg_dVrg
        #J(i)(probably only need Irg)(maybe instead i need to do node_Vrg)
        J_vec[self.node_Vrg] = -(Irg - (dIrg_dVrg*prev_v[self.node_Vrg]) - (dIrg_dVig*prev_v[self.node_Vig]) - (dIrg_dQg*prev_v[self.node_Qg]))#j stamp for real current(may not need all of these terms)
        idx_y += 1
        ##Y(i,j) 2
        Y_row[idx_y] = self.node_Vrg
        Y_col[idx_y] = self.node_Vig
        Y_val[idx_y] = dIrg_dVig
        idx_y +=1
        ##Y(i,k) 3
        Y_row[idx_y] = self.node_Vrg
        Y_col[idx_y] = self.node_Qg
        Y_val[idx_y] = dIrg_dQg
        idx_y +=1

        ##imaginary current row
        ##Y(j,i) 4
        Y_row[idx_y] = self.node_Vig
        Y_col[idx_y] = self.node_Vrg
        Y_val[idx_y] = dIig_dVrg
        ##J(j)(probably only need Iig)
        J_vec[self.node_Vig] = -(Iig - (dIig_dVrg*prev_v[self.node_Vrg]) - (dIig_dVig*prev_v[self.node_Vig]))#J stamp for imaginary current
        idx_y += 1
        ##Y(j,j) 5
        Y_row[idx_y] = self.node_Vig
        Y_col[idx_y] = self.node_Vig
        Y_val[idx_y] = -dIig_dVig
        idx_y +=1
        ##Y(j,k) 6
        Y_row[idx_y] = self.node_Vig
        Y_col[idx_y] = self.node_Qg
        Y_val[idx_y] = dIig_dQg
        idx_y +=1
        
        ##Reactivepower row
        ##Y(g,i) 7
        Y_row[idx_y] = self.node_Qg
        Y_col[idx_y] = self.node_Vrg
        Y_val[idx_y] = 2*prev_v[self.node_Vrg]
        
        ##J(g)(proaboly only needthe square)
        J_vec[self.node_Qg] = -(np.square(self.Vset) -(2*prev_v[self.node_Vrg]*prev_v[self.node_Vrg]) -(2*prev_v[self.node_Vig]*prev_v[self.node_Vig]))
        
        idx_y +=1
        
        #Y(g,j) 8
        Y_row[idx_y] = self.node_Qg
        Y_col[idx_y] = self.node_Vig
        Y_val[idx_y] = 2*prev_v[self.node_Vig]
        idx_y +=1
        
        return idx_y
    def initialize(self,Vinit): ##MENTIONED SOMETHNG ABOUT JUST SETTING AS 1S AND 0S
        #Vinit[self.node_Vrg] = 1#These need to be something else
        #Vinit[self.node_Vig] = 1
        Vinit[self.node_Qg] = self.Qinit
        
        pass
        