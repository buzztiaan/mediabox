class ViewerState(object):
    """
    Class for remembering the state of a viewer, so that it can be quickly
    restored again without the viewer's help.
    """
    __slots__ = ["item_offset", "selected_item", "collection_visible",
                 "toolbar_set"]

    def __init__(self):
        self.item_offset = 0
        self.selected_item = -1
        self.collection_visible = True
        self.toolbar_set = None

