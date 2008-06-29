from upnp.SOAPProxy import SOAPProxy

import gtk
import os


_Switch_Power_service_name = "urn:schemas-upnp-org:service:SwitchPower:1"


class UPnPBinaryLight (object):
    """
    UPnP Binary Light class wich extends a UPnPDevice type with convinient functions
    """

    def __init__ ( self ) :
        
        self.__switch_power_service_proxy = self.__set_switch_power_service_proxy ()
        #Need to improve error when the upnp binary light device is badly implemendted and does not have a switchpower service or the scpd file doesnt have the correct standar actions
        self.__status_subscriber_number = 0
        self.__status = 0
        

    def __set_switch_power_service_proxy (self):

        service_data = self.__services[_Switch_Power_service_name]
        
        if ( service_data ):
            scpd_url, ctrl_url, event_url = service_data
            return ( SOAPProxy( ctrl_url, _Switch_Power_service_name, scpd_url, event_url = envent_url ) )

        return ( None )

    def set_new_target_value (self, new_target_value):

       self.__switch_power_service_proxy.SetTarget ( 'NewTargetValue', new_target_value )


    def subscribe_to_status_events (self):

        if ( self.__status_subscriber_number < 1 ):
            self.__switch_power_service_proxy.subscribe_to_notifications ()
        
        self.__status_subscriber_number += 1


    def unsubscribe_from_status_events (self):

        if ( self.__status_subscriber_number > 0 ):
            self.__status_subscriber_number -= 1
        
            if ( self.__status_subscriber_number < 1 ):
                self.__switch_power_service_proxy.unsubscribe_to_notifications ()


    def get_status (self):

        if ( self__status_subscriber_number > 0 ): #since we are subscribed there is no need to query for the value
            return ( self.__status )

        else:
            return ( self.get_status_force_check )


    def get_status_force_check (self): #this checks the status value from the server sync, ignoring if the proxy is subscribed or not
        
        new_status = self.__switch_power_service_proxy.GetStatus()
        
        if ( new_status != self.__status ):
            self.__status = new_status
            if ( self.__status_subscriber_number > 0 ):
                #emit signal
                x = 1  #just to avoid error until emit signal is done


