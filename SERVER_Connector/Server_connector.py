from datetime import datetime, timedelta
import os
import debugpy
from pandas.tseries.offsets import Day
import statistics
debugpy.debug_this_thread()
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
from numpy import add, e, empty
import numpy
import pandas
from time import sleep, time
from pandas import DataFrame, Timestamp
from threading import Thread
import json
from SERVER_Connector.svr_Ports import Real_Ports
from multiprocessing import Process
from multiprocessing import Queue

import socket
import struct
from SERVER_Connector.RealData import RealData
from SERVER_Connector.RealData_1min import RealData_1min
from SERVER_Connector.RealData_5min import RealData_5min
from SERVER_Connector.RealData_30min import RealData_30min
from Trading_Bot.Alexander_Elder import Three_dimension
from Trading_Bot.Parabolic_SAR import Parabolic
from Trading_Bot.CrossUP60min import CrossUp60
from Trading_Bot.Medianwith30min import Median30
from Trading_Bot.MedianV2 import stUP5
import DBconnector.DBManager
from DBconnector.Updater import Update_Data


CONNECTIONS = [] #접속한 client의 쓰레드

class Server_Connector():
    def __init__(self, BuyQ1, SellQ1, Stock1Q, queue_Tick, queue_1min, \
        queue_ATR, queue_ewm_5, queue_ewm_20, queue_ewm_30, tick_1minQ1, \
        queue_30min, Stock4Q, Stock3Q, queue_30fromDB, queue_20min, queue_5min, \
        BuyQ4, SellQ4, tick_1minQ2, queue_ewm_5DB, queue_5fromDB):
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
        self.clients = {}
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
        self.queue_5min = queue_5min
        self.queue_30min = queue_30min
        self.queue_ATR = queue_ATR
        self.queue_ewm_5 = queue_ewm_5
        self.queue_ewm_20 = queue_ewm_20
        self.queue_ewm_30 = queue_ewm_30
        # self.queue_bollinger = queue_bollinger
        self.queue_5fromDB = queue_5fromDB
        self.queue_30fromDB = queue_30fromDB
        self.queue_20min = queue_20min
        
        self.queue_ewm_5DB = queue_ewm_5DB
        ###################################
        self.buyQ1 = BuyQ1
        self.sellQ1 = SellQ1
        self.buyQ4 = BuyQ4
        self.sellQ4 = SellQ4
        self.stock4Q = Stock4Q
        self.stock1Q = Stock1Q
        self.stock3Q = Stock3Q
        


        self.tick_1minQ1 = tick_1minQ1
        self.tick_1minQ2 = tick_1minQ2
        ###################################
        # self.min1Q = min1Q
        self.tick_data = {}
        # self.tick_1mindata_alex = {}
        self.tick_1mindata = {}
        self.tick_5mindata = {}
        self.tick_30mindata = {}
        self.tick_bollinger = {}
        self.ATR = {}
        self.ewm_5 = {}
        self.ewm_20 = {}
        self.ewm_30 = {}

        #DB
        self.con = DBconnector.DBManager.dbcon()
        #Process
        self.procs = []
        #######################################################################################################################
        '''장중 프로젝트 정지되었을때 이부분 주석 처리 후 구동'''
        today = datetime.today().strftime("%Y%m%d")
        self.previous_day= datetime.today()- timedelta(days=1)
        bdd = numpy.busdaycalendar(weekmask='1111100', holidays=["2021-10-04", "2021-10-11"])
        while not numpy.is_busday(self.previous_day.strftime("%Y-%m-%d"), busdaycal=bdd):
            self.previous_day = self.previous_day - timedelta(days=1)
        
        self.previous_day = self.previous_day.strftime("%Y%m%d")#str(self.previous_day.year) + str(self.previous_day.month) + str(self.previous_day.day)
        sql = f"SELECT distinct(code) as code FROM kiwoom.tick_1min WHERE 체결날짜 = '{self.previous_day}'"
        df = pandas.read_sql_query(sql, self.con.db)
        for code in df['code']:
            self.ewm_5[code] = []
            self.ewm_20[code] = []
            self.ewm_30[code] = []
            self.ATR[code] = []
            self.tick_1mindata[code] = RealData_1min(code)
            self.tick_5mindata[code] = RealData_5min(code)
