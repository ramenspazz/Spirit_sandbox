import linecache as lc

#set the variable name var in the config file to value val
def set_config_var(fname, var, val):
    try:
        print('Opening ' + fname + '\n')
        fp = open(fname, 'r+') # open file for read + write
        prev_len = 0
        while True:
            #this loop reads lines and updates the file pointer
            #location each iteration until the desired text
            #is reached (overshoots one line)
            prev = fp.readline()
            if var in prev:
                prev_len = len(prev)
                break
            pass
        #backtrack one line by length of desired text -> go up one line
        fp.seek(fp.tell() - prev_len)
        fp.write(var + ' ' + str(val) + '\n')
        fp.close()
        pass
    except IOError:
        print('File error!\n\n\n')
        return(-1)
    return(0)

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
