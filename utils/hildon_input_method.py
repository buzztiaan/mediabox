try:
    import ctypes
    import c_gobject

    _libgtk = ctypes.CDLL("libgtk-x11-2.0.so.0")
    _libgdk = ctypes.CDLL("libgdk-x11-2.0.so.0")


    _c_im_ctx = _libgtk.gtk_im_multicontext_new(None)
    _im_ctx = c_gobject.wrap(_c_im_ctx)

    _current_signal_handler = None
except:
    pass


def show_im(win, cb, *args):
    global _current_signal_handler

    if (_current_signal_handler):
        _im_ctx.disconnect(_current_signal_handler)
    
    _current_signal_handler = _im_ctx.connect("commit", cb, *args)
    
    _libgtk.gtk_im_context_set_client_window(_c_im_ctx, hash(win.window))
    _libgtk.gtk_im_context_show(_c_im_ctx)