#######################################################################################################################################################################################################
            sql_atr = f"with temp_atr as (SELECT * FROM kiwoom.indicator_atr WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 21) select  * from temp_atr order by 체결시간 asc"
            df_atr = pandas.read_sql_query(sql_atr, self.con.db)
            for i in df_atr.index:
                self.ATR[code].append([df_atr['code'][i], str(df_atr['체결시간'][i].strftime("%H%M%S")), df_atr['tr'][i], df_atr['atr_5'][i], df_atr['atr_20'][i], df_atr['center_line'][i], str(df_atr['체결날짜'][i].strftime("%Y%m%d"))])
#######################################################################################################################################################################################################
            sql_ewm_5 = f"with temp_ewm_5 as (SELECT * FROM kiwoom.indicator_5ewm_test WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 21) select  * from temp_ewm_5 order by 체결시간 asc"
            df_5ewm = pandas.read_sql_query(sql_ewm_5, self.con.db)
            if not df_5ewm.empty:
                for i in df_5ewm.index:
                    self.ewm_5[code].append([df_5ewm['code'][i], str(df_5ewm['체결시간'][i].strftime("%H%M%S")), df_5ewm['ewm_5'][i], str(df_5ewm['체결날짜'][i].strftime("%Y%m%d"))])
#######################################################################################################################################################################################################
            sql_ewm_20 = f"with temp_ewm_20 as (SELECT * FROM kiwoom.indicator_20ewm_test WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1300' AND '1530' order by 체결시간 desc limit 31) select  * from temp_ewm_20 order by 체결시간 asc"
            df_20ewm = pandas.read_sql_query(sql_ewm_20, self.con.db)
            if not df_20ewm.empty:
                for i in df_20ewm.index:
                    self.ewm_20[code].append([df_20ewm['code'][i], str(df_20ewm['체결시간'][i].strftime("%H%M%S")), df_20ewm['ewm_20'][i], str(df_20ewm['체결날짜'][i].strftime("%Y%m%d"))])
#######################################################################################################################################################################################################
            sql_ewm_30 = f"with temp_ewm_30 as (SELECT * FROM kiwoom.indicator_30ewm WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 21) select  * from temp_ewm_30 order by 체결시간 asc"
            df_30ewm = pandas.read_sql_query(sql_ewm_30, self.con.db)
            if not df_30ewm.empty:
                for i in df_30ewm.index:
                    self.ewm_30[code].append([df_30ewm['code'][i], str(df_30ewm['체결시간'][i].strftime("%H%M%S")), df_30ewm['ewm_30'][i], str(df_30ewm['체결날짜'][i].strftime("%Y%m%d"))])
##########tick_1min_test처럼 수정해야함!!!-->체결강도DB컬럼추가~
            sql_tick_1min = f"with temp_tick_1min as (SELECT * FROM kiwoom.tick_1min_test WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1400' AND '1530' order by 체결시간 desc limit 31) select * from temp_tick_1min order by 체결시간 asc"
            df_tick_1min = pandas.read_sql_query(sql_tick_1min, self.con.db)
            for i in df_tick_1min.index:
                self.tick_1mindata[code].append(str(df_tick_1min['체결시간'][i].strftime("%H%M%S")), df_tick_1min['현재가'][i], df_tick_1min['거래량'][i], \
                    df_tick_1min['시가'][i], df_tick_1min['고가'][i], df_tick_1min['저가'][i], df_tick_1min['체결강도'][i],str(df_tick_1min['체결날짜'][i].strftime("%Y%m%d")))
#######################################################################################################################################################################################################            
            sql_tick_5min = f"with temp_tick_5min as (SELECT * FROM kiwoom.tick_5min_test WHERE code = '{code}' AND 체결날짜 = '{self.previous_day}' AND \
                체결시간 BETWEEN '1300' AND '1530' order by 체결시간 desc limit 31) select * from temp_tick_5min order by 체결시간 asc"
            df_tick_5min = pandas.read_sql_query(sql_tick_5min, self.con.db)
            for i in df_tick_5min.index:
                self.queue_5fromDB.put([code, str(df_tick_5min['체결시간'][i].strftime("%H%M%S")), df_tick_5min['현재가'][i], df_tick_5min['거래량'][i], \
                    df_tick_5min['고가'][i], df_tick_5min['저가'][i], df_tick_5min['시가'][i], df_tick_5min['vwap'][i], df_tick_5min['누적거래량'][i], df_tick_5min['누적거래대금'][i], str(df_tick_5min['체결날짜'][i].strftime("%Y%m%d"))])
