class ViewerState(object):

    __slots__ = ["item_offset", "selected_item", "collection_visible", "caps"]

    def __init__(self):
        self.item_offset = 0
        self.selected_item = -1
        self.collection_visible = True
        self.caps = 0
