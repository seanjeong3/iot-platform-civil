import json
import os

def prepare_database_param(filepath):
	param = json.loads(open(filepath).read())["ws_info"]
	param["webserver_path"] = "{0}/webserver".format(os.getcwd())
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
	os.system('npm install --prefix {0}'.format(param["webserver_path"]))


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


def uninstall_webserver(filepath):
	print("here")
