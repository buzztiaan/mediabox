from com import Component, MediaOutput, msgs
from ui.dialog import OptionDialog
from utils import logging


class MediaOutputService(Component):

    def __init__(self):

        self.__outputs = []
        self.__current_output = None
    
        Component.__init__(self)
        
        
    def handle_CORE_EV_APP_STARTED(self):
    
        if (self.__outputs):
            self.__current_output = self.__outputs[0]
        else:
            logging.error("no output device available")

        
    def handle_MEDIA_SVC_GET_OUTPUT(self):
    
        return self.__current_output


    def handle_COM_EV_COMPONENT_LOADED(self, output):
    
        if (isinstance(output, MediaOutput)):
            self.__outputs.append(output)


    def handle_MEDIA_EV_OUTPUT_ADDED(self, output):
    
        if (isinstance(output, MediaOutput)):
            self.__outputs.append(output)
        
        
    def handle_MEDIA_EV_OUTPUT_REMOVED(self, output):
    
        try:
            self.__outputs.remove(output)
        except:
            pass


    def handle_MEDIA_ACT_SELECT_OUTPUT(self, output):
    
        if (isinstance(output, MediaOutput)):
            self.__current_output = output

        elif (output == None):
            dlg = OptionDialog("Select Output Device")
            for output in self.__outputs:
                dlg.add_option(None, output.TITLE)
            #end for
            ret = dlg.run()
            if (ret == 0):
                choice = dlg.get_choice()
                self.__current_output = self.__outputs[choice]
            #end if
        #end if
        
        self.emit_message(msgs.MEDIA_ACT_STOP)
