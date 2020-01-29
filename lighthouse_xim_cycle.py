#!/usr/bin/env python3

# lighting sequence for the "A Love Letter to the Lighthouse in the expanded field" performance
# using the Xicato XIM LED modules
# 2020-01-31 francesco.anselmo@gmail.com

FADE_TIME = 1000 # in milliseconds
OSC_PORT = 5005

import signal
import cfg
import sys
import re
import platform
from collections import OrderedDict
from OSC import OSCServer,OSCClient, OSCMessage

system = platform.system()
debug = False
dimming = None
server = OSCServer(("0.0.0.0", OSC_PORT))

# set up cfg
if system == "Darwin":
    cfg.MACOS = True
    cfg.WINDOWS = False
    cfg.LINUX = False
elif system == "Windows":
    cfg.WINDOWS = True
    cfg.MACOS = False
    cfg.LINUX = False
elif system == "Linux":
    cfg.LINUX = True
    cfg.WINDOWS = False
    cfg.MACOS = False
else:
    print('Sorry, this operating system is not supported by this program.')
    sys.exit(0)

from pyfiglet import Figlet
import ble_xim_pkg as ble_xim
import time
from threading import Thread, Lock

def sortFn(item):
    return item.deviceId

### Dimming rotation thread class
class XIMDimmingRotation(Thread):
    def __init__(self, xim, deviceList, fadeTime=1000, parent=None, interval=0.050):
        Thread.__init__(self)
        self.xim = xim
        self.fadeTime = fadeTime
        self._keep_alive = True
        self._parent = parent
        self._interval = interval
        self.lock = Lock()
        self.ximNumber = len(deviceList)
        self.active = False
        self.allOn = False
        self.deviceList = deviceList

    def updateDeviceList(self):
        self.deviceList = self.xim.get_device_list()
        self.orderedDeviceList = OrderedDict()
        keys = sorted(self.deviceList.keys(), key = lambda x: x.deviceId)
        self.groupedDeviceList = [[], [], [], []]
        count = 0
        for key in keys:
            self.orderedDeviceList[key] = self.deviceList[key]
            self.groupedDeviceList[count % 4].append(key)
            print(count % 4)
            count = count + 1
        print(self.groupedDeviceList[0])
        print(self.groupedDeviceList[1])
        print(self.groupedDeviceList[2])
        print(self.groupedDeviceList[3])
        self.ximNumber = len(self.deviceList)
    
    def run(self):
        # if self.ximNumber>0:
        print('run')
        if True:
            self.updateDeviceList()
            # print(d)
            while self._keep_alive:
                with self.lock:
                    # dim LEDs in sequence
                    # try:
                    for group in self.groupedDeviceList:
                        if self.active:
                            # print("XIM: " + str(ximID))
                            # put light to maximum brightness
                            # devices = filter(lambda ndi: ndi.deviceId == [ximID], self.deviceList)
                            # print(devices)
                            print('dim on')
                            for device in group:
                                intensity = 10
                                values = {"light_level":intensity, "fade_time":self.fadeTime, "response_time":0, "override_time":0, "lock_light_control":False}
                                print(device)
                                ble_xim.advLightControl(device, values)
                                time.sleep(0.05)
                            time.sleep(self.fadeTime/1000 + 0.1)
                            # put light to minimum brightness
                            print('dim off')
                            for device in group:
                                print(device)
                                intensity = 0
                                values = {"light_level":intensity, "fade_time":self.fadeTime, "response_time":0, "override_time":0, "lock_light_control":False}
                                ble_xim.advLightControl(device, values)
                                time.sleep(0.05)
                            time.sleep(self.fadeTime/1000 + 0.1)
                    # except:
                    #     pass
                        # print('runHost encountered an error (this is normal on exit)')
                    # sleep until next loop is due
                    if self.active:
                        self.active = False
                        print('Rotation Sequence ended')
                        action_set_all(False) # Need to force turn off all since it sometimes stuck turned on.
                    time.sleep(self._interval)

    def stop(self):
        with self.lock:
            # stop the loop in the run method
            self._keep_alive = False


