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
    calc_iter = 0
    js = 1e-7 # current value
    STTdir = [1, 0, 0] # polarization direction
    hdir = [0.0, 0.0, 1.0] # magnetic Field direction
    hval = 25
    sim_count = 0 
    load_fname = 'start.ovf'
    
    usr_in = collect_input(int, 'Load state (0/1)?: ')
    if usr_in == 1:
        load_fname = collect_input(str, 'Enter filename to load: ')
        print('\nLoading {:s}...\n'.format(load_fname))
        io.chain_read(i_state,load_fname)
        print('Done!\n')
    elif usr_in == 0:
        usr_in = collect_input(int, 'Set state None, Random, skyrmion, or minus-z (0/1/2/3): ')
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
            print('Setting all spins to -z...\n')
            configuration.minus_z(i_state)
            pass

        print('Done!\n')
        io.chain_write(i_state,"start.ovf")
        print('Wrote start.ovf\n')
    #end load block
    sim_count = 0
    usr_in = 0
    while usr_in != -1:
        usr_in = collect_input(int, 'preform minimization?(-1/1): ')
        if usr_in == 1:
            calc_iter = collect_input(int, 'set num itterations to minimize: ')
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
            parameters.llg.set_iterations(i_state,calc_iter,calc_iter)
            simulation.start(i_state,Mtd,0)
            cur_fname = 
            if os.path.isfile("min_{:d}.ovf".format(sim_count)):
                os.remove("min_{:d}.ovf".format(sim_count))
                pass
            io.chain_write(i_state,"min_{:d}.ovf".format(sim_count))
            simulation.stop_all
            plot_out.Plot_Lattice(cur_fname, x_size, y_size)
            print('Done!\n')
            sim_count += 1
        continue

    last_sim_count = sim_count
    sim_count = 0
    while calc_iter != -1:  
        calc_iter = collect_input(int, 'set num itterations to run, -1 to quit: ')
        if calc_iter == -1:
            #return to top of loop and exit
            continue
        hval = collect_input(float, 'enter H field strength: ') # magnetic Field direction
        js = collect_input(float,'enter current val: ') # Spin Torque magnitude EDIT SET TO 0 norm 3e-04
        temp = convert_from_dimcord_j(DMI, Exchange, js, hval, x_size, y_size, lc)
        js = temp[0]
        hval = temp[1]
        print('H = {:9f}T\nJ = {:12f}A\n'.format(hval, js))
        for i in range(len(STTdir)):
            STTdir[i] = collect_input(float, 'input Polerization element {:d}: '.format(i+1))

        parameters.llg.set_stt(i_state,True,js,STTdir)
        parameters.llg.set_temperature(i_state,0.0)
        parameters.llg.set_damping(i_state, alphaD)
        parameters.llg.set_convergence(i_state, convThr)
        parameters.llg.set_output_configuration(i_state,True,True,4)
        hamiltonian.set_field(i_state,hval,hdir)
        parameters.llg.set_timestep(i_state, tS)

        print('Running simulation...\n')

        if not read_config:#no config loaded, running sandbox
            itt_num = int(calc_iter / 10)
            parameters.llg.set_iterations(i_state,itt_num,itt_num)
            counter = 0
            while counter < 10:
                if (counter == 0) and (usr_in == 1):
                    io.chain_read(i_state,"min_{:d}.ovf".format(last_sim_count))
                elif (counter == 0) and (usr_in == -1):
                    io.chain_read(i_state,load_fname)
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
            if sim_count != 0:
                prev_fname = 'r_{:d}.ovf'.format(sim_count - 1)
                io.chain_read(i_state, prev_fname)
                pass
            cur_fname = 'r_{:d}.ovf'.format(sim_count)
            parameters.llg.set_iterations(i_state,calc_iter,calc_iter)
            if os.path.isfile(cur_fname):
                    os.remove(cur_fname)
                    pass
            simulation.start(i_state,Mtd,Slvr)
            io.chain_write(i_state, cur_fname)
            simulation.stop_all
            plot_out.Plot_Lattice(cur_fname, x_size, y_size)
        sim_count += 1
        continue
    print('Done!')
    return(0) #run_simulation
