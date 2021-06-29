# -*- coding: utf-8 -*-
#Nome: Leonardo Erthal
#Data: 18/03
#

import numpy as np
import subprocess
import argparse
import os
import sys

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

def window_cost(manycore, x_start, y_start, w_size, x_size, y_size):
	free_page_cnt = 0

	x_limit = x_start + w_size[0]
	if x_limit > x_size:
		x_limit = x_size

	y_limit = y_start + w_size[1]
	if y_limit > y_size:
		y_limit = y_size

	for x in range(x_start, x_limit):
		for y in range(y_start, y_limit):
			free_page_cnt = free_page_cnt + manycore[x][y]
	
	return free_page_cnt

def next_window(selected_window, w, x_size, y_size, stride):
	if selected_window[0] + w[0] < x_size:
		selected_window = (selected_window[0] + stride, selected_window[1])

		if selected_window[0] + w[0] > x_size:
			selected_window = (x_size - w[0], selected_window[1])

	elif selected_window[1] + w[1] < y_size:
		selected_window = (0, selected_window[1] + stride)

		if selected_window[1] + w[1] > y_size:
			selected_window = (0, y_size - w[1])

	else:
		selected_window = (0, 0)

	return selected_window

def window_search(manycore, task_cnt, w, stride, max_local_tasks, x_size, y_size, last_selected_window):
	raise_x = False

	while w[0]*w[1]*max_local_tasks < task_cnt:
		if raise_x:
			w = (w[0] + 1, w[1])
			raise_x = False
		else:
			w = (w[0], w[1] + 1)
			raise_x = True
		last_selected_window = (PKG_X_SIZE - w[0], PKG_Y_SIZE - w[1])			
	
	selected_window = next_window(last_selected_window, w, x_size, y_size, stride)

	while True:
		while selected_window[0] > last_selected_window[0] or selected_window[1] > last_selected_window[1]:
			free_pages = window_cost(manycore, selected_window[0], selected_window[1], w, x_size, y_size)

			if free_pages >= task_cnt:
				return selected_window, w

			selected_window = next_window(selected_window, w, x_size, y_size, stride)

		while selected_window[0] < last_selected_window[0] or selected_window[1] < last_selected_window[1]:
			free_pages = window_cost(manycore, selected_window[0], selected_window[1], w, x_size, y_size)

			if free_pages >= task_cnt:
				return selected_window, w

			selected_window = next_window(selected_window, w, x_size, y_size, stride)

		# Verify the last one ("equal" to the last_selected_window)
		free_pages = window_cost(manycore, selected_window[0], selected_window[1], w, x_size, y_size)

		if free_pages >= task_cnt:
			return selected_window, w

		if raise_x:
			w = (w[0] + 1, w[1])
			raise_x = False
		else:
			w = (w[0], w[1] + 1)
			raise_x = True
		last_selected_window = (PKG_X_SIZE - w[0], PKG_Y_SIZE - w[1])
		selected_window = next_window(last_selected_window, w, x_size, y_size, stride)

def antecessors(sucessors, t):
	antecessors = []
	for x in range(len(sucessors)):
		if t in sucessors[x]:
			antecessors.append(x)
	return antecessors

def initial(sucessors):
	initials = []
	for task in range(len(sucessors)):
		antecessors_list = antecessors(sucessors, task)
		if antecessors_list == []:
			initials.append(task)

	return initials

def order_sucessors(t, sucessors, mapping_order, ordered):
	mapping_order.append(t)
	while ordered < len(mapping_order):
		for sucessor in sucessors[mapping_order[ordered]]:
			if sucessor != -1 and sucessor not in mapping_order:
				mapping_order.append(sucessor)
		ordered = ordered + 1

	return mapping_order, ordered

def get_mapping_order(initials, sucessors):
	ordered = 0
	mapping_order = []
	for initial in initials:
		mapping_order, ordered = order_sucessors(initial, sucessors, mapping_order, ordered)

	# print(mapping_order)
	if ordered < len(sucessors):
		for task in range(len(sucessors)):
			if task not in mapping_order:
				mapping_order, ordered = order_sucessors(task, sucessors, mapping_order, ordered)

	# print(mapping_order)

	return mapping_order


