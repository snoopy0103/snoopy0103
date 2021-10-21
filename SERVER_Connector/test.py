from threading import *
from socket import *
import json
import struct
 
class ClientSocket:
 
    def __init__(self):        
        self.bConnect = False
    def __del__(self):
        self.stop()
 
    def connectServer(self):
        self.client = socket(AF_INET, SOCK_STREAM)           
 
        try:
            self.client.connect( ('127.0.0.1', 5555) )
        except Exception as e:
            print('Connect Error : ', e)
            return False
        else:
            self.bConnect = True
            self.t = Thread(target=self.read_obj, args=(self.client,))
            self.t.start()
            print('Connected')
 
        return True
 
    def stop(self):
        self.bConnect = False       
        if hasattr(self, 'client'):            
            self.client.close()
            del(self.client)
            print('Client Stop') 

    def send_obj(self, obj):
        msg = json.dumps(obj)
        if self.client:
        	frmt = "=%ds" % len(msg)
        	packed_msg = struct.pack(frmt, bytes(msg,'ascii'))
        	packed_hdr = struct.pack('!I', len(packed_msg))
        	self._send(packed_hdr)
        	self._send(packed_msg)
			
    def _send(self, msg):
        sent = 0
        while sent < len(msg):
        	sent += self.client.send(msg[sent:])
			
    def _read(self, size):
        data = b''
        while len(data) < size:
        	data_tmp = self.client.recv(size-len(data))
        	data += data_tmp
        	if data_tmp == b'':
        		raise RuntimeError("socket connection broken")
        return data

    def _msg_length(self):
        d = self._read(4)
        s = struct.unpack('!I', d)
        return s[0]
	
    def read_obj(self, client):
        size = self._msg_length()
        data = self._read(size)
        frmt = "=%ds" % size
        msg = struct.unpack(frmt, data)
        return json.loads(str(msg[0],'ascii'))

if __name__ == '__main__':
    addj = ClientSocket()
    addj.connectServer()
    idx = 1
    while True:
        if idx <= 1000:
            msg = {'type_msg': 'test1', '사과': 2}
            # msg = json.dumps(msg)
            addj.send_obj(msg)
            idx+=1
        else:
            break