### BleXimThread class
class BleXimThread(Thread):
    def __init__(self, parent=None, interval=0.050):
        Thread.__init__(self)
        self._keep_alive = True
        self._parent = parent
        self._interval = interval
        self.lock = Lock()
        # ordinarily we would have a LogHandler to keep event/packet logs in case anything goes wrong
        # in this case, our example is so simple we don't need it
        ble_xim.initialize(None)


    def run(self):
        ble_xim.start()
        while self._keep_alive:
            with self.lock:
                # run the stack
                try:
                    ble_xim.runHost()
                except:
                    pass
                    # print('runHost encountered an error (this is normal on exit)')
                # sleep until next loop is due
                time.sleep(self._interval)

    def stop(self):
        with self.lock:
            # stop the ble_xim stack
            ble_xim.stop()
            # stop the loop in the run method
            self._keep_alive = False

    def get_device_list(self):
        # gets device ids for devices that are XIMs or XIDs
        netDevIdList = ble_xim.getXimIdList()
        return {netDevId : ble_xim.getLightStatus(netDevId) for netDevId in netDevIdList}
### BleXimThread class




def exit_handler(sig, frame):
    sys.exit(0)

### Actions
def action_print_devices():
    print('action: print_devices')
    dimming.updateDeviceList()
    for item in dimming.orderedDeviceList:
        name = ble_xim.getDeviceName(item)
        intensity = dimming.deviceList[item].intensity
        print "{}({}): {}".format(item.deviceId, name, intensity)

def action_set_intensity_for(device_id = -1, intensity = 0):
    print('action: set_intensity_for: device_id: ' + str(device_id) + " with intensity: " + str(intensity))
    # dimming.updateDeviceList()
    devices = dimming.orderedDeviceList.items()
    if len(devices) >= device_id:
        device = dimming.orderedDeviceList.items()[device_id - 1] # orderedList is 0 based index, the LED ID is one based index.
        # we only want to deal with one device so if our filtered list has more than one member we don't proceed
        # now we create the values dictionary.
        # the names and acceptable values of each parameter can be found in the API documentation for each call
        values = {"light_level":intensity, "fade_time":0, "response_time":0, "override_time":0, "lock_light_control":False}
        # finally, actually issue the advertising command
        ble_xim.advLightControl(device[0], values)
    else:
        print "Error: could not locate device with ID {}".format(device_id)

# all lights on / off
def action_set_all(on = True):
    print('action: set all to ' + ("on" if on else "off"))
    # dimming.updateDeviceList()
    dimming.active = False
    for device in dimming.deviceList:
        # print("XIM: " + str(ximID))
        # put light to maximum brightness
        # print(devices)
        intensity = 100 if on else 0
        values = {"light_level":intensity, "fade_time":500, "response_time":0, "override_time":0, "lock_light_control":False}
        ble_xim.advLightControl(device, values)
        time.sleep(0.15)

# dynamic dimming rotation
def action_dim_rotation(on = True):
    print('action: set dimming rotation:  ' + ("on" if on else "off"))
    # dimming.updateDeviceList()
    if on:
        dimming.allOn = False
        dimming.active = True
    else:
        dimming.active = False

# dynamic dimming rotation
def action_dim_rotation(on = True):
    print('action: set dimming rotation:  ' + ("on" if on else "off"))
    # dimming.updateDeviceList()
    if on:
        dimming.allOn = False
        dimming.active = True
    else:
        dimming.active = False

# OSC Handlers

### OSC Message Callbacks
def fader_callback(path, tags, args, source):
    num = map(int, re.findall('\d', path.split('/')[-1]))[0]
    action_set_intensity_for(num, args[0] * 100)

def set_all_callback(path, tags, args, source):
    num = map(int, re.findall('\d', path.split('/')[-1]))[0]
    action_set_all(True if num == 1 else False)

