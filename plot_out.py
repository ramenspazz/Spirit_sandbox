import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

def Plot_Lattice(f_name, n_cols, n_rows):
	###===============================================###
	# Itterativly add temporary vectors pulled from		#
	# output file to a color coded 2D vector field plot #
	# where color represents the vectors' z-magnitude.	#
	# 				color plot is O(n^2)				#
	###===============================================###
	with open(f_name, 'r') as fp:
		#start file parsing and plotting
		U = np.zeros((n_rows, n_cols)) #initialize data containers
		V = np.zeros((n_rows, n_cols)) #initialize data containers
		
		count = 0 # initilize counter
		for ln in fp:
			if '#' in ln:
				pass
			elif ln[0] == '\n':
				pass
			else:
				temp = [float(i) for i in ln.split()]
				U[count / n_cols][count % n_rows] = temp[0]
				V[count / n_cols][count % n_rows] = temp[1]
				#C[count / n_cols, count % n_rows] = temp[2]
				count += 1
				pass
		q = plt.quiver(U, V, units='xy', angles='xy', pivot='tip', width=0.1, scale=1)
		plt.show()
	return