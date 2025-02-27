from parsers.parser import parse_raw
from scripts.PowerFlow import PowerFlow
from scripts.process_results import process_results
from scripts.initialize import initialize
from models.Buses import Buses
import numpy as np


def solve(TESTCASE, SETTINGS):
    """Run the power flow solver.

    Args:
        TESTCASE (str): A string with the path to the test case.
        SETTINGS (dict): Contains all the solver settings in a dictionary.

    Returns:
        None
    """
    # TODO: PART 1, STEP 0 - Initialize all the model classes in the models directory (models/) and familiarize
    #  yourself with the parameters of each model. Use the docs/DataFormats.pdf for assistance.

    # # # Parse the Test Case Data # # #
    case_name = TESTCASE
    parsed_data = parse_raw(case_name)

    # # # Assign Parsed Data to Variables # # #
    bus = parsed_data['buses']
    slack = parsed_data['slack']
    generator = parsed_data['generators']
    transformer = parsed_data['xfmrs']
    branch = parsed_data['branches']
    shunt = parsed_data['shunts']
    load = parsed_data['loads']

    # # # Solver Settings # # #
    tol = SETTINGS['Tolerance']  # NR solver tolerance
    max_iters = SETTINGS['Max Iters']  # maximum NR iterations
    enable_limiting = SETTINGS['Limiting']  # enable/disable voltage and reactive power limiting

    # # # Assign System Nodes Bus by Bus # # #
    # We can use these nodes to have predetermined node number for every node in our Y matrix and J vector.
    bus_counter = 0

    for ele in bus:
        Buses.bus_key_[ele.Bus] = bus_counter
        bus_counter +=1
        ele.assign_nodes()

    # Assign any slack nodes
    for ele in slack:
        ele.assign_nodes(bus)

    for ele in generator:
        ele.assign_nodes(bus)
    for ele in transformer:
        ele.assign_nodes(bus)
    for ele in branch:
        ele.assign_nodes(bus)
    for ele in shunt:
        ele.assign_nodes(bus)
    for ele in load:
        ele.assign_nodes(bus)

    # # # Initialize Solution Vector - V and Q values # # #

    # determine the size of the Y matrix by looking at the total number of nodes in the system
    size_Y = Buses._node_index.__next__()
    #size_Y = size_Y-1
    
    ###FEEL LIKE I NEED SOMETHING LIKE Y_ROW_LIN = COPY(ROW), AND THEN SAME FOR COL AND VAL AS WELL AS NONLINEAR

    # TODO: PART 1, STEP 1 - Complete the function to initialize your solution vector v_init.
    v_init = np.zeros(size_Y)  # create a solution vector filled with zeros of size_Y
    #print(v_init)
    initialize(v_init,slack,bus,generator)

    # # # Run Power Flow # # #
    powerflow = PowerFlow(case_name, tol, max_iters, enable_limiting)

    # TODO: PART 1, STEP 2 - Complete the PowerFlow class and build your run_powerflow function to solve Equivalent
    #  Circuit Formulation powerflow. The function will return a final solution vector v. Remove run_pf and the if
    #  condition once you've finished building your solver.
    NR_counter = 0
    #INITIALIZES EMPYT ARRAYS THAT KEEP TRACK OF EFFICENCY
    Dense_eff = []
    Sparse_eff = []
    run_pf = True
    if run_pf:
        v = powerflow.run_powerflow(v_init, bus, slack, generator, transformer, branch, shunt, load, size_Y, Dense_eff, Sparse_eff)
        #print(v)
        
    # # # Process Results # # #
    # TODO: PART 1, STEP 3 - Write a process_results function to compute the relevant results (voltages, powers,
    #  and anything else of interest) and find the voltage profile (maximum and minimum voltages in the case).
    #  You can decide which arguments to pass to this function yourself.
    #print(NR_counter)
    process_results(v, bus,Dense_eff,Sparse_eff)