#######################################################################################################################################################################################################
            # sql_tick_30min = f"select * from kiwoom.tick_30min where code = '{code}' and 체결날짜 = '{today}'"
            # df_tick_30min = pandas.read_sql_query(sql_tick_30min, self.con.db)
            # for i in df_tick_30min.index:
            #     self.queue_30fromDB.put([code, str(df_tick_30min['체결시간'][i].strftime("%H%M%S")), df_tick_30min['현재가'][i], df_tick_30min['거래량'][i], \
            #         df_tick_30min['고가'][i], df_tick_30min['저가'][i], str(df_tick_30min['체결날짜'][i].strftime("%Y%m%d"))])
                
#######################################################################################################################################################################################################                
        print('DB 로드 완료')
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
                self.clients[addr] = client
                # self.clients.append(client)
                self.ip.append(addr)
                #읽기 스레드
                t = Thread(target=self.read_obj, args=(addr, client))
                self.clients[addr] = [client, t.getName()]
                self.threads.append(t)
                t.start()
                t1 = Thread(target=self.send_buysell, daemon=True)                
                t1.start()
        # self.removeAllClients()
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

    def send_buysell(self):
        while True:
            if not self.buyQ1.empty():
                buyitem = self.buyQ1.get()
                for key in buyitem.keys():
                    for user in self.clients.keys():
                        if user[0] == key:
                            self.send_obj(buyitem[key], self.clients[user][0])
            if not self.sellQ1.empty():
                sellitem = self.sellQ1.get()
                for key in sellitem.keys():
                    for user in self.clients.keys():
                        if user[0] == key:
                            self.send_obj(sellitem[key], self.clients[user][0])
            if not self.buyQ4.empty():
                buyitem = self.buyQ4.get()
                for key in buyitem.keys():
                    for user in self.clients.keys():
                        if user[0] == key:
                            self.send_obj(buyitem[key], self.clients[user][0])
            if not self.sellQ4.empty():
                sellitem = self.sellQ4.get()
                for key in sellitem.keys():
                    for user in self.clients.keys():
                        if user[0] == key:
                            self.send_obj(sellitem[key], self.clients[user][0])                            


    def send_obj(self, obj, client):
        msg = json.dumps(obj)
        
        frmt = "=%ds" % len(msg)
        packed_msg = struct.pack(frmt, bytes(msg,'ascii'))
        packed_hdr = struct.pack('!I', len(packed_msg))
        self._send(packed_hdr, client)
        self._send(packed_msg, client)
			
    def _send(self, msg, client):
        sent = 0
        try:
            # for c in self.clients:
            while sent < len(msg):
                sent += client.send(msg[sent:])
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
                        # self.tick_5min(temp_list)
                        self.tick_1min(temp_list)
                        # self.tick_30min(temp_list)
                        # self.make_Indicators(code, temp_list[2][:4], temp_list[28])
                    elif type_msg == '조건검색':
                        for user in self.clients.keys():
                            if self.clients[user][0] == client:
                                if user[0] == '192.168.0.4':
                                    pass
                                    # self.stock4Q.put(msg['code'])
                                elif user[0] == '127.0.0.1':
                                    self.stock1Q.put({user[0]: msg['code']})
                                    self.stock4Q.put({user[0]: msg['code']})
                                elif user[0] == '192.168.0.3':
                                    self.stock3Q.put(msg['code'])

                    elif type_msg == 'test':
                        code = msg['code']
                        memo = ['memo']
                        self.send_obj(code, client)

        self.removeClient(addr, client)
        
    def tick_1min(self, temp_list):
        code = temp_list[0]
        mintime = temp_list[2]
        mintime = mintime[:4]
        mindate = temp_list[28]
        if code in self.tick_1mindata.keys():
            if self.tick_1mindata[code].체결시간 == []:
                전체누적거래대금 = int(temp_list[3]) * int(temp_list[9])
                self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[9], temp_list[9], 전체누적거래대금, temp_list[22], temp_list[28])
                return
            temptime = self.tick_1mindata[code].체결시간[-1]
            if temptime == mintime:
                self.tick_1mindata[code].현재가[-1] = temp_list[3]
                self.tick_1mindata[code].누적거래량[-1] = temp_list[9] + self.tick_1mindata[code].누적거래량[-1]
                self.tick_1mindata[code].전체누적거래량[-1] = temp_list[9] + self.tick_1mindata[code].전체누적거래량[-1]
                self.tick_1mindata[code].거래량[-1] = temp_list[9]
                self.tick_1mindata[code].전체누적거래대금[-1] = (int(temp_list[3]) * int(temp_list[9])) + self.tick_1mindata[code].전체누적거래대금[-1]
                if temp_list[3] > self.tick_1mindata[code].고가[-1]:
                    self.tick_1mindata[code].고가[-1] = temp_list[3]
                if temp_list[3] < self.tick_1mindata[code].저가[-1]:
                    self.tick_1mindata[code].저가[-1] = temp_list[3]
                self.tick_1mindata[code].체결강도[-1] = temp_list[22]
                #로봇전송용
                # list_qtemp1 = [code, self.tick_1mindata[code].체결시간[-1], self.tick_1mindata[code].현재가[-1], \
                #        self.tick_1mindata[code].거래량[-1], self.tick_1mindata[code].시가[-1], self.tick_1mindata[code].고가[-1], self.tick_1mindata[code].저가[-1]]
                list_qtemp2 = [code, self.tick_1mindata[code].체결시간[-1], self.tick_1mindata[code].현재가[-1], \
                       self.tick_1mindata[code].거래량[-1], self.tick_1mindata[code].시가[-1], self.tick_1mindata[code].고가[-1], \
                           self.tick_1mindata[code].저가[-1], self.tick_1mindata[code].전체누적거래량[-1], self.tick_1mindata[code].전체누적거래대금[-1], self.tick_1mindata[code].체결강도[-1], mindate]
                # self.tick_1minQ1.put(list_qtemp1)
                self.tick_1minQ2.put(list_qtemp2)
            else:
                if not self.tick_1mindata[code] ==[]:
                    list_qtemp = [code, self.tick_1mindata[code].체결시간[-1], self.tick_1mindata[code].현재가[-1], \
                       self.tick_1mindata[code].누적거래량[-1], self.tick_1mindata[code].시가[-1], self.tick_1mindata[code].고가[-1], self.tick_1mindata[code].저가[-1], \
                           mindate]
                    #DB저장용
                    self.queue_1min.put(list_qtemp)
                #로봇전송용
                전체누적거래량 = int(self.tick_1mindata[code].전체누적거래량[-1]) + int(temp_list[9])
                전체누적거래대금 = int(self.tick_1mindata[code].전체누적거래대금[-1]) + int(temp_list[3]) * int(temp_list[9])
                # list_temp1 = [code, mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3]]
                list_temp2 = [code, mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], 전체누적거래량, 전체누적거래대금, temp_list[22], mindate]
                # self.tick_1minQ1.put(list_temp1)
                self.tick_1minQ2.put(list_temp2)
                #메모리저장용
                전체누적거래량 = int(self.tick_1mindata[code].전체누적거래량[-1]) + int(temp_list[9])
                전체누적거래대금 = int(self.tick_1mindata[code].전체누적거래대금[-1]) + int(temp_list[3]) * int(temp_list[9])
                self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[9], 전체누적거래량, 전체누적거래대금, temp_list[22], mindate)
        else:
            self.tick_1mindata[code] = RealData_1min(code)
            # self.tick_1mindata_alex.update(self.tick_1mindata)
            전체누적거래대금 = int(temp_list[3]) * int(temp_list[9])
            self.tick_1mindata[code].append(mintime, temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[9], temp_list[9], 전체누적거래대금, temp_list[22], mindate)
    
    def tick_5min(self, temp_list):
        timemin = datetime.now().minute
        code = temp_list[0]
        mintime = temp_list[2]
        min2time = mintime[2:4]
        mindate = temp_list[28]
        if code in self.tick_5mindata.keys():
            if self.tick_5mindata[code].체결시간 == []:
                self.tick_5mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[9], temp_list[9], temp_list[28])
                return
            temptime = self.tick_5mindata[code].체결시간[-1][2:4]
            temphour = self.tick_5mindata[code].체결시간[-1][:2]

            if int(min2time)%5 == 0 and int(self.tick_5mindata[code].체결시간[-1][2:4])%5 != 0:
                if not self.tick_5mindata[code] == []:
                    list_qtemp = [code, self.tick_5mindata[code].체결시간[-1], self.tick_5mindata[code].현재가[-1], \
                       self.tick_5mindata[code].거래량[-1], self.tick_5mindata[code].고가[-1], self.tick_5mindata[code].저가[-1], \
                           self.tick_5mindata[code].시가[-1], self.tick_5mindata[code].전체누적거래량[-1], mindate]
                    #로봇전송용
                    # self.queue_5min.put(list_qtemp)
                    #DB저장용(수정필요 누적거래량)
                    list_qtempDB = [code, self.tick_5mindata[code].체결시간[-1], self.tick_5mindata[code].현재가[-1], \
                       self.tick_5mindata[code].분5누적거래량[-1], self.tick_5mindata[code].고가[-1], self.tick_5mindata[code].저가[-1], \
                           self.tick_5mindata[code].시가[-1], mindate]                    
                    # self.queue_5minDB.put(list_qtempDB)
                #메모리저장용
                self.tick_5mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[9], temp_list[9] + self.tick_5mindata[code].전체누적거래량[-1], mindate)
            else:
                self.tick_5mindata[code].체결시간[-1] = temp_list[2]
                self.tick_5mindata[code].현재가[-1] = temp_list[3]
                self.tick_5mindata[code].분5누적거래량[-1] = temp_list[9] + self.tick_5mindata[code].분5누적거래량[-1]
                self.tick_5mindata[code].전체누적거래량[-1] = temp_list[9] + self.tick_5mindata[code].전체누적거래량[-1]
                self.tick_5mindata[code].거래량[-1] = temp_list[9]
                if temp_list[3] > self.tick_5mindata[code].고가[-1]:
                    self.tick_5mindata[code].고가[-1] = temp_list[3]
                if temp_list[3] < self.tick_5mindata[code].저가[-1]:
                    self.tick_5mindata[code].저가[-1] = temp_list[3]
                #로봇전송용


            # if int(timemin)%5 != 0:
            #     self.tick_5mindata[code].체결시간[-1] = temp_list[2]
            #     self.tick_5mindata[code].현재가[-1] = temp_list[3]
            #     self.tick_5mindata[code].거래량[-1] = temp_list[9] + self.tick_5mindata[code].거래량[-1]
            #     if temp_list[3] > self.tick_5mindata[code].고가[-1]:
            #         self.tick_5mindata[code].고가[-1] = temp_list[3]
            #     if temp_list[3] < self.tick_5mindata[code].저가[-1]:
            #         self.tick_5mindata[code].저가[-1] = temp_list[3]
            #     #로봇전송용

            # else:
            #     if not self.tick_5mindata[code] == []:
            #         list_qtemp = [code, self.tick_5mindata[code].체결시간[-1], self.tick_5mindata[code].현재가[-1], \
            #            self.tick_5mindata[code].거래량[-1], self.tick_5mindata[code].고가[-1], self.tick_5mindata[code].저가[-1], \
            #                self.tick_5mindata[code].시가[-1], mindate]
            #         #로봇전송용
            #         self.queue_5min.put(list_qtemp)
            #         #DB저장용
            #         self.queue_5minDB.put(list_qtemp)
            #     #메모리저장용
            #     self.tick_5mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate)
        else:
            self.tick_5mindata[code] = RealData_5min(code)
            self.tick_5mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[9], temp_list[9], mindate)            



        #     if int(temphour) == 9 and int(mintime) < 5:
        #         self.tick_5mindata[code].체결시간[-1] = temp_list[2]
        #         self.tick_5mindata[code].현재가[-1] = temp_list[3]
        #         self.tick_5mindata[code].거래량[-1] = temp_list[9] + self.tick_5mindata[code].거래량[-1]
        #         if temp_list[3] > self.tick_5mindata[code].고가[-1]:
        #             self.tick_5mindata[code].고가[-1] = temp_list[3]
        #         if temp_list[3] < self.tick_5mindata[code].저가[-1]:
        #             self.tick_5mindata[code].저가[-1] = temp_list[3]                
        #     else:
        #         if int(self.tick_5mindata[code].체결시간[-1][2:4]) < 5 and int(temphour) == 9:
        #             if not self.tick_5mindata[code] == []:
        #                 list_qtemp = [code, self.tick_5mindata[code].체결시간[-1], self.tick_5mindata[code].현재가[-1], \
        #                    self.tick_5mindata[code].거래량[-1], self.tick_5mindata[code].고가[-1], self.tick_5mindata[code].저가[-1], \
        #                        self.tick_5mindata[code].시가[-1], mindate]
        #                 self.queue_5min.put(list_qtemp)
        #         self.tick_5mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate)
        # else:
        #     self.tick_5mindata[code] = RealData_5min(code)
        #     self.tick_5mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate)

    def tick_30min(self, temp_list):
        code = temp_list[0]
        mintime = temp_list[2]
        mintime = mintime[2:4]
        mindate = temp_list[28]
        if code in self.tick_30mindata.keys():
            if self.tick_30mindata[code].체결시간 == []:
                self.tick_30mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], temp_list[28])
                return
            if int(self.tick_30mindata[code].체결시간[-1][:2]) > 9 or \
                (int(self.tick_30mindata[code].체결시간[-1][:2]) == 9 and \
                int(self.tick_30mindata[code].체결시간[-1][2:4]) > 30):
                return
            # if int(self.tick_30mindata[code].체결시간[-1][:2]) > 9 or \
            #     int(self.tick_30mindata[code].체결시간[-1][:2]) == 8 or \
            #     (int(self.tick_30mindata[code].체결시간[-1][:2]) == 9 and \
            #     int(self.tick_30mindata[code].체결시간[-1][2:4]) > 30):
            #     return
            temptime = self.tick_30mindata[code].체결시간[-1][2:4]
            temphour = self.tick_30mindata[code].체결시간[-1][:2]
            if int(temphour) == 9 and int(mintime) < 30:
                self.tick_30mindata[code].체결시간[-1] = temp_list[2]
                self.tick_30mindata[code].현재가[-1] = temp_list[3]
                self.tick_30mindata[code].거래량[-1] = temp_list[9] + self.tick_30mindata[code].거래량[-1]
                if temp_list[3] > self.tick_30mindata[code].고가[-1]:
                    self.tick_30mindata[code].고가[-1] = temp_list[3]
                if temp_list[3] < self.tick_30mindata[code].저가[-1]:
                    self.tick_30mindata[code].저가[-1] = temp_list[3]                
            else:
                if int(self.tick_30mindata[code].체결시간[-1][2:4]) < 30 and int(temphour) == 9:
                    if not self.tick_30mindata[code] == []:
                        list_qtemp = [code, self.tick_30mindata[code].체결시간[-1], self.tick_30mindata[code].현재가[-1], \
                           self.tick_30mindata[code].거래량[-1], self.tick_30mindata[code].고가[-1], self.tick_30mindata[code].저가[-1], \
                               mindate]
                        self.queue_30min.put(list_qtemp)
                self.tick_30mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate)                    
        else:
            self.tick_30mindata[code] = RealData_30min(code)
            self.tick_30mindata[code].append(temp_list[2], temp_list[3], temp_list[9], temp_list[3], temp_list[3], temp_list[3], mindate)

    def make_Indicators(self, code, mintime, mindate):
        temp_TR = 0
        tempATR_5 = 0
        tempATR_20 = 0
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
            #ATR_5
            if len(self.ATR[code]) > 5:
                for i in range(len(self.ATR[code]), len(self.ATR[code]) - 5, -1):
                    tempATR_5 += self.ATR[code][i-1][2] / 5
            #ATR_20
            if len(self.ATR[code]) > 20:
                for i in range(len(self.ATR[code]), len(self.ATR[code]) - 20, -1):
                    tempATR_20 += self.ATR[code][i-1][2] / 20
            if temptime == mintime:
                if self.ATR[code] == []:
                    self.ATR[code].append([code, mintime, temp_TR, tempATR_20, tempAVG,mindate])
                self.ATR[code][-1][2] = temp_TR
                self.ATR[code][-1][3] = tempATR_5
                self.ATR[code][-1][4] = tempATR_20
                self.ATR[code][-1][5] = tempAVG
            else:
                if not self.ATR[code] == []:
                    self.queue_ATR.put(self.ATR[code][-1])
                self.ATR[code].append([code, mintime, temp_TR, tempATR_5, tempATR_20, tempAVG, mindate])
                
                
