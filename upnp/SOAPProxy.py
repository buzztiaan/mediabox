from io import HTTPConnection, Downloader, parse_addr
from utils.MiniXML import MiniXML
from utils import logging

#import urllib
import httplib


_SOAP_ENVELOPE = """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
 s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <s:Body>%s</s:Body>
</s:Envelope>
""".strip()

_XMLNS_UPNP = "urn:schemas-upnp-org:service-1-0"
_XMLNS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"


class SOAPError(StandardError): pass



class SOAPProxy(object):
    """
    Lightweight SOAP proxy for UPnP stuff.
    """

    def __init__(self, endpoint, namespace, scpdurl):
    
        self.__endpoint = endpoint
        self.__namespace = namespace
        self.__signatures = {}
        
        # callback for async IO
        self.__async_callback = None
        
        self.__parse_scpd(scpdurl)


    def set_async_cb(self, cb):
        """
        Sets a callback to be used for asynchronous IO. Set to None to disable
        asynchronous IO. Asynchronous IO is disabled by default.
        """
    
        self.__async_callback = cb


    def __getattr__(self, name):
    
        def f(cb, *args):
            out = ""
            out += "<u:%s xmlns:u=\"%s\">" % (name, self.__namespace)
            soap_args, soap_out = self.__signatures[name]
            cnt = 0
            for a in soap_args:
                out += "<%s>%s</%s>" % (a, args[cnt], a)
                cnt += 1
            #end for
            out += "</u:%s>" % name

            data = _SOAP_ENVELOPE % out
            logging.debug("=== SOAP Request ===\n%s\n===" % data)

            if (cb):
                self.__post_soap_async(name, data, cb)
                return None
            else:
                return self.__post_soap(name, data)
        
        return f
        
        
    def __parse_scpd(self, scpdurl):
    
        def on_download(data, s, t, xml):
            xml[0] += data
        
        xml = [""]
        dl = Downloader(scpdurl, on_download, xml)
        dl.wait_until_closed()

        scpd = MiniXML(xml[0], _XMLNS_UPNP).get_dom()
        for c in scpd.get_children():
            name = c.get_name()
            if (name == "{%s}specVersion" % _XMLNS_UPNP):
                pass
            elif (name == "{%s}actionList" % _XMLNS_UPNP):
                for action in c.get_children():
                    self.__parse_action(action)
            elif (name == "{%s}serviceStateTable" % _XMLNS_UPNP):
                pass
        #end for


    def __parse_action(self, node):
    
        action_name = ""
        action_args = []
        action_out = []
        
        action_name = node.get_pcdata("{%s}name" % _XMLNS_UPNP)
        arglist = node.get_child("{%s}argumentList" % _XMLNS_UPNP)        
        for arg in arglist.get_children():
            arg_name, arg_type = self.__parse_argument(arg)
            if (arg_type == "in"):
                action_args.append(arg_name)
            elif (arg_type == "out"):
                action_out.append(arg_name)
        #end for
        
        logging.debug("SOAPAction: %s(%s): %s" \
                      % (action_name, ", ".join(action_args),
                         ", ".join(action_out)))
        self.__signatures[action_name] = (action_args, action_out)
                

    def __parse_argument(self, node):    
    
        arg_name = node.get_pcdata("{%s}name" % _XMLNS_UPNP)
        direction = node.get_pcdata("{%s}direction" % _XMLNS_UPNP)

        return (arg_name, direction)

           
    def __parse_soap_response(self, body, name):

        out = []    
        logging.debug("=== SOAP Response ===\n%s\n===" % body)
        
        envelope = MiniXML(body).get_dom()
        resp = envelope.get_child().get_child()
        if (resp.get_name() == "{%s}Fault" % _XMLNS_SOAP):
            faultcode = resp.get_pcdata("faultcode")
            faultstring = resp.get_pcdata("faultstring")
            detail = resp.get_child("detail")
            raise SOAPError((faultcode, faultstring, str(detail)))
                
        else:
            soap_args, soap_out = self.__signatures[name]
            for o in soap_out:
                out.append(resp.get_pcdata(o))
        #end if

        return out
        

    def __post_soap(self, name, soap):
    
        length = len(soap)
        soap_action = "\"" + self.__namespace + "#" + name + "\""

        host, port, path = parse_addr(self.__endpoint)
        
        
        if (port):
            conn = httplib.HTTPConnection(host, port)
        else:
            conn = httplib.HTTPConnection(host)

        conn.putrequest("POST", path)
        conn.putheader("Host", port and "%s:%d" % (host, port) or host)
        conn.putheader("User-Agent", "MediaBox")
        conn.putheader("Content-Type", "text/xml; charset=\"utf-8\"")
        conn.putheader("Content-Length", `length`)
        conn.putheader("SOAPAction", soap_action)
        conn.endheaders()

        conn.send(soap)

        response = conn.getresponse()
        values = self.__parse_soap_response(response.read(), name)
        
        return values


    def __post_soap_async(self, name, soap, async_cb):
    
        def on_soap_response(resp):
            if (resp and resp.finished()):
                values = self.__parse_soap_response(resp.read(), name)
                try:
                    async_cb(*values)
                except:
                    import traceback; traceback.print_exc()
            #end if
    
        length = len(soap)
        soap_action = "\"" + self.__namespace + "#" + name + "\""

        host, port, path = parse_addr(self.__endpoint)
        conn = HTTPConnection(host, port)
        conn.putrequest("POST", path)
        conn.putheader("Host", port and "%s:%d" % (host, port) or host)
        conn.putheader("User-Agent", "MediaBox")
        conn.putheader("Content-Type", "text/xml; charset=\"utf-8\"")
        conn.putheader("Content-Length", `length`)
        conn.putheader("SOAPAction", soap_action)
        conn.endheaders()

        conn.send(soap, on_soap_response)

                


#p = SOAPProxy("http://192.168.0.102:49152/web/cds_control",
#              "urn:schemas-upnp-org:service:ContentDirectory:1", 
#              "http://192.168.0.102:49152/web/cds.xml")
#print p.Browse("0", "BrowseDirectChildren", "*", "0", "0", "")
