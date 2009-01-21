from GridButton import GridButton

_Switch_Power_service_name = "urn:schemas-upnp-org:service:SwitchPower:1"

class BinaryLight_Button (GridButton) :

    def __init__(self, device, button_on_image, button_off_image) :

        GridButton.__init__(self, device.get_friendly_name(), button_on_image, button_off_image, 0)  #TODO change friendly name with proper name and real state

        self.__device = device
        self.__switch_power_service_proxy = device.get_service_proxy ( _Switch_Power_service_name )
        self.__status = 0 #TODO get real value

        self.upnp_uuid = device.get_udn()

        self.__device.subscribe ( _Switch_Power_service_name, self.__status_changed )


    def button_clicked (self) :

        if (self.__status == 0) :
            self.__switch_power_service_proxy.SetTarget (self.__do_nothing, 1)
            #self.__switch_power_service_proxy.SetTarget ( 1 )
        else :        
            self.__switch_power_service_proxy.SetTarget (self.__do_nothing, 0)
            #self.__switch_power_service_proxy.SetTarget ( 0 )


    def __do_nothing (self, *values):
        pass


    def __status_changed (self, signal, new_status) :

        if ( signal == "changed::status" ):

            if ( int (new_status) == 0 ) :
                if ( self.__status == 1 ) :
                    self.set_state (0)
            elif ( self.__status == 0 ) :
                self.set_state (1)

