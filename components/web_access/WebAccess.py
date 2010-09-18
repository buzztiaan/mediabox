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
    font-family: Arial, Helvetica, Sans;
  }
  
  p {
    font-size: 10pt;
    color: #fff;
  }
  
  img {
    border: none;
  }
  
  div.navbar {
    position: fixed;
    top: 0px;
    left: 0px;
    min-width: 100%%;
    max-width: 100%%;
    min-height: 64px;
    max-height: 64px;
    background-color: #000;
    font-size: 12pt;
    color: #fff;
  }
</style>
<body>
<iframe style="display: none;" name="if"></iframe>
<div style="margin-top: 64px;">
  %s
</div>
<div class="navbar">
  <a href="/?clientid=%s&action=nav-shelf">[Shelf]</a>&nbsp;&nbsp;&nbsp;
  <a href="/?clientid=%s&action=nav-up">[Up]</a>&nbsp;&nbsp;&nbsp;
  <a href="/?clientid=%s&action=volume-down" target="if">[-]</a>&nbsp;&nbsp;&nbsp;
  <a href="/?clientid=%s&action=volume-up" target="if">[+]</a>&nbsp;&nbsp;&nbsp;
  <a href="/?clientid=%s&action=media-previous" target="if">[|&lt;]</a>&nbsp;&nbsp;&nbsp;
  <a href="/?clientid=%s&action=media-pause" target="if">[||]</a>&nbsp;&nbsp;&nbsp;
  <a href="/?clientid=%s&action=media-next" target="if">[&gt;|]</a>&nbsp;&nbsp;&nbsp;
  <a href="/?clientid=%s&action=ui-fullscreen" target="if">[Fullscreen]</a>&nbsp;&nbsp;&nbsp;
  %s
</div>
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


    __client_cnt = 0
    

    def __init__(self):
    
        # table: clientid -> path_stack
        self.__path_stacks = {}
    
        self.__current_file = None
        self.__artist = ""
        self.__title = ""
    
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
            error = self.call_service(msgs.HTTPSERVER_SVC_BIND,
                                      self, ip, _PORT)
            if (error):
                self.__lbl_info.set_text("Error: %s" % error)
            else:
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
            
            
    def __send_contents(self, request, clientid, name, contents):
    
        data = ""
        for f in contents:
            url = urlquote.quote(f.full_path, "")
            url += "?clientid=%s" % clientid

            if (not f.mimetype.endswith("-folder")):
                url += "&action=play"
                target = "target='if'"
            else:
                target = ""

            # look up thumbnail
            if (not f.icon):
                tn, is_final = self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, f)
            else:
                tn = f.icon
            
            # build item
            data += _FILE % (url,
                             target,
                             urlquote.quote(tn, "") + 
                             "?clientid=%s&action=load" % clientid,
                             f.name)
                             
        #end for
        
        if (self.__title):
            title = self.__title
            if (self.__artist):
                title += " / " + self.__artist
        elif (self.__current_file):
            title = self.__current_file.name + "   " + \
                    self.__current_file.info
        else:
            title = ""
        request.send_html(_LISTING % (name, data,
                                      clientid, clientid,
                                      clientid, clientid,
                                      clientid, clientid,
                                      clientid, clientid,
                                      title))
        
        
        
    def handle_HTTPSERVER_EV_REQUEST(self, owner, request):
                            
        def on_child(f, name, contents):
            if (f):
                contents.append(f)
            else:
                self.__send_contents(request, clientid, name, contents)
                           
        if (owner != self): return

        path = urlquote.unquote(request.get_path()[1:])
        if (not path):
            path = "media:///"

        # get parameters
        params = request.get_params()
        action = params.get("action", ["open"])[0]
        clientid = params.get("clientid", [""])[0]
        if (not clientid):
            clientid = str(self.__client_cnt)
            self.__client_cnt += 1

        # prepare path stack for client
        if (not clientid in self.__path_stacks):
            self.__path_stacks[clientid] = []
        path_stack = self.__path_stacks[clientid]


        print "requesting", clientid, path, action

        if (action == "volume-down"):
            self.emit_message(msgs.INPUT_EV_VOLUME_DOWN, True)
            request.send_html("<html><body>OK</body></html>")

        elif (action == "volume-up"):
            self.emit_message(msgs.INPUT_EV_VOLUME_UP, True)
            request.send_html("<html><body>OK</body></html>")

        elif (action == "media-previous"):
            self.emit_message(msgs.MEDIA_ACT_PREVIOUS)
            request.send_html("<html><body>OK</body></html>")

        elif (action == "media-next"):
            self.emit_message(msgs.MEDIA_ACT_NEXT)
            request.send_html("<html><body>OK</body></html>")

        elif (action == "media-pause"):
            self.emit_message(msgs.MEDIA_ACT_PAUSE)
            request.send_html("<html><body>OK</body></html>")

        elif (action == "ui-fullscreen"):
            self.emit_message(msgs.INPUT_EV_FULLSCREEN, True)
            request.send_html("<html><body>OK</body></html>")

        elif (action == "nav-up"):
            if (len(path_stack) > 1):
                path_stack.pop()
                f = path_stack.pop()
            else:
                f = self.call_service(msgs.CORE_SVC_GET_FILE, "media:///")
                path_stack[:] = []

            path_stack.append(f)
            f.get_contents(0, 0, on_child, f.name, [])
              
        elif (action == "nav-shelf"):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, "media:///")
            path_stack[:] = [f]
            f.get_contents(0, 0, on_child, f.name, [])

        elif (action == "open"):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f):
                path_stack.append(f)
                f.get_contents(0, 0, on_child, f.name, [])
            else:
                request.send_error("404 Not Found", _NOT_FOUND)
            
        elif (action == "play"):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f):
                print "loading"
                self.emit_message(msgs.MEDIA_ACT_LOAD, f)
                request.send_html("<html><body>OK</body></html>")
                
            else:
                request.send_error("404 Not Found", _NOT_FOUND)
        
        else:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f and f.is_local):
                request.send_file(open(f.get_resource(), "r"),
                                  f.name,
                                  f.mimetype)
            
            elif (f and not f.is_local):
                request.send_redirect(f.get_resource())
                
            else:
                request.send_error("404 Not Found", _NOT_FOUND)
            
        #end if


    def handle_MEDIA_EV_LOADED(self, player, f):
    
        self.__current_file = f
        self.__artist = ""
        self.__title = ""


    def handle_MEDIA_EV_TAG(self, tag, value):
    
        if (tag == "ARTIST"):
            self.__artist = value
        elif (tag == "TITLE"):
            self.__title = value

