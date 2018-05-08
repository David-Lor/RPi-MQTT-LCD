
#Native libraries
import json
#Installed libraries
import paho.mqtt.client as mqtt
#Package modules
from lcd_manager import LCDPrint, destroy_current


TOPIC = "$lcd"

def on_connect(client, userdata, flags, rc):
	client.subscribe(TOPIC)

def on_message(client, userdata, msg):
	try:
		payload = json.loads(msg.payload)
		#LineA and LineB are required
		lineA = payload["lineA"]
		lineB = payload["lineB"]
		#Check if clear order was sent:
		if type(lineA) is str and lineA == "**clearscreen**":
			destroy_current(clear=True)
			return
		#Priority is optional, 100 by default
		if "priority" in payload:
			priority = payload["priority"]
		else:
			priority = 100
		#min_time is optional, 0 by default
		if "min_time" in payload:
			min_time = payload["min_time"]
		else:
			min_time = 0
		#max_time is optional, 0 by default
		if "max_time" in payload:
			max_time = payload["max_time"]
		else:
			max_time = 0
		#rotate_frequency is optional, 0.5 by default
		if "rotate_freq" in payload:
			rotfreq = payload["rotate_freq"]
		else:
			rotfreq = 0.5
		#autoclear is optional, 0 by default
		if "autoclear" in payload:
			autoclear = bool(payload["autoclear"])
		else:
			autoclear = False
		#center is optional, 1 by default
		if "center" in payload:
			center = bool(payload["center"])
		else:
			center = True
		LCDPrint(
			lineA=lineA,
			lineB=lineB,
			priority=priority,
			min_time=min_time,
			max_time=max_time,
			rotate_frequency=rotfreq,
			clear_on_destroy=autoclear,
			center=center
		)
	except Exception as ex:
		print(ex)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

def loop():
	client.loop_forever()
