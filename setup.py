# Proper command format: 
# python setup.py [install,uninstall] [cassandra,node.js] [none, <filename.json>]

import sys
import os

INSTALL_ARG = ["install", "uninstall"]
TARGET_ARG = ["database", "webserver"]

# Read arguments
def read_arg():
	arg = {}
	# check argument 1
	if len(sys.argv)<2:
		print('Error: arg_2 is missing {0}'.foramt(INSTALL_ARG))
		exit(0)
	elif sys.argv[1] not in INSTALL_ARG:
		print('Error: unexpected arg_2 {0}. It should be {1}'.format(sys.argv[1],INSTALL_ARG))
		exit(0)
	else:
		arg["install"] = sys.argv[1]
	# check argument 2
	if len(sys.argv)<3:
		print('Error: arg_3 is missing {0}'.format(TARGET_ARG))
		exit(0)
	elif sys.argv[2] not in TARGET_ARG:
		print('Error: unexpected arg_3 {0}. It should be {1}'.format(sys.argv[2],TARGET_ARG))
		exit(0)
	else:
		arg["target"] = sys.argv[2]
	# check argument 3
	arg["input"] = None
	if len(sys.argv)==4:
		if not os.path.isfile(sys.argv[3]):
			print('Error: file {0} does not exist'.format(sys.argv[3]))
			exit(0)
		else:
			arg["input"] = sys.argv[3]
	# check redundant arguments
	if len(sys.argv) > 4:
		print('Error: too many arguments')
		exit(0)
	# return a dictionary argument
	return arg



# Get confirmation from user and start installation/uninstallation
def check_and_start(install, target, func, arg):
	while True:
		ans = raw_input('Start {0} {1} [(y)/n]'.format(install, target)) or 'y'
		if ans == 'y':
			break
		elif ans == 'n':
			print('{0} has been canceled'.format(install))
			exit(0)
		else:
			print('Please answer in [y/n]')
	func(arg)



def install_database(arg):
	print('dummy install database')
def install_webserver(arg):
	print('dummy install webserver')
def uninstall_database(arg):
	print('dummy install database')
def uninstall_webserver(arg):
	print('dummy uninstall webserver')



if __name__ == '__main__':
	arg = read_arg()
	if arg["install"]=="install":
		if arg["target"]=="database":
			check_and_start("installation", "database", install_database, arg)
		elif arg["target"]=="webserver":
			check_and_start("installation", "webserver", install_webserver, arg)
	elif arg["install"]=="uninstall":
		if arg["target"]=="database":
			check_and_start("uninstallation", "database", uninstall_database, arg)
		elif arg["target"]=="webserver":
			check_and_start("uninstallation", "webserver",uninstall_webserver, arg)


