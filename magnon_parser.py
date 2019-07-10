import fileinput
import os

def parse_magnon(fname, x_size, y_size):
    with open(fname, 'r') as fp1:
        with open('outfile', 'a') as fp2:
            fp1.seek(0,2)
            endloc = fp1.tell()
            fp1.seek(0)
            count = 0
#TODO first read the lattice size
            while True:
                in_string = fp1.readline()
                if in_string == '#':
                    continue
                if (x_size/2 - 1) == (count % x_size):
                    count = count + 1
                    fp2.write(in_string)
                elif (x_size/2 + 1) == (count % x_size):
                    count = count + 1
                    fp2.write(in_string)
                elif (in_string == '') and (fp1.tell() == endloc):
                    print('EOF reached!!\n\n')
                    break
                else:
                    count = count + 1
x = int(raw_input('Enter x: '))
y = int(raw_input('Enter y: '))
fname = raw_input('Enter file name to parse: ')
parse_magnon(fname, x, y)