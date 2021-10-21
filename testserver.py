import debugpy
debugpy.debug_this_thread()
from numpy import e
import pandas
import zmq
from time import sleep
from pandas import DataFrame, Timestamp
from threading import Thread
import json
from ZMQ_Connector.svr_Ports import Real_Ports
import socket
import queue
import struct
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
FORMAT = '[%(asctime)-15s][%(levelname)s][%(module)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT)

class ZeroMQ_Connector():
    def __init__(self):
        self.HEADER_LENGTH = 1024
        self.ADDR_FEEDER = (Real_Ports.IP, Real_Ports.PORT_FEEDER)
        self.ADDR_TRADDER1 = (Real_Ports.IP, Real_Ports.PORT1)
        self.ADDR_TRADDER2 = (Real_Ports.IP, Real_Ports.PORT2)
        self.ADDR_TRADDER3 = (Real_Ports.IP, Real_Ports.PORT3)
        self.ADDR_TRADDER4 = (Real_Ports.IP, Real_Ports.PORT4)
 ##################################################################################################
        self.server_socket_feed = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_feed.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket_feed.bind(self.ADDR_FEEDER)
        

        self.server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket1.bind(self.ADDR_TRADDER1)

        self.server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket2.bind(self.ADDR_TRADDER2)

        self.server_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket3.bind(self.ADDR_TRADDER3)

        self.server_socket4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket4.bind(self.ADDR_TRADDER4)

        self.bListen_feed = False       
        self.bListen_socket1 = False
        self.bListen_socket2 = False
        self.bListen_socket3 = False
        self.bListen_socket4 = False
        self.clients = []
        self.ip = []
        self.threads = []
        self.socket_list = [self.server_socket_feed, self.server_socket1, self.server_socket2, self.server_socket3, self.server_socket4]

        #틱데이터 저장
        self.queue_Tick = queue.Queue()
        self.tick_data = {}

