import numpy as np
from numpy.linalg import solve
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

class PowerFlow:

    def __init__(self,
                 case_name,
                 tol,
                 max_iters,
                 enable_limiting):
        """Initialize the PowerFlow instance.

        Args:
            case_name (str): A string with the path to the test case.
            tol (float): The chosen NR tolerance.
            max_iters (int): The maximum number of NR iterations.
            enable_limiting (bool): A flag that indicates if we use voltage limiting or not in our solver.
        """
        # Clean up the case name string
        case_name = case_name.replace('.RAW', '')
        case_name = case_name.replace('testcases/', '')

        self.case_name = case_name
        self.tol = tol
        self.max_iters = max_iters
        self.enable_limiting = enable_limiting

    def solve(self,Y_row_lin, Y_row_nonlin, Y_col_lin, Y_col_nonlin, Y_val_lin, Y_val_nonlin, J_vec_lin, J_vec_non_lin,size_Y):
        #essitially takes in the Y and J matrix in order to solve 
        #V_k = np.linalg.solve(Y,J)
        Y_row = Y_row_lin + Y_row_nonlin
        Y_col = Y_col_lin + Y_col_nonlin
        Y_val = Y_val_lin + Y_val_nonlin
        J_vec = J_vec_lin + J_vec_non_lin
        #maybe need a J_val vect and a J col vector
        Y_mtx = csr_matrix((Y_val, (Y_row, Y_col)), shape=(size_Y,size_Y)) #CONVERTING TO A SPARSE MATRIX THAT CAN BE PUT INTO SOLVER
        print(type(Y_mtx))
        print(type(J_vec))
        Ydense = Y_mtx.todense() 
        #print(Ydense)

        ####found this code online in order to check for 0 row or 0 cols
        check_row = np.all((Ydense == 0), axis=1)
        print('Rows that contain only zero:')
        for i in range(len(check_row)):
            if check_row[i]:
                print('Row: ', i)
        # check_col = np.all((Ydense == 0), axis=0)
        # print('Columns that contain only zero:')
        # for j in range(len(check_col)):
        #     if check_col[j]:
        #         print('Column: ', j)
        ################################

        V_k = spsolve(Y_mtx, J_vec)
        #V_k = solve(Ydense, J_vec)
        ##DO I NEED TO KEEP TRACK TO THE PREVIOUS V VECTOR IN ORDER TO CALCULAT THE ERROR

        return V_k
        

    def apply_limiting(self):
        #not sure what happens here possible huristics
        pass

    def check_error(self,v_current,v_prev,err_max):
        #CHECKES THE NR TO SEE IF IT CONVERGES IF SO THIS IS OUR V VECTOR
        hist_nr =np.amax(np.abs(v_prev))
        err_max = np.abs(np.amax(np.abs(v_current))-hist_nr)

        v_prev = v_current

        return err_max
        

    def stamp_linear(self,Y_row_lin,Y_col_lin,Y_val_lin,branch,shunt,transformer,prev_v, idx_y):
        #GO THROUGH EACH EACH CLASS OF OBJECT AND STAMP LINEAR PARTS 
        #EX:
        #for gen in generators:
        #generators.stamp_lin(Y,j)
        #for branch in branches:
        #branches.stamp_lin(Y,J)
        #etc
        #idx_y = 0
        for branches in branch:
           idx_y= branches.sparse_stamp_lin(Y_row_lin,Y_col_lin,Y_val_lin, idx_y)#these are the other imputs that are needed in branches

        for shunts in shunt:
            idx_y = shunts.sparse_stamp_lin(Y_row_lin, Y_col_lin,Y_val_lin, idx_y)#NOT SURE ABOUT HOW TO HANDLE SHUNTS AT THE MOMENT
        
        #for transformers in transformer:
        #    transformers.sparse_stamp_lin()

        ###not sure what this needs to return
        return idx_y

    def stamp_nonlinear(self,Y_row_non_lin,Y_col_non_lin,Y_val_non_lin,J_vec_non_lin, generator,load,slack, prev_v,idx_y):
        #GO THROUGH EACH EACH CLASS OF OBJECT AND STAMP LINEAR PARTS 
        #EX:
        #for gen in generators:
        #generators.stamp_non_lin(Y,j)
        #for branch in branches:
        #branches.stamp_non_lin(Y,J)
        #etc
        #idx_y = 0 #not sure about this

        for generators in generator:
            idx_y=generators.sparse_stamp_non_lin(Y_row_non_lin,Y_col_non_lin, Y_val_non_lin,J_vec_non_lin, idx_y, prev_v)#NOT SURE ABOUT HOW TO HANDLE SHUNTS AT THE MOMENT
             
        for loads in load:
            idx_y =loads.sparse_stamp_non_lin(Y_row_non_lin, Y_col_non_lin,Y_val_non_lin,J_vec_non_lin, idx_y,prev_v)

        for slack in slack: #NOT SURE IF SOMETHING IS WRONG WITH THIS CONFIGURATION
            idx_y = slack.sparse_stamp_non_lin(Y_row_non_lin, Y_col_non_lin, Y_val_non_lin, J_vec_non_lin, idx_y, prev_v)

        #NOT SURE WHAT TO RETURN
        
        #return idx_y

    def run_powerflow(self,
                      v_init,
                      bus,###NOT SURE WHAT TO DO WITH BUS
                      slack,
                      generator,
                      transformer,
                      branch,
                      shunt,
                      load,
                      size_Y):
        """Runs a positive sequence power flow using the Equivalent Circuit Formulation.

        Args:
            v_init (np.array): The initial solution vector which has the same number of rows as the Y matrix.
            bus (list): Contains all the buses in the network as instances of the Buses class.
            slack (list): Contains all the slack generators in the network as instances of the Slack class.
            generator (list): Contains all the generators in the network as instances of the Generators class.
            transformer (list): Contains all the transformers in the network as instance of the Transformers class.
            branch (list): Contains all the branches in the network as instances of the Branches class.
            shunt (list): Contains all the shunts in the network as instances of the Shunts class.
            load (list): Contains all the loads in the network as instances of the Load class.

        Returns:
            v(np.array): The final solution vector.

        """
        #CREATING THE ARRAYS TO STORE OUR SPARSE MATRIXES(POSSIBLY CALL IN INITIALIZE)
        new_size = size_Y*10
        row = np.zeros(size_Y*10)
        col = np.zeros(size_Y*10)
        val = np.zeros(size_Y*10)
        # Y_row_lin = []
        # Y_col_lin = []
        # Y_val_lin =[]
        # Y_row_non_lin = []
        # Y_col_non_lin = []
        # Y_val_non_lin = []
        # J_vec_lin = []
        # J_vec_non_lin = []
        #######WHAT i THINK IT SHOULD BE
        # Y_row_lin = np.zeros(size_Y)
        # Y_col_lin = np.zeros(size_Y)
        # Y_val_lin =np.zeros(size_Y)
        # Y_row_non_lin = np.zeros(size_Y)
        # Y_col_non_lin = np.zeros(size_Y)
        # Y_val_non_lin = np.zeros(size_Y)
        # J_vec_lin = np.zeros(size_Y)
        # J_vec_non_lin = np.zeros(size_Y)
        ##############
        Y_row_lin = np.zeros(new_size)
        Y_col_lin = np.zeros(new_size)
        Y_val_lin =np.zeros(new_size)
        Y_row_non_lin = np.zeros(new_size)
        Y_col_non_lin = np.zeros(new_size)
        Y_val_non_lin = np.zeros(new_size)
        J_vec_lin = np.zeros(size_Y)
        J_vec_non_lin = np.zeros(size_Y)
        ##############

        # # # Copy v_init into the Solution Vectors used during NR, v, and the final solution vector v_sol # # #
        v = np.copy(v_init)
        v_sol = np.copy(v)
        idx_y = 0
        # # # Stamp Linear Power Grid Elements into Y matrix # # #
        # TODO: PART 1, STEP 2.1 - Complete the stamp_linear function which stamps all linear power grid elements.
        #  This function should call the stamp_linear function of each linear element and return an updated Y matrix.
        #  You need to decide the input arguments and return values.
        ####I INTITIALIZE ROW,COL, AND VAL IN SOLVE SO I WILL PROBABLY NEED TO ADD MAKE LINEAR AND NON LINEAR COPIES AND GIVE THEM AS INPUTS
        idx_y= self.stamp_linear(Y_row_lin,Y_col_lin,Y_val_lin,branch,shunt, transformer,v_init,idx_y) ##FEEL LIKE THIS NEEDS TO BE FED SOME OTHER INFO, LIKE IDX_Y

        # # # Initialize While Loop (NR) Variables # # #
        # TODO: PART 1, STEP 2.2 - Initialize the NR variables
        err_max = 1#really bad intial guess  # maximum error at the current NR iteration
        tol = self.tol#settings["Tolerance"]#None  # chosen NR tolerance
        NR_count = 0  # current NR iteration(HOW SHOULD WE USE THIS?)

        # # # Begin Solving Via NR # # #
        # TODO: PART 1, STEP 2.3 - Complete the NR While Loop
        Hidx_y = idx_y
        while err_max > tol and NR_count <100:#20 should be setting["max iter"]
            ##NEED SOME MECHANISM TO KEEP TRACK TO WHERE LIN AND NONLINEAR STOP AND END RESPECTIVELY SO THAT i CAN RESET NONLIN TO 0 AND RESTAMP IT


            # # # Stamp Nonlinear Power Grid Elements into Y matrix # # #
            # TODO: PART 1, STEP 2.4 - Complete the stamp_nonlinear function which stamps all nonlinear power grid
            #  elements. This function should call the stamp_nonlinear function of each nonlinear element and return
            #  an updated Y matrix. You need to decide the input arguments and return values.
            self.stamp_nonlinear(Y_row_non_lin,Y_col_non_lin,Y_val_non_lin,J_vec_non_lin, generator,load,slack,v_sol,idx_y)#feel like something is off

            # # # Solve The System # # #
            # TODO: PART 1, STEP 2.5 - Complete the solve function which solves system of equations Yv = J. The
            #  function should return a new v_sol.
            #  You need to decide the input arguments and return values.
            v = self.solve(Y_row_lin, Y_row_non_lin, Y_col_lin, Y_col_non_lin, Y_val_lin, Y_val_non_lin, J_vec_lin, J_vec_non_lin,size_Y)

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 1, STEP 2.6 - Finish the check_error function which calculates the maximum error, err_max
            #  You need to decide the input arguments and return values.
            err_max = self.check_error(v, v_sol, err_max)
            print(err_max)

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 2, STEP 1 - Develop the apply_limiting function which implements voltage and reactive power
            #  limiting. Also, complete the else condition. Do not complete this step until you've finished Part 1.
            #  You need to decide the input arguments and return values.
            if self.enable_limiting and err_max > tol:
                self.apply_limiting()
            else:
                pass
            NR_count +=1
            Y_row_non_lin = np.zeros(new_size)
            Y_col_non_lin = np.zeros(new_size)
            Y_val_non_lin = np.zeros(new_size)
            J_vec_non_lin = np.zeros(size_Y)
            idx_y = Hidx_y
            v_sol = v
        return v
