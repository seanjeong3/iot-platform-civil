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


# Install database dependency using shell commands
def install_database_dependency():
	print("[install_database.py] sudo apt-get update")
	os.system('sudo apt-get update')
	print("[install_database.py] sudo apt install openjdk-8-jre-headless")
	os.system('sudo apt install openjdk-8-jre-headless')
	print("[install_database.py] sudo apt install python-pip")
	os.system('sudo apt install python-pip')
	print("[install_database.py] pip install cassandra-driver")
	os.system('pip install cassandra-driver')


# Download Cassandra (v3.9) and unzip it to the cassandra_path
def install_cassandra(param):
	os.system("wget https://archive.apache.org/dist/cassandra/3.9/apache-cassandra-3.9-bin.tar.gz")
	os.system('tar -zxvf apache-cassandra-3.9-bin.tar.gz -C {0}'.format(param["cassandra_path"]))
	os.system("rm apache-cassandra-3.9-bin.tar.gz")
	os.system('sudo chown -R $USER:$GROUP {0}'.format(param["cassandra_home"]))


# Update Cassandra configuration according to setup.json
def update_cassandra_config(param):
	# Update cassandra.yaml
	with open('{0}/conf/cassandra.yaml'.format(param["cassandra_home"]), 'r') as f :
		filedata = f.read()
		filedata = filedata.replace('cluster_name: \'Test Cluster\'', 'cluster_name: \'{0}\''.format(param["cluster_name"]))
		filedata = filedata.replace('- seeds: "127.0.0.1"', '- seeds: \"{0}\"'.format(", ".join([s for s in param["seeds"]])))
		filedata = filedata.replace('# hints_directory: /var/lib/cassandra/hints', 'hints_directory: {0}'.format(param["hints_directory"]))
		filedata = filedata.replace('# data_file_directories:', 'data_file_directories:')
		filedata = filedata.replace('#     - /var/lib/cassandra/data', '     - {0}'.format(param["data_file_directories"]))
		filedata = filedata.replace('# commitlog_directory: /var/lib/cassandra/commitlog', 'commitlog_directory: {0}'.format(param["commitlog_directory"]))
		filedata = filedata.replace('# saved_caches_directory: /var/lib/cassandra/saved_caches', 'saved_caches_directory: {0}'.format(param["saved_caches_directory"]))
		filedata = filedata.replace('listen_address: localhost', 'listen_address: {0}'.format(param["listen_address"]))
		if param["broadcast_address"]:
			filedata = filedata.replace('# broadcast_address: 1.2.3.4', 'broadcast_address: {0}'.format(param["ip_address"])) # param["ip_address"]
		filedata = filedata.replace('rpc_address: localhost', 'rpc_address: {0}'.format(param["rpc_address"]))
		if param["broadcast_rpc_address"]:
			filedata = filedata.replace('# broadcast_rpc_address: 1.2.3.4', 'broadcast_rpc_address: {0}'.format(param["ip_address"])) # param["ip_address"]
		filedata = filedata.replace('# rpc_min_threads: 16', 'rpc_min_threads: {0}'.format(param["rpc_min_threads"]))
		filedata = filedata.replace('# rpc_max_threads: 2048', 'rpc_max_threads: {0}'.format(param["rpc_max_threads"]))
		filedata = filedata.replace('read_request_timeout_in_ms: 5000', 'read_request_timeout_in_ms: {0}'.format(param["read_request_timeout_in_ms"]))
		filedata = filedata.replace('range_request_timeout_in_ms: 10000', 'range_request_timeout_in_ms: {0}'.format(param["range_request_timeout_in_ms"]))
		filedata = filedata.replace('write_request_timeout_in_ms: 2000', 'write_request_timeout_in_ms: {0}'.format(param["write_request_timeout_in_ms"]))
		filedata = filedata.replace('counter_write_request_timeout_in_ms: 5000', 'counter_write_request_timeout_in_ms: {0}'.format(param["counter_write_request_timeout_in_ms"]))
		filedata = filedata.replace('cas_contention_timeout_in_ms: 1000', 'cas_contention_timeout_in_ms: {0}'.format(param["cas_contention_timeout_in_ms"]))
		filedata = filedata.replace('truncate_request_timeout_in_ms: 60000', 'truncate_request_timeout_in_ms: {0}'.format(param["truncate_request_timeout_in_ms"]))
		filedata = filedata.replace('request_timeout_in_ms: 10000', 'request_timeout_in_ms: {0}'.format(param["request_timeout_in_ms"]))
		filedata = filedata.replace('authenticator: AllowAllAuthenticator', 'authenticator: {0}'.format(param["authenticator"]))
		filedata = filedata.replace('authorizer: AllowAllAuthorizer', 'authorizer: {0}'.format(param["authorizer"]))
		filedata = filedata.replace('endpoint_snitch: SimpleSnitch', 'endpoint_snitch: {0}'.format(param["endpoint_snitch"]))
		filedata = filedata.replace('batch_size_warn_threshold_in_kb: 5', 'batch_size_warn_threshold_in_kb: {0}'.format(param["batch_size_warn_threshold_in_kb"]))
		filedata = filedata.replace('batch_size_fail_threshold_in_kb: 50', 'batch_size_fail_threshold_in_kb: {0}'.format(param["batch_size_warn_threshold_in_kb"]))
		filedata += '\n'
		filedata += 'auto_bootstrap: false'
		with open('{0}/conf/cassandra.yaml'.format(param["cassandra_home"]), 'w') as f :
			f.write(filedata)
	# Update cassandra-rackdc.properties
	with open('{0}/conf/cassandra-rackdc.properties'.format(param["cassandra_home"]), 'r') as f :
		filedata = f.read()
		filedata = filedata.replace('dc=dc1', 'dc={0}'.format(param["data_center_id"]))
		filedata = filedata.replace('rack=rack1', 'rack={0}'.format(param["rack_id"]))


def export_cassandra_path(param):
	# Still need to manually source it!
	os.system('echo  "export CQLSH_NO_BUNDLED=true" >> ~/.profile')
	os.system('echo  "export PATH=\"{0}/bin:\$PATH\"" >> ~/.profile'.format(param["cassandra_home"]))


def make_session_keep_alive():
	os.system('sudo sysctl -w net.ipv4.tcp_keepalive_time=60 net.ipv4.tcp_keepalive_probes=3 net.ipv4.tcp_keepalive_intvl=10')


# Enable auth (default id: cassandra, default pw: cassandra)
def enable_cassandra_auto_auth(param):
	if param["authenticator"] == "PasswordAuthenticator":
		os.system('mkdir -p {0}/.cassandra'.format(param["home_path"]))
		os.system('touch {0}/.cassandra/cqlshrc'.format(param["home_path"]))
		os.system('echo "[authentication]" >> {0}/.cassandra/cqlshrc'.format(param["home_path"]))
		os.system('echo "username = cassandra" >> {0}/.cassandra/cqlshrc'.format(param["home_path"]))
		os.system('echo "password = cassandra" >> {0}/.cassandra/cqlshrc'.format(param["home_path"]))


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
	update_cassandra_config(param)
	export_cassandra_path(param)
	make_session_keep_alive()
	enable_cassandra_auto_auth(param)




