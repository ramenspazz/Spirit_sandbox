#file start
from __future__ import print_function
import file_parser
import fileinput
import sympy as sy
import numpy as np
import random
import math
import os
#testing import

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
        
def gen_h_file(x_size, y_size, J, D, x_periodic, y_periodic):
    with file_parser.Parse_File('h.txt') as fp:
        fp.delete_contents()
        usr_in = collect_input(int, 'Use seperated dmi, one value over whole lattice, or checkerboard(0/1/2)? ')

        in_string = '{:<6d}  {:<6d}  {:<6d}  {:<6d}  {:<6d}  {:<6.3f}  {:<6.3f}  {:<6d}  {:<6d}  {:<6d}\n'
        fp.write_to_file('{:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}\n'.format('i','j','da','db','dc','Jij','Dij','Dija','Dijb','Dijc'))
        if usr_in == 0:
            divider = collect_input(int, 'Enter number of dmi to impliment: ')
            divider = x_size / divider
            print('periodic in x = {:d}, periodic in y = {:d}\n'.format(x_periodic, y_periodic))
            print('Generating DMI at {:d} for {:d}x{:d} system...\n'.format(divider, x_size, y_size))
            #assign dmi in the x direction
            for i in range(x_size*y_size):
                #switch signs on the DMI when half of the xsize is reached
                d = math.floor(i/divider) % 2
                if (x_size - 1) == (i % x_size):
                    continue
                else:
                    if d == 0:
                        fp.write_to_file(in_string.format(i,i+1,0,0,0,J,D,1,0,0))
                    else:
                        fp.write_to_file(in_string.format(i,i+1,0,0,0,J,D,-1,0,0))
            #assign dmi in the y direction
            for j in range(x_size*(y_size - 1)):
                d = math.floor(i/divider) % 2
                if d == 0:
                    fp.write_to_file(in_string.format(j,j+x_size,0,0,0,J,D,0,1,0))
                else:
                    fp.write_to_file(in_string.format(j,j+x_size,0,0,0,J,D,0,-1,0))
            #end split dmi
        elif usr_in == 1:
            type_dmi = collect_input(int, 'Neel or Bloc DMI(-1/1)? ')
            for i in range(x_size*y_size):
                #switch signs on the DMI when half of the xsize is reached
                if (x_size - 1) == (i % x_size):
                    continue
                else:
                    if type_dmi + 1 == 0:
                        fp.write_to_file(in_string.format(i,i+1,0,0,0,J,D,0,type_dmi,0))
                    else:
                        fp.write_to_file(in_string.format(i,i+1,0,0,0,J,D,type_dmi,0,0))
            for j in range(x_size*(y_size - 1)):
                if type_dmi + 1 == 0:
                    fp.write_to_file(in_string.format(j,j+x_size,0,0,0,J,D,type_dmi,0,0))
                else:
                    fp.write_to_file(in_string.format(j,j+x_size,0,0,0,J,D,0,type_dmi,0))
                    #fp.write_to_file(in_string.format(j,x_size*(y_size - 1) + j,0,0,0,J,D,0,type_dmi,0))
################################################################
# this algorithim assumes that the y size of the system is 
# divisible by 3 and x size by 2=>4
################################################################
# create DMI pairs with pattern:
# | + | - |
# |+|-|+|-|
# | + | - |
# First, the x direction is traversed, assigning n->n+1 if it is
# not an edge case. Then y is traversed, assigning n->n+rowsize,
# where each will switch signs as the given region requires.
################################################################
        elif usr_in == 2:
            flag = True
            divider = 2 #start the generation of dmi at half of width
            for i in range(x_size*y_size):
                # if the current element is a multipul of a third of the row size
                check = (i / x_size) % (y_size / 3)
                if flag:
                    divider = 4
                else:
                    divider = 2
                temp = int(math.floor(i / (x_size/divider)))
                exponent = temp % divider
                d = int(math.pow(-1,exponent))
                if not ((i / x_size) == (y_size - 1)):
                    if ((i / x_size) % (y_size / 3)) == 0:
                        fp.write_to_file(in_string.format(i,i+x_size,0,0,0,J,D,-1 * d,0,0))
                    else:
                        fp.write_to_file(in_string.format(i,i+x_size,0,0,0,J,D,d,0,0))
                if (x_size - 1) == (i % x_size):
                    if(check + 1 == 3):
                        flag = not flag
                    continue 
                else:
                    fp.write_to_file(in_string.format(i,i+1,0,0,0,J,D,0,d,0))
    #end with
