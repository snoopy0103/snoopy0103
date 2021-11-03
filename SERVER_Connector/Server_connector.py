from datetime import datetime, timedelta
import os
import debugpy
from pandas.tseries.offsets import Day
debugpy.debug_this_thread()
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
from numpy import add, e, empty
import numpy
import pandas
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
from Trading_Bot.Alexander_Elder import Three_dimension
import DBconnector.DBManager
from DBconnector.Updater import Update_Data


CONNECTIONS = [] #접속한 client의 쓰레드

class Server_Connector():
    def __init__(self, BuyQ, SellQ, StockQ, EwmQ, queue_Tick, queue_1min, \
        queue_ATR, queue_ewm_5, queue_ewm_10, queue_ewm_30):
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

        # self.관심종목 = 관심종목

        #틱데이터 저장
        # self.queue_Tick = Queue()
        # self.queue_1min = Queue()
        # self.queue_TR = Queue()
        # self.queue_Current_Line = Queue()
        # self.queue_ATR = Queue()
        # self.queue_ewm_5 = Queue()
        # self.queue_ewm_10 = Queue()
        # self.queue_ewm_30 = Queue()
        self.queue_Tick = queue_Tick
        self.queue_1min = queue_1min
        self.queue_ATR = queue_ATR
        self.queue_ewm_5 = queue_ewm_5
        self.queue_ewm_10 = queue_ewm_10
        self.queue_ewm_30 = queue_ewm_30
        ###################################
        self.buyQ = BuyQ
        self.sellQ = SellQ
        self.stockQ = StockQ
        
        self.ewmQ = EwmQ

        ###################################
        # self.min1Q = min1Q
        self.tick_data = {}
        # self.tick_1mindata_alex = {}
        self.tick_1mindata = {}
        self.ATR = {}
        self.ewm_5 = {}
        self.ewm_10 = {}
        self.ewm_30 = {}

        #DB
        self.con = DBconnector.DBManager.dbcon()
        #Process
        self.procs = []
        #######################################################################################################################
        '''장중 프로젝트 정지되었을때 이부분 주석 처리 후 구동'''
        self.previous_day= datetime.today()- timedelta(days=1)
        bdd = numpy.busdaycalendar(weekmask='1111100', holidays=["2021-10-04", "2021-10-11"])
        while not numpy.is_busday(self.previous_day.strftime("%Y-%m-%d"), busdaycal=bdd):
            self.previous_day = self.previous_day - timedelta(days=1)
        
        self.previous_day = str(self.previous_day.year) + str(self.previous_day.month) + str(self.previous_day.day)
        sql = f"SELECT distinct(code) as code FROM kiwoom.tick_1min WHERE 체결날짜 = '{self.previous_day}'"
        df = pandas.read_sql_query(sql, self.con.db)
        for code in df['code']:
            self.ewm_5[code] = []
            self.ewm_10[code] = []
            self.ewm_30[code] = []
            self.ATR[code] = []
            self.tick_1mindata[code] = RealData_1min(code)

            sql_atr = f"with temp_atr as (SELECT * FROM kiwoom.indicator_atr WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 21) select  * from temp_atr order by 체결시간 asc"
            df_atr = pandas.read_sql_query(sql_atr, self.con.db)
            for i in df_atr.index:
                self.ATR[code].append([df_atr['code'][i], str(df_atr['체결시간'][i].strftime("%H%M%S")), df_atr['tr'][i], df_atr['atr'][i], df_atr['center_line'][i], str(df_atr['체결날짜'][i].strftime("%Y%m%d"))])

            sql_ewm_5 = f"with temp_ewm_5 as (SELECT * FROM kiwoom.indicator_5ewm WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 21) select  * from temp_ewm_5 order by 체결시간 asc"
            df_5ewm = pandas.read_sql_query(sql_ewm_5, self.con.db)
            if not df_5ewm.empty:
                for i in df_5ewm.index:
                    self.ewm_5[code].append([df_5ewm['code'][i], str(df_5ewm['체결시간'][i].strftime("%H%M%S")), df_5ewm['ewm_5'][i], str(df_5ewm['체결날짜'][i].strftime("%Y%m%d"))])

            sql_ewm_10 = f"with temp_ewm_10 as (SELECT * FROM kiwoom.indicator_10ewm WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 21) select  * from temp_ewm_10 order by 체결시간 asc"
            df_10ewm = pandas.read_sql_query(sql_ewm_10, self.con.db)
            if not df_10ewm.empty:
                for i in df_10ewm.index:
                    self.ewm_10[code].append([df_10ewm['code'][i], str(df_10ewm['체결시간'][i].strftime("%H%M%S")), df_10ewm['ewm_10'][i], str(df_10ewm['체결날짜'][i].strftime("%Y%m%d"))])

            sql_ewm_30 = f"with temp_ewm_30 as (SELECT * FROM kiwoom.indicator_30ewm WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 21) select  * from temp_ewm_30 order by 체결시간 asc"
            df_30ewm = pandas.read_sql_query(sql_ewm_30, self.con.db)
            if not df_30ewm.empty:
                for i in df_30ewm.index:
                    self.ewm_30[code].append([df_30ewm['code'][i], str(df_30ewm['체결시간'][i].strftime("%H%M%S")), df_30ewm['ewm_30'][i], str(df_30ewm['체결날짜'][i].strftime("%Y%m%d"))])

            sql_tick_1min = f"with temp_tick_1min as (SELECT * FROM kiwoom.tick_1min WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1200' AND '1530' order by 체결시간 desc limit 31) select  * from temp_tick_1min order by 체결시간 asc"
            df_tick_1min = pandas.read_sql_query(sql_tick_1min, self.con.db)
            for i in df_tick_1min.index:
                self.tick_1mindata[code].append(str(df_tick_1min['체결시간'][i].strftime("%H%M%S")), df_tick_1min['현재가'][i], df_tick_1min['거래량'][i], \
                    df_tick_1min['시가'][i], df_tick_1min['고가'][i], df_tick_1min['저가'][i], str(df_tick_1min['체결날짜'][i].strftime("%Y%m%d")))
        print('DB 로드 완료')
        # self.tick_1mindata_alex.update(self.tick_1mindata)
        self.start()
        #######################################################################################################################

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
        # self.tick_generator()
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
                        # name = msg['name']
                        # market = msg['market']
                        self.tick_data[code] = RealData(code)
                        # self.tick_1mindata[code] = RealData_1min(code)#, name, market)
                        self.ATR[code] = []
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
                        if not code in self.tick_data.keys():
                            self.tick_data[code] = RealData(code)
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
                        self.make_Indicators(code, temp_list[2][:4], temp_list[28])
                        self.tick_1min(temp_list)
                        
                    elif type_msg == '관심종목':
                        if addr[1] in self.관심종목.keys():
                            self.관심종목[addr[1]].append(msg['code'])
                        else:
                            self.관심종목[addr[1]] = []
                            self.관심종목[addr[1]].append(msg['code'])
        self.removeClient(addr, client)

    def tick_1min(self, temp_list):
        code = temp_list[0]
        mintime = temp_list[2]
        mintime = mintime[:4]
        mindate = temp_list[28]
        if code in self.tick_1mindata.keys():
            if self.tick_1mindata[code].체결시간 == []:
                self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[28])
                return
            temptime = self.tick_1mindata[code].체결시간[-1]
            if temptime == mintime:
                self.tick_1mindata[code].현재가[-1] = temp_list[3]
                self.tick_1mindata[code].거래량[-1] = temp_list[9] + self.tick_1mindata[code].거래량[-1]
                if temp_list[3] > self.tick_1mindata[code].고가[-1]:
                    self.tick_1mindata[code].고가[-1] = temp_list[3]
                if temp_list[3] < self.tick_1mindata[code].저가[-1]:
                    self.tick_1mindata[code].저가[-1] = temp_list[3]
            else:
                # list_temp = self.tick_1mindata[code].last()
                # list_temp.insert(0, code)
                list_temp = [code, mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate]
                self.queue_1min.put(list_temp)
                # self.tick_1mindata_alex.update(self.tick_1mindata)
                self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate)
        else:
            self.tick_1mindata[code] = RealData_1min(code)
            # self.tick_1mindata_alex.update(self.tick_1mindata)
            self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate)

    def make_Indicators(self, code, mintime, mindate):
        alex = []
        temp_TR = 0
        tempATR = 0
        tempAVG = 0
        if not code in self.tick_1mindata.keys():
            return
        if len(self.tick_1mindata[code].체결시간) > 1:
            temptime = self.tick_1mindata[code].체결시간[-1]
            #TR
            temp_TR = max(self.tick_1mindata[code].고가[-1] - self.tick_1mindata[code].저가[-1], 
            abs(self.tick_1mindata[code].고가[-1] - self.tick_1mindata[code].현재가[-2]), 
            abs(self.tick_1mindata[code].저가[-1] - self.tick_1mindata[code].현재가[-2]))
            #Center Line
            if len(self.tick_1mindata[code].체결시간) > 20:
                for i in range(len(self.tick_1mindata[code].체결시간), len(self.tick_1mindata[code].체결시간)-20, -1):
                    tempAVG += self.tick_1mindata[code].현재가[i-1] / 20
            #ATR
            if len(self.ATR[code]) > 20:
                
                for i in range(len(self.ATR[code]), len(self.ATR[code]) - 20, -1):
                    tempATR += self.ATR[code][i-1][2] / 20
            if temptime == mintime:
                if self.ATR[code] == []:
                    self.ATR[code].append([code, mintime, temp_TR, tempATR, tempAVG,mindate])
                self.ATR[code][-1][2] = temp_TR
                self.ATR[code][-1][3] = tempATR
                self.ATR[code][-1][4] = tempAVG
            else:
                self.ATR[code].append([code, mintime, temp_TR, tempATR, tempAVG, mindate])
                self.queue_ATR.put([code, mintime, temp_TR, tempATR, tempAVG, mindate])
                
