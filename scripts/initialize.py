
def initialize(v_init,slack, bus,generator, load):#:generator,transformer,branch, shunt,load): 
    #NOT SURE WHAT GOES HERE BUT HAVE TO THOUGHTS
    #1. COULD BE WERE WE DO SOMTHING LIKE DC OR AC INTIALIZATION AND GET FIRST V VECTOR GUESS
    # 2.WHERE WE CALL EACH OBJECT AND ASSING THE NODED INDEXES  
    #3. CALL EACH ELEMENT AND CALL THERE INITIALIZE FUNCTION
    for Buses in bus:
        Buses.initialize(v_init)
    for slack in slack:
        slack.initialize(v_init)
    for generators in generator:
        generators.initialize(v_init)
    #for transformers in transformer:
    #    transformers.initialize(v_init)
    #for branches in branch:
    #    branches.initialize(v_init)
    #for shunts in shunt:
    #    shunts.initialize(v_init)
    #for loads in load:
    #    loads.initialize(v_init)
    
    #do I need a line to specifically return v_init
    pass