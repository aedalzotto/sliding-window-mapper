# -*- coding: utf-8 -*-
#Nome: Leonardo Erthal
#Data: 18/03
#
import numpy as np
X_SIZE = 8;
Y_SIZE = 8;

def window_cost(x,y,w_size):
    x = X_SIZE - x - 1; #Modifica x por causo do numpy
    z = 0;
    ate = x - w_size + 1;
    for aux in range(w_size**2):
        if (x >= 0 and y <= 7): #7 é o valor maximo de y
            z = z + m[x][y];
        else:
            x = ate;
            if (y == 7): #7 é o valor maximo y
                break;
        print(z)
        if (x == ate): 
            x = x + size - 1;
            y = y + 1;
        else:
            x = x - 1;
    return z;

arr = np.arange(64);
m = arr.reshape(8,8);
print(m)
r = window_cost(6,6,3);
print(r)