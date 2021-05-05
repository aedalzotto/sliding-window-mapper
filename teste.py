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

#dependence_list = [5,-2,-3,-4,-5,0]
#dependence_list = [3,2,-3,-3,-1]
#dependence_list = [3,-3,-3,-1]
#dependence_list = [3,0,-1,-2]
#dependence_list = [3,2,-3,-3,0]
dependence_list = [5,-2,-3,0,2,-5,-3]

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
	tam = len(dp_list)
	out = []
	for x in range(tam):
		if (t in dp_list[x]):
			out.append(x)
	return out

def initial(dp_list):
	out = []
	for task in range(len(dp_list)):
		x = antecessor_task(dp_list, task)
		if (x == []):
			out.append(task)
	return out


#print(dependence_list)
lista = build_app(dependence_list)
#print(lista)
#print(antecessor_task(lista,2))
#print(initial(lista))

free_page_matrix = np.random.randint(PKG_MAX_LOCAL_TASKS + 1, size=(X_SIZE, Y_SIZE))
print(free_page_matrix)

def window_cost(x_start, y_start, w_size):
	free_page_cnt = 0
	free_page_pe = 0

	x_limit = x_start + w_size
	if x_limit > X_SIZE:
		x_limit = X_SIZE

	y_limit = y_start + w_size
	if y_limit > Y_SIZE:
		y_limit = Y_SIZE

	for x in range(x_start, x_limit):
		for y in range(y_start, y_limit):
			free_page_cnt = free_page_cnt + free_page_matrix[x][y]
			if (free_page_matrix[x][y] != 0):
				free_page_pe = free_page_pe + 1
	
	return free_page_cnt, free_page_pe

free_pages_window = 0
selected_window = LAST_WINDOW
w = int(np.sqrt(APP_TASKS/PKG_MAX_LOCAL_TASKS))
if (w < 3):
	w = 3

#free_pages = window_cost(2, 2, 3)
#print("Free pages = {:d}".format(free_pages))
free_pe = 0

while (True):
	#Alterar a busca para começar a partir da última janela selecionada
	while (True):
		free_pages,free_pe = window_cost(selected_window[0], selected_window[1], w)
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
		print(selected_window)
		print(free_pages)
	print(selected_window)
	print(free_pages)
	if (free_pages_window >= APP_TASKS):
		LAST_WINDOW = selected_window
		break
	else:
		w = w + 1
		selected_window = (0,0) # VERIFICAR SE É (0,0) OU LAST_WINDOW
print(free_pages_window)
print(free_pe)

def map(t, selected_window, w):
	# ignorar parte 1
	# cost = -1
	# sucessores = 1
	# verificar antecessores
	# Parte 3:
	# Definir limites da janela e iterar (igual a função window_cost)
	# Para cada PE verificado iterar em sucessores e antecessores.
	# If uma das tarefas iteradas estiver mapeadas (seja antecessor ou sucessor) soma a distância mahantan a variavel c
	# If c for menor que cost
	# atualiza cost e xy candidato
	# Ao final quando encontrar xy ótimo decrementar uma página livre
	cost = -1
	sucessor_task = build_app(dependence_list)
	list_comunicating = antecessor_task(sucessor_task, t) + sucessor_task[t]
	print(list_comunicating)

	for x in range(selected_window[0], selected_window[0] + w):
		for y in range(selected_window[1], selected_window[1] + w):
			if (free_page_matrix[x][y] != 0): #PE apto a receber a task t
				# COMO SABER SE AS TASKS ANTECESSORAS E SUCESSOR ESTAM MAPEADAS (???)
				##### ERRO ENCONTRADO!!! #####
				# NÃO TEM VARIAVEL COM A JANELA SELECIONADA, SABEMOS SÓ A CAPACIDADE MAXIMA DA JANELA (free_pages_window)
				# E A QUANTIDADE DE PE'S DISPONIVEIS NESTA JANELA (free_pe)
				c = 0
				

				if (c < cost):
					cost = c
					selected_PE = (x,y)
	free_page_matrix[selected_PE[0]][selected_PE[1]] = free_page_matrix[selected_PE[0]][selected_PE[1]] - 1 #decrementar pagina livre
	return selected_PE

print(LAST_WINDOW)
print(selected_window)
print(w)
print(free_page_matrix[0][0])
map(0,selected_window,w)