# -*- coding: utf-8 -*-
#Nome: Leonardo Erthal
#Data: 18/03
#

import numpy as np
import argparse

def build_app(app_descr):
	descr_len = len(app_descr) - 1
	sucessors = []
	aux = []
	for x in range(descr_len):
		if (app_descr[x + 1] > 0):
			aux.append(app_descr[x + 1] - 1)
		else:
			aux.append(abs(app_descr[x + 1]) - 1)
			sucessors.append(aux)
			aux = []
	return sucessors

def window_cost(manycore, x_start, y_start, w_size, x_size, y_size, max_local_tasks):
	free_page_cnt = 0
	free_page_pe = 0

	x_limit = x_start + w_size
	if x_limit > x_size:
		x_limit = x_size

	y_limit = y_start + w_size
	if y_limit > y_size:
		y_limit = y_size

	min_free_pages = max_local_tasks

	for x in range(x_start, x_limit):
		for y in range(y_start, y_limit):
			free_page_cnt = free_page_cnt + manycore[x][y]
			if (manycore[x][y] != 0):
				free_page_pe = free_page_pe + 1
				if (manycore[x][y] < min_free_pages):
					min_free_pages = manycore[x][y]
	
	return free_page_cnt, free_page_pe, min_free_pages

def window_search(manycore, task_cnt, w, stride, max_local_tasks, x_size, y_size, last_selected_window):
	if w**2 * max_local_tasks < task_cnt:
		w = int(np.sqrt(task_cnt/max_local_tasks))
	
	selected_window = last_selected_window
	picked_window = selected_window
	tasks_per_pe = 0
	free_pages_window = 0

	while True:
		while True:
			free_pages, free_pe, min_free_pages = window_cost(manycore, selected_window[0], selected_window[1], w, x_size, y_size, max_local_tasks)
			#print(free_pages)
			#print(selected_window)
			#print(free_pages)

			if free_pages > free_pages_window:
				free_pages_window = free_pages
				picked_window = selected_window

				tasks_per_pe = int(task_cnt/free_pe) + (1 if task_cnt % free_pe else 0)
				if tasks_per_pe > min_free_pages:		# Guarantee worst case
					tasks_per_pe = PKG_MAX_LOCAL_TASKS

				if free_pages_window >= w**2 * max_local_tasks: #totalmente livre
					break

			if selected_window[1] + stride < y_size and selected_window[1] + w != y_size:
				selected_window = (selected_window[0], selected_window[1] + stride)

				if selected_window[1] + w > y_size:
					selected_window = (selected_window[0], y_size - w)

			elif selected_window[0] + w != x_size:
				selected_window = (selected_window[0] + stride, 0)

				if selected_window[0] + w > x_size:
					selected_window = (x_size - w,selected_window[1])

			else:
				selected_window = (0, 0)

			if selected_window == last_selected_window:
				break
			 
		if free_pages_window >= task_cnt:
			break
		else:
			w = w + 1
			selected_window = last_selected_window

	return picked_window, tasks_per_pe, w

def antecessors(sucessors, t):
	antecessors = []
	for x in range(len(sucessors)):
		if t in sucessors[x]:
			antecessors.append(x)
	return antecessors

def map(manycore, selected_window, selected_w, sucessors, t, pending, mapped, tasks_per_pe):
	cost = np.inf
	communicating = antecessors(sucessors, t) + sucessors[t]
	communicating = list(filter(lambda a: a != -1, communicating))

	selected_PE = (0, 0)

	if mapped[t] != (-1, -1):
		return "Task already mapped"

	for x in range(selected_window[0], selected_window[0] + selected_w):
		for y in range(selected_window[1], selected_window[1] + selected_w):
			if manycore[x][y] != 0 and pending[x][y] < tasks_per_pe: #PE apto a receber a task t
				c = 0
				for aux in communicating:
					#print(aux)
					if mapped[aux] != -1: #task sucessora ou antecessora mapeada
						#print(mapped[aux])
						c = c + abs(mapped[aux][0] - x) + abs(mapped[aux][1] - y) #cost igual a distancia Mahantan
						# print("C  ",c)
				if (c < cost):
					cost = c
					selected_PE = (x, y)

	return selected_PE

################################################################################

parser = argparse.ArgumentParser(description='Sliding window mapper for many-cores')
parser.add_argument('size', type=int, help="many-core dimension in either X or Y")
parser.add_argument('page_number', type=int, help="many-core page number for each PE")

parser.add_argument('--w', type=int, help="sliding window starting size", default=3)
parser.add_argument('--stride', type=int, help="sliding window stride", default=2)

args = parser.parse_args()

PKG_MAX_LOCAL_TASKS = args.page_number
PKG_MIN_W = args.w
PKG_STRIDE = args.stride

PKG_X_SIZE = args.size
PKG_Y_SIZE = args.size