##############################################################################################################
        # #5MA
        # if len(self.tick_5mindata[code].체결시간) > 5:
        #     temptime = self.tick_5mindata[code].체결시간[-1]
        #     temp5AVG = 0
        #     for i in range(len(self.tick_5mindata[code].체결시간), len(self.tick_5mindata[code].체결시간)-5, -1):
        #         temp5AVG += self.tick_5mindata[code].현재가[i-1] / 5
        #     if not code in self.ewm_5.keys():
        #         self.ewm_5[code] = []
        #     if temptime == mintime:
        #         if self.ewm_5[code] == []:
        #             self.ewm_5[code].append([code, mintime, temp5AVG, mindate])
        #         self.ewm_5[code][-1][2] = temp5AVG
        #         #로봇에 보낼 큐
        #         self.queue_ewm_5.put()

        #     else:
        #         if code in self.ewm_5.keys():
        #             #DB
        #             if not self.ewm_5[code] == []:
        #                 self.queue_ewm_5DB.put(self.ewm_5[code][-1])
        #             self.ewm_5[code].append([code, mintime, temp5AVG, mindate])
        #             #로봇에 보낼 큐

        # #20MA
        # if len(self.tick_5mindata[code].체결시간) > 20:
        #     temp20AVG = 0
        #     stdvalue = list()
        #     for i in range(len(self.tick_5mindata[code].체결시간), len(self.tick_5mindata[code].체결시간)-20, -1):
        #         temp20AVG += self.tick_5mindata[code].현재가[i-1] / 20
        #     if not code in self.ewm_20.keys():
        #         self.ewm_20[code] = []
        #     if not code in self.tick_bollinger.keys():
        #         self.tick_bollinger[code] = []
        #     if temptime == mintime:
        #         if self.ewm_20[code] == []:
        #             self.ewm_20[code].append([code, mintime, temp20AVG, mindate])
        #         self.ewm_20[code][-1][2] = temp20AVG
        #         #####################bollinger################################
        #         if len(self.ewm_20[code]) > 20:
        #             for i in self.ewm_20[code][-20:]:
        #                 stdvalue.append(i[2])
        #             std = statistics.stdev(stdvalue)
        #             highvalue = temp20AVG + std * 2
        #             lowvalue = temp20AVG - std * 2
        #         else:
        #             std = 0
        #             highvalue = 0
        #             lowvalue = 0
        #         ##############################################################
        #         #로봇에 보낼 용도#########################################################
        #         self.queue_20min.put([code, mintime, temp20AVG, std, highvalue, lowvalue])
        #         ##########################################################################
        #         self.tick_bollinger[code][-1][2] = std
        #         self.tick_bollinger[code][-1][3] = highvalue
        #         self.tick_bollinger[code][-1][4] = lowvalue
        #         # list_qtemp = [code, self.tick_1mindata[code].체결시간[-1], self.tick_1mindata[code].현재가[-1], \
        #         #     self.tick_1mindata[code].거래량[-1], self.tick_1mindata[code].고가[-1], self.tick_1mindata[code].저가[-1], \
        #         #     self.ATR[code][-1][2], self.ATR[code][-1][3], self.ATR[code][-1][4], self.ewm_10[code][-1][2]]
        #         # self.tick_1minQ.put(list_qtemp)
        #         ########################################
        #     else:
        #         if code in self.ewm_20.keys():
        #             #####################bollinger################################
        #             if len(self.ewm_20[code]) > 20:
        #                 for i in self.ewm_20[code][-20:]:
        #                     stdvalue.append(i[2])
        #                 std = statistics.stdev(stdvalue)
        #                 highvalue = temp20AVG + std * 2
        #                 lowvalue = temp20AVG - std * 2
        #             else:
        #                 std = 0
        #                 highvalue = 0
        #                 lowvalue = 0
        #             ##############################################################                    
        #             #DB
        #             if not self.ewm_20[code] == []:
        #                 self.queue_ewm_20.put(self.ewm_20[code][-1])
        #             if not self.tick_bollinger[code] == []:
        #                 self.queue_bollinger.put(self.tick_bollinger[code][-1])
        #             else:
        #                 self.queue_bollinger.put([code, mintime, temp20AVG, std, highvalue, lowvalue])
        #                 #로봇에 보낼 용도#######################
        #                 # list_qtemp = [code, self.tick_1mindata[code].체결시간[-1], self.tick_1mindata[code].현재가[-1], \
        #                 #     self.tick_1mindata[code].거래량[-1], self.tick_1mindata[code].고가[-1], self.tick_1mindata[code].저가[-1], \
        #                 #     self.ATR[code][-1][2], self.ATR[code][-1][3], self.ATR[code][-1][4], self.ewm_10[code][-1][2]]
        #                 # self.tick_1minQ.put(list_qtemp)
        #             ########################################
        #             self.ewm_20[code].append([code, mintime, temp20AVG, mindate])

        # #30EWM
        # if len(self.tick_1mindata[code].체결시간) > 30:
        #     temp30AVG = 0
        #     for i in range(len(self.tick_1mindata[code].체결시간), len(self.tick_1mindata[code].체결시간)-30, -1):
        #         temp30AVG += self.tick_1mindata[code].현재가[i-1] / 30
        #     if not code in self.ewm_30.keys():
        #         self.ewm_30[code] = []
        #     if temptime == mintime:
        #         if self.ewm_30[code] == []:
        #             self.ewm_30[code].append([code, mintime, temp30AVG, mindate])
        #         self.ewm_30[code][-1][2] = temp30AVG
        #     else:
        #         if code in self.ewm_30.keys():
        #             if not self.ewm_30[code] == []:
        #                 self.queue_ewm_30.put(self.ewm_30[code][-1])
        #             # alex.append([code, mintime, temp30AVG, mindate])
        #             self.ewm_30[code].append([code, mintime, temp30AVG, mindate])
        # # if len(alex) >= 3:
        # #     self.ewmQ.put(alex)
                
    def removeClient(self, addr, client):
        for code in self.clients.keys():
            if self.clients[code] == client:
                break
        # for k, v in enumerate(self.clients):
        #     if v == client:
        #         idx = k
        #         break
        client.close()
        self.ip.remove(addr)
        # self.clients.remove(client)
        for k, v in enumerate(self.threads):
            if v.getName() == self.clients[code][1]:
                del self.threads[k]
                break
        del self.clients[code]
        self.resourceInfo()
    
    # def removeAllClients(self):
    #     for c in self.clients:
    #         c.close()
    #     self.ip.clear()
    #     self.clients.clear()
    #     self.threads.clear()
    #     self.resourceInfo()
    
    def resourceInfo(self):
        print('Number of Client ip\t: ', len(self.ip))
        print('Number of Client socket\t: ', len(self.clients))
        print('Number of Client thread\t: ', len(self.threads))

                
    ##########################################################################

