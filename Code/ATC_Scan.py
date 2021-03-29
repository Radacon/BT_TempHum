import sys
from datetime import datetime
import bluetooth._bluetooth as bluez
import time
import pickle

from bluetooth_utils import (toggle_device, enable_le_scan,
                             parse_le_advertising_events,
                             disable_le_scan, raw_packet_to_str)

#Mac Address List
mac_names=[["DE:AD:BE","EF:00:00","00:00:00","00:00:00","00:00:00","00:00:00","00:00:00","00:00:00","00:00:00","00:00:00","AA:BB:CC","DD:EE:FF","11:11:11"],
		["Master_Bedroom","Master_Bathroom","Hallway","Office","Sewing_Room","Guest_Bathroom","Livingroom","Entryway","Kitchen","Garage","Stairwell","Movie_Room","Movie_Room_Bathroom"],
		[0,0,0,0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]

#mac_names[0][] is the last 3 mac address
#mac_names[1][] is the name associated with that mac address
#mac_names[2][] is the temperature of that device
#mac_names[3][] is the humiditiy of that device
#mac_names[4][] is the battery level of that device
#mac_names[5][] is the last RX time
#mac_names[6][] is the last RX counter value
print(mac_names[0])

# Use 0 for hci0
dev_id = 0
toggle_device(dev_id, True)

try:
    sock = bluez.hci_open_dev(dev_id)
except:
    print("Cannot open bluetooth device %i" % dev_id)
    raise



#data_str[22:26] <- Temperature, data_str[26:28] <- Humidity, data_str[28:30] <- Battery (%), data_str[30:34] <-Battery (mV uint16_t), data_str[34:36] <- Frame Packet Counter Increments every sample interval)





# Set filter to "True" to see only one packet per device
enable_le_scan(sock, filter_duplicates=False)

try:
    def le_advertise_packet_handler(mac, adv_type, data, rssi):
        data_str = raw_packet_to_str(data)
        # Check for ATC preamble
        if data_str[6:10] == '1a18':
            frame_cnt = int(data_str[34:36],16)
            #Check for Valid MAC (in the mac address list)
            for address in mac_names[0]:
                if mac[-8:]==address:
                    #Check for valid packet Counter Value (this keeps us from logging old data)
                    for last_frame in mac_names[6]:
                        #account for 0xff->0x00 rollover
                        if (frame_cnt>last_frame or (last_frame == 255 and frame_cnt==0)):
                            sns_name_index = mac_names[0].index(mac[-8:])
                            mac_names[6][sns_name_index]=frame_cnt
                            #sanity check to make sure we're only updating when the frame_cnt changes not everytime a broadcast is read
#                            if(mac_names[1][sns_name_index]==mac_names[1][1]):
#                                print(mac_names[1][1],mac_names[6][1])
                            sns_name=mac_names[1][sns_name_index]
                            temp = int(data_str[22:26], 16) / 10
                            temp = temp * (9/5) + 32
                            temp = str(round(temp,1))
                            hum = int(data_str[26:28], 16)
                            batt = int(data_str[28:30], 16)
                            mac_names[2][sns_name_index]=temp
                            mac_names[3][sns_name_index]=hum
                            mac_names[4][sns_name_index]=batt
                            mac_names[5][sns_name_index]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            #Write to data file
                            with open("temp-hums.txt", "wb") as f:   #Pickling
                                pickle.dump(mac_names, f)
                            f.close()
    # Called on new LE packet
    parse_le_advertising_events(sock,
                                handler=le_advertise_packet_handler,
                                debug=False)
# Scan until Ctrl-C
except KeyboardInterrupt:
    disable_le_scan(sock)
