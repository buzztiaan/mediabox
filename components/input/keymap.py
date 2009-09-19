from com import msgs


_KEYMAP = {
    "Escape":       msgs.HWKEY_EV_ESCAPE,
    "Return":       msgs.HWKEY_EV_ENTER,
    "F1":           msgs.HWKEY_EV_F1,
    "F2":           msgs.HWKEY_EV_F2,
    "F3":           msgs.HWKEY_EV_F3,
    "F4":           msgs.HWKEY_EV_F4,
    "F5":           msgs.HWKEY_EV_F5,
    "F6":           msgs.HWKEY_EV_F6,
    "F7":           msgs.HWKEY_EV_F7,
    "F8":           msgs.HWKEY_EV_F8,
    "F9":           msgs.HWKEY_EV_F9,
    "F10":          msgs.HWKEY_EV_F10,
    "F11":          msgs.HWKEY_EV_F11,
    "F12":          msgs.HWKEY_EV_F12,
    "Up":           msgs.HWKEY_EV_UP,
    "Down":         msgs.HWKEY_EV_DOWN,
    "Left":         msgs.HWKEY_EV_LEFT,
    "Right":        msgs.HWKEY_EV_RIGHT,
    "XF86Headset":  msgs.HWKEY_EV_HEADSET,
    "BackSpace":    msgs.HWKEY_EV_BACKSPACE
}


def get(keycode):

    return _KEYMAP.get(keycode)

