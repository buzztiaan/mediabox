class ViewerState(object):
    """
    Class for remembering the state of a viewer, so that it can be quickly
    restored again without the viewer's help.
    """
    __slots__ = ["items", "item_offset", "selected_item", "view_mode",
                 "toolbar_set"]

    def __init__(self):
        self.items = []
        self.item_offset = 0
        self.selected_item = -1
        self.view_mode = 1
        self.toolbar_set = None