print("Sliding window mapper for many-cores")
print("\tMany-core size: {}x{}".format(PKG_X_SIZE, PKG_Y_SIZE))
print("\tMaximum tasks per PE: {}".format(PKG_MAX_LOCAL_TASKS))
print("\tSliding window mininum size: {}".format(PKG_MIN_W))
print("\tSliding window stride: {}".format(PKG_STRIDE))

################################################################################

applications = {
	"aes": [9, 2, 3, 4, 5, 6, 7, 8, -9, -1, -1, -1, -1, -1, -1, -1, -1],
	"dijkstra": [7, -7, -7, -7, -7, -7, 1, 2, 3, 4, -5, 0],
	"dtw": [6, 2, 3, 4, -5, -6, -6, -6, -6, 2, 3, 4, -5],
	"fixe_base_test_16": [14, 0, 0, 0, 0, -1, -1, 4, 11, 12, -13, 4, 11, 12, -14, -2, -2, 0, 0, 3, 5, -9, 3, 6, -10],
	"mpeg": [5, -4, -1, -2, 0, -3],
	"MPEG4": [12, -8, -8, -8, -10, -9, -8, -10, 1, 2, 3, 5, 6, 11, -12, -6, 3, 4, 7, -11, -8, 0],
	"MWD": [12, 0, -12, -6, 2, -10, -9, -9, -10, -3, -11, 7, -8, -1, -5],
	"prod_cons": [2, 0, -1],
	"synthetic1": [6, -3, -3, 4, -5, -6, -6, 0],
	"VOPD": [12, 4, -8, -3, -9, -3, -1, -11, -5, -4, -12, -7, 6, -12, -6]
}

free_pages_system = PKG_MAX_LOCAL_TASKS * PKG_X_SIZE * PKG_Y_SIZE
running = {}
appid = 0
manycore = np.full((PKG_X_SIZE, PKG_Y_SIZE), PKG_MAX_LOCAL_TASKS)
last_selected_window = (0, 0)

opt = -1
while opt == -1:
	print("\nSelect an option:")
	print("\tA - Add application")
	print("\tR - Remove application")
	print("\tE - Exit")
	opt = input("Type your option: ")
	if opt == 'A':
		print("\nAvailable applications:")
		for app in applications:
			print("\t{}".format(app))
		
		print("\tB - Back to main menu")
		app_opt = -1
		while app_opt == -1:
			app_opt = input("Type your option: ")
			if app_opt == 'B':
				break
			else:
				try:
					app_descr = applications[app_opt]

					task_cnt = app_descr[0]
					if task_cnt > free_pages_system:
						print("Not enough free pages. App requires {} and system has {} free.".format(task_cnt, free_pages))
						opt = -1
						break

					free_pages_system = free_pages_system - task_cnt
					print("free pages = "+str(free_pages_system))
					
					sucessors = build_app(app_descr)
					selected_window, tasks_per_pe, selected_w = window_search(manycore, task_cnt, PKG_MIN_W, PKG_STRIDE, PKG_MAX_LOCAL_TASKS, PKG_X_SIZE, PKG_Y_SIZE, last_selected_window)
					print(selected_window)
					print(selected_w)
					last_selected_window = selected_window

					pending = np.zeros((PKG_X_SIZE, PKG_Y_SIZE))
					mapped = []
					for x in range(task_cnt):
						mapped.append((-1, -1))

					for t in range(len(sucessors)):
						selected_PE = map(manycore, selected_window, selected_w, sucessors, t, pending, mapped, tasks_per_pe)
						# print("Task "+str(t), selected_PE)
						mapped[t] = selected_PE
						manycore[selected_PE[0]][selected_PE[1]] = manycore[selected_PE[0]][selected_PE[1]] - 1 #decrementar pagina livre
						pending[selected_PE[0]][selected_PE[1]] = pending[selected_PE[0]][selected_PE[1]] + 1
						# print(pending)

					running[appid] = (mapped, app_opt)
					# running.append((appid, ))
					print(running[appid])
					appid = appid + 1
						
				except:
					app_opt = -1
					print("Invalid option, try again!")
		
		opt = -1
	elif opt == 'R':
		print("Removing application")

		for id in running.keys():
			print("\t{} - {}".format(id, running[id][1]))

		print("\tB - Back to main menu")
		app_opt = -1
		while app_opt == -1:
			app_opt = input("Type your option: ")
			if app_opt == 'B':
				break
			else:
				try:
					app = running[int(app_opt)]
					for pe in app[0]:
						manycore[pe[0]][pe[1]] = manycore[pe[0]][pe[1]] + 1
						free_pages_system = free_pages_system + 1

					del running[int(app_opt)]

				except:
					app_opt = -1
					print("Invalid option, try again!")

		opt = -1
	elif opt == 'E':
		break
	else:
		opt = -1
		print("Invalid option, try again!")

exit()

# def initial(dp_list):
# 	out = []
# 	for task in range(len(dp_list)):
# 		x = antecessor_task(dp_list, task)
# 		if (x == []):
# 			out.append(task)
# 	return out
