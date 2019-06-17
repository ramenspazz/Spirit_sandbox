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
#custom scripts
import plot_out
import sim_script
import file_parser
import generate_configs

def main():
	in_var = 0
	config_fname = ''

	while in_var != -1:
		#initial parameters
		x_size = 0
		y_size = 0
		Mtd = 1
		convThr = 1.00e-12 # Convergence condition
		tS = 0.001 # LLG time step
		STTdir = [1, 0, 0] # polarization direction
		hdir = [0.0, 0.0, 1.0] # magnetic Field direction
		K =  0.0  # Anisotropy
		Kdir = [0.0, 0.0, 1.0] # Anisotropy direction
		J = 10.0
		DMI = 3.0
		Dij = []

		read_config = int(raw_input('read in a config file?(0/1): '))
		if read_config:
			config_fname = raw_input('enter config your_file_name.txt: ')
			in_var = int(raw_input('Generate new r_pos and h file (0/1)?: '))
			if in_var == 1:
				x_size = int(raw_input('x lattice size: '))
				y_size = int(raw_input('y lattice size: '))
				generate_configs.gen_r_pos(x_size,y_size)
				generate_configs.gen_h_file(x_size,y_size, J, DMI)

		hval = float(raw_input("enter H field strength:")) # magnetic Field direction
		js = float(raw_input("enter current val:")) # Spin Torque magnitude EDIT SET TO 0 norm 3e-04
		alphaD = float(raw_input('enter alpha: ')) # Damping

		if read_config:
			betaD = float(raw_input('enter beta: '))
			with file_parser.Parse_File(config_fname) as fp:
				fp.set_config_var('llg_beta', betaD)
				pass
		else:
			x_size = int(raw_input('x lattice size: '))
   			y_size = int(raw_input('y lattice size: '))

		for i in range(len(STTdir)):
				STTdir[i] = float(raw_input('input Polerization element: '))
		
		Slvr = int(raw_input('enter solver num(1-3):'))
		
		with state.State(configfile=config_fname, quiet=True) as i_state:
			sim_script.run_simulation(i_state, Mtd, Slvr, convThr, tS, hval, js, STTdir, hdir, K, Kdir, J, DMI, Dij, alphaD, x_size, y_size, read_config)

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
