def COM_EV_COMPONENT_LOADED(component): pass
"""
Gets emitted when a component is loaded.

@param component: component object
"""

def COM_EV_LOADING_MODULE(name): pass
"""
Gets emitted when a module gets loaded. A module is a collection of components.

@param name: name of the module
"""



def COM_EV_APP_STARTED(): pass
"""
Gets emitted when the core application has finished initialising.
"""

def COM_EV_APP_SHUTDOWN(): pass
"""
Gets emitted when the application is shutting down. Plugins should listen for
this message if they need to clean up at exit.
"""

def CORE_ACT_APP_CLOSE(): pass
"""
Closes the application.
"""

def CORE_ACT_APP_MINIMIZE(): pass
"""
Minimizes the application window.
"""

def CORE_EV_APP_IDLE_BEGIN(): pass
"""
Gets emitted when the application goes into idle state to save battery.
Plugins should listen to this message if they need to take action for saving
battery.
"""

def CORE_EV_APP_IDLE_END(): pass
"""
Gets emitted when the application wakes up from idle state.
"""

def CORE_SVC_LAUNCH_APPLET(applet_id): pass
"""
Launches the applet specified by the applet ID.
@since: 2009.10.18

@param applet_id: applet ID string
"""

def CORE_EV_DEVICE_ADDED(device_id, device): pass
"""
Gets emitted when a new storage device has been added. The device ID is a
string unique among all storage devices.

@param device_id: ID string of the device
@param device: the device object
"""

def CORE_EV_DEVICE_REMOVED(device_id): pass
"""
Gets emitted when a storage device is removed.

@param device_id: ID string of the device
"""

def CORE_EV_FOLDER_INVALIDATED(folder): pass
"""
Gets emitted when the contents of a folder become invalid and the folder needs
to be reloaded.

@param folder: file object representing the folder
"""

def CORE_EV_FOLDER_VISITED(folder): pass
"""
Gets emitted when a folder gets visited by the user.
@since: 0.97

@param folder: file object representing the folder
"""

def CORE_SVC_LIST_PATH(path): pass
"""
@deprecated: do not use; it will be removed
"""

def CORE_SVC_GET_FILE(path): pass
"""
Looks up the file object for the given full path string.

@param path: path string
@return: file object or C{0}
"""

def CORE_ACT_SCAN_MEDIA(force_rescan): pass
"""
Instructs the media scanner to scan the media library.

@param force_rescan: whether to force a scan even if the library has not changed
"""

def CORE_ACT_SET_TITLE(title): pass
"""
Sets the title bar text.

@param title: title text
"""

def CORE_ACT_SET_INFO(info): pass
"""
Sets the title bar info text.

@param info: info text
"""

def CORE_ACT_SET_TOOLBAR(toolbar_set): pass
"""
Sets the toolbar widgets.
@deprecated: this is not used anymore

@param toolbar_set: list of widgets
"""

def CORE_ACT_SEARCH_ITEM(search_term): pass
"""
Instructs viewers to search for the given search term.

@param search_term: search term
"""

def CORE_EV_SEARCH_CLOSED(): pass
"""
Gets emitted when the search mode is left.
"""

def CORE_EV_THEME_CHANGED(): pass
"""
Gets emitted when the theme has changed.
"""


def MEDIA_ACT_LOAD(f): pass
"""
Instructs the current media player to load the given file.
@since: 0.97

@param f: file object to load
"""

def MEDIA_ACT_PLAY(): pass
"""
Instructs the current media player to play.
"""

def MEDIA_ACT_PAUSE(): pass
"""
Instructs the current media player to pause.
"""

def MEDIA_ACT_STOP(): pass
"""
Instructs the current media player to stop.
"""

def MEDIA_ACT_SEEK(seconds): pass
"""
Instructs the current media player to seek for the given position.
@since: 0.97
"""

def MEDIA_ACT_PREVIOUS(): pass
"""
Instructs the current media player to skip to the previous item.
"""

def MEDIA_ACT_NEXT(): pass
"""
Instructs the current media player to skip to the next item.
"""

def MEDIA_EV_LOADED(player, f): pass
"""
Gets emitted when a media player has loaded a file.

@param player: the player that has loaded the file
@param f: file object
"""

