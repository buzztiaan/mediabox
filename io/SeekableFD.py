class SeekableFD(object):
    """
    Wrapper class for network FDs to allow seek operations.
    """
    
    def __init__(self, fd):
    
        self.__fd = fd
        self.__buffer = ""
        self.__pos = 0
        

    def __del__(self):
    
        if (self.__fd):
            self.close()
        
        
    def read(self, size = 1024):
    
        l = len(self.__buffer)
        if (self.__pos < l):
            amount = min(l - self.__pos, size)
            remaining_amount = size - amount
        else:
            amount = 0
            remaining_amount = size

        data = ""        
        if (amount):
            data += self.__buffer[self.__pos:self.__pos + amount]
            self.__pos += amount
            
        if (remaining_amount):
            d = self.__fd.read(remaining_amount)
            self.__pos += remaining_amount            
            self.__buffer += d
            data += d

        #print "BUFFER", len(self.__buffer)
        return data
        
        
        
    def seek(self, pos, whence = 0):
    
        # 'whence' is not supported
        
        if (pos < len(self.__buffer)):
            pass
        else:
            difference = pos - len(self.__buffer)
            self.read(difference)
            
        self.__pos = pos
        
        
    def tell(self):
    
        return self.__pos
        
        
    def close(self):
    
        self.__buffer = None
        self.__fd.close()
        self.__fd = None

