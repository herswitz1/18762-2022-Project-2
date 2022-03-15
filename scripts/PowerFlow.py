import numpy as np
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

    def solve(self,Y_row_lin, Y_row_nonlin, Y_col_lin, Y_col_nonlin, Y_val_lin, Y_val_nonlin, J_vec_lin, J_vec_non_lin):
        #essitially takes in the Y and J matrix in order to solve 
        #V_k = np.linalg.solve(Y,J)
        Y_row = Y_row_lin + Y_row_nonlin
        Y_col = Y_col_lin + Y_col_nonlin
        Y_val = Y_val_lin + Y_val_nonlin
        J_vec = J_vec_lin + J_vec_non_lin
        Y_mtx = csr_matrix(Y_val, (Y_row, Y_col), shape=(len(Y_row),len(Y_col))) #CONVERTING TO A SPARSE MATRIX THAT CAN BE PUT INTO SOLVER
        V_k = spsolve(Y_mtx, J_vec)
        ##DO I NEED TO KEEP TRACK TO THE PREVIOUS V VECTOR IN ORDER TO CALCULAT THE ERROR

        return V_k
        

    def apply_limiting(self):
        #not sure what happens here possible huristics
        pass

    def check_error(self):
        #CHECKES THE NR TO SEE IF IT CONVERGES IF SO THIS IS OUR V VECTOR
        pass

    def stamp_linear(self,Y_row_lin,Y_col_lin,Y_val_lin,branch,shunt,transformer):
        #GO THROUGH EACH EACH CLASS OF OBJECT AND STAMP LINEAR PARTS 
        #EX:
        #for gen in generators:
        #generators.stamp_lin(Y,j)
        #for branch in branches:
        #branches.stamp_lin(Y,J)
        #etc
        for branches in branch:
            branches.sparse_stamp_lin(Y_row_lin,Y_col_lin,Y_val_lin,J_vec, idx_y, prev_v)#these are the other imputs that are needed in branches

        for shunts in shunt:
            shunts.sparse_stamp_lin()#NOT SURE ABOUT HOW TO HANDLE SHUNTS AT THE MOMENT
        
        for transformers in transformer:
            transformer.sparse_stamp_lin()

        ###not sure what this needs to return

    def stamp_nonlinear(self,Y_row_nonlin,Y_col_nonlin,Y_val_nonlin,generator,load,slack):
        #GO THROUGH EACH EACH CLASS OF OBJECT AND STAMP LINEAR PARTS 
        #EX:
        #for gen in generators:
        #generators.stamp_non_lin(Y,j)
        #for branch in branches:
        #branches.stamp_non_lin(Y,J)
        #etc

        for generators in generator:
            generators.sparse_stamp_non_lin()#NOT SURE ABOUT HOW TO HANDLE SHUNTS AT THE MOMENT
        
        for loads in load:
            loads.sparse_stamp_non_lin()

        for slack in slack: #NOT SURE IF SOMETHING IS WRONG WITH THIS CONFIGURATION
            slack.sparse_stamp_non_lin()

        #NOT SURE WHAT TO RETURN
        
        pass

    def run_powerflow(self,
                      v_init,
                      bus,###NOT SURE WHAT TO DO WITH BUS
                      slack,
                      generator,
                      transformer,
                      branch,
                      shunt,
                      load):
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

        # # # Copy v_init into the Solution Vectors used during NR, v, and the final solution vector v_sol # # #
        v = np.copy(v_init)
        v_sol = np.copy(v)

        # # # Stamp Linear Power Grid Elements into Y matrix # # #
        # TODO: PART 1, STEP 2.1 - Complete the stamp_linear function which stamps all linear power grid elements.
        #  This function should call the stamp_linear function of each linear element and return an updated Y matrix.
        #  You need to decide the input arguments and return values.
        ####I INTITIALIZE ROW,COL, AND VAL IN SOLVE SO I WILL PROBABLY NEED TO ADD MAKE LINEAR AND NON LINEAR COPIES AND GIVE THEM AS INPUTS
        self.stamp_linear(Y_row_lin,Y_col_lin,Y_val_lin,branch,shunt) ##FEEL LIKE THIS NEEDS TO BE FED SOME OTHER INFO, LIKE IDX_Y

        # # # Initialize While Loop (NR) Variables # # #
        # TODO: PART 1, STEP 2.2 - Initialize the NR variables
        err_max = None  # maximum error at the current NR iteration
        tol = None  # chosen NR tolerance
        NR_count = None  # current NR iteration

        # # # Begin Solving Via NR # # #
        # TODO: PART 1, STEP 2.3 - Complete the NR While Loop
        while err_max > tol:
            ##NEED SOME MECHANISM TO KEEP TRACK TO WHERE LIN AND NONLINEAR STOP AND END RESPECTIVELY SO THAT i CAN RESET NONLIN TO 0 AND RESTAMP IT


            # # # Stamp Nonlinear Power Grid Elements into Y matrix # # #
            # TODO: PART 1, STEP 2.4 - Complete the stamp_nonlinear function which stamps all nonlinear power grid
            #  elements. This function should call the stamp_nonlinear function of each nonlinear element and return
            #  an updated Y matrix. You need to decide the input arguments and return values.
            self.stamp_nonlinear(Y_row_nonlin,Y_col_nonlin,Y_val_nonlin,generator,load,slack)

            # # # Solve The System # # #
            # TODO: PART 1, STEP 2.5 - Complete the solve function which solves system of equations Yv = J. The
            #  function should return a new v_sol.
            #  You need to decide the input arguments and return values.
            self.solve(Y_row_lin, Y_row_nonlin, Y_col_lin, Y_col_nonlin, Y_val_lin, Y_val_nonlin, J_vec_lin, J_vec_non_lin)

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 1, STEP 2.6 - Finish the check_error function which calculates the maximum error, err_max
            #  You need to decide the input arguments and return values.
            self.check_error()

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 2, STEP 1 - Develop the apply_limiting function which implements voltage and reactive power
            #  limiting. Also, complete the else condition. Do not complete this step until you've finished Part 1.
            #  You need to decide the input arguments and return values.
            if self.enable_limiting and err_max > tol:
                self.apply_limiting()
            else:
                pass

        return v
