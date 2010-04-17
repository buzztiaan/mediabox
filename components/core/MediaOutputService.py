from com import Component, MediaOutput, msgs
from utils import logging


class MediaOutputService(Component):
    """
    Component for selecting the media renderer.
    """

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
            print "ADDED OUTPUT", output
        
        
    def handle_MEDIA_EV_OUTPUT_REMOVED(self, output):
    
        try:
            self.__outputs.remove(output)
        except:
            pass


    def handle_MEDIA_ACT_SELECT_OUTPUT(self, output):
    
        if (isinstance(output, MediaOutput)):
            self.__current_output = output
            self.emit_message(msgs.MEDIA_ACT_STOP)

        elif (output == None):
            from ui.dialog import OptionDialog
            dlg = OptionDialog("Select Media Renderer")
            for output in self.__outputs:
                dlg.add_option(None, output.TITLE)
            #end for
            ret = dlg.run()
            if (ret == dlg.RETURN_OK):
                choice = dlg.get_choice()
                self.__current_output = self.__outputs[choice]
                self.emit_message(msgs.MEDIA_ACT_STOP)
            #end if
        #end if
        
