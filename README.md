# iot-platform-civil
An IoT platform for the management of data collected from civil infrastructure monitoring

# Installation (single-node)
The platform includes Cassandra database and web server built upon Node.js. The platform currently has been tested on Ubuntu 16.04 and Ubuntu 18.04. For installation, please follow the steps below:
1. Install database
```sh
python setup.py install database installation/setup_single.json
```
2. Install web server
```sh
python setup.py install webserver installation/setup_single.json
```

# Run (single-node)
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



