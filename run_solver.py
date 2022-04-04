
from scripts.Solve import solve


# path to the grid network RAW file
#casename = 'testcases/PEGASE-13659_flat_start.RAW'
#casename = 'testcases/GS-4_prior_solution.RAW'
casename = 'testcases/IEEE-14_prior_solution.RAW'
#casename = 'testcases/IEEE-118_prior_solution.RAW'
#casename = 'testcases/PEGASE-9241_flat_start.RAW'
# the settings for the solver
settings = {
    "Tolerance": 1E-5,
    "Max Iters": 1000,
    "Limiting":  True,
}

# run the solver
solve(casename, settings)