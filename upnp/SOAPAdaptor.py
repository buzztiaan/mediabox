"""
Base class for SOAP adaptors.
"""


from utils.MiniXML import MiniXML
from upnp import errors


_XMLNS_UPNP = "urn:schemas-upnp-org:service-1-0"
_XMLNS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"

_SOAP_ENVELOPE = """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
 s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <s:Body>%s</s:Body>
</s:Envelope>
""".strip()

_SOAP_FAULT = """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
 s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <s:Body>
  <s:Fault>
   <faultcode>s:Client</faultcode>
    <faulstring>UPnPError</faultstring>
    <detail>
     <UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
      <errorCode>%d</errorCode>
      <errorDescription>%s</errorDescription>
     </UPnPError>
    </detail>
  </s:Fault>
 </s:Body>
</s:Envelope>
""".strip()


class SOAPAdaptor(object):

    def __init__(self, namespace, scpd_xml):
    
        self.__signatures = {}
        self.__namespace = namespace
        
        self.__parse_scpd(scpd_xml)
        
        
    def feed_soap(self, xml):
        """
        Feeds the adaptor with a SOAP request.
        """

        envelope = MiniXML(xml).get_dom()
        body = envelope.get_child()
        method = body.get_child()
        method_name = method.get_name()
        
        # strip off namespace
        idx = method_name.find("}")
        if (idx != -1):
            method_name = method_name[idx + 1:]

        args = {}
        for c in method.get_children():
            arg_name = c.get_name()
            arg_value = c.get_pcdata()

            # strip off namespace
            idx = arg_name.find("}")
            if (idx != -1):
                arg_name = arg_name[idx + 1:]

            args[arg_name] = arg_value
        #end for
        
        if (hasattr(self, method_name)):
            handler = getattr(self, method_name)
            try:
                values = handler(**args)
            except errors.UPnPError as e:
                return (False, self.__make_fault(e.get_error()))
            except:
                return (False, self.__make_fault(errors.ACTION_FAILED))
            else:
                return (True, self.__make_soap(method_name, values))
                
        else:
            return (False, self.__make_fault(errors.INVALID_ACTION))
        #end if


    def __make_soap(self, name, values):
    
        out = ""
        out += "<u:%sResponse xmlns:u=\"%s\">" % (name, self.__namespace)
        soap_args, soap_out = self.__signatures[name]
        cnt = 0
        for a in soap_out:
            out += "<%s>%s</%s>" % (a, values[cnt], a)
            cnt += 1
        #end for
        out += "</u:%sResponse>" % name

        return _SOAP_ENVELOPE % out
        
        
    def __make_fault(self, fault):
    
        print "handling fault", fault
        return _SOAP_FAULT % fault


    def __parse_scpd(self, xml):
            
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
        
        #logging.debug("SOAPAction: %s(%s): %s" \
        #              % (action_name, ", ".join(action_args),
        #                 ", ".join(action_out)))
        self.__signatures[action_name] = (action_args, action_out)
                

    def __parse_argument(self, node):    
    
        arg_name = node.get_pcdata("{%s}name" % _XMLNS_UPNP)
        direction = node.get_pcdata("{%s}direction" % _XMLNS_UPNP)

        return (arg_name, direction)

