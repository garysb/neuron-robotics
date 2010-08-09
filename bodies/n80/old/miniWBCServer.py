import bluetooth

class ServerWB:
    
    def __init__(self):
        
        self._sockfd = None
        self._clifd = None
        
        self._BUFF_READ = 600
        self._NUMBER_PEOPLE = 1
        self._LOCAL_ADDR = ''
        self._PORT_NUMBER = 1
    
    def getBufferLen(self):
        
        return self._BUFF_READ
    
    def openSocket(self):
        
        try:
            
            self._sockfd = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            
        except:
            
            raise
    
    def closeSocket(self, opz):
        
        try:
            
            if opz == 0:
                
                self._sockfd.close()
                
            elif opz == 1:
                
                self._clifd[0].close()
        
        except:
            
            raise
    
    def bindSocket(self):
        
        try:
            
            self._sockfd.bind((self._LOCAL_ADDR, self._PORT_NUMBER))
            
        except:
            
            raise
    
    def listenSocket(self):
        
        try:
            
            self._sockfd.listen(self._NUMBER_PEOPLE)
            
        except:
            
            raise
    
    def acceptSocket(self):
        
        try:
            
            self._clifd = self._sockfd.accept()
            
            return self._clifd
            
        except:
            
            raise