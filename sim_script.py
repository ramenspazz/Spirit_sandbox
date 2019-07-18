#file entry point
import sys
import os
import random
import plot_out
import math
#spirit inclues
from spirit import configuration, constants
from spirit import hamiltonian, geometry, io
from spirit import parameters, quantities
from spirit import simulation, state, system

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def collect_input(val_type, prompt):
	while True:	
		try:
			val = raw_input(prompt)
			return(val_type(val))
		except ValueError:
			print('Invalid input!\n')
			continue

def convert_from_dimcord_j(DMI, Exchange, J_param, H_param, x, y, lc):
    #e = float(1.602176634*math.pow(10,-19))
    #h_bar = float(1.054571800*math.pow(10,-34))
    #Bohr_magneton = float(5.7883809)*float(math.pow(10,-5)) # 5.7883809e-05/A*m^2
    Amp_scale = float(3.038534338)*float(math.pow(10,13)) # 2e*(joule/metre^2)/h_bar -> 4.87e-07A for current scale

    current = float(J_param) * float(DMI) * Amp_scale * lc**2 * 1e-18

    H_field = float(H_param) * math.pow(DMI,2) / float(5.8e+5 * 2 * Exchange)

    return([current,H_field])

def run_simulation(i_state, Mtd, Slvr, convThr, tS, K, Kdir, Exchange, DMI, Dij, alphaD, x_size, y_size, read_config, lc):
    Skyrmion_size = 0
    calc_ittr = 0
    js = 1e-7 # current value
    STTdir = [1, 0, 0] # polarization direction
    hdir = [0.0, 0.0, 1.0] # magnetic Field direction
    hval = 25
    sim_count = 0 
    load_fname = 'start.ovf'
    startup = True

    while True:
        clear_screen()
        if startup: # load initial state or set up new state
            usr_in = collect_input(int, 'Create new state or Load state (0/1)?: ')
            if usr_in == 1:
                load_fname = collect_input(str, 'Enter filename to load: ')
                print('\nLoading {:s}...\n'.format(load_fname))
                io.chain_read(i_state,load_fname)
                print('Done!\n')
            elif usr_in == 0:
                usr_in = collect_input(int, 'Set state None, Random, skyrmion, or plus-z (0/1/2/3): ')
                if usr_in == 2:
                    Skyrmion_size = collect_input(int, "Enter Skyrmion size: ")

                #initialize initial conditions of simulation
                #hamiltonian.set_anisotropy(i_state,K,Kdir)
                print('Setting up initial state...\n')
                if not read_config:#if config file was set, dont set custom lattice size or BC
                    hamiltonian.set_dmi(i_state,1,[DMI], 1)
                    geometry.set_n_cells(i_state,[x_size, y_size, 1])
                    hamiltonian.set_boundary_conditions(i_state, [1,1,0])
                parameters.llg.set_temperature(i_state,0.0)
                parameters.llg.set_damping(i_state, alphaD)
                parameters.llg.set_convergence(i_state, convThr)
                parameters.llg.set_output_configuration(i_state,True,True,4)
                hamiltonian.set_field(i_state,hval,hdir)
                parameters.llg.set_stt(i_state,True,0,STTdir)
                parameters.llg.set_timestep(i_state, tS)
                parameters.llg.set_iterations(i_state,1,1)

                if usr_in == 1:
                    print('Initilizing random state...\n')
                    configuration.random(i_state) #initialize random
                    pass
                elif usr_in == 2:
                    if not read_config:
                        configuration.plus_z(i_state) #set all spin to +z
                    print('Initilizing Skyrmion...\n')
                    configuration.skyrmion(i_state, Skyrmion_size, phase=-90) #initialize skyrmion
                    if os.path.isfile("start.ovf"):
                        os.remove("start.ovf")
                        pass
                    pass
                elif usr_in == 3:
                    print('Setting all spins to +z...\n')
                    configuration.plus_z(i_state)
                    pass
                print('Done!\n')
                io.chain_write(i_state,"start.ovf")
                print('Wrote start.ovf\n')
            #end load block
            startup = False
            continue
        #end if startup block

        usr_in = collect_input(str, 'Enter command:\nl to load\nm to minimize\nr to run simulation\np to plot\nq to quit\n')
        print('\n')

        if usr_in == 'l':
            clear_screen()
            load_fname = collect_input(str, 'Enter filename to load: ')
            print('\nLoading {:s}...\n'.format(load_fname))
            io.chain_read(i_state,load_fname)
            print('Done!\n')
        #end load block
        elif usr_in == 'p':
            usr_in = 1
            while usr_in == 1:
                usr_in = collect_input(int, '-1 to exit, 1 to plot.')
                if usr_in == 1:
                    usr_in = raw_input("enter file name to plot: ")
                    xs = collect_input(int, 'x = ')
                    ys = collect_input(int, 'y = ')
                    plot_out.Plot_Lattice(usr_in, xs, ys)
                    usr_in = 1
        #end plotting block
        elif usr_in == 'm':
            clear_screen()
            sim_count = 0
            usr_in = 0
            while usr_in != -1:
                usr_in = collect_input(int, 'preform minimization?(-1/1): ')
                if usr_in == 1:
                    calc_ittr = collect_input(int, 'set num itterations to minimize: ')
                    hval = collect_input(float, 'enter H field strength: ') # magnetic Field direction
                    js = 0
                    hval = convert_from_dimcord_j(DMI, Exchange, js, hval, x_size, y_size, lc)[1]

                    print('H = {:f}T'.format(hval))

                    parameters.llg.set_temperature(i_state,0.0)
                    parameters.llg.set_damping(i_state, alphaD)
                    parameters.llg.set_convergence(i_state, convThr)
                    parameters.llg.set_output_configuration(i_state,True,True,4)
                    hamiltonian.set_field(i_state,hval,hdir)
                    parameters.llg.set_stt(i_state,True,0,STTdir)
                    #hamiltonian.set_anisotropy(i_state,K,Kdir)
                    parameters.llg.set_timestep(i_state, tS)
                    parameters.llg.set_direct_minimization(i_state, use_minimization=True)
                    #minimize
                    print('Minimizing\n')
                    parameters.llg.set_iterations(i_state,calc_ittr,calc_ittr)
                    simulation.start(i_state,Mtd,0)
                    cur_fname = 'min_{:d}.ovf'.format(sim_count)
                    if os.path.isfile(cur_fname):
                        os.remove(cur_fname)
                        pass
                    io.chain_write(i_state,cur_fname)
                    simulation.stop_all
                    plot_out.Plot_Lattice(cur_fname, x_size, y_size)
                    print('Done!\n')
                    sim_count += 1
                continue
        #end minimize block
        elif usr_in == 'r':
            clear_screen()
            sim_count = 0
            sim_time = 0
            prev_ittr = 0
            prev_sim_time = 0

            parameters.llg.set_temperature(i_state,0.0)
            parameters.llg.set_damping(i_state, alphaD)
            parameters.llg.set_convergence(i_state, convThr)
            #parameters.llg.set_output_configuration(i_state,True,True,4)

            while True:            
                sim_time = collect_input(int, 'set time to run in fs, 0 to use last used values, -1 to exit simulation mode: ')
                if sim_time == -1:
                    break
                elif sim_time == 0:
                    if sim_count == 0:
                        print('Run one simulation first!\n')
                        continue
                    calc_ittr = prev_ittr
                    print('H = {:f}T\nJ = {:f}A\nP = ({:f},{:f},{:f})\nItterations = {:d} = {:f}fs'.format(hval,js, STTdir[0],STTdir[1],STTdir[2],int(prev_ittr),prev_sim_time))
                else:
                    calc_ittr = int(float(sim_time) * 0.001 / tS) #n_fs * fs/(dt*ps)
                    prev_ittr = calc_ittr
                    prev_sim_time = sim_time
                    hval = collect_input(float, 'enter H field strength: ') # magnetic Field direction
                    js = collect_input(float,'enter current val: ') # Spin Torque magnitude EDIT SET TO 0 norm 3e-04
                    temp = convert_from_dimcord_j(DMI, Exchange, js, hval, x_size, y_size, lc)
                    js = temp[0]
                    hval = temp[1]
                    for i in range(len(STTdir)):
                        STTdir[i] = collect_input(float, 'input Polerization element {:d}: '.format(i+1))
                    print('H = {:f}T\nJ = {:f}A\nP = ({:f},{:f},{:f})\nItterations = {:d} = {:f}fs'.format(hval,js, STTdir[0],STTdir[1],STTdir[2],int(prev_ittr),sim_time))
                #end quit/re-run/new-sim block

                #setup initial parameters user for simulation
                parameters.llg.set_stt(i_state,True,js,STTdir)
                #parameters.llg.set_temperature(i_state,0.0)
                #parameters.llg.set_damping(i_state, alphaD)
                #parameters.llg.set_convergence(i_state, convThr)
                #parameters.llg.set_output_configuration(i_state,True,True,4)
                hamiltonian.set_field(i_state,hval,hdir)
                parameters.llg.set_timestep(i_state, tS)
                parameters.llg.set_iterations(i_state,calc_ittr,calc_ittr)

                print('Running simulation...\n')

                cur_fname = 'r_{:d}.ovf'.format(sim_count)
                if os.path.isfile(cur_fname):
                #if current filename already exists within directory
                #remove it
                        os.remove(cur_fname)

                simulation.start(i_state,Mtd,Slvr)
                io.chain_write(i_state, cur_fname)
                simulation.stop_all
                plot_out.Plot_Lattice(cur_fname, x_size, y_size)
                sim_count += 1

                print('Done!')
                continue
            #while not (sim_time == -1):    
        #end run simulation block
        elif usr_in == 'q':
        #break and exit loop to quit program
            break
    clear_screen()
    return(0) #run_simulation