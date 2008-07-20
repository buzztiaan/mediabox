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
    
        return self.__status
        
        
    def get_header(self, h):
    
        return self.__headers.get(h, "")
        
        
    def set_finished(self):
    
        self.__finished = True
        
    
    def finished(self):
    
        return self.__finished
        
    
    def feed(self, data):
               
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
        print "FINISHED", self.__finished


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
                self.__finished = True
                break
        #end while
       
       
    def get_amount(self):
    
        return (self.__body_length, self.__content_length)
       
       
    def body_length(self):
    
        return self.__body_length
               
        
    def read(self):
    
        data = self.__body#[self.__read_pos:]
        #self.__read_pos += len(data)
        self.__body = ""

        return data
        
        
    def close(self):
    
        pass
        
        
    def getheaders(self):
    
        return self.__headers
