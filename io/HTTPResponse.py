"""
HTTP response object.
"""

from utils import network

_STATE_NEW = 0
_STATE_HEADERS_DONE = 1
_STATE_BODY_DONE = 2

_METHODS_WITHOUT_PAYLOAD = ["GET", "NOTIFY", "M-SEARCH", "SUBSCRIBE"]


class HTTPResponse(object):
    """
    Class for representing a HTTP response.
    This class implements the logic for detecting end of transmission and
    for decoding chunked transfers.    
    """

    def __init__(self):
        """
        Creates an empty HTTP response object waiting to be fed with data.
        """

        self.__state = _STATE_NEW
        self.__hdata = ""
        self.__headers = None

        self.__body = ""
        self.__body_length = 0
        
        self.__transfer_encoding = ""
        self.__content_length = 0
        
        self.__chunk_size_remaining = 0
        self.__incomplete_chunk_header = ""
        
        self.__finished = False
        
        #self.__read_pos = 0
        
        
    def get_status(self):
        """
        Returns the numeric HTTP status code.
        
        @return: numeric status code
        """
    
        return self.__status
        
        
    def _get_headers(self):
    
        return self.__headers
        
        
    def get_header(self, h):
        """
        Returns the value of the given header. Returns an empty string if the
        specified header does not exist.
        
        @param h: name of header
        @return: value of header
        """
    
        if (not self.__headers):
            return ""
        else:
            return self.__headers[h]
        
        
    def set_finished(self):
        """
        Marks this response as finished. This is used by the L{HTTPConnection}.
        """
    
        self.__finished = True
        
    
    def finished(self):
        """
        Returns whether this response is finished.
        
        @return: whether this response is finished
        """
    
        return self.__finished
        
    
    def feed(self, data):
        """
        Feeds this response with chunks of data. This is used by the
        L{HTTPConnection}.
        
        @param data: string of data
        """
        
        if (self.__state == _STATE_NEW):
            self.__hdata += data
            idx = self.__hdata.find("\r\n\r\n")
            if (idx != -1):
                self.__headers = network.HTTPHeaders(self.__hdata)
                
                self.__transfer_encoding = self.__headers["TRANSFER-ENCODING"].upper()
                self.__content_length = int(self.__headers["CONTENT-LENGTH"] or "-1")
                
                if (self.__transfer_encoding == "CHUNKED"):
                    self.__feed_chunked(self.__hdata[idx + 4:])
                else:
                    self.__body = self.__hdata[idx + 4:]
                    self.__body_length = len(self.__body)
                
                
                if (self.__headers.method in _METHODS_WITHOUT_PAYLOAD):
                    self.__finished = True
                    self.__state = _STATE_BODY_DONE
                else:
                    self.__state = _STATE_HEADERS_DONE
                
            else:
                # not finished reading headers yet
                pass
            
        elif (self.__state == _STATE_HEADERS_DONE):
            if (self.__transfer_encoding == "CHUNKED"):
                self.__feed_chunked(data)
            else:
                self.__body += data
                self.__body_length += len(data)

                if (self.__content_length >= 0 and
                      self.__body_length >= self.__content_length):
                    self.__finished = True
                
            if (self.__finished):
                self.__state = _STATE_BODY_DONE

        #end if


    def __feed_chunked(self, data):
    
        while (data):
            if (not self.__incomplete_chunk_header):
                # finish reading current chunk, if any
                size1 = min(len(data), self.__chunk_size_remaining)
                self.__chunk_size_remaining -= size1
                self.__body += data[:size1]
                self.__body_length += size1
                #print "CHUNK", data[:size1]
                data = data[size1:]
        
            else:
                data = self.__incomplete_chunk_header + data
                size1 = len(self.__incomplete_chunk_header)
                self.__incomplete_chunk_header = ""
        
            # read in next chunk size
            idx = data.find("\r\n", 1) #, size1)
            if (idx != -1):
                # size line is complete
                #print "CS", data[:idx]
                self.__chunk_size_remaining = \
                                            int(data[:idx], 16)
                data = data[idx + 2:]
            else:
                self.__incomplete_chunk_header = data
                break
                
            # the final chunk is always of size 0
            if (self.__chunk_size_remaining == 0):
                print "detected NULL chunk"
                self.__finished = True
                break
        #end while
       
       
    def get_amount(self):
        """
        Returns the currently downloaded amount and the content length.
        The content length may be C{-1} if the server did not send the
        C{Content-Length} header.

        @return: tuple C{(amount, content_length)}
        """
    
        return (self.__body_length, self.__content_length)
       
       
    def get_body(self):
        
        return self.read()
       
       
    def body_length(self):
        """
        Returns the length of the currently downloaded body.
        
        @return: body length
        """
    
        return self.__body_length
               
        
    def read(self):
        """
        Reads data from this response.
        
        @returns: string of data
        """
    
        data = self.__body#[self.__read_pos:]
        #self.__read_pos += len(data)
        self.__body = ""

        return data
        
        
    def close(self):
        """
        Closes this response.
        """
    
        pass

