import json
import os

def prepare_database_param(filepath):
	param = json.loads(open(filepath).read())["ws_info"]
	param["webserver_home"] = "{0}/webserver".format(os.getcwd())
	return param


# Install webserver dependency using shell commands
def install_webserver_dependency():
	print("[install_webserver.py] sudo apt-get update")
	os.system('sudo apt-get update')
	print("[install_webserver.py] sudo apt install openjdk-8-jre-headless")
	os.system('sudo apt install openjdk-8-jre-headless')


# Install node.js and npm
def install_nodejs():
	print("[install_webserver.py] curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -")
	os.system('curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -')
	print("[install_webserver.py] sudo apt-get install -y nodejs")
	os.system('sudo apt-get install -y nodejs')
	print("[install_webserver.py] sudo apt install aptitude")
	os.system('sudo apt install aptitude')
	print("[install_webserver.py] sudo aptitude install npm")
	os.system('sudo aptitude install npm')


def install_npm(param):
	os.system('npm install --prefix {0}'.format(param["webserver_home"]))


def update_webserver(param):
	# Update webServer.js
	with open('{0}/webServer.js'.format(param["webserver_home"]), 'r') as f :
		filedata = f.read()
		filedata = filedata.replace('var portno = 3000;', 'var portno = {0};'.format(param["port"]))
		filedata = filedata.replace("['localhost:9042']", "[{0}]".format(", ".join(["'"+s+":9042'" for s in param["database_nodes"]])))
		with open('{0}/webServer.js'.format(param["webserver_home"]), 'w') as f :
			f.write(filedata)


def stop_webserver():
	os.system('pkill -f \'webServer.js\'')


def remove_webserver_folders(param):
	if os.path.isdir("{0}/etc".format(param["webserver_home"])):
		os.system('sudo rm -rf {0}/etc'.format(param["webserver_home"]))
	if os.path.isdir("{0}/node_modules".format(param["webserver_home"])):
		os.system('sudo rm -rf {0}/node_modules'.format(param["webserver_home"]))
	if os.path.isfile("{0}/package-lock.json".format(param["webserver_home"])):
		os.system('sudo rm -rf {0}/package-lock.json'.format(param["webserver_home"]))


def install_webserver(filepath):
	# Prepare parameters
	print("[install_webserver.py] Read webserver parameters.")
	param = prepare_database_param(filepath)
	# Install dependencies
	print("[install_webserver.py] Install webserver dependency.")
	install_webserver_dependency()
	# Install node.js
	print("[install_webserver.py] Install node.js.")
	install_nodejs()
	# Install npm on the webserver folder
	install_npm(param)
	# Update webServer.js according to input param
	update_webserver(param)


def uninstall_webserver(filepath):
	# Prepare parameters
	print("[install_webserver.py] Read webserver parameters.")
	param = prepare_database_param(filepath)
	while True:
		print("[install_webserver.py] This action will permenantly REMOVE installed web server modules")
		ans = raw_input('[install_webserver.py] Do you want to proceed? [(y)/n]') or 'y'
		if ans == 'y':
			print("[install_webserver.py] uninstall started")
			break
		elif ans == 'n':
			print('[install_webserver.py] uninstall webserver has been canceled'.format(install))
			exit(0)
		else:
			print('[install_webserver.py] Please answer in [y/n]')
	print("[install_webserver.py] Stop web server process.")
	stop_webserver()
	print("[install_webserver.py] Remove web server module folders.")
	remove_webserver_folders(param)
	
