from MiniXML import MiniXML
from utils import logging

import urllib
import urlparse
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
        
        self.__parse_scpd(scpdurl)


    def __getattr__(self, name):
    
        def f(*args):
            out = ""
            out += "<u:%s xmlns:u=\"%s\">" % (name, self.__namespace)
            soap_args = self.__signatures[name]
            cnt = 0
            for a in soap_args:
                out += "<%s>%s</%s>" % (a, args[cnt], a)
                cnt += 1
            #end for
            out += "</u:%s>" % name
            
            logging.debug("=== SOAP Request ===\n%s\n===" % (_SOAP_ENVELOPE % out))
            return self.__post_soap(name, _SOAP_ENVELOPE % out)
        
        return f
        
        
    def __parse_scpd(self, scpdurl):
    
        #print "SCPD", scpdurl
        xml = urllib.urlopen(scpdurl).read()
        scpd = MiniXML(xml, _XMLNS_UPNP).get_dom()
        
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
        
        action_name = node.get_pcdata("{%s}name" % _XMLNS_UPNP)
        arglist = node.get_child("{%s}argumentList" % _XMLNS_UPNP)        
        for arg in arglist.get_children():
            arg_name = self.__parse_argument(arg)
            if (arg_name): action_args.append(arg_name)
        #end for
        
        self.__signatures[action_name] = action_args
                

    def __parse_argument(self, node):    
    
        arg_name = node.get_pcdata("{%s}name" % _XMLNS_UPNP)
        direction = node.get_pcdata("{%s}direction" % _XMLNS_UPNP)

        if (direction == "in"):
            return arg_name
        else:
            return ""

            
    def __parse_soap_response(self, response):
    
        out = []
    
        headers = response.getheaders()
        body = response.read()
        logging.debug("=== SOAP Response ===\n%s\n===" % body)
        
        envelope = MiniXML(body).get_dom()
        resp = envelope.get_child().get_child()
        if (resp.get_name() == "{%s}Fault" % _XMLNS_SOAP):
            faultcode = resp.get_pcdata("faultcode")
            faultstring = resp.get_pcdata("faultstring")
            detail = resp.get_child("detail")
            raise SOAPError((faultcode, faultstring, str(detail)))
                
        else:
            for entry in resp.get_children():
                out.append(entry.get_child().get_value())
        #end if
            
        return out
        




        
        
    def __post_soap(self, name, soap):
    
        length = len(soap)
        soap_action = "\"" + self.__namespace + "#" + name + "\""
        
        urlparts = urlparse.urlparse(self.__endpoint)
        if (":" in urlparts[1]):
            host, port = urlparts[1].split(":")
            port = int(port)
        else:
            host = urlparts[1]
            port = 0
        path = urlparts[2]
        
        if (port):
            conn = httplib.HTTPConnection(host, port)
        else:
            conn = httplib.HTTPConnection(host)

        conn.putrequest("POST", path)
        conn.putheader("User-Agent", "MediaBox")
        conn.putheader("Content-Type", "text/xml; charset=\"utf-8\"")
        conn.putheader("Content-Length", `length`)
        conn.putheader("SOAPAction", soap_action)
        conn.endheaders()

        conn.send(soap)

        response = conn.getresponse()
        values = self.__parse_soap_response(response)
        
        return values



#p = SOAPProxy("http://192.168.0.102:49152/web/cds_control",
#              "urn:schemas-upnp-org:service:ContentDirectory:1", 
#              "http://192.168.0.102:49152/web/cds.xml")
#print p.Browse("0", "BrowseDirectChildren", "*", "0", "0", "")
