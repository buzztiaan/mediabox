"""
Async HTTP connection arround gobject loop, developed for MediaBox
(c) 2008 Hugo Baldasano  <hugo.calleja@gmail.com>

This package is licensed under the terms of the GNU LGPL.
"""


import gobject
import socket
import urlparse


class GAsyncHTTPConnection (object):

    """
    data has to be finished with a blank line, meaning that it should be finished like this: data = "The message we want to send, ..., end of the message\r\n\r\n"
    return_callback has to be like this return_callback (success, connection, response, *args)
    """

    def __init__ (self, address, data, return_callback, *args):  #TODO improve the class with functions post_request, post_headers, etc...
    
        self.__return_callback = return_callback
        self.__return_arguments = args
        
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect ( address )
        except:
            gobject.idle_add ( self.__execute_callback, False, None )
            return

        self.__working_callback_id = gobject.io_add_watch ( self.__socket, gobject.IO_OUT, self.__send_data, data, len(data) )
        self.__timeout_callback_id = gobject.timeout_add (10000, self.__timeout)
        

    def __del__(self):
    
        if ( self.__working_callback_id > 0 ):  gobject.source_remove (self.__timeout_callback_id)
        if ( self.__timeout_callback_id > 0 ):  gobject.source_remove (self.__working_callback_id)
        self.__socket.close()


    def __timeout (self):

        gobject.source_remove (self.__working_callback_id)
        self.__socket.close()
        print 'DEBUG: HTTP connection TIMEOUT'
        self.__return_callback (False, self, None, self.__return_arguments)
        return (False)


    def __send_data (self, socket, condition, data, remaining_length):

        length_sent = socket.send (data)
        
        gobject.source_remove (self.__timeout_callback_id)

        remaining_length -= length_sent    

        if ( remaining_length <= 0 ):  #all data sent, listen for response
            response = ""
            self.__working_callback_id = gobject.io_add_watch ( socket, gobject.IO_IN, self.__recieve_respond, response )
            self.__timeout_callback_id = gobject.timeout_add (10000, self.__timeout)
        else :
            self.__working_callback_id = gobject.io_add_watch ( socket, gobject.IO_OUT, self.__send_data, data[length_sent:], remaining_length )
            self.__timeout_callback_id = gobject.timeout_add (10000, self.__timeout)
        
        return (False)


    def __recieve_respond (self, socket, condition, response):

        readed = socket.recv (4096)

        gobject.source_remove (self.__timeout_callback_id)

        response += readed

        index = response.find('\r\n\r\n')
        if ( index == -1 ) :    #the headers are not yet complete
            self.__timeout_callback_id = gobject.timeout_add (10000, self.__timeout)
            self.__working_callback_id = gobject.io_add_watch ( socket, gobject.IO_IN, self.__recieve_respond, response )
            return (False)

        lines = response[:index+2].splitlines()
        status_header = lines[0].upper()

        headers = {}
        for l in lines[1:]:
            idx = l.find(":")
            if not ( idx == -1 ):
                key = l[:idx].strip().upper()
                value = l[idx + 1:].strip()
                headers[key] = value
        #end for

        if ( "CONTENT-LENGTH" in headers ) :
            body_length = int(headers["CONTENT-LENGTH"])
            
            body = response[index+4:]

            if ( len(body) < body_length ):  #More body to be recieved
                self.__working_callback_id = gobject.io_add_watch(socket, gobject.IO_IN, self.__recieve_more_body, body, body_length, status_header, headers)
                self.__timeout_callback_id = gobject.timeout_add (10000, self.__timeout)
                return (False)

        else :
            body = None 

        self.__timeout_callback_id = 0
        self.__working_callback_id = 0

        responseclass = AsyncHTTPResponse ( status_header, headers, body )
        self.__return_callback (True, self, responseclass, *self.__return_arguments)
        #gobject.idle_add ( self.__execute_callback, True, response ) ????

        return (False)


    def __recieve_more_body (self, socket, condition, body, body_length, status_header, headers):

        readed = socket.recv (4096)

        gobject.source_remove (self.__timeout_callback_id)
        
        body += readed

        if ( len(body) < body_length ):  #More body to be recieved
            #self.__working_callback_id = gobject.io_add_watch(socket, gobject.IO_IN, self.__recieve_more_body, body, body_length, status_header, headers)
            self.__timeout_callback_id = gobject.timeout_add (10000, self.__timeout)
            return (True)  #The callback will be triggered again

        self.__timeout_callback_id = 0
        self.__working_callback_id = 0

        responseclass = AsyncHTTPResponse ( status_header, headers, body )
        self.__return_callback (True, self, responseclass, *self.__return_arguments)
        return (False)


    def __execute_callback (self, success, response) :

        self.__return_callback (success, self, response, *self.__return_arguments)
        return(False)



class AsyncHTTPResponse (object):

    def __init__(self, status_header, headers, body):

        self.body = body
        self.__status_header = status_header
        self.__headers = headers


    def get_body(self):
    
        return self.body


    def get_status (self):

        return (self.__status_header)
        #TODO parse status_header


    def get_headers (self):
        return ( self.__headers )


    def get_header (self, header_name):

        if header_name in self.__headers :
            return self.__headers[header_name]
        else :
            return None


#Utility function
def parse_addr (addr):
        
    urlparts = urlparse.urlparse(addr)
    if (":" in urlparts[1]):
        host, port = urlparts[1].split(":")
        port = int(port)
    else:
        host = urlparts[1]
        port = 0
    path = urlparts[2]

    return host, port, path


