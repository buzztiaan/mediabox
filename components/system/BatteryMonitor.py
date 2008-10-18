# based on battery-status script by ag2
# original script (C) ag2 2007

from com import Component, msgs
from utils import maemo
import config

import time
import dbus, dbus.service
import gobject


class _Request(dbus.service.Object): 
  def __init__(self, bus_name): 
    dbus.service.Object.__init__(self, bus_name, '/com/nokia/bme/request')

  @dbus.service.signal('com.nokia.bme.request') 
  def timeleft_info_req(self): 
     pass

  @dbus.service.signal('com.nokia.bme.request') 
  def status_info_req(self):
     pass


class BatteryMonitor(Component):

    def __init__(self):
    
        self.__last_check = 0
        self.__is_charging = False
        
        # the maximum known battery fill level
        self.__max_battery = config.get_max_battery()
    
        Component.__init__(self)
        
        
        system_bus = maemo.get_system_bus()
        system_bus.add_signal_receiver(self.__timeleft_cb, 'battery_timeleft')
        system_bus.add_signal_receiver(self.__charging_on_cb, 'charger_charging_on')
        system_bus.add_signal_receiver(self.__charging_off_cb, 'charger_charging_off')
        bus_name = dbus.service.BusName('com.nokia.bme.request', system_bus) 
        self.__request = _Request(bus_name)
        
        gobject.idle_add(self.__request.timeleft_info_req)


    def __timeleft_cb(self, idle_time, active_time):

        print "BATTERY:", idle_time, active_time
        if (idle_time > self.__max_battery):
            self.__max_battery = idle_time
            config.set_max_battery(idle_time)

        percent = min(100, 100.0 * idle_time / self.__max_battery)
        self.emit_event(msgs.SYSTEM_EV_BATTERY_REMAINING, percent)


    def __charging_on_cb(self):
    
        self.__is_charging = True
        
        
    def __charging_off_cb(self):
    
        self.__is_charging = False
       
        
    #def handle_event(self, msg, *args):
    #
    #    # no matter what event
    #    now = time.time()
    #    if (now > self.__last_check + 60):
    #        self.__last_check = now
    #        self.__check_battery()
            
            
    def __check_battery(self):
    
        #self.__request.status_info_req()
        self.__request.timeleft_info_req()

