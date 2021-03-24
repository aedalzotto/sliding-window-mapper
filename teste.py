# -*- coding: utf-8 -*-
#Nome: Leonardo Erthal
#Data: 18/03
#

import numpy as np

APP_TASKS = 9

X_SIZE = 8
Y_SIZE = 8

PKG_MAX_LOCAL_TASKS = 4

LAST_WINDOW = (1, 1)
STRIDE = 2

free_page_matrix = np.random.randint(PKG_MAX_LOCAL_TASKS + 1, size=(X_SIZE, Y_SIZE))
print(free_page_matrix)

def window_cost(x_start, y_start, w_size):
	free_page_cnt = 0

	x_limit = x_start + w_size
	if x_limit > X_SIZE:
		x_limit = X_SIZE

	y_limit = y_start + w_size
	if y_limit > Y_SIZE:
		y_limit = Y_SIZE

	for x in range(x_start, x_limit):
		for y in range(y_start, y_limit):
			free_page_cnt = free_page_cnt + free_page_matrix[x][y]
	
	return free_page_cnt

free_pages_window = 0
selected_window = (-1, -1)
w = 3





free_pages = window_cost(2, 2, 3)
print("Free pages = {:d}".format(free_pages))


