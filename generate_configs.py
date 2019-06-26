#file start
import file_parser
import fileinput
import sympy as sy
import numpy as np
import math
import os

def gen_h_file(xsize, ysize, J, D):
    with file_parser.Parse_File('h.txt') as fp:
        fp.delete_contents()
        
        in_string = '{:<6d}  {:<6d}  {:<6d}  {:<6d}  {:<6d}  {:<6.3f}  {:<6.3f}  {:<6d}  {:<6d}  {:<6d}\n'
        fp.write_to_file('{:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}  {:<6s}\n'.format('i','j','da','db','dc','Jij','Dij','Dija','Dijb','Dijc'))
        
        for i in range(xsize*ysize):
            d = int(math.pow(-1,math.floor((i+1)/ysize)+1))
            fp.write_to_file(in_string.format(i,i+1,0,0,0,J,D,d,0,0))
            pass

        for j in range(xsize*(ysize-1)):
            fp.write_to_file(in_string.format(j,j+xsize,0,0,0,J,D,0,-1,0))
            pass

def gen_anis_pattern(x_size, y_size, pattern, K_mag = None):
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

        expr = sy.sympify(pattern)
        f = sy.utilities.lambdify('x', expr, "numpy")
        expr_in = np.arange(-10,11)
        expr_output = -1 * f(expr_in) + x_size/2
        write_flag = False
        skip_flag = False
        mirror_element = x_size/2 + f(expr_in)
        mirror_index = 0
        prev_line_y = 1
        print(expr_output)
        print(mirror_element)
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
                        fp.write_to_file(in_string.format(i,K,0,0,1))
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



def gen_anis_file(x_size, y_size, start, end, K_mag = None):
    with file_parser.Parse_File('anisotropy.txt') as fp:
        fp.delete_contents()
        write_flag = False
        header_string = '{:<6s} {:<6s} {:<6s} {:<6s} {:<6s}\n'.format('i', 'K', 'Kx', 'Ky', 'Kz')
        in_string = '{:<6d} {:<6.3f} {:<6.3f} {:<6.3f} {:<6.3f}\n'

        if K_mag != None:
            K = K_mag
        else:
            K = 1

        fp.write_to_file(header_string)
        for i in range(x_size*y_size):
            if (i == (start[0]*y_size + start[1])) and (not write_flag):
                #set the write flag to true so that
                #the next itterations can start writing
                #anis up till the specified endpoint passed
                #in function call
                write_flag = True
            elif (i == (end[0]*y_size + end[1])) and (write_flag):
                fp.write_to_file(in_string.format(i,K,0,0,1))
                write_flag = False
            elif write_flag:
                fp.write_to_file(in_string.format(i,K,0,0,1))
            else:
                fp.write_to_file(in_string.format(i,0,0,0,0))
            pass
        #start writing anis.txt
    return

def gen_r_pos(xsize, ysize):
    with file_parser.Parse_File('r_pos.txt') as fp:
        fp.delete_contents()
        fp.write_to_file('basis\n{:d}\n'.format(xsize*ysize))
        for i in range(xsize):
            for j in range(ysize):
                fp.write_to_file(str(i/float(xsize))+' '+str(j/float(ysize))+' 0\n')
                pass
        pass
    return
"""
def update_config(xsize, ysize):
    with file_parser.Parse_File('boundary.cfg') as fp:
        start_line = fp.find_line_number('basis')
"""