##################################################################################################
    def _get_response_(self):
        return self._thread_data_output

    def _set_response_(self, _resp=None):
        self. _thread_data_output = _resp
        
    def listen(self, server, Listen_tf):
        while Listen_tf:
            server.listen()
            try:
                client, addr = server.accept()
                
                print(f"Accepted new connection from {client}:{addr}")
            except Exception as e:
                print('Accept() Error : ', e)
                break
            else:                
                self.clients.append(client)
                self.ip.append(addr)                
                t = Thread(target=self.read_obj, args=(addr, client))
                self.threads.append(t)
                t.start()                
        self.removeAllClients()
        if server == self.server_socket_feed:
            self.server_socket_feed.close()
        if server == self.server_socket1:
            self.server_socket1.close()
        if server == self.server_socket2:
            self.server_socket2.close()
        if server == self.server_socket3:
            self.server_socket3.close()
        if server == self.server_socket4:
            self.server_socket4.close()

    def start(self):
        for notified_socket in self.socket_list:
            if notified_socket == self.server_socket_feed:
                self.bListen_feed = True
                self.t = Thread(target=self.listen, args=(notified_socket,self.bListen_feed))
                self.t.start()
                print('Feed Server Listening...')
            elif notified_socket == self.server_socket1:
                self.bListen_socket1 = True
                self.t = Thread(target=self.listen, args=(notified_socket,self.bListen_socket1))
                self.t.start()
                print('Client1 Server Listening...')
            elif notified_socket == self.server_socket2:
                self.bListen_socket2 = True
                self.t = Thread(target=self.listen, args=(notified_socket,self.bListen_socket2))
                self.t.start()
                print('Client2 Server Listening...')
            elif notified_socket == self.server_socket3:
                self.bListen_socket3 = True
                self.t = Thread(target=self.listen, args=(notified_socket,self.bListen_socket3))
                self.t.start()
                print('Client3 Server Listening...')
            elif notified_socket == self.server_socket4:
                self.bListen_socket4 = True
                self.t = Thread(target=self.listen, args=(notified_socket,self.bListen_socket4))
                self.t.start()            
                print('Client4 Server Listening...')
        return True    

    def stop(self):
        self.bListen = False
        if hasattr(self, 'server_socket_feed'):
            self.server_socket_feed.close()
            print('server_socket_feed stop')
        elif hasattr(self, 'server_socket1'):
            self.server_socket1.close()
            print('server_socket1 stop')
        elif hasattr(self, 'server_socket2'):
            self.server_socket2.close()
            print('server_socket2 stop')
        elif hasattr(self, 'server_socket3'):
            self.server_socket3.close()
            print('server_socket3 stop')
        elif hasattr(self, 'server_socket4'):
            self.server_socket4.close()
            print('server_socket4 stop')


    def send_obj(self, obj, server):
        msg = json.dumps(obj)
        if server:
        	frmt = "=%ds" % len(msg)
        	packed_msg = struct.pack(frmt, bytes(msg,'ascii'))
        	packed_hdr = struct.pack('!I', len(packed_msg))
        	self._send(server, packed_hdr)
        	self._send(server, packed_msg)

    def read_obj(self, addr, client):
        while True:
            try:
                size = self._msg_length(addr, client)
                data = self._read(size, addr, client)
                frmt = "=%ds" % size
                msg = struct.unpack(frmt, data)
            except Exception as e:
                print('Recv() Error: ', e)
                break
            else:
                msg_cp = json.loads(str(msg[0],'ascii'))
                for client_temp in self.clients:
                    if client == client_temp:
                        if msg_cp != "":
                            self.queue_Tick.put(msg_cp)
                            Scode = msg_cp['종목코드']
                            #del msg['종목코드']
                            msg_list = [msg_cp]
                            if Scode in self.tick_data:
                                self.tick_data[Scode].append(msg_list)
                            else:
                                self.tick_data[Scode] = msg_list
                    elif client == self.server_socket1: #봇 1번에서 받는 데이터(매수완료, 매도완료, 관심종목 등)
                        pass
                    elif client == self.server_socket2: #봇 2번에서 받는 데이터(매수완료, 매도완료, 관심종목 등)
                        pass
                    elif client == self.server_socket3: #봇 3번에서 받는 데이터(매수완료, 매도완료, 관심종목 등)
                        pass
                    elif client == self.server_socket4: #봇 4번에서 받는 데이터(매수완료, 매도완료, 관심종목 등)
                        pass
        self.removeClient(addr, client)

    
    def _send(self, server, msg):
        sent = 0
        while sent < len(msg):
        	sent += server.send(msg[sent:])
    
    def _read(self, size, addr, client):
        data = b''
        while len(data) < size:
        	data_tmp = client.recv(size-len(data))
        	data += data_tmp
        	if data_tmp == b'':
        		raise RuntimeError("소켓연결이 끊어짐: ", addr)
        return data 
    def _msg_length(self, addr, client):
        d = self._read(4, addr, client)
        s = struct.unpack('!I', d)
        return s[0]

    # def send(self, msg):
    #     try:
    #         for c in self.clients:
    #             c.send(msg.encode())
    #     except Exception as e:
    #         print('Send() Error: ', e)

    # def receive(self, addr, client):
    #     while True:
    #         try:
    #             recv = client.recv(self.HEADER_LENGTH)
    #         except Exception as e:
    #             print('Recv() Error: ', e)
    #             break
    #         else:
    #             msg = json.loads(recv.decode('utf-8'))
    #             self.queue_Tick.put(msg)
    #             if msg != "":
    #                 Scode = msg['종목코드']
    #                 #del msg['종목코드']
    #                 msg_list = [msg]
    #                 if Scode in self.tick_data:
    #                     self.tick_data[Scode].append(msg_list)
    #                 else:
    #                     self.tick_data[Scode] = msg_list
    #             # if msg:
    #             #     self.send(msg)
    #                 # print('[RECV]: ', addr, msg)
    #     self.removeClient(addr, client)

    def tick_generator(self):
        data = self.queue_Tick.get()
        Scode = data['종목코드']
        #del msg['종목코드']
        data_list = [data]
        if Scode in self.tick_data:
            self.tick_data[Scode].append(data_list)
        else:
            self.tick_data[Scode] = data_list

    def removeClient(self, addr, client):
        idx = -1
        for k, v in enumerate(self.clients):
            if v == client:
                idx = k
                break
        
        client.close()
        self.ip.remove(addr)
        self.clients.remove(client)

        del(self.threads[idx])
        self.resourceInfo()
    
    def removeAllClients(self):
        for c in self.clients:
            c.close()

        self.ip.clear()
        self.clients.clear()
        self.threads.clear()

        self.resourceInfo()
    
    def resourceInfo(self):
        print('Number of Client ip\t: ', len(self.ip))
        print('Number of Client socket\t: ', len(self.clients))
        print('Number of Client thread\t: ', len(self.threads))
    ##########################################################################

if __name__ == "__main__":
    
    assd = ZeroMQ_Connector()
    assd.start()
    dicQ = {"사과": 1, "배": 2, "바나나": 3}
    # assd.send_obj(dicQ, assd.server_socket_feed)