def MEDIA_EV_TAG(key, value): pass
"""
Gets emitted when a media tag gets reported.

@param key: name of the tag
@param value: value of the tag
"""

def MEDIA_EV_PLAY(): pass
"""
Gets emitted when media playback starts.
"""

def MEDIA_EV_PAUSE(): pass
"""
Gets emitted when media playback is paused.
"""

def MEDIA_EV_EOF(): pass
"""
Gets emitted when the player reaches the end of the media file.
"""

def MEDIA_EV_VOLUME_CHANGED(volume): pass
"""
Gets emitted when the media volume is changed.

@param volume: volume value in the range [0, 100]
"""

def MEDIA_EV_POSITION(position, total): pass
"""
Gets emitted regularly when the playback position changes.
@since: 0.96.5

@param position: position in seconds
@param total: total media length in seconds, or C{0} if the total length is unknown
"""

def MEDIA_EV_LYRICS(text): pass
"""
Gets emitted when a lyrics line is due.
@since: 0.96.5

@param text: text of the current lyrics line
"""

def MEDIA_EV_DOWNLOAD_PROGRESS(f, amount, total): pass
"""
Gets emitted when a file download progresses.
@since: 0.96.5

@param f: file object that is being downloaded
@param amount: download amount in bytes
@param total: total file size in bytes
"""

def MEDIA_EV_BOOKMARKED(f, bookmarks): pass
"""
Gets emitted when media bookmarks are set on a file. Bookmark positions are
given in seconds.
@since: 0.96.5

@param f: file object
@param bookmarks: list of bookmark positions
"""


def MEDIA_EV_OUTPUT_ADDED(output): pass
"""
Gets emitted when a new output device is added.
@since: 2009.11.01

@param output: a MediaOutput object
"""

def MEDIA_EV_OUTPUT_REMOVED(output): pass
"""
Gets emitted when output device is removed.
@since: 2009.11.01

@param output: a MediaOutput object
"""

def MEDIA_ACT_SELECT_OUTPUT(output): pass
"""
Selects the given media output. Pass C{None} for the output to let the
user choose.
@since: 2009.10.31

@param output: a MediaOutput object or C{None}
"""

def MEDIA_SVC_GET_OUTPUT(): pass
"""
Returns the currently selected media output.
@since: 2009.10.31

@return: a MediaOutput object
"""


def BOOKMARK_SVC_LIST(mimetypes): pass
"""
Lists the bookmarks of the given MIME types. Pass an empty list of MIME types
to get the bookmarks for all mimetypes.
@since: 0.96.5

@param mimetypes: list of MIME types
@return: list of file objects
"""

def BOOKMARK_SVC_ADD(f): pass
"""
Bookmarks the given file.
@since: 0.96.5

@param f: file object
"""

def BOOKMARK_SVC_DELETE(f): pass
"""
Deletes the bookmark for the given file.
@since: 0.96.5

@param f: file object
"""

def BOOKMARK_EV_INVALIDATED(): pass
"""
Gets emitted when the list of bookmarks changes.
@since: 0.96.5
"""


def THUMBNAIL_SVC_LOOKUP_THUMBNAIL(f): pass
"""
Looks up a thumbnail for the given file.

@param f: file object
@return: path of thumbnail file and whether the thumbnail is final
"""

def THUMBNAIL_SVC_LOAD_THUMBNAIL(f, cb, *args): pass
"""
Loads a thumbnail for the given file asynchronously, invoking the given callback
when a thumbnail has been found or was created.

@param f: file object
@param cb: callback handler
@param args: variable list of arguments to the callback handler
"""

def THUMBNAIL_EV_LOADING(): pass
"""
Gets emitted when the thumbnailer starts loading.
@since: 2010.08.08
"""


def UI_ACT_FREEZE(): pass
"""
Freezes UI updates globally. No parts of the UI are redrawn during a freeze.
Individual widgets may be thawed for rendering, though.
"""

def UI_ACT_THAW(): pass
"""
Thaws a globally frozen UI.
"""

def UI_ACT_RENDER(): pass
"""
Redraws the whole application UI. This action can be time-consuming, so use
with care.
"""

def UI_ACT_FULLSCREEN(v): pass
"""
Enters or leaves fullscreen mode.
@since: 2009.10.18

@param v: whether to enter (True) or leave (False) fullscreen mode.
"""


