import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays"
import pickle
# Our "on message" event

#Read Latest ATC Data Aggregate File
datafile="temp-hums.txt"

with open(datafile, "rb") as fp:   #Pickling
	ATC_Data=pickle.load(fp)

fp.close()

#ATC_Data Structured as follows:
#[0][] = last 6 digits of MAC
#[1][] = casual name of device
#[2][] = temperature (f)
#[3][] = humidity (%)
#[4][] = battery level (%)
#[5][] = last RX Time (system time)
#[6][] = last RX counter Value (0-255) with rolls over

#Okay now let's transmit all the data we gathered from the file

ourClient = mqtt.Client("makerio_mqtt") # Create a MQTT client object

ourClient.username_pw_set("paho", password = "paho")

ourClient.connect("192.168.0.27", 1883) # Connect to the test MQTT broker

#Publish to: /home/environment/ATCSensors/"dev_name"/"temp|hum|batt|last_rx|rx_cnt
for names in ATC_Data[1]:
	curr_index=ATC_Data[1].index(names)
#	print("Writing to:","/home/environment/ATCSensors/"+names+"/temp","With Data:",ATC_Data[2][curr_index])
	#Publish Temp
	ourClient.publish("/home/environment/ATCSensors/"+names+"/temp",ATC_Data[2][curr_index])
	#Pub Humidity
	ourClient.publish("/home/environment/ATCSensors/"+names+"/hum",ATC_Data[3][curr_index])
	#Pub Battery Level
	ourClient.publish("/home/environment/ATCSensors/"+names+"/batt",ATC_Data[4][curr_index])
	#Pub last RX Time
	ourClient.publish("/home/environment/ATCSensors/"+names+"/last_rx",ATC_Data[5][curr_index])
	#Pub last RX counter value
	ourClient.publish("/home/environment/ATCSensors/"+names+"/rx_cnt",ATC_Data[6][curr_index])

ourClient.disconnect()
