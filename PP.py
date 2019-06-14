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

import plot_out

### =====================================================================================
### =====================================================================================
#initial variables

def main():
	usr_in = 0
	rand_flag = False
	Skyrmion_size = 0

	while usr_in != -1:
		with state.State() as i_state:
			#initial parameters
			Mtd = 1
			Slvr = int(raw_input('enter solver num(1-3):'))
			alphaD = float(raw_input("enter alpha (rec0.6):")) # Damping
			convThr = 1.00e-12 # Convergence condition
			tS = 0.0001 # LLG time step
			hval = float(raw_input("enter H field strength:")) # magnetic Field direction
			js = float(raw_input("enter current val:")) # Spin Torque magnitude EDIT SET TO 0 norm 3e-04
			STTdir = [1, 0, 0]       # polarization dir

			for i in range(len(STTdir)):
					STTdir[i] = float(raw_input('input Polerization element: '))

			hdir = [0.0, 0.0, 1.0]       # magnetic Field direction
			K =  0.0                  # Anisotropy
			Kdir = [0.0, 0.0, 1.0]       # Anisotropy direction
			J = 10.0
			DMI = 3.0
			Dij = []

			usr_in = int(raw_input('Random or skyrmion(0/1): '))
			if usr_in == 1:
				Skyrmion_size = input("Enter Skyrmion size:")
			elif usr_in == 0:
				rand_flag = True
			calc_iter = int(raw_input("set num itterations to run: "))

			x_size = int(raw_input('x lattice size: '))
			y_size = int(raw_input('y lattice size: '))
			
			#initialize initial conditions of simulation
			#hamiltonian.set_anisotropy(i_state,K,Kdir)
			geometry.set_n_cells(i_state,n_cells=[x_size, y_size, 1])
			parameters.llg.set_output_configuration(i_state,True,True,4)
			parameters.llg.set_timestep(i_state, tS)
			parameters.llg.set_iterations(i_state,1,1)
			parameters.llg.set_stt(i_state,True,0,STTdir)
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
				print(counter + 1)
				pass #while counter < 10:
			print('Done!')
			pass #with state.State() as i_state:
		usr_in = 1
		while usr_in == 1:
			usr_in = int(raw_input("-1 to exit, 1 to plot last run.\n\n"))
			if usr_in == 1:
				usr_in = raw_input("enter file name to plot: ")
				plot_out.Plot_Lattice(usr_in, x_size, y_size)

		pass #while usr_in == 1:
	return(0)
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