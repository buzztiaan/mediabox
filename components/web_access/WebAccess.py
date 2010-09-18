from com import Configurator, msgs
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import OptionItem
from utils import mimetypes
from utils import network
from utils import urlquote
from theme import theme


_PORT = 18056


_NOT_FOUND = """
<html>
<head><title>MediaBox WebAccess</title></head>
<body>
Oops, the file you're looking for isn't there...
<hr>
<address>MediaBox Embedded HTTP Server</address>
</body>
</html>
"""

_LISTING = """
<html>
<head><title>%s - MediaBox WebAccess</title></head>
<style>
  body {
    background-color: #000;
  }
  p {
    font-size: 12px;
    font-family: Arial, Helvetica Sans;
    color: #fff;
  }
  img {
    border: none;
  }
</style>
<body>
<iframe style="display: none;" name="if"></iframe>
%s
</body>
</html>
"""

_FILE = """
<div style="float: left;
            width: 180px;
            height: 200px;
            text-align: center;">
  <a href="%s" %s>
    <img src="%s" style="width: 160px; height: 160px;"><br>
  </a>
  <p>%s</p>
</div>
"""


class WebAccess(Configurator):
    """
    Component for remote-access with a web browser.
    """

    ICON = theme.mb_logo
    TITLE = "Web Access"
    DESCRIPTION = "Access and remote-control MediaBox"


    def __init__(self):
    
        Configurator.__init__(self)
  
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        lbl = LabelItem("MediaBox WebAccess lets you access your media and " \
                        "remote-control MediaBox with a web browser.")
        self.__list.append_item(lbl)
        
        chbox = OptionItem("WebAccess is Off", "off",
                           "WebAccess is On", "on")

        chbox.select_by_value("off")
        chbox.connect_changed(self.__on_toggle_webaccess)
        self.__list.append_item(chbox)
      
        self.__lbl_info = LabelItem("")
        self.__list.append_item(self.__lbl_info)


    def __on_toggle_webaccess(self, value):
    
        ip = network.get_ip()
        if (value == "on"):
            self.call_service(msgs.HTTPSERVER_SVC_BIND,
                              self, ip, _PORT)
            self.__lbl_info.set_text("WebAccess-URL: http://%s:%d" % (ip, _PORT))
            self.__list.render()
        else:
            self.call_service(msgs.HTTPSERVER_SVC_UNBIND,
                              self, ip, _PORT)
            self.__lbl_info.set_text("")

        self.__list.invalidate()
        self.__list.render()
      
        
    def __on_child(self, f, request, name, contents):
    
        if (f):
            contents.append(f)
        else:
            self.__send_contents(request, name, contents)
            
            
    def __send_contents(self, request, name, contents):
    
        data = ""
        for f in contents:
            tn, is_final = self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, f)
            url = urlquote.quote(f.full_path, "")

            if (not f.mimetype.endswith("-folder")):
                url += "?action=play"
                target = "target='if'"
            else:
                target = ""
                
            data += _FILE % (url,
                             target,
                             urlquote.quote(tn, ""),
                             f.name)
        request.send_html(_LISTING % (name, data))
        
        
    def handle_HTTPSERVER_EV_REQUEST(self, owner, request):
                           
        if (owner != self): return

        path = urlquote.unquote(request.get_path()[1:])
        if (not path):
            path = "media:///"

        params = request.get_params()
        action = params.get("action", [""])[0]

        print "requesting", path, action

        f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
        if (f):
            if (f.mimetype.endswith("-folder")):
                f.get_contents(0, 0, self.__on_child, request, f.name, [])

            elif (action == "play"):
                print "loading"
                self.emit_message(msgs.MEDIA_ACT_LOAD, f)
                request.send_html("<html><body>OK</body></html>")
                    
            else:
                if (f.is_local):
                    request.send_file(open(f.get_resource(), "r"),
                                      f.name,
                                      f.mimetype)
                else:
                    request.send("HTTP/1.1 302 Redirect",
                                 {"LOCATION": f.get_resource()},
                                 "")
            #end if
            
        else:
            request.send_error("404 Not Found", _NOT_FOUND)

        #end if

