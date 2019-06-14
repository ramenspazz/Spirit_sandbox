#file entry point
import sys
import os
#spirit inclues
from spirit import configuration, constants
from spirit import hamiltonian, geometry, io
from spirit import parameters, quantities
from spirit import simulation, state, system

def run_simulation(i_state, Mtd, Slvr, convThr, tS, hval, js, STTdir, hdir, K, Kdir, J, DMI, Dij, alphaD, x_size, y_size):
    rand_flag = False
    Skyrmion_size = 0
    usr_in = int(raw_input('Random or skyrmion(0/1): '))
    if usr_in == 1:
        Skyrmion_size = input("Enter Skyrmion size:")
    elif usr_in == 0:
        rand_flag = True
    calc_iter = int(raw_input("set num itterations to run: "))

    #initialize initial conditions of simulation
    #hamiltonian.set_anisotropy(i_state,K,Kdir)
    geometry.set_n_cells(i_state,n_cells=[x_size, y_size, 1])
    parameters.llg.set_output_configuration(i_state,True,True,4)
    parameters.llg.set_timestep(i_state, tS)
    parameters.llg.set_iterations(i_state,1,1)
    parameters.llg.set_stt(i_state,True,0,STTdir)
    parameters.llg.set_damping(i_state, alphaD)
    hamiltonian.set_exchange(i_state,1,[J])
    hamiltonian.set_dmi(i_state,1,[DMI], 1) 
    hamiltonian.set_boundary_conditions(i_state, [1,1,0])

    if not rand_flag:
        configuration.plus_z(i_state) #set all spin to +z
        configuration.skyrmion(i_state, Skyrmion_size, phase=-90) #initialize skyrmion
    else:
        configuration.random(i_state) #initialize skyrm.

    simulation.start(i_state,Mtd,Slvr)
    if os.path.isfile("Start.txt"):
        os.remove("Start.txt")
        pass
    io.chain_write(i_state,"Start.txt")
    simulation.stop_all

    usr_in = int(raw_input('preform pre-minimization 5000 itt?(0/1): '))
    print('Running simulation...')
    if usr_in == 1:
        #minimize
        print('Minimizing\n')
        parameters.llg.set_iterations(i_state,5000,5000)
        simulation.start(i_state,Mtd,0)
        if os.path.isfile("Min.txt"):
            os.remove("Min.txt")
            pass
        io.chain_write(i_state,"Min.txt")
        simulation.stop_all

    itt_num = int(calc_iter / 10)
    parameters.llg.set_iterations(i_state,itt_num,itt_num)
    parameters.llg.set_stt(i_state,True,js,STTdir)
    counter = 0

    while counter < 10:
        if (counter == 0) and (usr_in == 1):
            io.chain_read(i_state,"Min.txt")
        elif (counter == 0) and (usr_in == 0):
            io.chain_read(i_state,"Start.txt")
        else:
            io.chain_read(i_state,"Grad_" + str(counter - 1) + ".txt")
        simulation.start(i_state,Mtd,Slvr)
        
        if os.path.isfile("Grad_" + str(counter) + ".txt"):
            os.remove("Grad_" + str(counter) + ".txt")
            pass
        io.chain_write(i_state,"Grad_" + str(counter) + ".txt")
        simulation.stop_all
        counter += 1
        print('Sim' + str(counter) + '/10 done\n')
        pass #while counter < 10:
    print('Done!')
    return(0) #run_simulation