if __name__ == '__main__':
    # manager = Manager()
    queue_Tick, queue_1min, queue_ATR, queue_ewm_5, queue_ewm_20, queue_ewm_30, queue_20min = \
    Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue()

    BuyQ1, SellQ1, BuyQ2, SellQ2, BuyQ3, SellQ3, BuyQ4, SellQ4, BuyQ5, SellQ6 = \
    Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue(), Queue()

    Stock1Q, Stock2Q, Stock3Q, Stock4Q, Stock5Q = Queue(), Queue(), Queue(), Queue(), Queue()
    tick_1minQ1, tick_1minQ2 = Queue(), Queue()
    queue_30min, queue_30minDB, queue_30fromDB, queue_bollingerDB, queue_5fromDB = Queue(), Queue(), Queue(), Queue(), Queue()
    queue_5min, queue_5minDB, queue_ewm_5DB = Queue(), Queue(), Queue()


    # tick_1mindata = manager.dict()

    #메인 프로세스
    wc = Process(target=Server_Connector, args=(BuyQ1, SellQ1, Stock1Q,   \
        queue_Tick, queue_1min, queue_ATR, queue_ewm_5, queue_ewm_20, queue_ewm_30, \
        tick_1minQ1, queue_30min, Stock4Q, Stock3Q, queue_30fromDB, queue_20min, queue_5min, \
        BuyQ4, SellQ4, tick_1minQ2, queue_ewm_5DB, queue_5fromDB))
    #DB 프로세스
    update_data = Process(target=Update_Data, name='DB_Updater',args=(queue_Tick, queue_1min, queue_ATR, \
        queue_ewm_5DB, queue_ewm_20, queue_ewm_30, BuyQ1, queue_30minDB, queue_5minDB, queue_bollingerDB), daemon=True)
    
    #로봇 프로세스
    # trading_bot_proc = Process(target=Three_dimension, name='Three_dimension',args=(BuyQ, SellQ, StockQ, EwmQ), daemon=True)

    # trading_bot_proc = Process(target=Parabolic, name='Keltner',args=(tick_1minQ, BuyQ, SellQ), daemon=True)

    # trading_bot_proc = Process(target=CrossUp60, name='CrossUp60',args=(queue_30min, BuyQ, SellQ, tick_1minQ, Stock2Q), daemon=True)

    # trading_bot_proc1 = Process(target=Median30, name='Median30',args=(queue_30min, BuyQ1, SellQ1, tick_1minQ1, Stock1Q, queue_30minDB, queue_30fromDB, queue_20min), daemon=True)

    trading_bot_proc2 = Process(target=stUP5, name='stUP5',args=(queue_5min, BuyQ4, SellQ4, tick_1minQ2, Stock4Q, queue_ewm_5, queue_20min, queue_5fromDB, queue_5minDB, queue_bollingerDB), daemon=True)

    wc.start()
    update_data.start()
    # trading_bot_proc1.start()
    trading_bot_proc2.start()
    wc.join()
    update_data.join()
    # trading_bot_proc1.join()
    trading_bot_proc2.join()




