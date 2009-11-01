from com import Component, MediaOutput, msgs


class MediaOutputService(Component):

    def __init__(self):

        self.__current_output = None
    
        Component.__init__(self)
        
        
    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        if (isinstance(comp, MediaOutput)):
            self.__current_output = comp
        
        
    def handle_MEDIA_SVC_GET_OUTPUT(self):
    
        return self.__current_output


    def handle_MEDIA_ACT_SELECT_OUTPUT(self, output):
    
        if (isinstance(output, MediaOutput)):
            self.__current_output = output
            print "SETTING OUTPUT", output

