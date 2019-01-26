import json
import os

def prepare_database_param(filepath):
	param = json.loads(open(filepath).read())["ws_info"]
	param["home_path"] = os.path.expanduser("~")
	param["current_path"] = os.getcwd()
	param["webserver_path"] = "{0}/webserver".format(os.getcwd())
	return param


# Install webserver dependency using shell commands
def install_database_dependency():
	print("[install_webserver.py] sudo apt-get update")
	os.system('sudo apt-get update')
	print("[install_webserver.py] sudo apt install openjdk-8-jre-headless")
	os.system('sudo apt install openjdk-8-jre-headless')
	print("curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -")
	os.system('curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -')
	print("sudo apt-get install -y nodejs")
	os.system('sudo apt-get install -y nodejs')
	print("sudo apt install npm")
	os.system('sudo apt install npm')


# Download Cassandra (v3.9) and unzip it to the cassandra_path
def install_cassandra(param):
	os.system("wget https://archive.apache.org/dist/cassandra/3.9/apache-cassandra-3.9-bin.tar.gz")
	os.system('tar -zxvf apache-cassandra-3.9-bin.tar.gz -C {0}'.format(param["cassandra_path"]))
	os.system("rm apache-cassandra-3.9-bin.tar.gz")
	os.system('sudo chown -R $USER:$GROUP {0}'.format(param["cassandra_home"]))


def install_webserver(filepath):
	# Prepare parameters
	print("[install_webserver.py] Read webserver parameters.")
	param = prepare_database_param(filepath)
	# Install dependencies
	print("[install_webserver.py] Install webserver dependency.")
	install_database_dependency()
	# # Install Cassandra 
	# print("[install_database.py] Install Cassandra.")
	# install_cassandra(param)
	# update_cassandra_config(param)
	# export_cassandra_path(param)
	# make_session_keep_alive()
	# enable_cassandra_auto_auth(param)


def uninstall_webserver(filepath):
	print("here")
