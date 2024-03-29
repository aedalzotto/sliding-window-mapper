#!/usr/bin/env python3
import numpy as np

from processor import Processor
from task import Task

class Application:
	def __init__(self, app_name, app_id, task_names, descriptor):
		self.name = app_name
		self.id = app_id
		self.task_cnt = descriptor[0]
		self.tasks = []

		successors = []
		task_id = 0
		for value in descriptor[1:]:
			if value != 0:
				successors.append(abs(value) - 1)

			if value <= 0:
				task = Task(task_names[task_id], task_id, successors)
				self.tasks.append(task)
				task_id += 1
				successors = []

	def get_id(self):
		return self.id

	def get_name(self):
		return self.name

	def get_initials_ids(self):
		initials = []
		for task in self.tasks:
			predecessors = self.get_predecessors(task.get_id())
			if predecessors == []:
				initials.append(task.get_id())

		return initials

	def get_predecessors(self, task_id):
		predecessors = []
		for t in self.tasks:
			if task_id in t.get_successors():
				predecessors.append(t.get_id())

		return predecessors

	def get_tasks(self):
		return self.tasks

	def order_successors(self, order, ordered):
		while ordered < len(order):
			for successor in self.tasks[order[ordered]].get_successors():
				if successor not in order:
					order.append(successor)
			ordered += 1
			
		return order, ordered

	def set_score(self, processors):
		manhattan_sum = 0
		edges = 0
		for task in self.tasks:
			manhattan_task = 0
			pe = task.get_mapped()
			successors = task.get_successors()
			edges += len(successors)
			for successor in successors:
				pe_succ = self.tasks[successor].get_mapped()
				manhattan_task += abs(pe[0] - pe_succ[0]) + abs(pe[1] - pe_succ[1])

			manhattan_sum += manhattan_task		# This accounts for the global application score

			# This does NOT account for the global applications score, only task internal score
			predecessors = self.get_predecessors(task.get_id())
			for predecessor in predecessors:
				pe_pred = self.tasks[predecessor].get_mapped()
				manhattan_task += abs(pe[0] - pe_pred[0]) + abs(pe[1] - pe_pred[1])

			if len(predecessors) + len(successors) > 0:
				task.set_score(manhattan_task / (len(predecessors) + len(successors)))
			else:
				task.set_score(0)
		
		if edges > 0:
			self.score = manhattan_sum / edges
		else:
			self.score = 0

		print("Application {} score = {}".format(self.id, self.score))

	def compute_bounding_box(self):
		xmin = np.inf
		xmax = 0
		ymin = np.inf
		ymax = 0

		# @todo Maybe change for a lamba expression
		for task in self.get_tasks():
			if task.get_mapped()[0] < xmin:
				xmin = task.get_mapped()[0]
			
			if task.get_mapped()[0] > xmax:
				xmax = task.get_mapped()[0]

			if task.get_mapped()[1] < ymin:
				ymin = task.get_mapped()[1]
			
			if task.get_mapped()[1] > ymax:
				ymax = task.get_mapped()[1]

		wx = xmax - xmin + 1
		wy = ymax - ymin + 1
		self.w = (wx, wy)
		self.bb = (xmin, ymin)

		print("Aplication {} has bounding box {}x{} with size {}x{}.".format(self.id, self.bb[0], self.bb[1], self.w[0], self.w[1])) # Bottom-left coordinates of the bounding box

	def get_bb(self):
		return self.bb, self.w

	def get_score(self):
		return self.score

	def get_tasks_same_app(self, pe):
		count = 0
		for task in self.get_tasks():
			mapped = task.get_mapped() #comparacao de pe c mapped
			if mapped == pe:
				count += 1 #conto todos q sao iguais
		return count