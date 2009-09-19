PLATFORM = "maemo4"

_osso_ctx = None


def create_osso_context(name, version, v):
    global _osso_ctx
    
    import osso
    _osso_ctx = osso.Context(name, version, v)


def get_product_code():
    """
    Returns the product code of the device.

     - Nokia 770:    SU-18
     - Nokia N800:   RX-34
     - Nokia N810:   RX-44
     - Nokia N810WE: RX-48
     - Nokia N900:   RX-51
     - Unknown:      ?
    
    @since: 0.96
    
    @return: product code
    """
    
    # you can override the product code by setting the environment variable
    # MEDIABOX_MAEMO_DEVICE
    product = os.environ.get("MEDIABOX_MAEMO_DEVICE")
    
    if (not product):
        try:
            lines = open("/proc/component_version", "r").readlines()
        except:
            lines = []
            
        product = "?"
        for line in lines:
            line = line.strip()
            if (line.startswith("product")):
                parts = line.split()
                product = parts[1].strip()
                break
        #end for
    #end if

    return product


def request_connection():
    """
    If the device is not connected, tries to establish the default connection
    or pop up the connection dialog.
    Does nothing if the device does already have a network connection.
    @since: 0.96.3
    """
    
    # dbus-send --type=method_call --system --dest=com.nokia.icd/com/nokia/icd com.nokia.icd.connect
    # dbus-send --system --dest=com.nokia.icd /com/nokia/icd_ui com.nokia.icd_ui.disconnect boolean:true
    
    try:
        import conic
        conn = conic.Connection()
        conn.request_connection(conic.CONNECT_FLAG_NONE)
    except:
        pass

