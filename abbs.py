#!/usr/bin/env python3
'''
{2}: A simple AOSC OS ABBS Repository manager.
Author: {0}
Version: {1}

Usage:
{2} [-V] subcommand [command] [options...] [arguments...]

Or:
{2} [-V] command [options...] [arguments...]

Run `{2} help [subcommand]' for the documentation of respective subfunction.

Options:
	-V		Enable verbose output

Subcommands:
'''

"""
TODO list
- Shortcuts for lazy ones like me.
- Exit points should be clear. exit() should not present in class methods(my thought).
"""
import os 
import re
import sys
import yaml
import argparse
import getpass
import subprocess


AUTHOR = 'Cyanoxygen <cyanoxygen@aosc.io>'
VER = '0.0.1'
REPOURL='https://github.com/aosc-dev/aosc-os-abbs.git'
EXEC=sys.argv[0]

sublist = []
names = []
loaded = {}

class _conf:
	"""
	Config file loader.
	If the config file is empty, then the setup procedure is triggered.

	This is going to be put global, so every class can access it.
	"""
	def __init__(self, conffile):
		"""
		Loads config file, if the conffile is empty, call askconf() to configure.
		"""
		# If such file does not exist we just "touch" it.
		if conffile.split('/')[-1] not in os.listdir(f'{os.environ["HOME"]}'):
			open(conffile, 'w+').close()
		self._file = open(conffile)
		self._parsed = yaml.full_load(self._file)
		# if it detects nothing, then direct to setup procedure
		if self._parsed == None:
			self.askconf()
			return
		
		# if else, reads configuration file.
		# WITH default values, partly.
		self.repopath = f'{os.environ["HOME"]}/aosc/abbs' if 'repopath' not in self._parsed else \
			self._parsed['repopath']
		self.cielpath = f'{os.environ["HOME"]}/aosc/ciel' if 'cielpath' not in self._parsed else \
			self._parsed['cielpath']
		self.fullname = '' if 'fullname' not in self._parsed else \
			self._parsed['fullname']
		self.username = '' if 'username' not in self._parsed else \
			self._parsed['username']
		self.gitname = '' if 'gitname' not in self._parsed else \
			self._parsed['gitname']
		self.email = '' if 'email' not in self._parsed else \
			self._parsed['email']
		
	def askconf(self):
		'''
		Once detected a empty config file, this function is called to configure this program.
		'''
		confed = False
		print('It looks like this is your first run. Let\'s get started.')
		normal = '\033[0m'
		cyan = '\033[36m'
		while confed == False:
			print('\nFirst, where would you like to store the abbs repository?')
			self.repopath = input(f'[{os.environ["HOME"]}/aosc/abbs] {cyan}')
			if self.repopath == '':
				self.repopath = f'{os.environ["HOME"]}/aosc/abbs'
			print(f'{normal}Your abbs repository will be stored at {self.repopath}.')
			print('\nThen, where would you like to store Ciel instances?')
			self.cielpath = input(f'[{os.environ["HOME"]}/aosc/ciel] {cyan}')
			if self.cielpath == '':
				self.cielpath = f'{os.environ["HOME"]}/aosc/ciel'
			print(f'{normal}Your Ciel repository will be stored at {self.cielpath}.')
			print('\nPlease specify your full name here. This will be seen in git commits, topics and etc.')
			self.fullname = input(f'Full name: {cyan}')
			print(f'{normal}\nPlease specify your username here. This will be used to login to our repo server.')
			self.username = input(f'Username: {cyan}').lower()
			print(f'{normal}\nPlease specify your GitHub account here.')
			print('If your GitHub username is same as the prievously entered username, just leave it blank.')
			self.gitname = input(f'Git username: {cyan}')
			if self.gitname == '':
				self.gitname = self.username
			print(f'{normal}\nEnter your email address here.')
			print('This will be seen in many places, and will be used with Git commits.')
			self.email = input(f'Email: {cyan}')
			print(f'{normal}Okay! Your configuration is listed as follows:')
			print(f'''\t\t\tRepo path: {self.repopath}
			Ciel path: {self.cielpath}
			Full name: {self.fullname}
			Username: {self.username}
			Email: {self.email}
			''')
			ans = 'a'
			while ans.lower() not in ['yes', 'no', 'y', 'n', '']:
				ans = input('Is that correct? [Y/n] ')
			if ans.lower() in ['yes', 'y', '']:
				self.save()
				confed = True

	def save(self):
		data = {
			'repopath': self.repopath,
			'cielpath': self.cielpath,
			'fullname': self.fullname,
			'username': self.username,
			'gitname': self.gitname,
			'email': self.email
		}
		try:
			yaml.dump(
				data=data,
				stream=self._file
			)
		except Exception as e:
			print(f'An error occured while saving conffile:\n{e}')
			print(f'Saving as `.abbs.yml.new\'')
			yaml.dump(
				data=data,
				stream=open(f'{os.environ["HOME"]}/.abbs.yml.new')
			)
		finally:
			self._file.close()


