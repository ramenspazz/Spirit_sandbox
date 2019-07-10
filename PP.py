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

def main():
	in_var = 0
	config_fname = ''
	#initial parameters
	x_size = 0
	y_size = 0
	Mtd = 1
	convThr = 1.00e-12 # Convergence condition
	tS = 0.001 # LLG time step
	k_val =  0.0  # Anisotropy
	Kdir = [0.0, 0.0, 1.0] # Anisotropy direction
	Exchange = 18.16
	DMI = 1.87
	Dij = []
	print('Welcome to spirit sandbox.\n')
	while in_var != -1:
		
		read_config = int(raw_input('read in a config file?(0/1): '))
		if read_config:
			config_fname = raw_input('enter config your_file_name.txt: ')
			in_var = int(raw_input('Generate new r_pos, h, and anisotropy file (0/1)?: '))
			if in_var == 1:
				x_size = int(raw_input('x lattice size: '))
				y_size = int(raw_input('y lattice size: '))

				#update bravis vector
				with file_parser.Parse_File('gen_config.txt') as fp:
					line_num = fp.find_line_number('bravais_vectors')
					fp.write_to_file('bravais_vectors\n', line_num)
					fp.write_to_file('{:d} 0 0\n'.format(x_size))
					fp.write_to_file('0 {:d} 0\n'.format(y_size))
					fp.write_to_file('0 0 1\n')

				generate_configs.gen_r_pos(x_size,y_size)
				
				in_var = int(raw_input('Use a custom DMI (0/1)?: '))
				if in_var == 1:
					DMI = float(raw_input('Enter value for DMI: '))
					generate_configs.gen_h_file(x_size,y_size, Exchange, DMI)
					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('interaction_pairs_file', 'h.txt\n')
				else:
					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('interaction_pairs_file', '.\n')

				in_var = int(raw_input('Use a custom anis (0/1)?: '))
				if in_var == 1:
					in_var = int(raw_input('Use random or pattern generated anisotropy (0/1)?: '))
					if in_var == 1:
						pattern = raw_input('Enter math expression here in terms of x\nEnter an integer for a box: ')
						width = int(raw_input('Enter width of pattern: '))
						k_val = float(raw_input('Enter K value: '))
						generate_configs.gen_anis_pattern(x_size,y_size, pattern, width, 0.9)
					elif in_var == 0:
						k_val = float(raw_input('Enter value for K: '))
						#convert K
						k_val = k_val * DMI**2 * math.pow(10,-6) / (8*Exchange)
						sigma = float(raw_input('Enter value for sigma: '))
						generate_configs.gen_anis_random(x_size,y_size, k_val, sigma)
					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('anisotropy_file', 'anisotropy.txt\n')
				else:
					with file_parser.Parse_File('gen_config.txt') as fp:
						fp.set_config_var('anisotropy_file', '.\n')
				
				file_parser.concatenate_files('gen_config.txt', 'r_pos.txt', config_fname)

		alphaD = float(raw_input('enter alpha: ')) # Damping

		if read_config:
			betaD = float(raw_input('enter beta: '))
			with file_parser.Parse_File(config_fname) as fp:
				fp.set_config_var('llg_beta', str(betaD))
				pass
		else:
			x_size = int(raw_input('x lattice size: '))
   			y_size = int(raw_input('y lattice size: '))
		
		Slvr = int(raw_input('enter solver num(1-4): '))
		
		with state.State(configfile=config_fname, quiet=True) as i_state:
			sim_script.run_simulation(i_state, Mtd, Slvr, convThr, tS, k_val, Kdir, Exchange, DMI, Dij, alphaD, x_size, y_size, read_config)
		in_var = 1
		while in_var == 1:
			in_var = int(raw_input("-1 to exit program, 0 to exit plotting, 1 to plot."))
			if in_var == 1:
				in_var = raw_input("enter file name to plot: ")
				xs = int(raw_input('x = '))
				ys = int(raw_input('y = '))
				plot_out.Plot_Lattice(in_var, xs, ys)
				in_var = 1
	return(0)#main()
#end main

if __name__ == "__main__":
	main()

### =====================================================================================
#   Below is a code snippet that can be used to rotate polerization of current: currently
#   unused
### =====================================================================================

"""
#rot_div = input("enter number of steps required for full rotation (integer): ")
#rot_div = 1
#theta_step = 2*np.pi/rot_div
for i in range(0,rot_div): # 16 total rotations in polerization direction
#	#rotate STTdir based on itt num and step size
#	STTdir[0] = np.cos(i*theta_step)
#	STTdir[1] = np.sin(i*theta_step)
	#start simulations
"""
