from GridButton import GridButton
from components.upnphouse_viewer.MyDialog import DeviceDialog
from ui.ImageButton import ImageButton
from ui.Label import Label
from ui.ProgressBar import ProgressBar

import theme
import gtk
import os

#_PATH = os.path.dirname(__file__)

_Switch_Power_service_name = "urn:schemas-upnp-org:service:SwitchPower:1"
_Dimming_service_name = "urn:schemas-upnp-org:service:Dimming:1"

class DimmableLight_Button (GridButton) :

    def __init__(self, device, button_on_image, button_off_image, open_dialog_func) :

        GridButton.__init__(self, device.get_friendly_name(), button_on_image, button_off_image, 0)  #TODO change friendly name with proper name and with real state


        self.__device = device
        self.__switch_power_service_proxy = device.get_service_proxy ( _Switch_Power_service_name )
        self.__status = 0 #TODO get real value
        self.__dimming_service_proxy = device.get_service_proxy ( _Dimming_service_name )
        self.__dimming = 100 #TODO get real value
        #TODO subscribe
        self.upnp_uuid = device.get_udn()

        self.__open_dialog_func = open_dialog_func

        self.option_button_image = theme.mb_item_btn_menu

        self.__device.subscribe ( _Switch_Power_service_name, self.__status_changed )
        self.__device.subscribe ( _Dimming_service_name, self.__dimming_changed )

        
    def button_clicked (self) :
        if (self.get_state() == 0) :
            self.__change_state (100)

        else :
            self.__change_state (0)


    def dialog_button_clicked (self) :
        self.__open_dialog_func ( self.__get_option_dialog () )


    def slider_used (self, position) :

        print 'DEBUG',position

        if ( position == 99.9 ): position = 100

        self.__change_state (position)


    def __change_state (self, new_state):

        if ( new_state == 0 ):
            if ( self.__status == 1 ) :
                self.__switch_power_service_proxy.SetTarget (self.__do_nothing, 0)
                #self.__switch_power_service_proxy.SetTarget ( 0 )

        else :

            if ( abs (self.__dimming - new_state) > 5 ) :

                self.__dimming_service_proxy.SetLoadLevelTarget (self.__do_nothing, new_state)
                #self.__dimming_service_proxy.SetLoadLevelTarget ( new_state )

            if ( self.__status == 0 ) :
                self.__switch_power_service_proxy.SetTarget (self.__do_nothing, 1)
                #self.__switch_power_service_proxy.SetTarget ( 1 )


    def __do_nothing (self, *values):
        pass


    def __get_option_dialog (self) :  #send part of this to init?

        dialog = DeviceDialog ( self.upnp_uuid, self.get_label() )
        dialog.set_size (350, 160)

        button = ImageButton (theme.window_close_1, theme.window_close_2, manual = True)
        button.connect_button_released(self.__close_dialog)
        dialog.add(button)
        button.set_pos ( 265, 52 )

        slider = ProgressBar ( show_time = False )

        #slider.set_position_by_percent ( float(self.get_state()) / 100 ) # Not working
        
        slider.connect_changed (self.slider_used)
        dialog.add(slider)
        slider.set_pos ( 30, 60 )

        return (dialog)


    def __close_dialog (self, px, py):

        self.__open_dialog_func ( None )


    def __dimmable_set_state (self, new_state):

        if ( new_state == 0 ):
            if ( self.get_state() > 0 ):
                self.set_state (0)
        elif ( self.get_state() == 0 ):
            self.set_state (new_state)

        #TODO check for dialog


    def __status_changed (self, signal, new_status):

        if ( signal == "changed::status" ):

            if ( int(new_status) == 0 ):
                self.__status = 0
                self.__dimmable_set_state ( 0 )
            else :
                self.__status = 1
                self.__dimmable_set_state ( self.__dimming )


    def __dimming_changed (self, signal, new_dimming):

        if ( signal == "changed::loadlevelstatus" ):

            self.__dimming = int(new_dimming)

            if ( not self.__status == 0 ):
                self.__dimmable_set_state ( self.__dimming )



