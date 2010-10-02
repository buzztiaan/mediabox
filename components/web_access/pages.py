from utils import urlquote
from theme import theme



def render_json_contents(clientid, contents):

    return render_listing_items(clientid, contents)


def render_page_browser(clientid):
    
    return "<html>" \
           "<head>" \
             + render_style() \
             + render_js(clientid) + \
           "</head>" \
           "<body onload='goHome(\"" + clientid + "\");'>" \
           "<div id='contents'></div>" \
           + render_navbar(clientid, "now_playing") + \
           "</body>" \
           "</html>"


def render_style():

    return "<style>" \
           "body {" \
           "  background-color: " + str(theme.color_mb_background) + ";" \
           "  font-family: Arial, Helvetica, Sans;" \
           "  color: " + str(theme.color_mb_text) + ";" \
           "}" \
           "p {" \
           "  font-size: 10pt;" \
           "}" \
           "img {" \
           "  border: none;" \
           "}" \
           "div.item {" \
           "  float: left;" \
           "  width: 180px;" \
           "  height: 200px;" \
           "  text-align: center;" \
           "}" \
           "img.item {" \
           "  width: 160px;" \
           "  height: 160px;" \
           "}" \
           "#navbar {" \
           "  position: fixed;" \
           "  top: 0px;" \
           "  left: 0px;" \
           "  min-width: 100%;" \
           "  max-width: 100%;" \
           "  min-height: 64px;" \
           "  max-height: 64px;" \
           "  background-color: #333;" \
           "  font-size: 16pt;" \
           "}" \
           "#contents {" \
           "  margin-top: 70px;" \
           "}" \
           "</style>"


def render_js(clientid):

    return """
    <script type="text/javascript">
    function createHTTPRequest()
    {
      return window.XMLHttpRequest ? new XMLHttpRequest()
                                   : new ActiveXObject('MSXML2.XMLHTTP');
    }
    
    function sendRequest(url, body, cb)
    {
      req.open((body == null) ? "GET" : "POST",
               url, true);
      if (cb != null)
      {
        req.onreadystatechange = cb;
      }
      else
      {
        req.onreadystatechange = null_cb;
      }
      req.send(body);
    }
    
    function null_cb()
    {
      //alert(req.readyState);
    }
    
    function makeItem(icon, caption, path, mimetype)
    {
      var item = document.createElement("div");
      item.setAttribute("class", "item");
            
      var img = document.createElement("img");
      img.setAttribute("class", "item");
      img.setAttribute("src", icon);
      
      if (mimetype.endsWith("-folder"))
      {
        img.setAttribute("onclick", "loadFolder('" + path + "')");
      }
      else
      {
        img.setAttribute("onclick", "loadFile('" + path + "')");
      }
      
      var p = document.createElement("p");
      p.innerHTML = caption;
      
      item.appendChild(img);
      item.appendChild(p);
      
      return item;
    }
    
    function onLoadFolder()
    {
      if (req.readyState != 4 || req.status != 200) return;
      
      contents = document.getElementById("contents");
      contents.innerHTML = "";

      // TODO: use safe JSON lib
      var items = eval(req.responseText);
      for (var i = 0; i < items.length; i++)
      {
        var item = items[i];
        e = makeItem(item[0], item[1], item[2], item[3]);
        contents.appendChild(e);
      }
    }
    
    function goHome()
    {
      loadFolder("media:///")
    }
    
    function goUp()
    {
      sendRequest("/nav-up?clientid=" + clientid,
                  null,
                  onLoadFolder);
    }
    
    function loadFolder(folder)
    {
      sendRequest("/open?clientid=" + clientid + "&path=" + folder,
                  null,
                  onLoadFolder);
    }
    
    function loadFile(path)
    {
      document.location.href = "/file?clientid=" + clientid + "&path=" + path;
    }
    
    String.prototype.startsWith = function(str) {return (this.match("^"+str)==str)}
    String.prototype.endsWith = function(str) {return (this.match(str+"$")==str)}
    
    var req = createHTTPRequest();
    var clientid = "%s";
    
    </script>
    """ % clientid


def render_title(folder):

    return "<title>" + folder.name + " - MediaBox WebAccess</title>"


def render_navbar(clientid, now_playing):

    return "<div id='navbar'>" \
           + render_navbutton(clientid, "goUp();", "mb_btn_dir_up_1") \
           + render_navbutton(clientid, "goHome();", "mb_btn_home_1") + \
           "&nbsp;&nbsp;&nbsp;" \
           + render_navbutton(clientid, "media-previous", "mb_btn_previous_1") \
           + render_navbutton(clientid, "media-pause", "mb_btn_pause_1") \
           + render_navbutton(clientid, "media-next", "mb_btn_next_1") \
           + now_playing + \
           "</div>"
    
def render_navbutton(clientid, action, icon):

    if (action.startswith("nav")):
        target = ""
    else:
        target = "target='if'"

    icon = urlquote.quote(icon)
    return """
           <img src="/theme?path=%s" align="middle" onclick="%s">
           """ % (icon, action)

    """
    return "<a href='/?clientid=%s&action=%s' %s>" \
           "<img src='/theme.%s?clientid=%s&action=load' align='middle'>" \
           "</a>" \
           % (clientid,
              action,
              target,
              icon,
              clientid)
    """
    

def render_listing_items(clientid, contents):

    out = "["
    for f, icon in contents:
        out += render_item(clientid, f, icon)
    out += "]"

    return out


def render_item(clientid, f, icon):

    icon = "/file?path=%s" % urlquote.quote(icon, "")
    name = urlquote.quote(f.name)
    link = urlquote.quote(f.full_path, "")

    return "[ '%s', '%s', '%s', '%s' ]," \
           % (icon,
              name,
              link,
              f.mimetype)