##############################################################################################################
        #5EWM
        if len(self.tick_1mindata[code].체결시간) > 5:
            temp5AVG = 0
            for i in range(len(self.tick_1mindata[code].체결시간), len(self.tick_1mindata[code].체결시간)-5, -1):
                temp5AVG += self.tick_1mindata[code].현재가[i-1] / 5
            if not code in self.ewm_5.keys():
                self.ewm_5[code] = []
            if temptime == mintime:
                if self.ewm_5[code] == []:
                    self.ewm_5[code].append([code, mintime, temp5AVG, mindate])
                self.ewm_5[code][-1][2] = temp5AVG
            else:
                if code in self.ewm_5.keys():
                    self.queue_ewm_5.put([code, mintime, temp5AVG, mindate])
                    alex.append([code, mintime, temp5AVG, mindate])
                    self.ewm_5[code].append([code, mintime, temp5AVG, mindate])

        #10EWM
        if len(self.tick_1mindata[code].체결시간) > 10:
            temp10AVG = 0
            for i in range(len(self.tick_1mindata[code].체결시간), len(self.tick_1mindata[code].체결시간)-10, -1):
                temp10AVG += self.tick_1mindata[code].현재가[i-1] / 10
            if not code in self.ewm_10.keys():
                self.ewm_10[code] = []
            if temptime == mintime:
                if self.ewm_10[code] == []:
                    self.ewm_10[code].append([code, mintime, temp10AVG, mindate])
                self.ewm_10[code][-1][2] = temp10AVG
            else:
                if code in self.ewm_10.keys():
                    self.queue_ewm_10.put([code, mintime, temp10AVG, mindate])
                    alex.append([code, mintime, temp10AVG, mindate])
                    self.ewm_10[code].append([code, mintime, temp10AVG, mindate])

        #30EWM
        if len(self.tick_1mindata[code].체결시간) > 30:
            temp30AVG = 0
            for i in range(len(self.tick_1mindata[code].체결시간), len(self.tick_1mindata[code].체결시간)-30, -1):
                temp30AVG += self.tick_1mindata[code].현재가[i-1] / 30
            if not code in self.ewm_30.keys():
                self.ewm_30[code] = []
            if temptime == mintime:
                if self.ewm_30[code] == []:
                    self.ewm_30[code].append([code, mintime, temp30AVG, mindate])
                self.ewm_30[code][-1][2] = temp30AVG
            else:
                if code in self.ewm_30.keys():
                    self.queue_ewm_30.put([code, mintime, temp30AVG, mindate])
                    alex.append([code, mintime, temp30AVG, mindate])
                    self.ewm_30[code].append([code, mintime, temp30AVG, mindate])
        if len(alex) >= 3:
            self.ewmQ.put(alex)
                
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
    manager = Manager()
    BuyQ, SellQ, StockQ, EwmQ, queue_Tick, queue_1min, queue_ATR, queue_ewm_5, queue_ewm_10, queue_ewm_30 = \
    Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue()

    # tick_1mindata = manager.dict()

    #메인 프로세스
    wc = Process(target=Server_Connector, args=(BuyQ, SellQ, StockQ, EwmQ,  \
        queue_Tick, queue_1min, queue_ATR, queue_ewm_5, queue_ewm_10, queue_ewm_30))
    #DB 프로세스
    update_data = Process(target=Update_Data, name='DB_Updater',args=(queue_Tick, queue_1min, queue_ATR, \
        queue_ewm_5, queue_ewm_10, queue_ewm_30, BuyQ), daemon=True)
    
    #로봇 프로세스
    trading_bot_proc = Process(target=Three_dimension, name='Three_dimension',args=(BuyQ, SellQ, StockQ, EwmQ), daemon=True)

    wc.start()
    update_data.start()
    trading_bot_proc.start()
    wc.join()
    update_data.join()
    trading_bot_proc.join()




