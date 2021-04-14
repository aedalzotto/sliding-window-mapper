# -*- coding: utf-8 -*-
#Nome: Leonardo Erthal
#Data: 18/03
#

import numpy as np

APP_TASKS = 9

X_SIZE = 8
Y_SIZE = 8

PKG_MAX_LOCAL_TASKS = 4

STRIDE = 2
LAST_WINDOW = (STRIDE,STRIDE)

#dependence_list = [5,-2,-3,-4,-5]
dependence_list = [3,2,-3,-3,-1]
#dependence_list = [3,-3,-3,-1]
#dependence_list = [3,-3,0,-2]

def build_app(dp_list):
	tam = len(dp_list) - 1
	d = []
	aux = []
	for x in range(tam):
		if (dp_list[x + 1] > 0):
			aux.append(dp_list[x+1]-1)
		else:
			aux.append(abs(dp_list[x+1])-1)
			d.append(aux)
			aux = []
	return d

def antecessor_task(dp_list, t):
	#Retornar uma lista de tarefas antecessoras á tarefa "t"
	print("oi")

lista = build_app(dependence_list)
print(lista)


free_page_matrix = np.random.randint(PKG_MAX_LOCAL_TASKS + 1, size=(X_SIZE, Y_SIZE))
#print(free_page_matrix)

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
selected_window = LAST_WINDOW
w = int(np.sqrt(APP_TASKS/PKG_MAX_LOCAL_TASKS))
if (w < 3):
	w = 3

#free_pages = window_cost(2, 2, 3)
#print("Free pages = {:d}".format(free_pages))

while (True):
	#Alterar a busca para começar a partir da última janela selecionada
	while (True):
		free_pages = window_cost(selected_window[0], selected_window[1], w)
		#print(free_pages)
		if (free_pages > free_pages_window):
			free_pages_window = free_pages
			if (free_pages_window >= (w**2 * PKG_MAX_LOCAL_TASKS)): #totalmente livre
				break
		if ((selected_window[1] + STRIDE) < Y_SIZE and (selected_window[1] + w != Y_SIZE)): 
			selected_window =  (selected_window[0],selected_window[1] + STRIDE)
			if ((selected_window[1] + w) > Y_SIZE):
				selected_window = (selected_window[0],Y_SIZE - w)
		elif ((selected_window[0] + w) != X_SIZE):
			selected_window = (selected_window[0] + STRIDE,0)
			if ((selected_window[0] + w) > X_SIZE):
				selected_window = (X_SIZE - w,selected_window[1])
		else:
			selected_window = (0,0)
		if (selected_window == LAST_WINDOW):
			break
		#print(selected_window)
	if (free_pages_window >= APP_TASKS):
		LAST_WINDOW = selected_window
		break
	else:
		w = w + 1
		selected_window = (0,0)
#print(free_pages_window)
