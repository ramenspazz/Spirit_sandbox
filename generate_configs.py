#file start
import file_parser
import math
import os

def gen_h_file(xsize, ysize, J, D):
    with file_parser.Parse_File('h.txt') as fp:
        fp.delete_contents()
        for i in range(xsize*ysize):
            fp.write_to_file(str(i)+' '+str(i+1)+' 0 0 0 '+str(J)+' '+str(D)+' '+str(math.pow(-1,(i+1)/100))+' 0 0\n')
            pass

        for j in range(xsize*ysize):
            fp.write_to_file(str(j)+' '+str(j+201)+' 0 0 0 '+str(J)+' '+str(D)+' 0 -1 0\n')
            pass

def gen_r_pos(xsize, ysize):
    with file_parser.Parse_File('r_pos.txt') as fp:
        fp.delete_contents()
        for i in range(xsize):
            for j in range(ysize):
                fp.write_to_file(str(i/float(xsize))+' '+str(j/float(ysize))+' 0\n')
                pass
        pass
    return

def update_config(xsize, ysize):
    with file_parser.Parse_File('boundary.cfg') as fp:
        start_line = fp.find_line_number('basis')