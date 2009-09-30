def DIALOG_SVC_OPTIONS(*options): pass
"""
Displays a dialog with option buttons. It takes a list of tuples consisting
of an icon pixbuf (or None) and a text label.
@since: 2009.09

@param options: variable list of (icon, label) tuples
"""

def DIALOG_SVC_CUSTOM(icon, header, widget): pass
"""
Displays a dialog with custom content.
@since: 0.96.5

@param icon: pixbuf object or C{None}
@param header: header text
@param widget: widget to use for content
@return: response value
"""


def DIALOG_SVC_ERROR(header, text): pass
"""
Displays an error dialog.
@since: 0.96.5

@param header: header text
@param text: message text
@return: response value
"""

def DIALOG_SVC_INFO(header, text): pass
"""
Displays an info dialog.
@since: 0.96.5

@param header: header text
@param text: message text
@return: response value
"""

def DIALOG_SVC_QUESTION(header, text): pass
"""
Displays a question dialog. The user can answer with "Yes" or "No".
@since: 0.96.5

@param header: header text
@param text: message text
@return: response value
"""

def DIALOG_SVC_TEXT_INPUT(header, text): pass
"""
Displays a text input dialog.
@since: 0.96.5

@param header: header text
@param text: message text
@return: response value
@return: text string
"""

def DIALOG_SVC_WARNING(header, text): pass
"""
Displays a warning dialog.
@since: 0.96.5

@param header: header text
@param text: message text
@return: response value
"""

def NOTIFY_SVC_SHOW_INFO(text): pass
"""
Shows a notification.

@param text: notification text string
"""

