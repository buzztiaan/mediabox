# -*- coding: UTF-8 -*-

from vkblayout import *

try:
    # GNOME
    import gconf
except:
    try:
        # Maemo    
        import gnome.gconf as gconf
    except:
        # last resort...
        from utils import gconftool as gconf


def get_default_layout():
    """
    Returns the default layout for the user's keyboard settings.
    """
    
    client = gconf.client_get_default()
    name = client.get_string("/apps/osso/inputmethod/int_kb_layout") or "C"
    
    try:
        layout = getattr(__module__, layout.upper())
    except:
        layout = C

    return layout



#
# layouts taken from N810 keyboards
#

EN = Layout(Block(0.8,
                  Row(Key("q", "Q", "1"),
                      Key("w", "W", "2"),
                      Key("e", "E", "3"),
                      Key("r", "R", "4"),
                      Key("t", "T", "5"),
                      Key("y", "Y", "6"),
                      Key("u", "U", "7"),
                      Key("i", "I", "8"),
                      Key("o", "O", "9"),
                      Key("p", "P", "0"),
                      Key("°", "°", "|")
                  ),
                  Row(Key("a", "A", "!"),
                      Key("s", "S", "\""),
                      Key("d", "D", "@"),
                      Key("f", "F", "#"),
                      Key("g", "G", "\\"),
                      Key("h", "H", "/"),
                      Key("j", "J", "("),
                      Key("k", "K", ")"),
                      Key("l", "L", "*"),
                      Key("'", "'", "?"),
                      Key(",", "<", ",")
                  ),
                  Row(Key("z", "Z", "¥"),
                      Key("x", "X", "^"),
                      Key("c", "C", "~"),
                      Key("v", "V", "%"),
                      Key("b", "B", "&"),
                      Key("n", "N", "$"),
                      Key("m", "M", "€"),
                      Key(";", ":", "£"),
                      Key("-", "_", "-"),
                      Key("+", "+", "="),
                      Key(".", ">", ".")
                  )
            ),
            Block(0.1,
                  Row(Key(" ", " ", " "))
            ),
            Block(0.1,
                  Row(BACKSPACE),
                  Row(ALT),
                  Row(SHIFT),
                  Row(HIDE)
            )
     )



DE = Layout(Block(0.8,
                  Row(Key("q", "Q", "1"),
                      Key("w", "W", "2"),
                      Key("e", "E", "3"),
                      Key("r", "R", "4"),
                      Key("t", "T", "5"),
                      Key("z", "Z", "6"),
                      Key("u", "U", "7"),
                      Key("i", "I", "8"),
                      Key("o", "O", "9"),
                      Key("p", "P", "0"),
                      Key("^", "°", "|")
                  ),
                  Row(Key("a", "A", "!"),
                      Key("s", "S", "\""),
                      Key("d", "D", "@"),
                      Key("f", "F", "#"),
                      Key("g", "G", "%"),
                      Key("h", "H", "\\"),
                      Key("j", "J", "/"),
                      Key("k", "K", "("),
                      Key("l", "L", ")"),
                      Key("ü", "Ü", "?"),
                      Key(",", ";", ",")
                  ),
                  Row(Key("y", "Y", "€"),
                      Key("x", "X", "~"),
                      Key("c", "C", "*"),
                      Key("v", "V", "&"),
                      Key("b", "B", "+"),
                      Key("n", "N", "<"),
                      Key("m", "M", ">"),
                      Key("ö", "Ö", "="),
                      Key("ä", "Ä", "'"),
                      Key("-", "_", "ß"),
                      Key(".", ":", ".")
                  )
            ),
            Block(0.1,
                  Row(Key(" ", " ", " "))
            ),
            Block(0.1,
                  Row(BACKSPACE),
                  Row(ALT),
                  Row(SHIFT),
                  Row(HIDE)
            )
     )


C = EN

