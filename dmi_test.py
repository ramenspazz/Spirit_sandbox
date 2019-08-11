from __future__ import print_function
import math

x_size = 12
y_size = 9
flag = False
prev = 0
divider = 2
for i in range(x_size*y_size):
    # if the current element is a multipul of a third of the row size
    check = (i / x_size) % (y_size / 3)
    if flag:
        divider = 4
    else:
        divider = 2
    temp = int(math.floor(i / (x_size/divider)))
    exponent = temp % divider
    print('{:d}'.format(exponent), end='')
    #d = int(math.pow(-1,exponent))
    if (x_size - 1) == (i % x_size):
        print('\n')
        if(check + 1 == 3):
            flag = not flag
        continue

for i in range(x_size*y_size):
    temp = int(math.floor(i / (x_size/3))) % 2
    print(temp)