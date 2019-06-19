import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

def Plot_Lattice(f_name, n_cols, n_rows):
	###===============================================###
	# Itterativly add temporary vectors pulled from     #
	# output file to a color coded 2D vector field plot #
	# where color represents the vectors' z-magnitude.  #
	# 		color plot is O(n^2)                #
	###===============================================###
	with open(f_name, 'r') as fp:
		#start file parsing and plotting
		X = np.arange(-n_cols/2,n_cols/2)
		Y = np.arange(-n_rows/2,n_rows/2)
		U = np.zeros((n_rows, n_cols)) #initialize data containers
		V = np.zeros((n_rows, n_cols)) #initialize data containers
		
		count = 0 # initilize counter
		for ln in fp:
			if '#' in ln:
				continue
			elif ln[0] == '\n':
				continue
			elif count > n_cols*n_rows:
				print('Too many entries!\n')
				return(-1)
			else:
				temp = [float(i) for i in ln.split()]
				U[count / n_cols][count % n_cols] = temp[0]
				V[count / n_cols][count % n_cols] = temp[1]
				#C[count / n_cols, count % n_rows] = temp[2]
				count += 1
				continue
		q = plt.quiver(U, V, units='xy', angles='xy', pivot='tip', width=0.1, scale=1)
		plt.show()
	return
