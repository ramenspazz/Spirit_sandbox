#file entry point
import sys
import os
import random
import plot_out
import math
import time
import numpy as np
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

def isclose(a,b,tol):
    if np.absolute(b - a) <= tol:
        return(True)
    else:
        return(False)

def convert_from_dimcord_j(DMI, Exchange, J_param, H_param, x, y, lc):
    #e = float(1.602176634*math.pow(10,-19))
    #h_bar = float(1.054571800*math.pow(10,-34))
    #Bohr_magneton = float(5.7883809)*float(math.pow(10,-5)) # 5.7883809e-05/A*m^2
    Ms = 1e+6
    Amp_scale = float(3.038534338)*float(math.pow(10,13)) # 2e*(joule/metre^2)/h_bar -> 4.87e-07A for current scale

    current = float(J_param) * float(DMI) * Amp_scale * lc**2 * 1e-18

    H_field = float(H_param) * math.pow(DMI,2) / float(Ms * 2 * Exchange)

    return([current,H_field])

def run_simulation(i_state, Mtd, Slvr, convThr, tS, K, Kdir, Exchange, DMI, Dij, alphaD, x_size, y_size, read_config, lc):
    Skyrmion_size = 0
    calc_ittr = 0
    js = 0 # current value
    STTdir = [0, 0, 0] # polarization direction
    hdir = [0.0, 0.0, 1.0] # magnetic Field direction
    hval = 0
    sim_count = 0 
    load_fname = 'start.ovf'
    startup = True

    while True:
        clear_screen()
        if startup: # load initial state or set up new state
            usr_in = collect_input(int, 'Load state from file (0/1)?: ')
            if usr_in == 1:
                load_fname = collect_input(str, 'Enter filename to load: ')
                print('\nLoading {:s}...\n'.format(load_fname))
                io.chain_read(i_state,load_fname)
                print('Done!\n')
            startup = False
            continue
        #end if startup block

        usr_in = collect_input(str, 'Enter command:\nl to load\nm to minimize\nr to run simulation\np to plot\nq to quit\n')
        print('\n')

        if usr_in == 'l':
            clear_screen()

            usr_in = collect_input(int, 'Create or ammend to state, Load state from file, or exit (0/1/-1)?: ')
            if usr_in == 1:
                load_fname = collect_input(str, 'Enter filename to load: ')
                print('\nLoading {:s}...\n'.format(load_fname))
                io.chain_read(i_state,load_fname)
                print('Done!\n')
            elif usr_in == 0:
                usr_in = collect_input(int, 'Set state None, Random, skyrmion, plus-z, minus-z, other settings (0/1/2/3/4/5): ')

                #initialize initial conditions of simulation
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
                #hamiltonian.set_dmi(i_state,1,[40],chirality=2)
                if usr_in == 1:
                    print('Initilizing random state...\n')
                    configuration.random(i_state) #initialize random
                    pass
                elif usr_in == 2:
                    Skyrmion_size = collect_input(int, "Enter Skyrmion size: ")
                    phase = collect_input(float, 'Enter Skyrmion phase: ')
                    pos = [0,0,0]
                    for i in range(len(pos)):
                        pos[i] = collect_input(int, 'Enter position {:d} for skyrmion (keep z = 0): '.format(i + 1))
                    print('Initilizing Skyrmion...\n')
                    configuration.skyrmion(i_state, Skyrmion_size, 1, phase, False, False, pos) #initialize skyrmion
                    if os.path.isfile("start.ovf"):
                        os.remove("start.ovf")
                        pass
                    pass
                elif usr_in == 3:
                    print('Setting all spins to +z...\n')
                    configuration.plus_z(i_state)
                    pass
                elif usr_in == 4:
                    print('Setting all spins to -z...\n')
                    configuration.minus_z(i_state)
                elif usr_in == 5:
                    convThr = collect_input(float, 'enter Value for convergance threshold (default is 1e-12): ')
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
                    sim_time = collect_input(float, 'set minimize time in fs: ')
                    calc_ittr = int(sim_time * 0.001 / tS) #n_fs * fs/(dt*ps)
                    hval = collect_input(float, 'enter H field strength: ') # magnetic Field direction
                    js = 0
                    hval = convert_from_dimcord_j(DMI, Exchange, js, hval, x_size, y_size, lc)[1]

                    print('H = {:f}T'.format(hval))
                    parameters.llg.set_temperature(i_state,0.0)
                    parameters.llg.set_damping(i_state, alphaD)
                    parameters.llg.set_convergence(i_state, convThr)
                    parameters.llg.set_timestep(i_state, tS)
                    hamiltonian.set_field(i_state,hval,hdir)
                    parameters.llg.set_stt(i_state,True,0,[0,0,0])
                    #minimize
                    print('Minimizing\n')
                    parameters.llg.set_iterations(i_state,calc_ittr,calc_ittr)
                    simulation.start(i_state, simulation.METHOD_LLG, simulation.SOLVER_VP)
                    cur_fname = 'min_{:d}.ovf'.format(sim_count)
                    if os.path.isfile(cur_fname):
                        os.remove(cur_fname)
                        pass
                    io.chain_write(i_state,cur_fname)
                    simulation.stop_all(i_state)
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
            #set per-run parameters
            parameters.llg.set_temperature(i_state,0)
            parameters.llg.set_damping(i_state, alphaD)
            parameters.llg.set_convergence(i_state, convThr)
            parameters.llg.set_timestep(i_state, tS)
            while True:            
                sim_time = collect_input(float, 'set time to run in fs, 0 to use last used values, -1 to exit simulation mode: ')
                if isclose(sim_time,-1,1e-8):
                    break
                elif isclose(sim_time, 0, 1e-8):
                    if sim_count == 0:
                        print('Run one simulation first!\n')
                        continue
                    calc_ittr = prev_ittr
                    print('H = {:f}T\nJ = {:f}microAmps\nP = ({:f},{:f},{:f})\nItterations = {:d} = {:f}fs'.format(hval,1e+6*js, STTdir[0],STTdir[1],STTdir[2],int(prev_ittr),prev_sim_time))
                elif (sim_time < (tS / 0.001)) and (not isclose(sim_time, (tS / 0.001), (tS / 0.001)/10.0)):
                    print('Enter a larger value!\n')
                    continue
                else:
                    calc_ittr = int(float(sim_time) * 0.001 / tS) #n_fs * fs/(dt*ps)
                    prev_ittr = calc_ittr
                    prev_sim_time = sim_time
                    hval = collect_input(float, 'enter H field strength: ') # magnetic Field direction
                    js = collect_input(float,'enter current val: ') # Spin Torque magnitude EDIT SET TO 0 norm 3e-04
                    temp = convert_from_dimcord_j(DMI, Exchange, js, hval, x_size, y_size, lc)
                    if isclose(0, js, 1e-7):
                        js = 0.0
                    else:
                        js = temp[0]
                    hval = temp[1]
                    for i in range(len(STTdir)):
                        STTdir[i] = collect_input(float, 'input Polerization element {:d}: '.format(i+1))
                    print('H = {:f}T\nJ = {:f}microAmps\nP = ({:f},{:f},{:f})\nItterations = {:d} = {:f}fs'.format(hval,1e+6*js, STTdir[0],STTdir[1],STTdir[2],int(prev_ittr),sim_time))
                #end quit/re-run/new-sim block

                print('Running simulation...\n')

                cur_fname = 'r_{:d}.ovf'.format(sim_count)
                if os.path.isfile(cur_fname):
                #if current filename already exists within directory
                #remove it
                    os.remove(cur_fname)

                parameters.llg.set_stt(i_state,True,js,STTdir)
                hamiltonian.set_field(i_state,hval,hdir)
                parameters.llg.set_iterations(i_state,calc_ittr,0)

                start = time.time()
                simulation.start(i_state,Mtd,Slvr)
                end = time.time()
                io.chain_write(i_state, cur_fname)
                simulation.stop_all(i_state)

                print('Done! Elapsed time: {:f}\n'.format(end - start))
                plot_out.Plot_Lattice(cur_fname, x_size, y_size)
                sim_count += 1
                continue
            #while not (sim_time == -1):    
        #end run simulation block
        elif usr_in == 'q':
        #break and exit loop to quit program
            break
    clear_screen()
    return(0) #run_simulation