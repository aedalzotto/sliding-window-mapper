#!/usr/bin/env python3

class Processor:
	def __init__(self, max_local_tasks):
		self.max_local_tasks = max_local_tasks
		self.free_pages = self.max_local_tasks

	def get_free_pages(self):
		return self.free_pages

	def get_tasks_diff_app(self):
		return self.max_local_tasks - self.free_pages

	def add_task(self):
		self.free_pages -= 1

	def remove_task(self):
		self.free_pages += 1
