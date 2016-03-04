import os
import subprocess
import threading
import sublime, sublime_plugin
from sys import platform as _platform

class KillableCmd(threading.Thread):
	def __init__(self, cmd, timeout, shell, env):

		threading.Thread.__init__(self)

		self.cmd = cmd
		self.shell = shell
		self.timeout = timeout
		self.env = env

	def run(self):

		startupinfo = None

		if sublime.platform() == "windows":
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		out, err = "", ""

		try:
			self.p = subprocess.Popen(
				self.cmd,
				startupinfo=startupinfo,
				stderr=subprocess.PIPE,
				stdout=subprocess.PIPE,
				shell=self.shell,
				env=self.env)

			out, err = map(lambda x: x.decode("utf-8").replace("\r", ""), self.p.communicate())

		except Exception as tryException:
			self.returnValue = "An error occured while opening a subprocess.\n{}".format(tryException)
			return

		if err or self.p.returncode != 0:
			self.returnValue = out + err
			return

		self.returnValue = out


	def Run(self):

		self.start()
		self.join(self.timeout)

		if self.is_alive():
			if hasattr(self, "p"):
				self.p.terminate()
			self.join()
			return "The execution took longer than " + str(self.timeout) + " second(s). Aborting..."

		return self.returnValue

