from com import Configurator, msgs
import pages
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import OptionItem
from utils import mimetypes
from utils import network
from utils import urlquote
from theme import theme


_PORT = 18056


class WebAccess(Configurator):
    """
    Component for remote-access with a web browser.
    
    The web server accepts:
    
     - MediaBox media paths (e.g. media:///) in URL-safe form
     - theme graphics paths (e.g. theme.mb_btn_dir_up_1)
     
    The parameter 'clientid' is supplied to associate the client with a path
    history in the navigator. Stateless requests may omit this parameter.
    
    The parameter 'action' specifies how the server should react on a certain
    path:
    
     - open:            opens a directory (this is the default action)
     - load:            transfers the file's contents to the client
     - play:            plays media in MediaBox
     - nav-up:          moves to the parent folder
     - nav-shelf:       moves to the shelf
     - media-pause:     play/pause action on MediaBox
     - media-previous:  goes to the previous track
     - media-next:      goes to the next track
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

        lbl = LabelItem("This is still an experimental feature and not " \
                        "fully working yet!")
        self.__list.append_item(lbl)
        
        chbox = OptionItem("WebAccess is Off", "off",
                           "WebAccess is On", "on")
        chbox.select_by_value("off")
        chbox.connect_changed(self.__on_toggle_webaccess)
        self.__list.append_item(chbox)
      
        self.__lbl_info = LabelItem("")
        self.__list.append_item(self.__lbl_info)


    def __on_toggle_webaccess(self, value):
        """
        Reacts on toggling the WebAccess in the configurator.
        """
    
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
            
            
    def __send_contents(self, request, clientid, folder, contents):
        """
        Sends the list of contents to the client.
        """

        if (self.__title):
            now_playing = self.__title
            if (self.__artist):
                now_playing += " / " + self.__artist
        elif (self.__current_file):
            now_playing = self.__current_file.name + "   " + \
                          self.__current_file.info
        else:
            now_playing = ""
    
        html = pages.render_json_contents(clientid, contents)
        request.send_html(html)
        
        
    def handle_HTTPSERVER_EV_REQUEST(self, owner, request):
                            
        def on_child(f, folder, contents):
            if (f):
                # look up thumbnail
                if (not f.icon):
                    icon, is_final = self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, f)
                else:
                    icon = f.icon
                contents.append((f, icon))
            else:
                self.__send_contents(request, clientid, folder, contents)

            return True
                           
        if (owner != self): return

        path = urlquote.unquote(request.get_path())
        #if (not path):
        #    path = "media:///"

        if (path.startswith("theme.")):
            path = getattr(theme, path[6:]).get_path()

        # get parameters
        params = request.get_query()
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

        if (path == "/"):
            request.send_html(pages.render_page_browser(clientid))

        elif (path == "/nav-home"):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, "media:///")
            path_stack[:] = [f]
            f.get_contents(0, 0, on_child, f, [])

        elif (path == "/nav-up"):
            if (len(path_stack) > 1):
                path_stack.pop()
                f = path_stack.pop()
            else:
                f = self.call_service(msgs.CORE_SVC_GET_FILE, "media:///")
                path_stack[:] = []

            path_stack.append(f)
            f.get_contents(0, 0, on_child, f, [])


        elif (path == "/open"):
            filepath = urlquote.unquote(params["path"][0])
            f = self.call_service(msgs.CORE_SVC_GET_FILE, filepath)
            
            if (f and f.mimetype.endswith("-folder")):
                path_stack.append(f)
                f.get_contents(0, 0, on_child, f, [])

            elif (f):
                parent = path_stack[-1]
                self.emit_message(msgs.MEDIA_ACT_LOAD, f)
                self.emit_message(msgs.MEDIA_ACT_CHANGE_PLAY_FOLDER, parent)
                request.send_html("<html><body>OK</body></html>")

            else:
                request.send_not_found("MediaBox WebAccess", filepath)
                        

        elif (path == "/file"):
            filepath = urlquote.unquote(params["path"][0])
            f = self.call_service(msgs.CORE_SVC_GET_FILE, filepath)
            print "FILE", f, f.is_local
            if (f and f.is_local):
                request.send_file(open(f.get_resource(), "r"),
                                  f.name,
                                  f.mimetype)

        elif (path == "/theme"):
            filepath = urlquote.unquote(params["path"][0])
            pbuf = getattr(theme, filepath)
            request.send_file(open(pbuf.get_path(), "r"),
                              filepath,
                              "image/x-png")            


        elif (action == "volume-down"):
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
            f.get_contents(0, 0, on_child, f, [])
              
        elif (action == "nav-shelf"):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, "media:///")
            path_stack[:] = [f]
            f.get_contents(0, 0, on_child, f, [])

        elif (action == "open"):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f):
                path_stack.append(f)
                print "opening", f.name
                f.get_contents(0, 0, on_child, f, [])
            else:
                request.send_not_found("MediaBox WebAccess", path)
            
        elif (action == "play"):
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f):
                print "loading"
                parent = path_stack[-1]
                self.emit_message(msgs.MEDIA_ACT_LOAD, f)
                self.emit_message(msgs.MEDIA_ACT_CHANGE_PLAY_FOLDER, parent)
                request.send_html("<html><body>OK</body></html>")
                
            else:
                request.send_not_found("MediaBox WebAccess", path)
        
        else:
            f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
            if (f and f.is_local):
                request.send_file(open(f.get_resource(), "r"),
                                  f.name,
                                  f.mimetype)
            
            elif (f and not f.is_local):
                request.send_redirect(f.get_resource())
                
            else:
                request.send_not_found("MediaBox WebAccess", path)
            
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

