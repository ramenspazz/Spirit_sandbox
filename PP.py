import sys
import os
import threading
from datetime import datetime
#spirit imports for main simulation
from spirit import configuration, constants
from spirit import hamiltonian, geometry, io
from spirit import parameters, quantities
from spirit import simulation, state, system
#scientific data processing
import numpy as np
from scipy import special
import math
#custom scripts
import plot_out
import sim_script
import file_parser
import generate_configs

def is_number(num):
    try:
        float(num)
        return(True)
    except ValueError:
        return(False)

def collect_input(val_type, prompt):
	while True:	
		try:
			val = raw_input(prompt)
			return(val_type(val))
		except ValueError:
			print('Invalid input!\n')
			continue

def main():
	in_var = 0
	config_fname = ''
	#initial parameters
	x_size = 0
	y_size = 0
	Mtd = 1
	convThr = 1.00e-12 # Convergence condition
	tS = 1e-06 # LLG time step
	k_val =  0.0  # Anisotropy
	Kdir = [0.0, 0.0, 1.0] # Anisotropy direction
	Exchange_mm = 18.16
	DMI_mm = 1.87
	Dij = []
	lc = 6
	symmetry = 4

	print('Welcome to spirit sandbox.\n')

	while in_var != -1:
		read_config = collect_input(int, 'read in a config file?(0/1): ')
		if read_config == 1:
			config_fname = raw_input('enter config your_file_name.txt: ')
			in_var = collect_input(int, 'Generate new r_pos, h, and anisotropy file (0/1)?: ')
			if in_var == 1:
				x_size = collect_input(int, 'x lattice size: ')
				y_size = collect_input(int, 'y lattice size: ')
				#set lattice constant
				with file_parser.Parse_File('gen_config.txt') as fp:
					lc = fp.file_readline(None, 'lattice_constant')
					lc = int(lc.split()[1])
				#update bravis vector
				with file_parser.Parse_File('gen_config.txt') as fp:
					line_num = fp.find_line_number('bravais_vectors')
					fp.write_to_file('bravais_vectors\n', line_num)
					fp.write_to_file('{:d} 0 0\n'.format(x_size))
					fp.write_to_file('0 {:d} 0\n'.format(y_size))
					fp.write_to_file('0 0 1\n')

				generate_configs.gen_r_pos(x_size,y_size)
				
				in_var = collect_input(int, 'Use a custom DMI (0/1)?: ')
				if in_var == 1:
					DMI_mm = collect_input(float, 'Enter value for DMI: ')
					DMI_atom = float(DMI_mm * (lc / 10) * 1.602e+04) / float(symmetry)
					Exchange_mm = collect_input(float, 'Enter value for Exchange: ')
					Exchange_atom = float(Exchange_mm * (lc / 10) * 1.602e+13) / float(2 * symmetry)
					print('DMI = {:5f}\nExchange = {:9.8f}'.format(DMI_atom, Exchange_atom))

					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('#DMI', '{:<8.5f}\n'.format(DMI_mm))
						fp.set_config_var('#EXCHANGE', '{:<18.17f}\n'.format(Exchange_mm))
					generate_configs.gen_h_file(x_size,y_size, Exchange_atom, DMI_atom)

					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('interaction_pairs_file', 'h.txt\n')
				else:
					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('interaction_pairs_file', '.\n')

				in_var = collect_input(int, 'Use a custom anis (0/1)?: ')

				if in_var == 1:
					in_var = collect_input(int, 'Use random or pattern generated anisotropy (0/1)?: ')
					if in_var == 1:
						pattern = raw_input('Enter math expression here in terms of x\nEnter an integer for a box: ')
						width = collect_input(int, 'Enter width of pattern: ')
						k_val = collect_input(float, 'Enter K value: ')
						generate_configs.gen_anis_pattern(x_size,y_size, pattern, width, 0.9)
					elif in_var == 0:
						k_val = collect_input(float, 'Enter value for K: ')
						#convert K
						k_val = k_val * DMI_mm**2 / (4 * Exchange_mm)
						k_val = k_val * 1.6021766e-05 # J/m^3 -> meV
						print('K = {:f}\n'.format(k_val))
						sigma = collect_input(float, 'Enter value for sigma in percent of K: ')
						generate_configs.gen_anis_random(x_size,y_size, k_val, k_val * sigma)

					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('anisotropy_file', 'anisotropy.txt\n')
				else:
					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('anisotropy_file', '.\n')
				
				file_parser.concatenate_files('gen_config.txt', 'r_pos.txt', config_fname)
				#generate new config file
			#read a config file

			elif in_var == 0:
				prev_vals = []
#TODO: complete functionality
				#Load previously used values to current values from old
				#config file. Can be modified to add as many values as needed.
				search = ['#DMI', '#EXCHANGE', 'lattice_constant']
				with file_parser.Parse_File(config_fname) as fp:
					for searchterm in search:
						cur_line = (fp.file_readline(None, searchterm)).split()
						prev_vals.append(float(cur_line[1]))
# TODO: add object to assign each value in loop and not by name after loop
					DMI_mm = prev_vals[0]
					Exchange_mm = prev_vals[1]
					lc = prev_vals[2]

					cur_line = fp.file_readline(None, 'bravais_vectors', True)
					cur_line = cur_line.split()
					x_size = int(cur_line[0])
					cur_line = fp.file_readline()
					cur_line = cur_line.split()
					y_size = int(cur_line[1])

					print('loaded values:\nlattice size: {:f}x{:f}\nDMI_mm: {:f}\nExchange_mm: {:18.17f}\nlattice constant: {:f}\n'.format(x_size,y_size,DMI_mm,Exchange_mm,lc))
		#if read_config == 1
		
		alphaD = collect_input(float, 'enter alpha: ') # Damping

		if read_config:
			betaD = collect_input(float, 'enter beta: ')
			with file_parser.Parse_File(config_fname) as fp:
				fp.set_config_var('llg_beta', str(betaD))
				pass
		else:
			x_size = collect_input(int, 'x lattice size: ')
   			y_size = collect_input(int, 'y lattice size: ')
		
		Slvr = collect_input(int, 'enter solver num(1-4): ')
		
		with state.State(configfile=config_fname, quiet=True) as i_state:
			sim_script.run_simulation(i_state, Mtd, Slvr, convThr, tS, k_val, Kdir, Exchange_mm, DMI_mm, Dij, alphaD, x_size, y_size, read_config, lc)
		in_var = 1
		while in_var == 1:
			in_var = collect_input(int, '-1 to exit program, 0 to exit plotting, 1 to plot.')
			if in_var == 1:
				in_var = raw_input("enter file name to plot: ")
				xs = collect_input(int, 'x = ')
				ys = collect_input(int, 'y = ')
				plot_out.Plot_Lattice(in_var, xs, ys)
				in_var = 1
	return(0)#main()
#end main

if __name__ == "__main__":
	main()