class RepoMan():
	"""
	{0} repo: ABBS Repository Manager
	Usage:
		{0} repo <command> [options] [arguments]

	Commands:
	init		Initiliaze AOSC ABBS repository to the configured path.
	update		Update the ABBS repository.
	push		Push your commits to the ABBS repository.
	status		Show currnet status of ABBS repository.
	
	Options:
	-f, --force	Force push.
	-r, --reinit	Remove repo directory and reinitiliaze it.
	
	"""
	name = 'repo'
	desc = "Manages the AOSC ABBS Repository."
	def __init__(self):
		self.repopath = conf.repopath

	def init_repo(self, argv):
		"""
		{0} repo init: Initiliaze (clone) the ABBS repository.

		Usage: 
		{0} repo init

		Repo path is configured in ~/.abbs.yml. If you want to use different path,
		you have to manually modify it.

		"""
		pprint('Cloning AOSC ABBS Repository...')
		try:
			os.listdir(self.repopath)
		except FileNotFoundError:
			try:
				os.makedirs(self.repopath)
			except PermissionError as e:
				pprint(f'Permission denied while creating directory: {e}. Failing.', 'ERROR')
				sys.exit(1)
		# Make sure the directory is empty
		if '.git' in os.listdir(self.repopath):
			pprint('Repository already exists. Failing.', 'ERROR')
			sys.exit(1)

		elif len(os.listdir(self.repopath)) > 0:
			pprint('Target directory is not empty. Failing.', 'ERROR')
			sys.exit(1)

		try:
			ret = subprocess.run(['git', 'clone', REPOURL, conf.repopath])
		except Exception as e:
			pprint(f'Repository initilization failed: {e}. Failing.', 'ERROR')
			sys.exit(1)

		if ret.returncode != 0:
			pprint('Repository initilization failed. Failing.', 'ERROR')
			try:
				os.rmdir(self.repopath)
			except:
				# This should definitely except an error.
				# in most cases git will remove the directory itself.
				pass
			finally:
				sys.exit(1)

	def dispatch(self, argv):
		"""
		Dispatch calls to different methods by provided arguments.
		argv[0] is always the name of this subfunction, e.g. 'repo'.
		argv is stripped version of sys.argv. 
		"""
		dispatch_map = {
			'init': self.init_repo
		}
		if len(argv) <= 1:
			loaded['help'].print_subusage([None, self.name])
			sys.exit(1)
		elif argv[1] in dispatch_map.keys():
			dispatch_map[argv[1]](argv[1:])
		else:
			print(f'TBD! your command of {self.name} is {argv[1]}.')
			sys.exit(0)


class CielMan:
	"""
	{0} ciel: Ciel Container Manager
	WARNING: Do NOT run this with root user. It will break your configuration.

	Usage:
		{0} ciel <command> [options...]

	Commands:
	init		Initiliaze a Ciel workspace.
	list		List Ciel instances.
	update		Update operating system in a instance.
	rollback	Roll back state of a Ciel instance.
	shell		Execute a shell from a Ciel instance.
	"""
	name = 'ciel'
	desc = "Manages local Ciel instances."
	def __init__(self):
		pass

	
	def dispatch(self, argv):
		"""
		Dispatch calls to different methods by provided arguments.
		argv[0] is always the name of this subfunction, e.g. 'repo'.
		argv is stripped version of sys.argv. 
		"""
		
		if len(argv) == 1:
			loaded['help'].print_subusage([None, self.name])
			sys.exit(1)

		else:
			print(f'TBD! your command of {self.name} is {argv[1]}.')
			sys.exit(0)


class PkgMan():
	"""
	{0} pkg: Package Manager
	
	Usage: {0} pkg <command> [options...] [arguments...]

	Commands:
	add		Add a package into pending list.
	build 		Build all packages from pending list.
	clear		Clear pending list.
	remove		Remove a package from built packages.
	remove-pending	Remove a pending package from pending list.
	list		List built packages.
	list-pending	List pending-build packages.
	push		Push built packages to the official repository.
	"""
	name = 'pkg'
	desc = "Manages locally built packages."
	def __init__(self):
		pass

	def dispatch(self, argv):
		"""
		Dispatch calls to different methods by provided arguments.
		argv[0] is always the name of this subfunction, e.g. 'repo'.
		argv is stripped version of sys.argv. 
		"""
		
		if len(argv) == 1:
			loaded['help'].print_subusage([None, self.name])
			sys.exit(1)

		else:
			print(f'TBD! your command of {self.name} is {argv[1]}.')
			sys.exit(0)