def UI_ACT_TALK(text_to_say): pass
"""
Says the given text. This action does nothing unless a component makes use of
it for, e.g., providing talk navigation.
@since: 0.96.5

@param text_to_say: text string
"""

def UI_ACT_SHOW_INFO(text): pass
"""
Displays an info notification.
@since: 2009.12.22

@param text: text to display
"""

def UI_ACT_HIDE_MESSAGE(): pass
"""
Hides the current overlay message, if there is any.
"""

def UI_EV_VIEWER_CHANGED(index): pass
"""
Gets emitted when viewer has changed.

@param index: index number of the viewer
"""

def UI_EV_DEVICE_SELECTED(device_id): pass
"""
Gets emitted when a storage device has been selected.

@param device_id: device ID string
"""

def UI_ACT_SHOW_DIALOG(name): pass
"""
Shows the dialog window given by its name.
@since: 2009.11.17

@param name: name of the dialog window
"""

def UI_ACT_SELECT_VIEW(name): pass
"""
Selects a view by name.

@param: name of the view
"""

def UI_ACT_SELECT_DEVICE(device_id): pass
"""
Selects a device by device ID.

@param device_id: device ID string
"""

def UI_ACT_SET_STATUS_ICON(widget): pass
"""
Sets the given widget as icon in the status area. A status icon should be 32x32
pixels in size.
@since: 0.96.5

@param widget: the widget to display in the status area
"""

def UI_ACT_UNSET_STATUS_ICON(widget): pass
"""
Removes the given widget from the status area if it was visible there.
The widget doesn't get destroyed, only hidden, and can be made visible again
with L{UI_ACT_SET_STATUS_ICON}.
@since: 0.96.5

@param widget: the widget to remove
"""


def HWKEY_EV_DECREMENT(): pass
"""
DECREMENT hardware key.
"""

def HWKEY_EV_INCREMENT(): pass
"""
INCREMENT hardware key.
"""

def HWKEY_EV_ENTER(): pass
"""
ENTER hardware key.
"""

def HWKEY_EV_FULLSCREEN(): pass
"""
FULLSCREEN hardware key.
"""

def HWKEY_EV_MENU(): pass
"""
MENU hardware key.
"""

def HWKEY_EV_ESCAPE(): pass
"""
ESCAPE hardware key.
"""

def HWKEY_EV_EJECT(): pass
"""
EJECT hardware key.
"""

def HWKEY_EV_BACKSPACE(): pass
"""
BACKSPACE hardware key.
"""

def HWKEY_EV_HEADSET(): pass
"""
HEADSET hardware key.
"""

def HWKEY_EV_HEADSET_DOUBLE(): pass
"""
HEADSET hardware key double click.
"""

def HWKEY_EV_HEADSET_TRIPLE(): pass
"""
HEADSET hardware key triple click.
"""

def HWKEY_EV_UP(): pass
"""
UP hardware key.
"""

def HWKEY_EV_DOWN(): pass
"""
DOWN hardware key.
"""

def HWKEY_EV_LEFT(): pass
"""
LEFT hardware key.
"""

def HWKEY_EV_RIGHT(): pass
"""
RIGHT hardware key.
"""

def HWKEY_EV_F1(): pass
"""
F1 hardware key.
"""

def HWKEY_EV_F2(): pass
"""
F2 hardware key.
"""

def HWKEY_EV_F3(): pass
"""
F3 hardware key.
"""

def HWKEY_EV_F4(): pass
"""
F4 hardware key.
"""

def HWKEY_EV_F5(): pass
"""
F5 hardware key.
"""

def HWKEY_EV_F6(): pass
"""
F6 hardware key.
"""

def HWKEY_EV_F7(): pass
"""
F7 hardware key.
"""

def HWKEY_EV_F8(): pass
"""
F8 hardware key.
"""

def HWKEY_EV_F9(): pass
"""
F9 hardware key.
"""

def HWKEY_EV_F10(): pass
"""
F10 hardware key.
"""

def HWKEY_EV_F11(): pass
"""
F11 hardware key.
"""

def HWKEY_EV_F12(): pass
"""
F12 hardware key.
"""

def HWKEY_EV_KEY(key): pass
"""
Any letter hardware key.

@param key: key code
"""

