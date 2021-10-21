from datetime import datetime, timedelta
import os
import debugpy
from pandas.tseries.offsets import Day
debugpy.debug_this_thread()
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
from numpy import add, e
import numpy
import pandas
import zmq
from time import sleep
from pandas import DataFrame, Timestamp
from threading import Thread
import json
from SERVER_Connector.svr_Ports import Real_Ports
from multiprocessing import Process
from multiprocessing import Manager
from multiprocessing import Queue
# import queue
import socket
import struct
from SERVER_Connector.RealData import RealData
from SERVER_Connector.RealData_1min import RealData_1min
import DBconnector.DBManager

CONNECTIONS = [] #접속한 client의 쓰레드

class Server_Connector():
    def __init__(self, buyQ, sellQ, 관심종목):
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

        self.관심종목 = 관심종목

        #틱데이터 저장
        # self.queue_Tick = queue.Queue()
        # self.queue_1min = queue.Queue()
        self.queue_Tick = Queue()
        self.queue_1min = Queue()
        self.buyQ = buyQ
        self.sellQ = sellQ
        # self.min1Q = min1Q
        self.tick_data = {}
        self.tick_1mindata = {}
        #DB
        self.con = DBconnector.DBManager.dbcon()
        #Process
        self.procs = []
        self.previous_day= datetime.today()- timedelta(days=1)
        bdd = numpy.busdaycalendar(weekmask='1111100', holidays=["2021-10-04", "2021-10-11"])
        while not numpy.is_busday(self.previous_day.strftime("%Y-%m-%d"), busdaycal=bdd):
            self.previous_day = self.previous_day - datetime.timedelta(days=1)

        # sql = 'SELECT CODE FROM kiwoom.COMPANY_INFO'
        # df = pandas.read_sql_query(sql, self.con)
        # for code in df['CODE']:
        #     self.tick_1mindata[code] = RealData_1min(code)
        #     sqlq = f"SELECT * FROM kiwoom.tick_1min WHERE CODE = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
        #         체결시간 BETWEEN '1500' AND '1530'"
        #     df2 = pandas.read_sql_query(sqlq, self.con)
        #     self.tick_1mindata[code].append(df2['체결시간'], df2['현재가'], df2['거래량'], df2['시가'], 
        #     df2['고가'], df2['저가'], df2['체결날짜'], df2['TR'], df2['ATR'])


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
                #사용자 관리
                self.clients.append(client)
                self.ip.append(addr)
                #읽기 스레드
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
                self.t1 = Thread(target=self.listen, args=(notified_socket,self.bListen_feed))
                self.t1.start()
                print('Feed Server Listening...')
            elif notified_socket == self.server_socket1:
                self.bListen_socket1 = True
                self.t2 = Thread(target=self.listen, args=(notified_socket,self.bListen_socket1))
                self.t2.start()
                print('Client1 Server Listening...')
            elif notified_socket == self.server_socket2:
                self.bListen_socket2 = True
                self.t3 = Thread(target=self.listen, args=(notified_socket,self.bListen_socket2))
                self.t3.start()
                print('Client2 Server Listening...')
            elif notified_socket == self.server_socket3:
                self.bListen_socket3 = True
                self.t4 = Thread(target=self.listen, args=(notified_socket,self.bListen_socket3))
                self.t4.start()
                print('Client3 Server Listening...')
            elif notified_socket == self.server_socket4:
                self.bListen_socket4 = True
                self.t5 = Thread(target=self.listen, args=(notified_socket,self.bListen_socket4))
                self.t5.start()            
                print('Client4 Server Listening...')
        self.tick_generator()
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
        try:
            for c in self.clients:
                while sent < len(msg):
                	sent += c.send(msg[sent:])
        except Exception as e:
            print('Send() Error: ', e)	

    def _read(self, size, addr, client):
        data = b''
        while len(data) < size:
            try:
        	    data_tmp = client.recv(size-len(data))
            except Exception as e:
                print('Recv() Error: ', e)
                break
            else:
        	    data += data_tmp
        	    if data_tmp == b'':
        	    	raise RuntimeError("socket connection broken")
        return data

    def _msg_length(self, addr, client):
        d = self._read(4, addr, client)
        s = struct.unpack('!I', d)
        return s[0]
	
    def read_obj(self, addr, client):
        while True:
            try:
                size = self._msg_length(addr, client)
                data = self._read(size, addr, client)
            except Exception as e:
                print('Recv() Error: ', e)
                break
            else:
                frmt = "=%ds" % size
                msg = struct.unpack(frmt, data)
                msg = json.loads(str(msg[0],'ascii'))
                if msg != "":
                    type_msg = msg['type_msg']
                    if type_msg == '종목등록':
                        code = msg['code']
                        name = msg['name']
                        market = msg['market']
                        self.tick_data[code] = RealData(code, name, market)
                        self.tick_1mindata[code] = RealData_1min(code, name, market)
                        
                    elif type_msg == '틱':
                        code = msg['code']
                        총시간 = msg['tick_data'][0]
                        체결시간 = msg['tick_data'][1]
                        현재가 = msg['tick_data'][2]
                        체결방향 = msg['tick_data'][3]
                        전일대비 = msg['tick_data'][4]
                        등락율 = msg['tick_data'][5]
                        최우선매도호가 = msg['tick_data'][6]
                        최우선매수호가 = msg['tick_data'][7]
                        거래량 = msg['tick_data'][8]
                        거래방향 = msg['tick_data'][9]
                        누적거래량 = msg['tick_data'][10]
                        누적거래대금 = msg['tick_data'][11]
                        시가 = msg['tick_data'][12]
                        고가 = msg['tick_data'][13]
                        저가 = msg['tick_data'][14]
                        전일대비기호 = msg['tick_data'][15]
                        전일거래량대비 = msg['tick_data'][16]
                        거래대금증감 = msg['tick_data'][17]
                        전일거래량대비율 = msg['tick_data'][18]
                        거래회전율 = msg['tick_data'][19]
                        거래비용 = msg['tick_data'][20]
                        체결강도 = msg['tick_data'][21]
                        시가총액 = msg['tick_data'][22]
                        장구분 = msg['tick_data'][23]
                        KO접근도 = msg['tick_data'][24]
                        상한가발생시간 = msg['tick_data'][25]
                        하한가발생시간 = msg['tick_data'][26]
                        체결날짜 = msg['tick_data'][27]
                        temp_list = [code, 총시간, 체결시간, 현재가, 체결방향, 전일대비, 등락율,
                                         최우선매도호가, 최우선매수호가, 거래량, 거래방향, 누적거래량, 누적거래대금,
                                         시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, 
                                         거래회전율, 거래비용, 체결강도,
                                         시가총액, 장구분, KO접근도,
                                         상한가발생시간, 하한가발생시간, 체결날짜]
                        self.tick_data[code].append(총시간, 체결시간, 현재가, 체결방향, 전일대비, 등락율,
                                         최우선매도호가, 최우선매수호가, 거래량, 거래방향, 누적거래량, 누적거래대금,
                                         시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, 
                                         거래회전율, 거래비용, 체결강도,
                                         시가총액, 장구분, KO접근도,
                                         상한가발생시간, 하한가발생시간, 체결날짜)
                        self.queue_Tick.put(temp_list)
                        self.tick_1min(temp_list)
                    elif type_msg == '관심종목':
                        if addr[1] in self.관심종목.keys():
                            self.관심종목[addr[1]].append(msg['code'])
                        else:
                            self.관심종목[addr[1]] = []
                            self.관심종목[addr[1]].append(msg['code'])
        self.removeClient(addr, client)
  

    def tick_generator(self):
        t = Thread(target= self.save_data)
        t.start()
    
    def tick_1min(self, temp_list):
        code = temp_list[0]
        mintime = temp_list[2]
        mintime = mintime[:4]
        if code in self.tick_1mindata.keys():
            if self.tick_1mindata[code].체결시간 == []:
                self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[28])
                return
            temptime = self.tick_1mindata[code].체결시간[-1]
            # temptime = temptime[2:4]
            if temptime == mintime:
                self.tick_1mindata[code].현재가[-1] = temp_list[3]
                self.tick_1mindata[code].거래량[-1] = temp_list[9] + self.tick_1mindata[code].거래량[-1]
                # self.tick_1mindata[code]['시가'][-1] = temp_list[13]
                if temp_list[3] > self.tick_1mindata[code].고가[-1]:
                    self.tick_1mindata[code].고가[-1] = temp_list[3]
                if temp_list[3] < self.tick_1mindata[code].저가[-1]:
                    self.tick_1mindata[code].저가[-1] = temp_list[3]
            else:
                list_temp = self.tick_1mindata[code].last()
                list_temp.insert(0, code)
                self.queue_1min.put(list_temp)
                self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[28])
                

    def save_data(self):
        while True:
            if self.queue_Tick.qsize() >= 1000:
                data = self.queue_Tick.get()
                sql = f"INSERT INTO kiwoom.tick \
                    (code, 총시간, 체결시간, 현재가, 체결방향, 전일대비, 등락율, 최우선매도호가, 최우선매수호가, 거래량, 거래방향,누적거래량, \
                    누적거래대금, 시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, \
                    거래회전율, 거래비용, 체결강도, 시가총액, 장구분, KO접근도, 상한가발생시간, 하한가발생시간, 체결날짜) \
                    VALUES \
                    ('{data[0]}', {data[1]}, '{data[2]}', {data[3]}, '{data[4]}', {data[5]}, {data[6]}, {data[7]}, {data[8]}, \
                     {data[9]}, '{data[10]}', {data[11]}, {data[12]}, {data[13]}, {data[14]}, {data[15]}, {data[16]}, {data[17]}, \
                     {data[18]}, {data[19]}, {data[20]}, {data[21]}, {data[22]}, {data[23]}, {data[24]}, {data[25]}, {data[26]}, \
                     {data[27]}, '{data[28]}') \
                    ON CONFLICT(code, 총시간, 누적거래량) \
                    DO UPDATE SET (code, 총시간, 체결시간, 현재가, 체결방향, 전일대비, 등락율, 최우선매도호가, 최우선매수호가, 거래량, 거래방향, \
                    누적거래량, 누적거래대금, 시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, \
                    거래회전율, 거래비용, 체결강도, 시가총액, 장구분, KO접근도, 상한가발생시간, 하한가발생시간, 체결날짜) = \
                    (excluded.code ,excluded.총시간, excluded.체결시간 ,excluded.현재가, excluded.체결방향, excluded.전일대비 ,excluded.등락율 ,excluded.최우선매도호가 \
                    ,excluded.최우선매수호가 ,excluded.거래량, excluded.거래방향, excluded.누적거래량 ,excluded.누적거래대금 ,excluded.시가 ,excluded.고가 \
                    ,excluded.저가 ,excluded.전일대비기호 ,excluded.전일거래량대비 ,excluded.거래대금증감 ,excluded.전일거래량대비율 \
                    ,excluded.거래회전율 ,excluded.거래비용 ,excluded.체결강도 ,excluded.시가총액 ,excluded.장구분 ,excluded.KO접근도 \
                    ,excluded.상한가발생시간 ,excluded.하한가발생시간, excluded.체결날짜)"
                self.con.execute(sql)
                self.con.commit()
            if self.queue_1min.qsize() >= 1000:
                data2 = self.queue_1min.get()
                sql2 = f"INSERT INTO kiwoom.tick_1min \
                    (code, 체결시간, 현재가, 거래량, 시가, 고가, 저가, 체결날짜) \
                    VALUES \
                    ('{data2[0]}', '{data2[1]}', {data2[2]}, {data2[3]}, {data2[4]}, {data2[5]}, {data2[6]}, '{data2[7]}') \
                    ON CONFLICT(CODE, 체결시간, 체결날짜) \
                    DO UPDATE SET (code, 체결시간, 현재가, 거래량, 시가, 고가, 저가, 체결날짜) \
                    = (excluded.code, excluded.체결시간, excluded.현재가, excluded.거래량, excluded.시가, excluded.고가, excluded.저가, excluded.체결날짜)"
                self.con.execute(sql2)
                self.con.commit()
                
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

  

    # def send(self, msg):
    #     # Prefix each message with a 4-byte length (network byte order)
    #     msg = struct.pack('>I', len(msg)) + msg
    #     self.client.sendall(msg)

    # def StartUserProcess(self):
    #     while True:
    #         read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)
    #         for notified_socket in read_sockets:
    #             #새로운 접속
    #             bl = self.UserLogin(notified_socket)
    #             if bl == 'True':
    #                 if notified_socket not in CONNECTIONS:
    #                     self._User_Thread = Thread(target=self.ReceiveMsg, name=f'{notified_socket}')
    #                     self._User_Thread.daemon = True
    #                     self._User_Thread.start()
    #                     CONNECTIONS.append(notified_socket)                        
    #         for notified_socket in exception_sockets:
    #             self.socket_list.remove(notified_socket)
    #             del self.clients[notified_socket]
    #             del CONNECTIONS[notified_socket]
    #             t = Thread.getThreadByName(f'notified_socket')
    #             t.do_run = False
    #             t.join()         
    
    # def ReceiveMsg(self):
    #     while True:
    #         read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)
    #         for notified_socket in read_sockets:
    #             message = self.receive_message(notified_socket)
    #             msg = json.loads(message.decode('utf-8'))
    #             if msg != "":
    #                 Scode = msg['종목코드']
    #                 #del msg['종목코드']
    #                 msg_list = [msg]
    #                 if Scode in self.tick_data:
    #                     self.tick_data[Scode].append(msg_list)
    #                 else:
    #                     self.tick_data[Scode] = msg_list

    #         for notified_socket in exception_sockets:
    #           self.socket_list.remove(notified_socket)
    #           del self.clients[notified_socket]
    #           del CONNECTIONS[notified_socket]
    #           t = Thread.getThreadByName(f'notified_socket')
    #           t.do_run = False
    #           t.join()              

    ##########################################################################
    
    # """
    # Set Status (to enable/disable strategy manually)
    # """
    # def _setStatus(self, _new_status=False):
    
    #     self. _ACTIVE = _new_status
    #     print("\n**\n[KERNEL] Setting Status to {} - Deactivating Threads.. please wait a bit. \n**". format(_new_status))
                
    # ##########################################################################
    
    # """
    # 주문전송(PUSH)
    # """
    # def remote_send(self, _socket, _data):
        
    #     try:
    #         _socket. send_string(_data, zmq. DONTWAIT)
    #     except zmq. error. Again:
    #         print("\nResource timeout.. please try again.")
    #         sleep(0.000000001)
      
    # ##########################################################################
    
    # def _get_response_(self):
    #     return self. _thread_data_output
    
    # ##########################################################################
    
    # def _set_response_(self, _resp=None):
    #     self. _thread_data_output = _resp
    
    # ##########################################################################
    
    # def _valid_response_(self, _input='zmq'):
        
    #     # Valid data types
    #     _types = (dict,DataFrame)
        
    #     # If _input = 'zmq', assume self._zmq._thread_data_output
    #     if isinstance(_input, str) and _input == 'zmq':
    #         return isinstance(self._get_response_(), _types)
    #     else:
    #         return isinstance(_input, _types)
            
    #     # Default
    #     return False
    
    # ##########################################################################
    
    # """
    # Function to retrieve data from MetaTrader (PULL or SUB)
    # """
    # def remote_recv(self, _socket):
        
    #     try:
    #         msg = _socket. recv_string(zmq. DONTWAIT)
    #         return msg
    #     except zmq. error. Again:
    #         print("\nResource timeout.. please try again.")
    #         sleep(0.000001)
            
    #     return None
        
    # ##########################################################################
    
    # # 거래 신호
    # def MAKE_NEW_TRADE_(self, _order=None):
        
    #     if _order is None:
    #         _order = self. _generate_default_order_dict()
        
    #     # Execute
    #     self. MTX_SEND_COMMAND_(**_order)
        
    # # 거래수정 신호
    # def MODIFY_TRADE_(self, _ticket, _SL, _TP): # in points
        
    #     try:
    #         self. temp_order_dict['_action'] = 'MODIFY'
    #         self. temp_order_dict['_SL'] = _SL
    #         self. temp_order_dict['_TP'] = _TP
    #         self. temp_order_dict['_ticket'] = _ticket
            
    #         # Execute
    #         self. MTX_SEND_COMMAND_(**self. temp_order_dict)
            
    #     except KeyError:
    #         print("[ERROR] Order Ticket {} not found!". format(_ticket))
    
    # # CLOSE ORDER
    # def CLOSE_TRADE_(self, _ticket):
        
    #     try:
    #         self. temp_order_dict['_action'] = 'CLOSE'
    #         self. temp_order_dict['_ticket'] = _ticket
            
    #         # Execute
    #         self. MTX_SEND_COMMAND_(**self. temp_order_dict)
            
    #     except KeyError:
    #         print("[ERROR] Order Ticket {} not found!". format(_ticket))
            

    
    # ##########################################################################
    # """
    # 매수/매도/취소등 모든 신호를 보냄
    # """
    # def MTX_SEND_COMMAND_(self, msg):
    #     _msg = msg
    #     # PUSH Socket으로 보낸다.
    #     self.remote_send(self._PUSH_SOCKET, _msg)
    
    # ##########################################################################
    
    # """
    # MARKET DATA 및 CLIENT 수신
    # """
    
    # def _DWX_ZMQ_Poll_Data_(self): #, string_delimiter=';'):
        
    #     while self._ACTIVE:
            
    #         sockets = dict(self._poller.poll())
            
    #         # CLIENT 수신(조건검색 종목, 매수/매도/취소 완료신호 등)
    #         if self._PULL_SOCKET in sockets and sockets[self._PULL_SOCKET] == zmq.POLLIN:
                
    #             try:
    #                 msg = self._PULL_SOCKET.recv_string(zmq.DONTWAIT)
                    
    #                 # 데이터를 받으면 판다스시리즈로 저장
    #                 if msg != '' and msg != None:
                        
    #                     try: 
    #                         _data = eval(msg)
                            
    #                         self._thread_data_output = _data
    #                         if self._verbose:
    #                             print(_data) # default logic
                                
    #                     except Exception as ex:
    #                         _exstr = "Exception Type {0}. Args:\n{1!r}"
    #                         _msg = _exstr.format(type(ex).__name__, ex.args)
    #                         print(_msg)
               
    #             except zmq.error.Again:
    #                 pass 
    #             except ValueError:
    #                 pass 
    #             except UnboundLocalError:
    #                 pass 
            
    #         # 키움증권 데이터 Feeding(대표하나만 연결)
    #         if self._SUB_SOCKET in sockets and sockets[self._SUB_SOCKET] == zmq.POLLIN:
                
    #             try:
    #                 msg = self._SUB_SOCKET.recv()
    #                 msg = msg.decode('utf-8')
    #                 msg = json.loads(msg)

    #                 print(msg)
    #                 _tempx = msg.encode('utf-8')
    #                 self._SUB_SOCKET.send(_tempx)

    #                 # if msg != "":
    #                 #     Scode = msg['종목코드']
    #                 #     #del msg['종목코드']

    #                 #     msg_list = [msg]
    #                 #     if Scode in self.tick_data:
    #                 #         self.tick_data[Scode].append(msg_list)
    #                 #     else:
    #                 #         self.tick_data[Scode] = msg_list
                    
    #             except zmq.error.Again:
    #                 pass 
    #             except ValueError:
    #                 pass 
    #             except UnboundLocalError:
    #                 pass 
                
    ##########################################################################

if __name__ == '__main__':
    # os.system('pause')
    
    addj = Server_Connector()
    addj.start()
    
    addj.t1.join()
    addj.t2.join()
    addj.t3.join()
    addj.t4.join()
    addj.t5.join()




