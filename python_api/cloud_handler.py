import requests
import json
import numpy as np
import dateutil.parser 
import datetime as dt
import StringIO
from PIL import Image

WEBSERVER_ADDRESS = 'http://13.64.110.84:3000/'
THERMISTOR_COEFF = {"C1": 0.001129241, "C2": 0.0002341077, "C3": 0.00000008775468};

class cloud_session:
	def __init__(self, user_id, password):
		self.user_id = user_id
		self.passwor = password
		self.login(user_id, password)

	# Example:
	# user_info = {"id":"demo_id",
	#              "pwd":"demo_pwd"}
	# url = "https://public1/admin/login"
	# res = self.session.post(url, 
	# 	    data=json.dumps(user_info))
	def login(self, user_id, password):
		self.session = requests.Session()
		url = WEBSERVER_ADDRESS + 'admin/login'
		data = {"user_id":user_id, "password":password}
		headers = {'content-type': 'application/json'}
		for i in range(0,3):
			response = self.session.post(url, data=json.dumps(data), headers=headers, verify=False)
			success = response.status_code == 200
			if success:
				break
		if not success:
			raise Exception("login: web service failed")
		return success

	# Input : data (Dictionary)
	# Return: success (Boolean)
	# Example:
	# data = {...} # Sensor data in JSON
	# url = "https://public1/sensordata"
	# res = self.session.post(url, 
	# 	    data=json.dumps(data))
	def send_sensordata(self, data):
		url = WEBSERVER_ADDRESS + 'sensordata'
		headers = {'content-type': 'application/json'}
		response = self.session.post(url, data=json.dumps(data), headers=headers, verify=False)
		success = response.status_code == 200
		if not success:
			raise Exception("send_sensordata: web service failed")
		return success

	# Input : data (Dictionary)
	# Return: success (Boolean)
	# Example
	# data = {"sensor_id": "TRB_u07_ch0",
	# 		"sensor_type": "Accelerometer",
	# 		}
	# url = "https://public1/sensor"
	# res = self.session.post(url, 
	# 	    data=json.dumps(data))
	def send_sensorinformation(self, data):
		url = WEBSERVER_ADDRESS + 'sensor'
		headers = {'content-type': 'application/json'}
		response = self.session.post(url, data=json.dumps(data), headers=headers, verify=False)
		success = response.status_code == 200
		if not success:
			raise Exception("send_sensorinformation: web service failed")
		return success

	# Input : data (Dictionary)
	# Return: success (Boolean)
	def send_imagedata(self, data):
		url = WEBSERVER_ADDRESS + 'imagedata'
		headers = {'content-type': 'application/json'}
		response = self.session.post(url, data=json.dumps(data), headers=headers, verify=False)
		success = response.status_code == 200
		if not success:
			raise Exception("send_sensordata: web service failed")
		return success

	# Input : sensor_id (string), begin_time (datetime), end_time (datetime)
	# Return: time (list<datetime>), value (list<float>)
	# Example:
	# params = {"sensor_id": "TRB_u07_ch0",
	# 		  "install": "2014-07-01T00:00:00",
	# 		  "remove": "2014-07-31T23:59:59",
	# 		 }
	# url = "https://public1/sensordata"
	# res = self.session.get(url, 
	# 	    params=params)
	def get_sensordata(self, sensor_id, begin_time, end_time):
		url = WEBSERVER_ADDRESS + 'sensordata/' + sensor_id
		params = {'event_time_begin':begin_time,'event_time_end':end_time}
		response = self.session.get(url, params=params, verify=False)
		success = response.status_code == 200
		if not success:
			raise Exception("get_sensordata: web service failed")
		dataset = (json.loads(response.content))["content"]
		time = []
		value = []
		for d in dataset:
			event_time = dateutil.parser.parse(d["event_time"])		
			data = d["data"]
			length = len(data)
			ts = 1.0/length
			value.extend(data)
			for i in range (0, length):
				time.append(event_time)
				event_time = event_time + dt.timedelta(milliseconds=ts*1000)

		return time, value

	# Input : sensor_type (string), install (datetime), remove (datetime)
	# Return: sensorlist (list<string>)
	# Example:
	# params = {"sensor_type": "Accelerometer",
	# 		  "install": "2014-07-01T00:00:00",
	# 		  "remove": "2014-07-31T23:59:59",
	# 		 }
	# url = "https://public1/sensor"
	# res = self.session.get(url, 
	# 	    params=params)
	def get_sensors(self, sensor_type=None, install=None, remove=None):
		url = WEBSERVER_ADDRESS + 'sensor' 
		params = {}
		if sensor_type != None:
			params['sensorType'] = sensor_type
		if install != None:
			params['install'] = install
		if remove != None:
			params['remove'] = remove
		response = self.session.get(url, params=params, verify=False)
		success = response.status_code == 200
		if not success:
			raise Exception("get_sensors: web service failed")
		dataset = (json.loads(response.content))["content"]
		sensorlist = []
		for d in dataset:	
			sensorlist.append(d["sensor_id"])
		return sensorlist

	# Input : sensor_id (string), property (array<string>), install (datetime), remove (datetime)
	# Return: sensorinformation (Dictionary)
	def get_sensorinformation(self, sensor_id, property=None, install=None, remove=None):
		url = WEBSERVER_ADDRESS + 'sensor/' + sensor_id 
		params = {}
		if property != None:
			params['property'] = property
		if install != None:
			params['install'] = install
		if remove != None:
			params['remove'] = remove
		response = self.session.get(url, params=params, verify=False)
		success = response.status_code == 200
		if not success:
			raise Exception("get_sensorinformation: web service failed")
		sensorinformation = (json.loads(response.content))["content"]
		return sensorinformation

	# Input : sensor_id (string), begin_time (datetime), end_time (datetime)
	# Return: time (list<datetime>), value (list<float>)
	def get_sensordata_converted(self, sensor_id, begin_time, end_time, temperature_unit = "Celsius"):
		sensor_info = self.get_sensorinformation(sensor_id, ["sensor_type", "install", "conversion_factor"], begin_time, end_time)
		if len(sensor_info) > 1:
			print "Multiple sensors exist under the sensor ID {0}.".format(sensor_id)
			for item in sensor_info:
				print "Install date: {0}".format(item["install"])
			raise Exception("Multiple sensors exist under same ID")
		sensor_info = sensor_info[0]
		if "conversion_factor" not in sensor_info:
			raise Exception("No conversion factor for the sensor ID {0}.".format(sensor_id))
		t, d = self.get_sensordata(sensor_id, begin_time, end_time)
		if len(d) == 0:
			return [0],[0]
		if sensor_info["sensor_type"] == "Accelerometer":
			data = np.array(d) * sensor_info["conversion_factor"] 
			data_detrend = data - np.mean(data)	
			return t, data_detrend
		elif sensor_info["sensor_type"] == "Strain gauge":
			data = np.array(d) * sensor_info["conversion_factor"] 
			return t, data
		elif sensor_info["sensor_type"] == "Thermistor":
			data = np.array(d)
			length = len(data)
			Th_Res = 11000.0 / ( (65535.0 / np.mean(data)) - 1.0);
			Celsius = (1.0 / (THERMISTOR_COEFF["C1"] + THERMISTOR_COEFF["C2"] * np.log(Th_Res) + THERMISTOR_COEFF["C3"] * (np.power(np.log(Th_Res),3)))) - 273.15;
			if temperature_unit == "Celsius":
				return t, np.full(length, Celsius)
			elif temperature_unit == "Farhenheit":
				Farhenheit = Celsius*(9.0/5.0) + 32.0
				return t, np.full(length, Farhenheit)
			else:
				raise Exception("Invalide temperature unit {0}.".format(temperature_unit))
		else:
			raise Exception("Sensor {0} had invalid sensor type: {1}.".format(sensor_id, sensor_info["sensor_type"]))

	# Input : camera_id (string), begin_time (datetime), end_time (datetime)
	# Return: time (list<datetime>), value (list<float>)
	def get_imagedata(self, camera_id, begin_time, end_time):
		url = WEBSERVER_ADDRESS + 'imagedata/' + camera_id
		params = {'event_time_begin':begin_time,'event_time_end':end_time}
		response = self.session.get(url, params=params)
		success = response.status_code == 200
		if not success:
			raise Exception("get_imagedata: web service failed")
		dataset = (json.loads(response.content))["content"]
		time = []
		value = []
		for d in dataset:
			event_time = dateutil.parser.parse(d["event_time"])		
			data = d["image"]["data"]
			string_data = ''.join(map(chr, data))
			img_buf = StringIO.StringIO(string_data)
			newimg = Image.open(img_buf)
			value.append(newimg)
			time.append(event_time)
		return time, value

	# Input : data (Dictionary)
	# Return: success (Boolean)
	def send_weatherdata(self, data):
		url = WEBSERVER_ADDRESS + 'weatherdata'
		headers = {'content-type': 'application/json'}
		response = self.session.post(url, data=json.dumps(data), headers=headers)
		success = response.status_code == 200
		if not success:
			raise Exception("send_weatherdata: web service failed")
		return success

	# Input : city (string), state (string), begin_time (datetime), end_time (datetime)
	# Return: time (list<datetime>), value (np.array())
	def get_weatherdata(self, state, city, begin_time, end_time, target=None):
		url = WEBSERVER_ADDRESS + 'weatherdata/' + state + '/' + city
		params = {'event_time_begin':begin_time,'event_time_end':end_time}
		response = self.session.get(url, params=params)
		success = response.status_code == 200
		if not success:
			raise Exception("get_sensordata: web service failed")
		dataset = (json.loads(response.content))["content"]
		time = []
		value = []
		if target == None:
			target = ['temperature', 'wind_chill', 'humidity', 'pressure', 'precipitation', 'dew_point', 'wind_speed', 'wind_direction', 'gust_speed', 'visibility', 'conditions', 'events']
		for d in dataset:
			event_time = dateutil.parser.parse(d["event_time"])		
			r = []
			for t in target:
				r.append(d[t])
			value.append(r)
			time.append(event_time)
		return time, value


