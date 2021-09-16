#!/usr/bin/env python3

class Processor:
	def __init__(self, max_local_tasks):
		self.max_local_tasks = max_local_tasks
		self.free_pages = self.max_local_tasks
		self.pending = 0

	def get_free_pages(self):
		return self.free_pages

	def get_tasks_diff_app(self):
		return self.max_local_tasks - (self.free_pages + self.pending)

	def get_tasks_same_app(self):
		return self.pending

	def add_task(self):
		self.pending += 1
		self.free_pages -= 1
	
	def clear_pending(self):
		self.pending = 0

	def remove_task(self):
		self.free_pages += 1