def map(manycore, selected_window, selected_w, sucessors, t, pending, mapped):
	cost = np.inf
	communicating = antecessors(sucessors, t) + sucessors[t]
	communicating = list(filter(lambda a: a != -1, communicating))

	selected_PE = (0, 0)

	if mapped[t] != (-1, -1):
		return "Task already mapped"

	manhattan = 0

	for x in range(selected_window[0], selected_window[0] + selected_w[0]):
		for y in range(selected_window[1], selected_window[1] + selected_w[1]):
			# print("PE {}x{}".format(x, y))
			if manycore[x][y] != 0: #PE apto a receber a task t
				c = 0
				m_dist = 0
				c = c + (PKG_MAX_LOCAL_TASKS - (manycore[x][y] + pending[x][y]))*4 # Terceiro critério: número de páginas ocupadas no PE
				c = c + pending[x][y]*2 # Manter tarefas do mesmo app espalhadas pelo many-core: segundo critério
				# print("Custo {}x{} pré = {}".format(x,y,c))
				for aux in communicating:
					# print("Tarefa comunicante {} mapeada em {}".format(aux, mapped[aux]))
					if mapped[aux] != (-1, -1): #task sucessora ou antecessora mapeada
						#print(mapped[aux])
						dist_calc = (abs(mapped[aux][0] - x) + abs(mapped[aux][1] - y))
						m_dist += dist_calc
						c = c + dist_calc*1 # Distância Manhattan: critério de maior importância
						# print("C  ",c)

				# print("Custo {}x{} pós = {}".format(x,y,c))
				if (c < cost):
					cost = c
					manhattan = m_dist
					selected_PE = (x, y)

	return selected_PE, manhattan

def edge_number(sucessors):
	edges = 0
	for sucessor_list in sucessors:
		if sucessor_list[0] != -1:
			edges += len(sucessor_list)

	return edges

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

app_tasks = {
	"aes": ["aes_master", "aes_slave_1", "aes_slave_2", "aes_slave_3", "aes_slave_4", "aes_slave_5", "aes_slave_6", "aes_slave_7", "aes_slave_8"],
	"dijkstra": ["dijkstra_0", "dijkstra_1", "dijkstra_2", "dijkstra_3", "dijkstra_4", "divider", "print"],
	"dtw": ["bank", "p1", "p2", "p3", "p4", "recognizer"],
	"fixe_base_test_16": ["DLAB", "DRGB", "DXYZ", "GFC", "LAB1", "LAB2", "P1", "P2", "RGB1", "RGB2", "RMS", "WRMS", "XYZ1", "XYZ2"],
	"mpeg": ["idct", "iquant", "ivlc", "print", "start"],
	"MPEG4": ["ADSP_0", "AU_0", "BAB_0", "IDCT_0", "MCPU_0", "RAST_0", "RISC_0", "SDRAM_0", "SRAM1_0", "SRAM2_0", "UPSAMP_0", "VU_0"],
	"MWD": ["BLEND", "HS", "HVS", "IN", "JUG1", "JUG2", "MEM1", "MEM2", "MEM3", "NR", "SE", "VS"],
	"prod_cons": ["cons", "prod"],
	"synthetic1": ["taskA", "taskB", "taskC", "taskD", "taskE", "taskF"],
	"VOPD": ["ACDC_0", "ARM_0", "IDCT2_0", "IQUANT_0", "ISCAN_0", "PAD_0", "RUN_0", "STRIPEM_0", "UPSAMP_0", "VLD_0", "VOPME_0", "VOPREC_0"]
}

def generate_platform(name, size, apps):
	f = open(name+"/debug/platform.cfg", "w")
	f.write("router_addressing XY\n")
	f.write("channel_number 1\n")
	f.write("mpsoc_x "+str(size)+"\n")
	f.write("mpsoc_y "+str(size)+"\n")
	f.write("flit_size 32\n")
	f.write("clock_period_ns 10\n")
	f.write("cluster_x "+str(size)+"\n")
	f.write("cluster_y "+str(size)+"\n")
	f.write("manager_position_x "+str(size)+"\n")
	f.write("manager_position_y "+str(size)+"\n")
	f.write("BEGIN_task_name_relation\n")
	for i in apps.keys():
		for x in range(len(app_tasks[apps[i]])):
			f.write(app_tasks[apps[i]][x]+" "+str((i << 8) + x)+"\n")
	f.write("END_task_name_relation\n")
	f.write("BEGIN_app_name_relation\n")
	for i in apps.keys():
		f.write(apps[i]+" "+str(i)+"\n")
	f.write("END_app_name_relation\n")
	f.close()

################################################################################

parser = argparse.ArgumentParser(description='Sliding window mapper for many-cores')
parser.add_argument('size', type=int, help="many-core dimension in either X or Y")
parser.add_argument('page_number', type=int, help="many-core page number for each PE")
parser.add_argument('test_name', help="output name for this program session")

parser.add_argument('--w', type=int, help="sliding window starting size", default=3)
parser.add_argument('--stride', type=int, help="sliding window stride", default=2)

args = parser.parse_args()

PKG_MAX_LOCAL_TASKS = args.page_number
PKG_MIN_W = (args.w, args.w)
PKG_STRIDE = args.stride

PKG_X_SIZE = args.size
PKG_Y_SIZE = args.size
test_name = args.test_name

