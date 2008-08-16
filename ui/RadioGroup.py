class RadioGroup(object):
    """
    Class for grouping checkboxes together to form radio buttons.
    """
    
    def __init__(self, *buttons):
    
        self.__buttons = buttons
    
        for btn in buttons:
            btn.connect_checked(self.__on_check, btn)
            btn.lock_unchecking()
            
            
    def __on_check(self, is_checked, checked_btn):
    
        if (is_checked):
            for btn in self.__buttons:
                if (btn != checked_btn):
                    btn.set_checked(False)
            #end for
        #end if
