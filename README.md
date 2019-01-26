# iot-platform-civil
An IoT platform for the management of data collected from civil infrastructure monitoring

# Installation
## Single-node
The platform includes Cassandra database and web server built upon Node.js. The platform currently has been tested on Ubuntu 16.04 and Ubuntu 18.04. For installation, please follow the steps below:
1. Install database
```sh
python setup.py install database installation/setup_single.json
```
2. Install web server
```sh
python setup.py install webserver installation/setup_single.json
```

## Multi-node
For multi-node platform, the file installation/setup_multi.json needs to be updated.
In the file, "seeds" data
```sh
"seeds": ["seed_ip1","seed_ip2","..."],
```
needs to include actual public IP addresses of the some of database nodes (i.e., [@seed nodes](https://docs.datastax.com/en/cassandra/3.0/cassandra/initialize/initMultipleDS.html)). For example, if you have two seed nodes "10.10.123.001" and "10.10.123.002", the "seeds" data needs to be updated as follows:
```sh
"seeds": ["10.10.123.001","10.10.123.002"],
```
In addition, "database_nodes" data
```sh
"database_nodes": ["127.0.0.1"]
```
needs to be updated to include all (or some) of database nodes's public IP address. For example, if you have four database nodes "10.10.123.001", "10.10.123.002", "10.10.123.003" and "10.10.123.004", the database_nodes needs to be updated as follows:
```sh
"database_nodes": ["10.10.123.001","10.10.123.002","10.10.123.003","10.10.123.004"]
```
Once the file installation/setup_multi.json is updated, please follow the steps below:
1. Install database on every database nodes
```sh
python setup.py install database installation/setup_multi.json
```
2. Install web server on every web server nodes
```sh
python setup.py install webserver installation/setup_multi.json
```

# Run
## Single-node
To run the platform, both Cassandra database and web server need to be executed as follows:
1. Run Cassandra 
```sh
cassandra
```
2. Run web server
```sh
node webserver/webServer.js
```
For the first run, database schema needs to be imported as follows:
```sh
python setup_schema.py
```

## Multi-node
For multi-node platform, both Cassandra database and web server need to be executed as follows:
1. Run Cassandra on every database nodes
```sh
cassandra
```
2. Run web server on every web server nodes
```sh
node webserver/webServer.js
```
For the first run, database schema needs to be imported as follows:
```sh
python setup_schema.py
```
It should be noted that data schema import needs to be done only on a SINGLE database node.

# Use
## REST API
The platform provides REST APIs for supporting storing & retrieval of sensor data, sensor information and other relevant domain information. 

## Python API
A python API is developed to make the use of platform easier. The API abstracts REST APIs so that users can store and retrieve data using Python script. 
