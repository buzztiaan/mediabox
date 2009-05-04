# -*- coding: UTF-8 -*-

from vkblayout import *
from utils import logging

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


def is_slide_open():
    """
    Returns whether the keyboard slide is open on the N810.
    """
    
    client = gconf.client_get_default()
    slide_open = client.get_bool("/system/osso/af/slide-open")
    return slide_open


def get_default_layout():
    """
    Returns the default layout for the user's keyboard settings.
    """
    
    client = gconf.client_get_default()
    #name = client.get_string("/apps/osso/inputmethod/int_kb_layout") or "C"
    name = client.get_string("/apps/osso/inputmethod/hildon-im-languages/language-0") or "C"
    if ("_" in name):
        name = name.split("_")[0]
    
    logging.debug("vkb layout is [%s]", name)
    
    layout = globals().get(name.upper(), C)

    return layout


def get_selector_layout():
    """
    Returns the keyboard layout for selecting other layouts.
    """
    
    layouts = [ name for name in globals().keys()
                if (len(name) == 2) and name == name.upper() ]
    layouts.sort()
    blocks = []
    block_width = 1.0 / len(layouts)

    for l in layouts:
        key = globals().get(l + "_KEY")
        if (key):
            key.set_layout(globals().get(l))
            block = Block(block_width, Row(key))
            blocks.append(block)
        #end if
    #end for
    
    return Layout(*blocks)




#
# layouts taken from N810 keyboards
#
# [x] US
# [ ] FISENODA
# [ ] PTES
# [ ] FR
# [x] DE
# [x] RU
# [ ] IT
#

US_KEY = Key("US\n(QWERTY)")
US = Layout(Block(0.05,
                  Row(LAYOUT)
            ),
            Block(0.75,
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


DE_KEY = Key("Deutsch\n(QWERTZ)")
DE = Layout(Block(0.05,
                  Row(LAYOUT)
            ),
            Block(0.75,
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
                      Key("ß", "°", "|")
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
                      Key("-", "_", "^"),
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


RU_KEY = Key("Русский\n(ЙЦУКЕН)")
RU = Layout(Block(0.05,
                  Row(LAYOUT)
            ),
            Block(0.75,
                  Row(Key("й", "Й", "1"),
                      Key("ц", "Ц", "2"),
                      Key("у", "У", "3"),
                      Key("к", "К", "4"),
                      Key("е", "Е", "5"),
                      Key("н", "Н", "6"),
                      Key("г", "Г", "7"),
                      Key("ш", "Ш", "8"),
                      Key("щ", "Щ", "9"),
                      Key("з", "З", "0"),
                      Key("^", "°", "|")
                  ),
                  Row(Key("ф", "Ф", "!"),
                      Key("ы", "Ы", "\""),
                      Key("в", "В", "@"),
                      Key("а", "А", "#"),
                      Key("п", "П", "\\"),
                      Key("р", "Р", "/"),
                      Key("о", "О", "("),
                      Key("л", "Л", ")"),
                      Key("д", "Д", ":"),
                      Key("ж", "Ж", ";"),
                      Key(".", ",", ".")
                  ),
                  Row(Key("я", "Я", "_"),
                      Key("ч", "Ч", "%"),
                      Key("с", "С", ""),
                      Key("м", "М", "="),
                      Key("и", "И", "&"),
                      Key("т", "Т", "*"),
                      Key("ь", "ь", "'"),
                      Key("б", "Б", "-"),
                      Key("ю", "Ю", "?"),
                      Key("х", "Х", "Ъ"),
                      Key("э", "Э", "Ё")
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

C = US