def dim_rotation_callback(path, tags, args, source):
    num = map(int, re.findall('\d', path.split('/')[-1]))[0]
    action_dim_rotation(True if num == 3 else False)

def print_devices_callback(path, tags, args, source):
    action_print_devices()


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        debug = True
        print("DEBUG")

    # display welcome message
    f1 = Figlet(font='script')
    print(f1.renderText('Lighthouse'))
    f2 = Figlet(font='small')
    print(f2.renderText('lighting control'))

    if not debug:
    # if Ctrl-C is invoked call the function to exit the program
        signal.signal(signal.SIGINT, exit_handler)
        # start thread
        xim = BleXimThread()
        xim.start()
        deviceList = None
        print("Detecting XIM LEDs, please wait ...")
        for i in range(20):
            deviceList = xim.get_device_list()
            time.sleep(.25)
        # start dimming rotation thread
        dimming = XIMDimmingRotation(xim, deviceList, FADE_TIME)
        dimming.start()
        print("Number of XIM LEDs: " + str(dimming.ximNumber))
    # basic command prompt loop
    commands = 'Enter:\n\td to detect and print devices\n\tb to set individual LED brightness\n\ta to set all lights to maximum brightness\n\to to switch off all lights\n\ts to start the dimming sequence\n\te to end the dimming sequence\n\t? show commands\n\tq to quit'
    print(commands)

    for i in range(1, 9):
        server.addMsgHandler( "/2/rotary" + str(i), fader_callback)
    

    server.addMsgHandler("/1/push1", set_all_callback) # On 
    server.addMsgHandler("/1/push2", set_all_callback) # Off

    server.addMsgHandler("/1/push3", dim_rotation_callback) # On 
    server.addMsgHandler("/1/push4", dim_rotation_callback) # Off

    server.addMsgHandler("/1/push8", print_devices_callback) # Off
    
    while True:

        if server != None:
            server.handle_request()
        else:
            choice = raw_input('> ')
            # print devices
            if choice == 'd':
                action_print_devices()
            # set intensity
            elif choice == 'b':
                # first get a valid device id and intensity
                device_id = None
                intensity = None
                while device_id is None or intensity is None:
                    device_id_raw = raw_input('device id: ')
                    intensity_raw = raw_input('intensity: ')
                    try:
                        # the device id needs to be boxed into a list of integers
                        # in this case the list is 1 integer
                        # hypothetically we could also handle unassigned ids, which are lists of 3 bytes
                        # but it's simpler to only allow assigned ids
                        # it's also typically more predictable behavior
                        device_id = [int(device_id_raw)]
                        print(device_id[0])
                        assert 1 <= device_id[0] <= 8, "Device id should be in the range of 1 - 8"
                    except:
                        # catch the parsing error
                        print 'invalid device id (this program only works with assigned IDs)'
                        device_id = None
                    try:
                        # intensity needs to be a float between 0 and 100
                        intensity = float(intensity_raw)
                        assert 0 <= intensity <= 100, "Error: intensity out of range"
                    except:
                        # catch the parsing error
                        print 'invalid intensity'
                        intensity = None
                if intensity != None and device_id != None:
                    action_set_intensity_for(int(device_id_raw), intensity)
                else:
                    print "Error: could not locate device with ID {}".format(device_id)

            # dynamic dimming rotation
            elif choice == 's':
                action_dim_rotation(True)
            # stop dynamic dimming rotation
            elif choice == 'e':
                action_dim_rotation(False)
            # all lights on to maximum
            elif choice == 'a':
                action_set_all(True)
            # all lights off
            elif choice == 'o':
                action_set_all(False)
            elif choice == '?':
                f1 = Figlet(font='script')
                print(f1.renderText('Lighthouse'))
                f2 = Figlet(font='small')
                print(f2.renderText('lighting control'))
                print(commands)
            # quit
            elif choice == 'q':
                dimming.active = False
                print('goodbye')
                # stop all the threads before exiting
                xim.stop()
                dimming.stop()
                sys.exit(0)
            # default case
            else:
                print('I\'m sorry, what was that?')
