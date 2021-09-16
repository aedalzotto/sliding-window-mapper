#!/usr/bin/env python3

from os import makedirs, getenv
from subprocess import Popen

class Debug:
	def __init__(self, testcase, size):
		self.testcase = testcase
		self.size = size

		makedirs(self.testcase+"/debug", exist_ok=True)
		self.generate_services()
		self.generate_platform({})

		self.traffic = open(self.testcase+"/debug/traffic_router.txt", "w")
		self.debugger_path = getenv('MEMPHIS_DEBUGGER_PATH')
		self.debugger = Popen(["java", "-jar", self.debugger_path+"/Memphis_Debugger.jar", self.testcase+"/debug/platform.cfg"])

	def generate_services(self):
		services = open(self.testcase+"/debug/services.cfg", "w")
		services.write("TASK_ALLOCATION 40\n")
		services.write("TASK_TERMINATED 70\n")
		services.write("\n")
		services.write("$TASK_ALLOCATION_SERVICE 40 221\n")
		services.write("$TASK_TERMINATED_SERVICE 70 221\n")
		services.close()

	def generate_platform(self, apps):
		f = open(self.testcase+"/debug/platform.cfg", "w")
		f.write("router_addressing XY\n")
		f.write("channel_number 1\n")
		f.write("mpsoc_x "+str(self.size)+"\n")
		f.write("mpsoc_y "+str(self.size)+"\n")
		f.write("flit_size 32\n")
		f.write("clock_period_ns 10\n")
		f.write("cluster_x "+str(self.size)+"\n")
		f.write("cluster_y "+str(self.size)+"\n")
		f.write("manager_position_x "+str(self.size)+"\n")
		f.write("manager_position_y "+str(self.size)+"\n")
		f.write("BEGIN_task_name_relation\n")
		for app in apps:
			for task in app.get_tasks():
				f.write(task.get_name()+" "+str((app.get_id() << 8) + task.get_id())+"\n")
		f.write("END_task_name_relation\n")
		f.write("BEGIN_app_name_relation\n")
		for app in apps:
			f.write(app.get_name()+" "+str(app.get_id())+"\n")
		f.write("END_app_name_relation\n")
		f.close()

	def reset(self):
		self.debugger.terminate()
		self.debugger = Popen(["java", "-jar", self.debugger_path+"/Memphis_Debugger.jar", self.testcase+"/debug/platform.cfg"])

	def end(self):
		self.traffic.close()
		self.debugger.terminate()

	def add_task(self, application, task_id, tick):
		pe = application.get_tasks()[task_id].get_mapped()
		self.traffic.write(str(tick)+"\t"+str((pe[0] << 8) + pe[1])+"\t40\t0\t0\t0\t"+str((pe[0] << 8) + pe[1])+"\t"+str((application.get_id() << 8) + task_id)+"\n")
	
	def update_traffic(self):
		self.traffic.flush()

	def remove_task(self, application, task_id, tick):
		pe = application.get_tasks()[task_id].get_mapped()
		self.traffic.write(str(tick)+"\t"+str((pe[0] << 8) + pe[1])+"\t70\t4\t0\t4\t-1\t"+str((int(application.get_id()) << 8) + task_id)+"\n")
