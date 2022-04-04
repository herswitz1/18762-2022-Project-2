
def initialize(v_init,slack, bus,generator):
    for Buses in bus:
        Buses.initialize(v_init)
    for slack in slack:
        slack.initialize(v_init)
    for generators in generator:
        generators.initialize(v_init)
    
    pass