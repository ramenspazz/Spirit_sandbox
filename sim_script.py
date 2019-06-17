#file entry point
import sys
import os
#spirit inclues
from spirit import configuration, constants
from spirit import hamiltonian, geometry, io
from spirit import parameters, quantities
from spirit import simulation, state, system

def run_simulation(i_state, Mtd, Slvr, convThr, tS, hval, js, STTdir, hdir, K, Kdir, J, DMI, Dij, alphaD, x_size, y_size, read_config):
    rand_flag = False
    Skyrmion_size = 0
    calc_iter = 0
    usr_in = int(raw_input('Random or skyrmion(0/1): '))
    if usr_in == 1:
        Skyrmion_size = input("Enter Skyrmion size:")
    elif usr_in == 0:
        rand_flag = True

    #initialize initial conditions of simulation
    #hamiltonian.set_anisotropy(i_state,K,Kdir)
    print('Setting up initial state...\n')
    if not read_config:#if config file was set, dont set custom lattice size or BC
        geometry.set_n_cells(i_state,n_cells=[x_size, y_size, 1])
        hamiltonian.set_boundary_conditions(i_state, [1,1,0])
        hamiltonian.set_dmi(i_state,1,[DMI], 1)
    parameters.llg.set_convergence(i_state, convThr)
    parameters.llg.set_output_configuration(i_state,True,True,4)
    parameters.llg.set_timestep(i_state, tS)
    parameters.llg.set_iterations(i_state,1,1)
    parameters.llg.set_stt(i_state,True,0,STTdir)
    parameters.llg.set_damping(i_state, alphaD)
    hamiltonian.set_exchange(i_state,1,[J])
    hamiltonian.set_anisotropy(i_state,K,Kdir)
    print('Done!\n')

    if not rand_flag:
        if not read_config:
            configuration.plus_z(i_state) #set all spin to +z
        print('Initilizing Skyrmion...\n')
        configuration.skyrmion(i_state, Skyrmion_size, phase=-90) #initialize skyrmion
        print('Done!\n')
    else:
        configuration.random(i_state) #initialize random
    print('Generating starting configuration...\n')
    simulation.start(i_state,Mtd,Slvr)
    if os.path.isfile("start.ovf"):
        os.remove("start.ovf")
        pass

    print('Writing start.ovf...\n')
    io.chain_write(i_state,"start.ovf")
    simulation.stop_all
    print('Done!\n')
    usr_in = int(raw_input('preform pre-minimization 5000 itt?(0/1): '))
    print('Running simulation...\n')
    if usr_in == 1:
        #minimize
        print('Minimizing\n')
        parameters.llg.set_iterations(i_state,5000,5000)
        simulation.start(i_state,Mtd,0)
        if os.path.isfile("min.ovf"):
            os.remove("min.ovf")
            pass
        io.chain_write(i_state,"min.ovf")
        simulation.stop_all

    calc_iter = int(raw_input("set num itterations to run: "))
    parameters.llg.set_stt(i_state,True,js,STTdir)
    print('Running simulation...\n')
    if not read_config:#no config loaded, running sandbox
        itt_num = int(calc_iter / 10)
        parameters.llg.set_iterations(i_state,itt_num,itt_num)
        counter = 0
        while counter < 10:
            if (counter == 0) and (usr_in == 1):
                io.chain_read(i_state,"min.ovf")
            elif (counter == 0) and (usr_in == 0):
                io.chain_read(i_state,"start.ovf")
            else:
                io.chain_read(i_state,"grad_" + str(counter - 1) + ".ovf")
            simulation.start(i_state,Mtd,Slvr)
            
            if os.path.isfile("grad_" + str(counter) + ".ovf"):
                os.remove("grad_" + str(counter) + ".ovf")
                pass
            io.chain_write(i_state,"grad_" + str(counter) + ".ovf")
            simulation.stop_all
            counter += 1
            print('Sim' + str(counter) + '/10 done\n')
            pass #while counter < 10:
    else:#config was read
        parameters.llg.set_iterations(i_state,calc_iter,calc_iter)
        if os.path.isfile("r_cfg.ovf"):
                os.remove("r_cfg.ovf")
                pass
        simulation.start(i_state,Mtd,Slvr)
        io.chain_write(i_state, 'r_cfg.ovf')
        simulation.stop_all
    print('Done!')
    return(0) #run_simulation