class SpecMan:
	"""
	{0} spec: Manage spec files in the ABBS Tree

	Usage:
		{0} spec <command> [options...] [arguments...]

	Commands:
	add		Add a new package
	edit 		Open a editor with the given package folder.
	check		Lint spec files
	ls 		Show all files in a package spec folder

	"""
	name = 'spec'
	desc = 'Manages spec files in the ABBS tree.'
	def __init__(self):
		pass

	def dispatch(self, argv):
		"""
		Dispatch calls to different methods by provided arguments.
		argv[0] is always the name of this subfunction, e.g. 'repo'.
		argv is stripped version of sys.argv. 
		"""
		
		if len(argv) == 1:
			loaded['help'].print_subusage([None, self.name])
			sys.exit(1)

		else:
			print(f'TBD! your command of {self.name} is {argv[1]}.')
			sys.exit(0)


class TopicMan:
	"""
	{0} topic: ABBS Tree Topic Manager
	Usage:
		{0} topic <command> [options] [arguments]

	Commands:
	select		Select a topic
	status		Show status of current topic
	list		List all topics
	close		Merge topics to the stable branch
	new		Create a topic
	edit		Edit a topic
	
	"""

	"""
	This class will handle all stuff related to AOSC Topics.  
	`__init__()` totally does nothing.
	"""
	name = 'topic'
	desc = 'Manages topics in the configured ABBS tree.'
	def __init__(self):
		pass


	def dispatch(self, argv):
		"""
		Dispatch calls to different methods by provided arguments.
		argv[0] is always the name of this subfunction, e.g. 'repo'.
		argv is stripped version of sys.argv. 
		"""
		
		if len(argv) == 1:
			loaded['help'].print_subusage([None, self.name])
			sys.exit(1)

		else:
			print(f'TBD! your command of {self.name} is {argv[1]}.')
			sys.exit(0)


class Help:
	"""
	This is used to generate and provide help messages.
	"""
	name = 'help'
	desc = 'Show help for each subcommands'
	def __init__(self):
		self.helps = {}
		for subcomm in sublist:
			self.helps[subcomm.name] = subcomm.__doc__

	def print_usage(self):
		"""
		Prints out the formatted __main__.__doc__, which is definitely usage of this program.
		"""
		print(__doc__.format(AUTHOR, VER, EXEC))
		for i in sublist:
			print(f'\t{i.name}\t\t{i.desc}')
		print()


	def print_subusage(self, argv: list):
		"""
		Prints out help messages of a subcommand.
		Help messages are defined in __doc__ of a subcommand.
		param:
		argv: list, generalized usage, contains arguments to this function.
			Only one argument in argv are used which will used to determine which help message to printout.
		"""
		if len(argv) == 1:
			print("You should specify which one you want to get help with.\n")
			return 1

		name = argv[1]
		if name not in self.helps:
			print(f'Subcommand {name} not found.')
			return 1
		else:
			print(self.helps[name].format(EXEC))

	def dispatch(self, argv):
		if len(argv) == 1:
			self.print_usage()
		else: 
			self.print_subusage(argv)


def pprint(msg, level='INFO'):
	colors = {
		'INFO': '\033[1;32m',
		'ERROR': '\033[1;31m',
		'WARN': '\033[1;33m'
	}
	normal = '\033[0m'
	print(f'[{colors[level]}{level:>5s}{normal}] {msg}')


def loadclass():
	"""
	Loads all classes defined in this file.
	We use 3 dicts and lists to store defined classes and objects.

	- sublist: all classes defined in this file
	- names: list of `name` cariable defined in respective classes
	- loaded: All objects created from classes in sublist
	"""
	# make these variables globally accessible
	global sublist, names, loaded
	# List of all defined classes(subfunctions)
	sublist = [Help, RepoMan, PkgMan, CielMan, SpecMan, TopicMan] 
	for sub in sublist:
		# Create objects
		names.append(sub.name)
		loaded[sub.name] = sub()

def main():
	"""
	`main()`: main dispatcher to subcommands (defined in these classes).

	Reads command line options and config files.
	Then action(s) will be executed by respective classes.
	"""
	# First, load all subcommands.
	global conf
	conf = _conf(f'{os.environ["HOME"]}/.abbs.yml')
	# Call the respective dispatch method of subfunctions
	loadclass()
	# Like apt, we need at least one subfunction to work.
	if len(sys.argv) == 1 or sys.argv[1] not in names:
		# no args or the second arg is invalid
		# print out the usage information by calling print_usage in Help() directly.
		# Since we load these objects in a dict called loaded identified by its name.
		loaded['help'].print_usage()
		sys.exit(1)
	subcommand = sys.argv[1]
	subargs = sys.argv[1:]
	# Hand control to dispatcher of respective subfunctions(objects).
	print(f'\nWelcome to abbs-py Version {VER}!')
	print(f'Welcome, \033[1;36m{conf.fullname} <{conf.email}>\033[0m!')
	print('=================================\n')

	loaded[subcommand].dispatch(subargs)


if __name__ == '__main__':
	main()