print("Sliding window mapper for many-cores")
print("Scenario name: {}".format(test_name))
print("\tMany-core size: {}x{}".format(PKG_X_SIZE, PKG_Y_SIZE))
print("\tMaximum tasks per PE: {}".format(PKG_MAX_LOCAL_TASKS))
print("\tSliding window mininum size: {}".format(PKG_MIN_W))
print("\tSliding window stride: {}".format(PKG_STRIDE))

## Create a platform description log
os.makedirs(test_name+"/debug", exist_ok=True)
generate_platform(test_name, PKG_X_SIZE, {})

services = open(test_name+"/debug/services.cfg", "w")
services.write("TASK_ALLOCATION 40\n")
services.write("TASK_TERMINATED 70\n")
services.write("\n")
services.write("$TASK_ALLOCATION_SERVICE 40 221\n")
services.write("$TASK_TERMINATED_SERVICE 70 221\n")
services.close()

################################################################################

free_pages_system = PKG_MAX_LOCAL_TASKS * PKG_X_SIZE * PKG_Y_SIZE
running = {}
apps_history = {}
appid = 0
tick = 0
manycore = np.full((PKG_X_SIZE, PKG_Y_SIZE), PKG_MAX_LOCAL_TASKS)
last_selected_window = (PKG_X_SIZE - PKG_MIN_W[0], PKG_X_SIZE - PKG_MIN_W[1])

traffic = open(test_name+"/debug/traffic_router.txt", "w")
dbg_path = os.getenv('MEMPHIS_DEBUGGER_PATH')
debugger = subprocess.Popen(["java", "-jar", dbg_path+"/Memphis_Debugger.jar", test_name+"/debug/platform.cfg"])

opt = -1
while opt == -1:
	print("\nSelect an option:")
	print("\tA - Add application")
	print("\tR - Remove application")
	print("\tD - Reset debugger")
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
						print("Not enough free pages. App requires {} and system has {} free.".format(task_cnt, free_pages_system))
						opt = -1
						break

					free_pages_system = free_pages_system - task_cnt
					# print("free pages = "+str(free_pages_system))
					
					sucessors = build_app(app_descr)
					selected_window, selected_w = window_search(manycore, task_cnt, PKG_MIN_W, PKG_STRIDE, PKG_MAX_LOCAL_TASKS, PKG_X_SIZE, PKG_Y_SIZE, last_selected_window)
					# print("Selected window is {} with w={}".format(selected_window, selected_w))
					# print(selected_w)
					last_selected_window = selected_window

					pending = np.zeros((PKG_X_SIZE, PKG_Y_SIZE))
					mapped = []
					for x in range(task_cnt):
						mapped.append((-1, -1))

					initial_tasks = initial(sucessors)
					mapping_order = get_mapping_order(initial_tasks, sucessors)					

					manhattan_sum = 0
					for task in mapping_order:
						selected_PE, manhattan = map(manycore, selected_window, selected_w, sucessors, task, pending, mapped)
						manhattan_sum += manhattan
						# print("Task "+str(t), selected_PE)
						mapped[task] = selected_PE
						manycore[selected_PE[0]][selected_PE[1]] = manycore[selected_PE[0]][selected_PE[1]] - 1 #decrementar pagina livre
						pending[selected_PE[0]][selected_PE[1]] = pending[selected_PE[0]][selected_PE[1]] + 1
						# print(pending)
						tick = tick + 1
						traffic.write(str(tick)+"\t"+str((mapped[task][0] << 8) + mapped[task][1])+"\t40\t0\t0\t0\t"+str((mapped[task][0] << 8) + mapped[task][1])+"\t"+str((appid << 8) + task)+"\n")

					print("Distância Manhattan média = {}".format(manhattan_sum / edge_number(sucessors)))

					traffic.flush()

					running[appid] = (mapped, app_opt)
					apps_history[appid] = app_opt
					generate_platform(test_name, PKG_X_SIZE, apps_history)
					# print(running[appid])
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
					app = running[int(app_opt)][0]
					for i in range(len(app)):
						manycore[app[i][0]][app[i][1]] = manycore[app[i][0]][app[i][1]] + 1
						free_pages_system = free_pages_system + 1
						tick = tick + 1
						traffic.write(str(tick)+"\t"+str((app[i][0] << 8)+app[i][1])+"\t70\t4\t0\t4\t-1\t"+str((int(app_opt) << 8)+i)+"\n")

					traffic.flush()

					del running[int(app_opt)]

				except:
					app_opt = -1
					print("Invalid option, try again!")

		opt = -1
	elif opt == 'D':
		debugger.terminate()
		debugger = subprocess.Popen(["java", "-jar", dbg_path+"/Memphis_Debugger.jar", test_name+"/debug/platform.cfg"])
		opt = -1
	elif opt == 'E':
		break
	else:
		opt = -1
		print("Invalid option, try again!")

traffic.close()
debugger.terminate()
sys.exit()
