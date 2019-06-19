import linecache as lc
import fileinput
import glob
import os

class Parse_File:
    #constructor
    def __init__(self, fname):
        self.fname = fname # set the file name
        self.fp = None
    #with enter statement
    def __enter__(self):
        self.fp = open(self.fname, 'r+') # open file and assign to fp
        return self
    #destructor
    def __exit__(self, exc_type, exc_value, traceback):
        self.fp.close()

    # returns the line number of the first instance of var found
    # TODO : start search from specific location in file
    def find_line_number(self, var):
        try:
            (self.fp).seek(0)
            prev_len = 0
            while True:
                #this loop reads lines and updates the file pointer
                #location each iteration until the desired text
                #is reached (overshoots one line)
                prev = self.fp.readline()
                if var in prev:
                    prev_len = len(prev)
                    break
                pass
            #backtrack one line by length of desired text -> go up one line
            ln_num = self.fp.tell() - prev_len
            (self.fp).seek(0)
        except IOError:
            print('File error!\n\n\n')
            return(-1)
        return(ln_num)

    #set the variable name var in file to value val
    def set_config_var(self, var, val):
        try:
            (self.fp).seek(self.find_line_number(var))
            (self.fp).write(var + ' ' + str(val) + '\n')
            pass
        except IOError:
            print('File error!\n\n\n')
            return(-1)
        return

    def write_to_file(self, val, line_num=None):
        try:
            if line_num is not None:
                (self.fp).seek(line_num)
            (self.fp).write(val)
        except IOError:
            print('File error!\n\n\n')
            return(-1)

    def delete_contents(self):
        (self.fp).seek(0)
        (self.fp).truncate()
        return


def list_keyword_and_edit(f_name):
	#streach goal: make tk gui to modify
    try:
        fp = open(f_name, 'r+') # open file for read + write
        editlist = []
		#build read lines
        for i, ln in enumerate(fp):
			if (ln[0] == "#") or (ln[0] == "\n"):
				pass
			else:
				#add variable lines to edit list
				editlist.append((i,ln))
				pass
        #display all variables to edit
        for i, var in enumerate(editlist):
            print('VN' + str(i + 1) + ': ' + var[1])
		#move fp to begining of file
        fp.seek(0)
        user_in = ''
        line_num = 0
        print('Enter q to quit editing here or at variable number prompt\n\n')
        while True:
            user_in = raw_input('Enter variable number to edit: ')
            if user_in == 'q':
                break
            line_num = int(user_in)
            user_in = raw_input(editlist[line_num - 1][1] + '\nReplace with?:\n')
            #find and replace line with user text
            while not(editlist[line_num - 1][1] == fp.readline()):
                #this loop reads lines and updates the file pointer
                #location each iteration until the desired text
                #is reached (overshoots one line)
                pass
            #backtrack one line by length of desired text -> go up one line
            fp.seek(fp.tell() - len(editlist[line_num - 1][1]))
            fp.write(user_in)
            pass
        pass
    finally:
        fp.close()
    print("end of editing\n\n")

#concatenates fname2 into fname1 -> fname1
def concatenate_files(fname1, fname2, outname):
    file_list = [fname1, fname2]
    print('Writing config file...')
    with open(outname, 'r+') as file:
        if os.path.isfile(outname):
            file.seek(0)
            file.truncate()
            pass
        input_lines = fileinput.input(file_list)
        file.writelines(input_lines)
    print('Done!')
    return