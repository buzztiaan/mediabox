from com import Widget, msgs
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP, text_extents
from ui.Button import Button
from Dialog import Dialog
from theme import theme

import gtk


class DialogService(Widget):

    def __init__(self):

        self.__buffer = None
        self.__response = -1
            
        Widget.__init__(self)
        
        self.__btn_ok = Button("OK")
        self.__btn_ok.set_visible(False)
        self.__btn_ok.connect_clicked(self.__on_btn_ok)
        self.add(self.__btn_ok)
        
        self.__dialog = Dialog()
        self.add(self.__dialog)


    def render_this(self):
    
        w, h = self.get_parent().get_size()
        screen = self.get_screen()

        TEMPORARY_PIXMAP.copy_buffer(self.__buffer, 0, 0, 0, 0, w, h)
        TEMPORARY_PIXMAP.fill_area(0, 0, w, h, theme.color_mb_overlay)
        screen.copy_buffer(TEMPORARY_PIXMAP, 0, 0, 0, 0, w, h)


    def __on_btn_ok(self):
    
        self.__response = 0


    def __on_btn_cancel(self):
    
        self.__response = 1


    def __on_btn_yes(self):
    
        self.__response = 0


    def __on_btn_no(self):
    
        self.__response = 1


    def __show_dialog(self):
    
        screen = self.get_screen()
        w, h = self.get_parent().get_size()
        if (not self.__buffer or (w, h) != self.__buffer.get_size()):
            self.__buffer = Pixmap(None, w, h)
    
        #self.emit_message(msgs.UI_ACT_FREEZE)
        self.__buffer.copy_buffer(screen, 0, 0, 0, 0, w, h)
        #self.emit_message(msgs.INPUT_EV_CONTEXT_MENU)
        #self.emit_message(msgs.UI_EV_VIEWER_CHANGED, -1)
        
        
        self.__dialog.set_geometry(0, 0, w, h)
        self.set_visible(True)
        self.push_actor(self)

        self.render()
        gtk.gdk.window_process_all_updates()


    def __hide_dialog(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
    
        screen.draw_pixmap(self.__buffer, x, y)
        self.set_visible(False)
        #self.emit_message(msgs.UI_ACT_THAW)
        self.pop_actor()
        
        
    def __run_dialog(self):
    
        self.__response = -1
        while (self.__response == -1):
            gtk.main_iteration(True)
        self.__hide_dialog()
        
        return self.__response


    def handle_DIALOG_SVC_QUESTION(self, header, text):
    
        self.__dialog.reset()
        self.__dialog.set_icon(theme.mb_dialog_question)
        self.__dialog.set_header(header)
        self.__dialog.set_body(text)
        self.__dialog.set_buttons(("Yes", self.__on_btn_yes),
                                  ("No", self.__on_btn_no))
    
        self.__show_dialog()
        self.emit_message(msgs.UI_ACT_TALK, "Question: " + text)
        return self.__run_dialog()
                

    def handle_DIALOG_SVC_ERROR(self, header, text):
    
        self.__dialog.reset()
        self.__dialog.set_icon(theme.mb_dialog_error)
        self.__dialog.set_header(header)
        self.__dialog.set_body(text)
        self.__dialog.set_buttons(("OK", self.__on_btn_ok))
    
        self.__show_dialog()
        self.emit_message(msgs.UI_ACT_TALK, "Error: " + text)
        return self.__run_dialog()
        
        
    def handle_DIALOG_SVC_WARNING(self, header, text):
    
        self.__dialog.reset()
        self.__dialog.set_icon(theme.mb_dialog_warning)
        self.__dialog.set_header(header)
        self.__dialog.set_body(text)
        self.__dialog.set_buttons(("OK", self.__on_btn_ok))
    
        self.__show_dialog()
        self.emit_message(msgs.UI_ACT_TALK, "Warning: " + text)
        return self.__run_dialog()
        
        
    def handle_DIALOG_SVC_INFO(self, header, text):
    
        self.__dialog.reset()
        self.__dialog.set_icon(theme.mb_dialog_info)
        self.__dialog.set_header(header)
        self.__dialog.set_body(text)
        self.__dialog.set_buttons(("OK", self.__on_btn_ok))
    
        self.__show_dialog()
        self.emit_message(msgs.UI_ACT_TALK, text)
        return self.__run_dialog()


    def handle_DIALOG_SVC_TEXT_INPUT(self, header, text):
    
        self.__dialog.reset()
        self.__dialog.set_header(header)
        self.__dialog.set_text_input(text)
        self.__dialog.set_buttons(("OK", self.__on_btn_ok),
                                  ("Cancel", self.__on_btn_cancel))

        self.__show_dialog()
        self.emit_message(msgs.VKB_ACT_SHOW, self.get_window())
        resp = self.__run_dialog()
        return (resp, self.__dialog.get_text_input())
        
        
    def handle_DIALOG_SVC_CUSTOM(self, icon, header, custom):
    
        self.__dialog.reset()
        if (icon):
            self.__dialog.set_icon(icon)
        self.__dialog.set_header(header)
        self.__dialog.set_custom_widget(custom)
        self.__dialog.set_buttons(("OK", self.__on_btn_ok))
    
        self.__show_dialog()
        return self.__run_dialog()


    def handle_INPUT_EV_ENTER(self):
    
        if (self.is_visible()):
            self.__dialog.trigger_button(0)
