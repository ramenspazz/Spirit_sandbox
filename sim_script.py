#file entry point
import sys
import os
#spirit inclues
from spirit import configuration, constants
from spirit import hamiltonian, geometry, io
from spirit import parameters, quantities
from spirit import simulation, state, system

def run_simulation(i_state, Mtd, Slvr, convThr, tS, js, K, Kdir, J, DMI, Dij, alphaD, x_size, y_size, read_config):
    rand_flag = False
    Skyrmion_size = 0
    calc_iter = 0
    STTdir = [1, 0, 0] # polarization direction
    hdir = [0.0, 0.0, 1.0] # magnetic Field direction

    usr_in = int(raw_input('Set None or Random or skyrmion(-1/0/1): '))
    if usr_in == 1:
        Skyrmion_size = input("Enter Skyrmion size:")
    elif usr_in == 0:
        rand_flag = True

    #initialize initial conditions of simulation
    #hamiltonian.set_anisotropy(i_state,K,Kdir)
    print('Setting up initial state...\n')
    if not read_config:#if config file was set, dont set custom lattice size or BC
        hamiltonian.set_boundary_conditions(i_state, [1,1,0])
        hamiltonian.set_dmi(i_state,1,[DMI], 1)
        geometry.set_n_cells(i_state,[x_size, y_size, 1])
    parameters.llg.set_temperature(i_state,0.0)
    parameters.llg.set_damping(i_state, alphaD)
    parameters.llg.set_convergence(i_state, convThr)
    parameters.llg.set_output_configuration(i_state,True,True,4)
    hamiltonian.set_field(i_state,hval,hdir)
    parameters.llg.set_stt(i_state,True,0,STTdir)
    hamiltonian.set_anisotropy(i_state,K,Kdir)
    parameters.llg.set_timestep(i_state, tS)
    parameters.llg.set_iterations(i_state,1,1)

    print('Done!\n')

    if not rand_flag:
        if not read_config:
            configuration.plus_z(i_state) #set all spin to +z
        print('Initilizing Skyrmion...\n')
        configuration.skyrmion(i_state, Skyrmion_size, phase=-90) #initialize skyrmion
        if os.path.isfile("start.ovf"):
            os.remove("start.ovf")
            pass
        pass
    else:
        print('Initilizing random state...\n')
        configuration.random(i_state) #initialize random
        pass
    print('Done!\n')
    io.chain_write(i_state,"start.ovf")
    print('Wrote start.ovf\n')
    
    usr_in = int(raw_input('preform minimization?(0/1): '))
    if usr_in == 1:
        calc_iter = int(raw_input("set num itterations to minimize: "))
        hval = float(raw_input("enter H field strength:")) # magnetic Field direction
        parameters.llg.set_temperature(i_state,0.0)
        parameters.llg.set_damping(i_state, alphaD)
        parameters.llg.set_convergence(i_state, convThr)
        parameters.llg.set_output_configuration(i_state,True,True,4)
        hamiltonian.set_field(i_state,hval,hdir)
        parameters.llg.set_stt(i_state,True,0,STTdir)
        hamiltonian.set_anisotropy(i_state,K,Kdir)
        parameters.llg.set_timestep(i_state, tS)
        #minimize
        print('Minimizing\n')
        parameters.llg.set_iterations(i_state,calc_iter,calc_iter)
        simulation.start(i_state,Mtd,0)
        if os.path.isfile("minf.ovf"):
            os.remove("min.ovf")
            pass
        io.chain_write(i_state,"min.ovf")
        simulation.stop_all
    
    sim_count = 0
    while calc_iter != -1:  
        calc_iter = int(raw_input("set num itterations to run, -1 to quit: "))

        if calc_iter == -1:
            #return to top of loop and exit
            continue

        hval = float(raw_input("enter H field strength:")) # magnetic Field direction

        js = float(raw_input("enter current val:")) # Spin Torque magnitude EDIT SET TO 0 norm 3e-04
        for i in range(len(STTdir)):
            STTdir[i] = float(raw_input('input Polerization element: '))

        parameters.llg.set_stt(i_state,True,js,STTdir)
        parameters.llg.set_temperature(i_state,0.0)
        parameters.llg.set_damping(i_state, alphaD)
        parameters.llg.set_convergence(i_state, convThr)
        parameters.llg.set_output_configuration(i_state,True,True,4)
        hamiltonian.set_field(i_state,hval,hdir)
        parameters.llg.set_stt(i_state,True,0,STTdir)
        hamiltonian.set_anisotropy(i_state,K,Kdir)
        parameters.llg.set_timestep(i_state, tS)

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
                    io.chain_read(i_state,"grad_{:d}.ovf".format(counter - 1))
                simulation.start(i_state,Mtd,Slvr)
                
                if os.path.isfile("grad_{:d}.ovf".format(counter)):
                    os.remove("grad_{:d}.ovf".format(counter))
                    pass
                io.chain_write(i_state,"grad_{:d}.ovf".format(counter))
                simulation.stop_all
                counter += 1
                print('Sim {:d}/10 done\n'.format(counter))
                pass #while counter < 10:
        else:#config was read
            parameters.llg.set_iterations(i_state,calc_iter,calc_iter)
            if os.path.isfile("r_{:d}.ovf".format(sim_count)):
                    os.remove("r_{:d}.ovf".format(sim_count))
                    pass
            simulation.start(i_state,Mtd,Slvr)
            io.chain_write(i_state, 'r_{:d}.ovf'.format(sim_count))
            simulation.stop_all
        sim_count += 1
        continue
    print('Done!')
    return(0) #run_simulation
