import numpy as np
from scipy.io import loadmat
from models.Buses import Buses
from tabulate import tabulate
def process_results(v, bus, Dense_eff, Sparse_eff):
    ##selecting which case considering
    #4 bus case C:\Users\hersc\OneDrive\Desktop\matpower\matpower7.1\mp_r_4.mat
    #matpower_data = loadmat(r'C:\Users\hersc\OneDrive\Desktop\matpower\matpower7.1\mp_r_4.mat')
    #14 Bus case C:\Users\hersc\OneDrive\Desktop\matpower\matpower7.1\mp_r_14.mat
    matpower_data = loadmat(r'testcases/result_14case')#this is for the 14 bus case
    #118 bus case C:\Users\hersc\OneDrive\Desktop\matpower\matpower7.1\mp_r_118.mat
    #matpower_data = loadmat(r'C:\Users\hersc\OneDrive\Desktop\matpower\matpower7.1\mp_r_118.mat')
    ##getting the desired infromation out of file
    ###################################################
    ##IMPORTANT:EACH TIME CHANGINGING CHASE NEED TO ADJUST 'RESULT_14CASE' TO NEW CASE CONSIDERING
    ###################################################
    mp_res = matpower_data['result_14case']['bus'][0,0]
    #putting desired information into vectors
    mp_res_mag = np.zeros(len(mp_res))
    mp_res_ang = np.zeros(len(mp_res))
    for i in range(len(mp_res)):
        mp_res_mag[i]=mp_res[i,7]
        mp_res_ang[i]=mp_res[i,8]

    #print(mp_res_mag)
    #print(mp_res_ang)

    v_pross_mag = np.zeros(len(mp_res))
    v_pross_ang = np.zeros(len(mp_res))
    Bus_num = np.zeros(len(mp_res))
    #getting reported values from simulation
    for Buses in bus:
        if Buses.Type == 1:
            V_mag = np.sqrt(np.square(v[Buses.node_Vr]) + np.square(v[Buses.node_Vi]))
            V_ang = np.rad2deg(np.arctan(v[Buses.node_Vi]/v[Buses.node_Vr]))
            print(str(Buses.Bus)+ ' is a PQ bus with' + ' voltage mag=' +str(V_mag) + ' and angle=' + str(V_ang))
            v_pross_mag[Buses.Bus-1] = V_mag
            v_pross_ang[Buses.Bus-1] = V_ang
            Bus_num[Buses.Bus-1] = Buses.Bus
        elif Buses.Type == 3:
            V_mag = np.sqrt(np.square(v[Buses.node_Vr]) + np.square(v[Buses.node_Vi]))
            V_ang = np.rad2deg(np.arctan(v[Buses.node_Vi]/v[Buses.node_Vr]))
            print(str(Buses.Bus)+ ' is a slack bus with' + ' voltage mag=' +str(V_mag) + ' and angle=' + str(V_ang))
            v_pross_mag[Buses.Bus-1] = V_mag
            v_pross_ang[Buses.Bus-1] = V_ang
            Bus_num[Buses.Bus-1] = Buses.Bus
        else:
            V_mag = np.sqrt(np.square(v[Buses.node_Vr]) + np.square(v[Buses.node_Vi]))
            V_ang = np.rad2deg(np.arctan(v[Buses.node_Vi]/v[Buses.node_Vr]))
            print(str(Buses.Bus)+ ' is a generator bus with' + ' voltage mag=' +str(V_mag) + ' and angle=' + str(V_ang))
            v_pross_mag[Buses.Bus-1] = V_mag
            v_pross_ang[Buses.Bus-1] = V_ang
            Bus_num[Buses.Bus-1] = Buses.Bus
    #print(v_pross_mag)
    #print(v_pross_ang)

    #find max an min values
    sim_max_mag = np.amax(v_pross_mag)
    sim_min_mag = np.amin(v_pross_mag)
    sim_max_ang = np.amax(v_pross_ang)
    sim_min_ang = np.amin(v_pross_ang)

    #calculating the average percent difference
    mag_avg_perc_diff = (np.abs(np.abs(mp_res_mag)-np.abs(v_pross_mag))/((np.abs(mp_res_mag)+np.abs(v_pross_mag))/2))*100#(np.abs(mp_res_mag-v_pross_mag)/((mp_res_mag+v_pross_mag)/2))*100
    ang_avg_perc_diff =(np.abs(np.abs(mp_res_ang)-np.abs(v_pross_ang))/((np.abs(mp_res_ang)+np.abs(v_pross_ang))/2))*100#(np.abs(mp_res_ang-v_pross_ang)/((mp_res_ang+v_pross_ang)/2))*100 #
    avg_mag_avg = sum(mag_avg_perc_diff)/len(mag_avg_perc_diff)
    avg_ang_avg = sum(ang_avg_perc_diff[1:])/len(ang_avg_perc_diff-1)
    #print(mag_avg_perc_diff)
    #print(ang_avg_perc_diff)

    #Sparsity performance
    Avg_dense_eff = sum(Dense_eff)/len(Dense_eff)
    Avg_spars_eff = sum(Sparse_eff)/len(Sparse_eff)

    #printing results
    print("RESULTS FOR "+ str(len(mp_res))+ " BUS SIMULATION VS MATPOWER")
    print("Average compuational performance with dense matrices: " + str(Avg_dense_eff))
    print("Average compuational performance with sparse matrices: " + str(Avg_spars_eff))
    print("simulation maximum magnitude "+ str(sim_max_mag))
    print("simulation maximum angle "+ str(sim_max_ang))
    print("simulation minimum magnitude "+ str(sim_min_mag))
    print("simulation minimum angle "+ str(sim_min_ang))
    print("Average of mag_avg_per_diff " + str(avg_mag_avg))
    print("Average of ang_avg_per_diff " + str(avg_ang_avg))
    info = {'Bus':Bus_num,"Sim mag":v_pross_mag , "Matpower mag":mp_res_mag,'Mag avg perc diff':mag_avg_perc_diff,"Sim ang":v_pross_ang , "Matpower ang":mp_res_ang,'Ang avg perc diff':ang_avg_perc_diff,}
    print(tabulate(info,headers='keys', tablefmt='fancy_grid'))
