#!/usr/bin/env python3

# lighting sequence for the "A Love Letter to the Lighthouse in the expanded field" performance
# using the Xicato XIM LED modules
# 2020-01-31 francesco.anselmo@gmail.com

FADE_TIME = 2000 # in milliseconds

import signal
import cfg
import sys
import platform
system = platform.system()
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

### Dimming rotation thread class
class XIMDimmingRotation(Thread):
    def __init__(self, xim, fadeTime=1000, parent=None, interval=0.050):
        Thread.__init__(self)
        self.xim = xim
        self.fadeTime = fadeTime
        self._keep_alive = True
        self._parent = parent
        self._interval = interval
        self.lock = Lock()
        self.ximNumber = len(self.xim.get_device_list())
        self.active = False
        self.allOn = False

    def run(self):
        # if self.ximNumber>0:
        if True:
            d = self.xim.get_device_list()
            # print(d)
            while self._keep_alive:
                with self.lock:
                    # dim LEDs in sequence
                    # try:
                    if self.active:
                        for ximID in range(1, self.ximNumber+1):
                            # print("XIM: " + str(ximID))
                            # put light to maximum brightness
                            devices = filter(lambda ndi: ndi.deviceId == [ximID], self.xim.get_device_list())
                            # print(devices)
                            intensity = 100
                            values = {"light_level":intensity, "fade_time":self.fadeTime, "response_time":0, "override_time":0, "lock_light_control":False}
                            ble_xim.advLightControl(devices[0], values)
                            time.sleep(self.fadeTime/1000 + 0.1)
                            # put light to minimum brightness
                            intensity = 0
                            values = {"light_level":intensity, "fade_time":self.fadeTime, "response_time":0, "override_time":0, "lock_light_control":False}
                            ble_xim.advLightControl(devices[0], values)
                            time.sleep(self.fadeTime/1000 + 0.1)
                    # except:
                    #     pass
                        # print('runHost encountered an error (this is normal on exit)')
                    # sleep until next loop is due
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

if __name__ == '__main__':
    # display welcome message
    f1 = Figlet(font='script')
    print(f1.renderText('Lighthouse'))
    f2 = Figlet(font='small')
    print(f2.renderText('lighting control'))

    # if Ctrl-C is invoked call the function to exit the program
    signal.signal(signal.SIGINT, exit_handler)
    # start thread
    xim = BleXimThread()
    xim.start()
    # start dimming rotation thread
    dimming = XIMDimmingRotation(xim, FADE_TIME)
    dimming.start()
    print("Detecting XIM LEDs, please wait ...")
    for i in range(20):
        dimming.ximNumber = len(xim.get_device_list())
        time.sleep(.25)
    print("Number of XIM LEDs: " + str(dimming.ximNumber))
    # basic command prompt loop
    commands = 'Enter:\n\td to detect and print devices\n\tb to set individual LED brightness\n\ta to set all lights to maximum brightness\n\to to switch off all lights\n\ts to start the dimming sequence\n\te to end the dimming sequence\n\t? show commands\n\tq to quit'
    print(commands)
    while True:
        choice = raw_input('> ')
        # print devices
        if choice == 'd':
            device_list = xim.get_device_list()
            dimming.ximNumber = len(xim.get_device_list())
            for netDevId in device_list:
                name = ble_xim.getDeviceName(netDevId)
                intensity = device_list[netDevId].intensity
                print "{}({}): {}".format(netDevId.deviceId, name, intensity)
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
            # within ble_xim_pkg devices are handled by a combination of network id and device id
            # so we filter the device list to only give us devices with a matching device id part
            devices = filter(lambda ndi: ndi.deviceId == device_id, xim.get_device_list())
            # we only want to deal with one device so if our filtered list has more than one member we don't proceed
            if len(devices) == 1:
                # now we create the values dictionary.
                # the names and acceptable values of each parameter can be found in the API documentation for each call
                values = {"light_level":intensity, "fade_time":0, "response_time":0, "override_time":0, "lock_light_control":False}
                # finally, actually issue the advertising command
                ble_xim.advLightControl(devices[0], values)
            elif len(devices) > 1:
                print "Error: Ambiguous device ID"
            else:
                print "Error: could not locate device with ID {}".format(device_id)
        # dynamic dimming rotation
        elif choice == 's':
            dimming.allOn = False
            dimming.active = False
            for ximID in range(1, dimming.ximNumber+1):
                # print("XIM: " + str(ximID))
                # put light to maximum brightness
                devices = filter(lambda ndi: ndi.deviceId == [ximID], xim.get_device_list())
                # print(devices)
                intensity = 0
                values = {"light_level":intensity, "fade_time":500, "response_time":0, "override_time":0, "lock_light_control":False}
                ble_xim.advLightControl(devices[0], values)
                time.sleep(0.15)
            dimming.active = True
        # stop dynamic dimming rotation
        elif choice == 'e':
            dimming.active = False
        # all lights on to maximum
        elif choice == 'a':
            dimming.active = False
            for ximID in range(1, dimming.ximNumber+1):
                # print("XIM: " + str(ximID))
                # put light to maximum brightness
                devices = filter(lambda ndi: ndi.deviceId == [ximID], xim.get_device_list())
                # print(devices)
                intensity = 100
                values = {"light_level":intensity, "fade_time":500, "response_time":0, "override_time":0, "lock_light_control":False}
                ble_xim.advLightControl(devices[0], values)
                time.sleep(0.15)
        # all lights off
        elif choice == 'o':
            dimming.active = False
            for ximID in range(1, dimming.ximNumber+1):
                # print("XIM: " + str(ximID))
                # put light to maximum brightness
                devices = filter(lambda ndi: ndi.deviceId == [ximID], xim.get_device_list())
                # print(devices)
                intensity = 0
                values = {"light_level":intensity, "fade_time":500, "response_time":0, "override_time":0, "lock_light_control":False}
                ble_xim.advLightControl(devices[0], values)
                time.sleep(0.15)
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
