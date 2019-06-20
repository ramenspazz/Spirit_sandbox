#file start
import file_parser
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