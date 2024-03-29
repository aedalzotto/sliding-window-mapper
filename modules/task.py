#!/usr/bin/env python3

class Task:
	def __init__(self, name, task_id, successors):
		self.name = name
		self.id = task_id
		self.successors = successors
		self.mapped = (-1, -1)

	def get_id(self):
		return self.id

	def get_name(self):
		return self.name

	def get_successors(self):
		return self.successors

	def get_mapped(self):
		return self.mapped

	def set_mapping(self, pe):
		self.mapped = pe

	def set_score(self, score):
		self.score = score

	def get_score(self):
		return self.score
