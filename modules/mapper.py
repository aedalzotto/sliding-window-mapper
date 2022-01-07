#!/usr/bin/env python3

import numpy as np
import traceback
from debug import Debug
from application import Application
from processor import Processor


class Mapper:
	__APPLICATIONS = {
		"aes": [9, 2, 3, 4, 5, 6, 7, 8, -9, -1, -1, -1, -1, -1, -1, -1, -1],
		"audio_video": [7, -6, -1, -6, -3, -4, 0, 2, -5],  # FIR is task 0 because is uppercase
		"dijkstra": [7, -7, -7, -7, -7, -7, 1, 2, 3, 4, -5, 0],
		"dtw": [6, 2, 3, 4, -5, -6, -6, -6, -6, 2, 3, 4, -5],
		"fixe_base_test_16": [14, 0, 0, 0, 0, -1, -1, 4, 11, 12, -13, 4, 11, 12, -14, -2, -2, 0, 0, 3, 5, -9, 3, 6, -10],
		"matrix_multi_master_slave": [6, 2, 3, 4, 5, -6, -1, -1, -1, -1, -1],
		"mpeg": [5, -4, -1, -2, 0, -3],
		"MPEG4": [12, -8, -8, -8, -10, -9, -8, -10, 1, 2, 3, 5, 6, 11, -12, -6, 3, 4, 7, -11, -8, 0],
		"MWD": [12, 0, -12, -6, 2, -10, -9, -9, -10, -3, -11, 7, -8, -1, -5],
		"prod_cons": [2, 0, -1],
		"quicksort_divider_conquer": [15, 3, 4, -15, 5, 6, -15, 1, 7, -8, 1, 9, -10, 2, 11, -12, 2, 13, -14, -3, -3, -4, -4, -5, -5, -6, -6, 1, -2],
		"synthetic1": [6, -3, -3, 4, -5, -6, -6, 0],
		"VOPD": [12, 4, -8, -3, -9, -3, -1, -11, -5, -4, -12, -7, 6, -12, -6]
	}

	__TASKS = {
		"aes": ["aes_master", "aes_slave_1", "aes_slave_2", "aes_slave_3", "aes_slave_4", "aes_slave_5", "aes_slave_6", "aes_slave_7", "aes_slave_8"],
		"audio_video": ["FIR", "adpcm_dec", "idct", "iquant", "ivlc", "join", "split"],
		# FIR is task 0 because is uppercase
		"dijkstra": ["dijkstra_0", "dijkstra_1", "dijkstra_2", "dijkstra_3", "dijkstra_4", "divider", "print"],
		"dtw": ["bank", "p1", "p2", "p3", "p4", "recognizer"],
		"fixe_base_test_16": ["DLAB", "DRGB", "DXYZ", "GFC", "LAB1", "LAB2", "P1", "P2", "RGB1", "RGB2", "RMS", "WRMS", "XYZ1", "XYZ2"],
		"matrix_multi_master_slave": ["master", "slave1", "slave2", "slave3", "slave4", "slave51"],
		"mpeg": ["idct", "iquant", "ivlc", "print", "start"],
		"MPEG4": ["ADSP_0", "AU_0", "BAB_0", "IDCT_0", "MCPU_0", "RAST_0", "RISC_0", "SDRAM_0", "SRAM1_0", "SRAM2_0", "UPSAMP_0", "VU_0"],
		"MWD": ["BLEND", "HS", "HVS", "IN", "JUG1", "JUG2", "MEM1", "MEM2", "MEM3", "NR", "SE", "VS"],
		"prod_cons": ["cons", "prod"],
		"quicksort_divider_conquer": ["sorting_1", "sorting_2", "sorting_3", "sorting_4", "sorting_5", "sorting_6", "sorting_7", "sorting_8", "sorting_9", "sorting_10", "sorting_11", "sorting_12", "sorting_13", "sorting_14", "sorting_master"],
		"synthetic1": ["taskA", "taskB", "taskC", "taskD", "taskE", "taskF"],
		"VOPD": ["ACDC_0", "ARM_0", "IDCT2_0", "IQUANT_0", "ISCAN_0", "PAD_0", "RUN_0", "STRIPEM_0", "UPSAMP_0", "VLD_0", "VOPME_0", "VOPREC_0"]
	}

	def __init__(self, max_local_tasks, min_w, stride, size, testcase):
		self.max_local_tasks = max_local_tasks
		self.min_w = min_w
		self.stride = stride
		self.size = size
		self.testcase = testcase

		self.debug = Debug(self.testcase, self.size)

		self.free_pages = self.max_local_tasks * self.size * self.size
		self.running = []
		self.history = []
		self.appid = 0
		self.tick = 0
		self.last_window = (self.size - self.min_w, self.size - self.min_w)

		self.processors = []
		for x in range(self.size):
			line = []
			for y in range(self.size):
				line.append(Processor(self.max_local_tasks))
			self.processors.append(line)

		# self.processors[0][0].add_task() # Mapping Task

		print("Sliding window mapper for many-cores")
		print("Scenario name: {}".format(self.testcase))
		print("\tMany-core size: {}x{}".format(self.size, self.size))
		print("\tMaximum tasks per PE: {}".format(self.max_local_tasks))
		print("\tSliding window mininum size: {}".format(self.min_w))
		print("\tSliding window stride: {}".format(self.stride))

	def interactive(self):
		opt = -1
		while True:
			print("\nSelect an option:")
			print("\tA - Add application")
			print("\tR - Remove application")
			print("\tD - Reset debugger")
			print("\tE - Exit")
			opt = input("Type your option: ")
			if opt == 'A':
				self.add_application()
			elif opt == 'R':
				self.remove_application()
			elif opt == 'D':
				self.debug.reset()
			elif opt == 'E':
				self.debug.end()
				exit()
			else:
				print("Invalid option, try again!")

	def add_application(self):
		print("\nAvailable applications:")

		count = 1
		application_names = list(Mapper.__APPLICATIONS.keys())
		for name in application_names:
			print("\t{} - {} ({})".format(count, name, str(len(Mapper.__TASKS.get(name)))))
			count += 1
		print("\tB - Back to main menu")

		descriptor = {}
		while True:
			opt = input("Type your option: ")
			if opt == 'B':
				return
			else:
				try:
					descriptor = list(Mapper.__APPLICATIONS.values())[int(opt) - 1]
					break
				except:
					print("Invalid option, try again!")
					continue

		# Check for space before building the application object
		task_cnt = descriptor[0]
		if task_cnt > self.free_pages:
			print("Not enough free pages. App requires {} and system has {} free.".format(task_cnt, self.free_pages))
			return

		# Remove the application size from the available pages and build the application object
		self.free_pages -= task_cnt
		application = Application(opt, self.appid, list(Mapper.__TASKS.values())[int(opt) - 1], descriptor)

		self.appid += 1

		## First mapping step: get the mapping window
		window, w = self.window_search(task_cnt)
		print("Window {}x{} with size {}x{}".format(window[0], window[1], w[0], w[1]))
		self.last_window = window

		## Second step: find the correct task mapping order
		order = self.mapping_order(application)
		print("Order = {}".format(order))

		## Final step: map each task
		for task_id in order:
			# Map task
			self.map(application, window, w, task_id)

			# Add debugging info
			self.tick += 1
			self.debug.add_task(application, task_id, self.tick)

		### Tasks are mapped. Compute a score for the application, for each task, and clear pending mapping
		application.set_score(self.processors)
		application.compute_bounding_box()
		self.running.append(application)
		self.history.append(application)

		self.debug.update_traffic()
		self.debug.generate_platform(self.history)

	def window_search(self, task_cnt):
		w = (self.min_w, self.min_w)

		# First check if the minimum window can hold the application
		# Increase in Wx or Wy alternately
		while w[0] * w[1] * self.max_local_tasks < task_cnt:
			if w[1] <= w[0]:
				w = (w[0], w[1] + 1)
			else:
				w = (w[0] + 1, w[1])

			# Reset the last selected window
			self.last_window = (self.size - w[0], self.size - w[1])

		window = self.next_window(self.last_window, w)

		while True:
			# Slide from the last window to the many-core top right corner
			while window[0] > self.last_window[0] or window[1] > self.last_window[1]:
				if self.window_pages(window, w) >= task_cnt:
					return window, w

				window = self.next_window(window, w)

			# Slide from the bottom left corner until the last window
			while window[0] < self.last_window[0] or window[1] < self.last_window[1]:
				if self.window_pages(window, w) >= task_cnt:
					return window, w

				window = self.next_window(window, w)

			# Verify the last window
			if self.window_pages(window, w) >= task_cnt:
				return window, w

			# If the function reached this point, it means that this window size cant hold the application
			# Increase Wx or Wy alternately
			if w[1] <= w[0]:
				w = (w[0], w[1] + 1)
			else:
				w = (w[0] + 1, w[1])

			# Reset the last selected window
			self.last_window = (self.size - w[0], self.size - w[1])
			window = self.next_window(self.last_window, w)

	def next_window(self, window, w):
		if window[0] + w[0] < self.size:
			# If we can slide in X
			window = (window[0] + self.stride, window[1])

			if window[0] + w[0] > self.size:
				window = (self.size - w[0], window[1])

		elif window[1] + w[1] < self.size:
			# If we cant slide in X, slide in Y and bring X back to 0
			window = (0, window[1] + self.stride)

			if window[1] + w[1] > self.size:
				window = (0, self.size - w[1])

		else:
			# If we cant slide in X and in Y, return to bottom left position
			window = (0, 0)

		return window

	def window_pages(self, window, w):
		page_cnt = 0

		for x in range(window[0], window[0] + w[0]):
			for y in range(window[1], window[1] + w[1]):
				page_cnt += self.processors[x][y].get_free_pages()

		return page_cnt

	def mapping_order(self, application):
		initials_ids = application.get_initials_ids()

		ordered = 0
		order = []
		for initial_id in initials_ids:
			order.append(initial_id)
			order, ordered = application.order_successors(order, ordered)

		for task in application.get_tasks():
			if task.get_id() not in order:
				order.append(task.get_id())
				order, ordered = application.order_successors(order, ordered)

		return order

	def map(self, application, window, w, task_id):
		cost = np.inf

		# Create a list of all communicating tasks
		communicating = application.get_predecessors(task_id) + application.get_tasks()[task_id].get_successors()
		# Make sure to not have duplicate entried
		communicating = list(set(communicating))

		pe = (0, 0)

		for x in range(window[0], window[0] + w[0]):
			for y in range(window[1], window[1] + w[1]):
				if self.processors[x][y].get_free_pages() > 0:  # PE able to receive task
					c = self.compute_cost((x, y), application, communicating)
					if c < cost:
						cost = c
						pe = (x, y)
						if cost == 0:
							self.processors[pe[0]][pe[1]].add_task()
							application.get_tasks()[task_id].set_mapping(pe)
							return

		self.processors[pe[0]][pe[1]].add_task()
		application.get_tasks()[task_id].set_mapping(pe)

	def remove_application(self):
		print("Removing application")

		for app in self.running:
			print("\t{} - {}".format(app.get_id(), app.get_name()))

	   # x = app.get_id()

		print("\tB - Back to main menu")

		while True:
			opt = input("Type your option: ")
			if opt == 'B':
				return

			try:
				app = next(x for x in self.running if x.get_id() == int(opt))
				break
			except:
				print("Invalid option, try again!")
				continue

		self.running.remove(app)		# Remove application from running list

		for task in app.get_tasks():
			pe = task.get_mapped()
			self.processors[pe[0]][pe[1]].remove_task()	# Remove task from processor
			self.free_pages += 1  						# Release free page in many-core
			self.tick += 1
			self.debug.remove_task(app, task.get_id(), self.tick)
			if self.running:  							# If there is any other running application, try to defrag
				self.defrag(pe)

		self.debug.update_traffic()

	def defrag(self, pe):
		frag = sorted(self.running, key=lambda x: x.get_score(), reverse=True)	# Order running applications by the most fragmented (worst score)
		for app in frag:
			bb_f, w_f = app.get_bb()			# Gets the bounding box of the running app
			if self.is_in_bb(bb_f, w_f, pe):	# If the removed task was in the application bounding box, try to defrag
				tasks = sorted(app.get_tasks(), key=lambda x: x.get_score(), reverse=True)  # Order the tasks from the worst to best (by score)
				for task in tasks:
					if self.try_migration(pe, app, task.get_id()):
						app.set_score(self.processors)				# If migrated, compute new score and return
						return

	def is_in_bb(self, bb, w, pe):
		if pe[0] >= bb[0] and pe[0] < bb[0] + w[0] and pe[1] >= bb[1] and pe[1] < bb[1] + w[1]:
			return True
		else:
			return False

	def try_migration(self, pe, application, task_id):
		communicating = application.get_predecessors(task_id) + application.get_tasks()[task_id].get_successors()
		communicating = list(set(communicating))			# Get the set of communicating tasks
		old_pe = application.tasks[task_id].get_mapped()	# Gets the PE where the task is actually mapped

		application.get_tasks()[task_id].set_mapping(-1, -1)	# Fake removal of the task to compute
		self.processors[old_pe[0]][old_pe[1]].remove_task()

		new_cost = self.compute_cost(pe, application, communicating)
		old_cost = self.compute_cost(old_pe, application, communicating)	# The old cost should be updated

		application.get_tasks()[task_id].set_mapping(old_pe, 0)		# Re-map the task -- unfake the removal

		if new_cost < old_cost:		# Should migrate
			print("Migrating task {} from PE {}x{} to PE {}x{}.".format(task_id, old_pe[0], old_pe[1], pe[0], pe[1]))
			
			self.tick += 1												# Remove task from old PE
			self.debug.remove_task(application, task_id, self.tick)
			application.get_tasks()[task_id].set_mapping(pe, 0)

			self.processors[pe[0]][pe[1]].add_task()					# Add task to new PE
			self.tick += 1
			self.debug.add_task(application, task_id, self.tick)
			return True
		else:
			self.processors[old_pe[0]][old_pe[1]].add_task()		# Re-map the task to processor
			return False

	def compute_cost(self, pe, application, communicating):
		c = 0
		same_app = application.get_tasks_same_app(pe)
		c += (self.processors[pe[0]][pe[1]].get_mapped_task_cnt() - same_app) * 4  # Cost of 4 for each task of a different app
		c += same_app * 2
		for comm in communicating:
			mapped = application.get_tasks()[comm].get_mapped()
			if mapped != (-1, -1):
				dist = abs(mapped[0] - pe[0]) + abs(mapped[1] - pe[1])
				c += dist  # Cost of 1 for each hop to each comm tas
		return c
