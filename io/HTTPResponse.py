"""
HTTP response object.
"""

class HTTPResponse(object):
    """
    Class for representing a HTTP response.
    This class implements the logic for detecting end of transmission and
    for decoding chunked transfers.    
    """

    def __init__(self, status_header, headers):
        
        self.__status = int(status_header.split()[1])
        self.__headers = headers
        self.__body = ""
        self.__body_length = 0
        
        self.__transfer_encoding = headers.get("TRANSFER-ENCODING", "").upper()
        self.__content_length = int(headers.get("CONTENT-LENGTH", "-1"))
        
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
        
        
    def get_header(self, h):
        """
        Returns the value of the given header. Returns an empty string if the
        specified header does not exist.
        
        @param h: name of header
        @return: value of header
        """
    
        return self.__headers.get(h, "")
        
        
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

        if (self.__transfer_encoding == "CHUNKED"):
            self.__feed_chunked(data)
        
        else:
            self.__body += data
            self.__body_length += len(data)

            if (self.__content_length > 0):
                if (self.__body_length >= self.__content_length):
                    self.__finished = True
            elif (self.__content_length == 0):
                self.__finished = True

        #print len(data), self.__body_length
        #if (not data):
        #    self.__finished = True
        #print "FINISHED", self.__finished, self.__content_length, self.__body_length


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
        
        
    def getheaders(self):
        """
        Returns a dictionary of the HTTP response headers.
        
        @return: dictionary of headers
        """
    
        return self.__headers

