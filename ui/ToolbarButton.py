from Button import Button
from theme import theme


class ToolbarButton(Button):

    def __init__(self, icon):
    
        Button.__init__(self, "", icon)
        self.set_images(theme.ui_toolbar_button_1, theme.ui_toolbar_button_2)

