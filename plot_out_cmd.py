import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.colors import LinearSegmentedColormap

def Plot_Lattice(f_name, n_cols, n_rows):
	###===============================================###
	# Itterativly add temporary vectors pulled from		#
	# output file to a color coded 2D vector field plot #
	# where color represents the vectors' z-magnitude.	#
	# 				color plot is O(n^2)				#
	###===============================================###
	with open(f_name, 'r') as fp:
		#start file parsing and plotting
		X = np.arange(-n_cols/2,n_cols/2)
		Y = np.arange(-n_rows/2,n_rows/2)
		#initialize data containers
		U = np.zeros((n_rows, n_cols))
		V = np.zeros((n_rows, n_cols))
		M = np.zeros((n_rows, n_cols))
		
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
				M[count / n_cols][count % n_cols] = (temp[2]+1)/2
				count += 1
				continue
		
		#mycmap = LinearSegmentedColormap.from_list('mycmap', ['blue', 'white', 'red'])
		q = plt.quiver(U, V, M, cmap='plasma', units='xy', angles='xy', pivot='middle', width=0.25, scale=1.5)
		plt.show()
	return

plot_name = raw_input('Enter file name to plot: ')
#xs = int(raw_input('x = '))
#ys = int(raw_input('y = '))

Plot_Lattice(plot_name, 150,50)
