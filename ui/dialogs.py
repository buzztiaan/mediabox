from theme import theme

import gtk


def info(title, message):

    return choice(title, message, ("OK",), theme.mb_dialog_info)


def warning(title, message):

    return choice(title, message, ("OK",), theme.mb_dialog_warning)
    

def error(title, message):

    return choice(title, message, ("OK",), theme.mb_dialog_error)


def question(title, message):

    return choice(title, message, ("Yes", "No"), theme.mb_dialog_question)
    
    
    
def choice(title, message, buttons, icon = None):

    btns = []
    cnt = 0
    for b in buttons:
        btns.append(b)
        btns.append(cnt)
        cnt += 1

    dlg = gtk.Dialog(title, None, gtk.DIALOG_MODAL, tuple(btns))

    hbox = gtk.HBox(spacing = 12)
    hbox.set_border_width(12)
    hbox.show()
    dlg.vbox.pack_start(hbox, False, False)

    if (icon):
        img = gtk.Image()
        img.set_from_pixbuf(icon)
        img.show()
        hbox.pack_start(img, False, False)
    
    lbl = gtk.Label(message)
    lbl.show()
    #dlg.vbox.pack_start(lbl, False, False)
    hbox.pack_start(lbl, True, True)
                      
    response = dlg.run()
    dlg.destroy()
    
    return response
    
