import json
import os
import socket

def prepare_database_param(filepath):
	param = json.loads(open("setup.json").read())["db_info"]
	param["ip_address"] = socket.gethostbyname(socket.gethostname())
	param["home_path"] = os.path.expanduser("~")
	param["current_path"] = os.getcwd()
	param["cassandra_path"] = "{0}/cassandra".format(os.getcwd())
	param["cassandra_home"] = "{0}/cassandra/apache-cassandra-3.9".format(os.getcwd())
	param["hints_directory"] = "{0}/{1}".format(param["cassandra_home"],param["hints_directory"]) if param["hints_directory"][0] != "/" else param["hints_directory"]
	param["data_file_directories"] = "{0}/{1}".format(param["cassandra_home"],param["data_file_directories"]) if param["data_file_directories"][0] != "/" else param["data_file_directories"]
	param["commitlog_directory"] = "{0}/{1}".format(param["cassandra_home"],param["commitlog_directory"]) if param["commitlog_directory"][0] != "/" else param["commitlog_directory"]
	param["saved_caches_directory"] = "{0}/{1}".format(param["cassandra_home"],param["saved_caches_directory"]) if param["saved_caches_directory"][0] != "/" else param["saved_caches_directory"]
	return param


def create_database_folders(param):
	# Check if there already exists something on the cassandra_home. If so stop installation.
	if os.path.isdir(param["cassandra_home"]):
		print("[install_database.py] ERROR: cassandra_home path {0} is already in use".format(param["cassandra_home"]))
		exit(0)
	else:
		os.makedirs(param["cassandra_home"])
		# print("{0} is created".format(param["cassandra_home"]))
	# hints_directory
	if os.path.isdir(param["hints_directory"]):
		print("[install_database.py] ERROR: hints_directory path {0} is already in use".format(param["hints_directory"]))
		exit(0)
	else:
		os.makedirs(param["hints_directory"])
		# print("{0} is created".format(param["hints_directory"]))
	# data_file_directories
	if os.path.isdir(param["data_file_directories"]):
		print("[install_database.py] ERROR: data_file_directories path {0} is already in use".format(param["data_file_directories"]))
		exit(0)
	else:
		os.makedirs(param["data_file_directories"])
		# print("{0} is created".format(param["data_file_directories"]))
	# commitlog_directory
	if os.path.isdir(param["commitlog_directory"]):
		print("[install_database.py] ERROR: commitlog_directory path {0} is already in use".format(param["commitlog_directory"]))
		exit(0)
	else:
		os.makedirs(param["commitlog_directory"])
		# print("{0} is created".format(param["commitlog_directory"]))
	# saved_caches_directory
	if os.path.isdir(param["saved_caches_directory"]):
		print("[install_database.py] ERROR: saved_caches_directory path {0} is already in use".format(param["saved_caches_directory"]))
		exit(0)
	else:
		os.makedirs(param["saved_caches_directory"])
		# print("{0} is created".format(param["saved_caches_directory"]))
	os.system('sudo chown -R $USER:$GROUP {0}'.format(param["hints_directory"]))
	os.system('sudo chown -R $USER:$GROUP {0}'.format(param["data_file_directories"]))
	os.system('sudo chown -R $USER:$GROUP {0}'.format(param["commitlog_directory"]))
	os.system('sudo chown -R $USER:$GROUP {0}'.format(param["saved_caches_directory"]))


def install_database_dependency():
	print("[install_database.py] sudo apt-get update")
	os.system('sudo apt-get update')
	print("[install_database.py] sudo apt install openjdk-8-jre-headless")
	os.system('sudo apt install openjdk-8-jre-headless')
	print("[install_database.py] sudo apt install python-pip")
	os.system('sudo apt install python-pip')
	print("[install_database.py] pip install cassandra-driver")
	os.system('pip install cassandra-driver')


def install_cassandra(param):
	os.system("wget https://archive.apache.org/dist/cassandra/3.9/apache-cassandra-3.9-bin.tar.gz")
	os.system('tar -zxvf apache-cassandra-3.9-bin.tar.gz -C {0}'.format(param["cassandra_path"]))
	os.system("rm apache-cassandra-3.9-bin.tar.gz")
	os.system('sudo chown -R $USER:$GROUP {0}'.format(param["cassandra_home"]))



def install_database(filepath):
	# Prepare parameters
	print("[install_database.py] Read database parameters.")
	param = prepare_database_param(filepath)
	# Create necessary folders
	print("[install_database.py] Create database folders.")
	create_database_folders(param)
	# Install dependencies
	print("[install_database.py] Create database dependency.")
	install_database_dependency()
	# Install Cassandra 
	print("[install_database.py] Install Cassandra.")
	install_cassandra(param)