# ------8<------8<------8<---- Examples ----8<------8<------8<------
# if __name__ == '__main__':
# 	myse = cloud_session("ex_client_01", "pwd0000")
	# t, v = myse.get_weatherdata("MI", "Newport", "2016-08-01T00:00:00", "2016-08-02T00:00:00", ["temperature", "precipitation", "humidity"])

	# t, v = myse.get_imagedata("test", "2016-07-01T00:00:00", "2016-08-03T00:00:00")
	# v[0].save("result10.png")

	# import sys
	# print myse.get_sensorinformation("TRB_u51_ch0", install="2013-12-02T00:00:00", remove="2014-08-04T00:00:00")
	# t,d = myse.get_sensordata_converted("TRB_u07_ch0","2014-07-01T00:00:00","2014-07-31T23:59:59")

	# import matplotlib.pyplot as plt
	# import matplotlib.dates as md

	# print len(d)
	# ax=plt.gca()
	# ax.xaxis_date()
	# xfmt = md.DateFormatter('%m/%d')
	# ax.xaxis.set_major_formatter(xfmt)
	# plt.plot(t,d)
	# plt.xlabel("Date (month/day)")
	# plt.ylabel("Acceleration (mg)")
	# plt.title("Acceleration measured by TRB_u07_ch0")
	# # plt.ylim([-80,80])
	# # plt.xlim([0,225000])
	# plt.show()


	# a =  myse.get_sensors("Accelerometer")
	# print a

	# from parser import parse_imagedata
	# data = parse_imagedata("test", dateutil.parser.parse("2016-08-01T00:00:00"), "inspection_01.jpg")
	# myse.send_imagedata(data)

	# import time
	# tick = time.time()
	# t,d = myse.get_sensordata("TRB_u28_ch2","2016-08-01T00:00:00","2016-08-02T00:00:00")
	# print "MAX: {0}".format(max(res))
	# print "MIN: {0}".format(min(res))
	# tock = time.time() - tick
	# print tock

	# tick = time.time()
	# t,d = myse.get_sensordata_converted("TRB_u28_ch2","2016-08-01T00:00:00","2016-08-02T00:00:00")
	# print "MAX: {0}".format(max(d))
	# print "MIN: {0}".format(min(d))
	# tock = time.time() - tick
	# print tock