#end gen_h_file

def gen_anis_pattern(x_size, y_size, pattern, width, K_mag = None):
    with file_parser.Parse_File('anisotropy.txt') as fp:
        print('generating pattern...\n')
        fp.delete_contents()
        header_string = '{:<6s} {:<6s} {:<6s} {:<6s} {:<6s}\n'.format('i', 'K', 'Kx', 'Ky', 'Kz')
        in_string = '{:<6d} {:<6.3f} {:<6.3f} {:<6.3f} {:<6.3f}\n'

        if K_mag != None:
            K = K_mag
        else:
            K = 1
        fp.write_to_file(header_string)

        expr_in = np.arange(-width/2,width/2 + 1)
        if sy.sympify(pattern).is_integer:
            print('Int type detected!\n')
            expr_output = [x_size/2 - int(pattern)] * width
            mirror_element = [x_size/2 + int(pattern)] * width
            print(expr_output)
        else:
            expr = sy.sympify(pattern)
            f = sy.utilities.lambdify('x', expr, "numpy")
            expr_output = x_size/2 - f(expr_in)
            mirror_element = x_size/2 + f(expr_in)
        write_flag = False
        skip_flag = False
        mirror_index = 0
        prev_line_y = 1

        for i in range(x_size*y_size):
            cur_pos = [i % x_size + 1, int(i / x_size) + 1] #update current position each itteration in loop. x y
            if prev_line_y < cur_pos[1]:
                skip_flag = False
            if (not write_flag) and (not skip_flag):
                for j, element in enumerate(expr_output): 
                    #check if the currently indexed position is equal to a point on the graph
                    #print('element {:d} {:f}, y = {:d}, cur pos = {:d}'.format(i,element,expr_in[j] + y_size/2, cur_pos[0]))
                    #if the current point is equal tp the cur pos x and is not
                    #along the axis of reflection, set the write flag to true
                    #unitl the mirror point across the axis of reflection is reached
                    if (cur_pos[0] == math.floor(element)) and (cur_pos[1] == math.floor(expr_in[j] + y_size/2)):
                        write_flag = True
                        skip_flag = True
                        prev_line_y = cur_pos[1]
                        mirror_index = j
                        fp.write_to_file(in_string.format(i,K,0,0,1))
                        break
                    elif (cur_pos[0] == x_size/2) and (cur_pos[0] == math.floor(element)):
                        skip_flag = True
                        prev_line_y = cur_pos[1]
                        #fp.write_to_file(in_string.format(i,K,0,0,1))
                        break
                if write_flag:
                    continue
            elif write_flag: # if not write_flag:
                fp.write_to_file(in_string.format(i,K,0,0,1))
                if cur_pos[0] == math.ceil(mirror_element[mirror_index]):
                    write_flag = False
                    skip_flag = True
                continue
            fp.write_to_file(in_string.format(i,0,0,0,0))
            prev_line_y = cur_pos[1]
    return


def gen_anis_random(x_size, y_size, K_mag = None, sigma = None):
    with file_parser.Parse_File('anisotropy.txt') as fp:
        print('generating pattern...\n')
        fp.delete_contents()
        header_string = '{:<6s} {:<6s} {:<6s} {:<6s} {:<6s}\n'.format('i', 'K', 'Kx', 'Ky', 'Kz')
        in_string = '{:<6d} {:<6.3f} {:<6.3f} {:<6.3f} {:<6.3f}\n'

        if K_mag != None:
            K = K_mag
        else:
            K = 1
        if sigma != None:
            S = sigma
        else:
            S = 1
        fp.write_to_file(header_string)

        for i in range(x_size*y_size):
            fp.write_to_file(in_string.format(i,random.gauss(K, S),0,0,1))
    return

def gen_r_pos(x_size, y_size):
    with file_parser.Parse_File('r_pos.txt') as fp:
        fp.delete_contents()
        fp.write_to_file('basis\n{:d}\n'.format(x_size*y_size))
        for i in range(x_size):
            for j in range(y_size):
                fp.write_to_file(str(i/float(x_size))+' '+str(j/float(y_size))+' 0\n')
                pass
        pass
    return