import os
import sys
from threading import Thread
import datetime
import statistics

class stUP5():
    def __init__(self, queue_5min, BuyQ4, SellQ4, tick_1minQ2, Stock4Q, queue_ewm_5DB, queue_20min, queue_5fromDB, queue_5minDB, queue_bollingerDB):
        self.stocklist = {}
        self.tick_5min_dic = {}
        self.MA5_dic = {}
        self.MA20_dic = {}
        self.tick_bollinger = {}
        self.buylist = {}
        self.selllist = {}
        self.tick_1min_dic = {}
        self.분할매수 = {}
        self.분할매도 = {}
        self.손절 = {}
        self.queue_5min = queue_5min
        self.tick_1minQ = tick_1minQ2
        self.buyQ = BuyQ4
        self.sellQ = SellQ4        
        self.stockQ = Stock4Q
        self.queue_5minDB = queue_5minDB
        self.queue_5fromDB = queue_5fromDB
        self.queue_bollingerDB = queue_bollingerDB
        self.start()

    def start(self):
        while True:
            if not self.stockQ.empty():
                stock = self.stockQ.get()
                for key in stock.keys():
                    if not key in self.stocklist.keys():
                        self.stocklist[key] = []
                    if type(stock[key]) == list:
                        self.stocklist[key] += stock[key]
                    else:
                        self.stocklist[key].append(stock[key])

            if not self.queue_5fromDB.empty():
                if not code in self.tick_5min_dic.keys():
                    self.tick_5min_dic[code] = []                
                tick_5min = self.queue_5fromDB.get()
                code = tick_5min[0]
                체결시간 = tick_5min[1]
                가격 = int(tick_5min[2])
                거래량 = int(tick_5min[3])
                고가 = int(tick_5min[4])
                저가 = int(tick_5min[5])
                시가 = int(tick_5min[6])
                vwap = float(tick_5min[7])
                누적거래량 = self.tick_1min_dic[code][-1][8]
                누적거래대금 = self.tick_1min_dic[code][-1][9]
                list_data = [체결시간, 가격, 거래량, 고가, 저가, 시가, vwap, 누적거래량, 누적거래대금]
                self.tick_5min_dic[code].append(list_data)


            # if not self.queue_5min.empty():
            #     tick_5min = self.queue_5min.get()
            #     code = tick_5min[0]
            #     체결시간 = tick_5min[1]
            #     현재가 = int(tick_5min[2])
            #     거래량 = int(tick_5min[3])
            #     고가 = int(tick_5min[4])
            #     저가 = int(tick_5min[5])
            #     시가 = int(tick_5min[6])
            #     전체누적거래량 = int(tick_5min[7])

            #     if not code in self.tick_5min_dic.keys():
            #         self.tick_5min_dic[code] = []
            #         누적거래대금 = 현재가 * 거래량
            #         vwap = 누적거래대금 / 거래량
                    
            #         list_5mintemp = [체결시간, 현재가, 거래량, 고가, 저가, 시가, vwap, 전체누적거래량, 누적거래대금]
            #         self.tick_5min_dic[code].append(list_5mintemp)
            #     else:
            #         확인_5분 = int(체결시간[2:4])
            #         거래대금 = 현재가 * 거래량
            #         전확인_5분 = int(self.tick_5min_dic[code][-1][0][2:4])
            #         전_거래대금 = int(self.tick_5min_dic[code][-1][8])
            #         누적거래대금 = 거래대금 + 전_거래대금
            #         vwap = 누적거래대금 / 전체누적거래량

            #         if 확인_5분%5 == 0 and 전확인_5분%5 != 0:
            #             list_5mintemp = [체결시간, 현재가, 거래량, 고가, 저가, 시가, vwap, 전체누적거래량, 누적거래대금]
            #             self.tick_5min_dic[code].append(list_5mintemp)
            #         else:
            #             self.tick_5min_dic[code][-1][0] = 체결시간
            #             self.tick_5min_dic[code][-1][1] = 현재가
            #             self.tick_5min_dic[code][-1][2] = 거래량
            #             if 고가 > self.tick_5min_dic[code][-1][3]:
            #                 self.tick_5min_dic[code][-1][3] = 고가
            #             if 저가 < self.tick_5min_dic[code][-1][4]:
            #                 self.tick_5min_dic[code][-1][4] = 저가
            #             self.tick_5min_dic[code][-1][6] = vwap
            #             self.tick_5min_dic[code][-1][7] = 전체누적거래량
            #             self.tick_5min_dic[code][-1][8] = 누적거래대금



            # #장중 켰을때 DB에서 불러옴
            # if not self.queue_5fromDB.empty():
            #     tick_5minDB = self.queue_5fromDB.get()
            #     code = tick_5minDB[0]
            #     tempt = tick_5minDB[1]
            #     temp_h = tempt[:2]
            #     temp_m = tempt[2:4]
            #     if temp_h == '09' and int(temp_m) < 5:
            #         if not code in self.tick_5min_dic.keys():
            #             self.tick_5min_dic[code] = []
            #             self.tick_5min_dic[code].append(tick_5minDB)

            if not self.tick_1minQ.empty():
                tick_1min = self.tick_1minQ.get() 
                code = tick_1min[0]
                체결시간 = tick_1min[1]
                가격 = tick_1min[2]
                거래량 = tick_1min[3]
                시가 = tick_1min[4]
                고가 = tick_1min[5]
                저가 =  tick_1min[6]
                전체누적거래량 = tick_1min[7]
                전체누적거래대금 = tick_1min[8]
                체결강도 = float(tick_1min[9])
                mindate = tick_1min[10]
                체결강도5 = 0
                vwap = 0
                분5_고가 = 0
                분5_저가 = 0
                분5_시가 = 0
                분5_거래량 = 0
                분5_누적거래량 = 0
                분5_누적거래대금 = 0
                vwap = 0
                if not code in self.tick_1min_dic.keys():
                    self.tick_1min_dic[code] = []
                    # high_d = 고가
                    # low_d = 저가
                    # line_236 = ((high_d - low_d)) * 0.764 + low_d
                    # line_382 = ((high_d - low_d)) * 0.618 + low_d
                    # line_50 = ((high_d - low_d)) * 0.5 + low_d
                    # line_618 = ((high_d - low_d)) * 0.382 + low_d
                    self.tick_1min_dic[code].append([체결시간, 가격, 거래량, 시가, 고가, 저가, 전체누적거래량, 전체누적거래대금, 체결강도, 체결강도5]) #high_d, low_d, 체결강도, 체결강도5, line_236, line_382, line_50, line_618])
                #5분 데이터 만들기
                if not code in self.tick_5min_dic.keys():
                    self.tick_5min_dic[code] = []
                if len(self.tick_1min_dic[code]) > 5:
                    분5_고가 = self.tick_1min_dic[code][-1][4]
                    분5_저가 = self.tick_1min_dic[code][-1][5]
                    분5_시가 = self.tick_1min_dic[code][-1][3]
                    분5_누적거래량 = self.tick_1min_dic[code][-1][6]
                    분5_누적거래대금 = self.tick_1min_dic[code][-1][7]
                    vwap = 분5_누적거래대금 / 분5_누적거래량
                    for i in range(len(self.tick_1min_dic[code]), len(self.tick_1min_dic[code]) - 5, -1):
                        전고가_5 = self.tick_1min_dic[code][i-1][4]
                        전저가_5 = self.tick_1min_dic[code][i-1][5]
                        if 분5_고가 < 전고가_5:
                            분5_고가 = 전고가_5
                        if 분5_저가 > 전저가_5:
                            분5_저가 = 전저가_5
                        분5_거래량 = self.tick_1min_dic[code][i-1][2]
                    if self.tick_5min_dic[code] == []:
                        self.tick_5min_dic[code].append([체결시간, 가격, 분5_거래량, 분5_고가, 분5_저가, 분5_시가, vwap, 분5_누적거래량, 분5_누적거래대금])                        
                    if int(체결시간[2:4])%5 == 0 and int(self.tick_5min_dic[code][-1][0][2:4])%5 != 0:
                        #DB
                        list_5toDB = [code, 체결시간, self.tick_5min_dic[code][-1][1], self.tick_5min_dic[code][-1][2], self.tick_5min_dic[code][-1][3], self.tick_5min_dic[code][-1][4], self.tick_5min_dic[code][-1][5], \
                            mindate, self.tick_5min_dic[code][-1][6], self.tick_5min_dic[code][-1][7], self.tick_5min_dic[code][-1][8]]
                        self.queue_5minDB.put(list_5toDB)
                        list_5mintemp = [체결시간, 가격, 분5_거래량, 분5_고가, 분5_저가, 분5_시가, vwap, 분5_누적거래량, 분5_누적거래대금]
                        self.tick_5min_dic[code].append(list_5mintemp)

                    else:
                        if self.tick_5min_dic[code] == []:
                            self.tick_5min_dic[code].append([체결시간, 가격, 분5_거래량, 분5_고가, 분5_저가, 분5_시가, vwap, 분5_누적거래량, 분5_누적거래대금])
                        #5분봉
                        self.tick_5min_dic[code][-1][0] = 체결시간
                        self.tick_5min_dic[code][-1][1] = 가격
                        self.tick_5min_dic[code][-1][2] = 분5_거래량
                        if 고가 > self.tick_5min_dic[code][-1][3]:
                            self.tick_5min_dic[code][-1][3] = 고가
                        if 저가 < self.tick_5min_dic[code][-1][4]:
                            self.tick_5min_dic[code][-1][4] = 저가
                        self.tick_5min_dic[code][-1][6] = vwap
                        self.tick_5min_dic[code][-1][7] = 분5_누적거래량
                        self.tick_5min_dic[code][-1][8] = 분5_누적거래대금
                #5MA
                if len(self.tick_5min_dic[code]) > 5:
                    temp5AVG = 0
                    if not code in self.MA5_dic.keys():
                        self.MA5_dic[code] = []
                    for i in range(len(self.tick_5min_dic[code]), len(self.tick_5min_dic[code])-5, -1):
                        temp5AVG += self.tick_5min_dic[code][i-1][1] / 5
                    if self.MA5_dic[code] == []:
                        self.MA5_dic[code].append([체결시간, temp5AVG])
                    temptime = self.MA5_dic[code][-1][0]
                    if temptime == 체결시간:
                        self.MA5_dic[code][-1][1] = temp5AVG
                    else:
                        if code in self.MA5_dic.keys():
                            self.MA5_dic[code].append([체결시간, temp5AVG])
                #20MA
                if len(self.tick_5min_dic[code]) > 20:
                    temp20AVG = 0
                    stdvalue = list()
                    std = 0
                    highvalue = 0
                    lowvalue = 0
                    for i in range(len(self.tick_5min_dic[code]), len(self.tick_5min_dic[code])-20, -1):
                        temp20AVG += self.tick_5min_dic[code][i-1][1] / 20
                    if not code in self.MA20_dic.keys():
                        self.MA20_dic[code] = []
                    if not code in self.tick_bollinger.keys():
                        self.tick_bollinger[code] = []
                    if self.MA20_dic[code] == []:
                        self.MA20_dic[code].append([체결시간, temp20AVG])
                    if self.tick_bollinger[code] == []:
                        self.tick_bollinger[code].append([체결시간, temp20AVG, std, highvalue, lowvalue])                        
                    temptime = self.MA20_dic[code][-1][0]
                    if temptime == 체결시간:
                        self.MA20_dic[code][-1][1] = temp20AVG
                        #####################bollinger################################
                        for i in self.tick_5min_dic[code][-20:]:
                            stdvalue.append(i[1])
                        std = statistics.stdev(stdvalue)
                        highvalue = temp20AVG + std * 2
                        lowvalue = temp20AVG - std * 2
                        ##############################################################
                        self.tick_bollinger[code][-1][2] = std
                        self.tick_bollinger[code][-1][3] = highvalue
                        self.tick_bollinger[code][-1][4] = lowvalue
                    else:
                        if code in self.MA20_dic.keys():
                            self.MA20_dic[code].append([체결시간, temp20AVG])
                        if code in self.tick_bollinger.keys():
                            #####################bollinger################################
                            for i in self.MA20_dic[code][-20:]:
                                stdvalue.append(i[2])
                            std = statistics.stdev(stdvalue)
                            highvalue = temp20AVG + std * 2
                            lowvalue = temp20AVG - std * 2
                            self.tick_bollinger[code].append([체결시간, temp20AVG, std, highvalue, lowvalue])
                            self.queue_bollingerDB.put([code, 체결시간, std, highvalue, lowvalue, mindate, temp20AVG])

                            ############################################################## 

                temptime = self.tick_1min_dic[code][-1][1]
                if temptime == 체결시간:
                    if code in self.tick_1min_dic.keys():
                        if code in self.tick_5min_dic.keys():
                            for key in self.stocklist.keys():
                                if code in self.stocklist[key]:
                                    if len(self.tick_1min_dic[code]) > 5:
                                        temp5체결 = 0
                                        for i in range(len(self.tick_1min_dic[code]), len(self.tick_1min_dic[code]) - 5, -1):
                                            temp5체결 += float(self.tick_1min_dic[code][i-1][9])
                                        if temp5체결 != 0:
                                            체결강도5 = temp5체결 / 5
                                    self.tick_1min_dic[code][-1][10] = 체결강도5
                                    high_5 = self.tick_5min_dic[code][-1][3]
                                    low_5 = self.tick_5min_dic[code][-1][4]
                                    open_5 = self.tick_5min_dic[code][-1][5]
####################                #############매수조건######################################################################
                                    if not code in self.tick_5min_dic.keys():
                                        vwap = self.tick_5min_dic[code][-1][6]
                                        위_vwap = 가격 > vwap





                                    if  not 가격 < open_5:
                                        #종가>중앙1차 and 중앙1차>시가
                                        if 가격 > high_5 and high_5 >= self.tick_1min_dic[code][-1][2]:
                                            # if float(self.tick_1min_dic[code][-1][9]) > 100 and 체결강도5 > 100:
                                            if not code in self.buylist.keys():
                                                    self.buyQ.put({key: ['BUY1차', code, 가격, 체결시간]})
                                                    self.buylist[code] = []
                                                    self.selllist[code] = []
                                                    self.buylist[code].append([code, 가격, 체결시간, '매수1차'])
                                                    self.분할매수[code] = 0
                                                    self.분할매도[code] = 0
                                                    self.손절[code] = 0
                                                    print(f"전략2 BUY!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                    print(f"체결강도: {self.tick_1min_dic[code][-1][9]}, 5분체결강도: {체결강도5}")
                                                    tmnow = datetime.datetime.now()
                                                    print(str(tmnow.minute) + ':' + str(tmnow.second))
####################                   ###########################################################################################
####################                   #############매도조건######################################################################
                                    if code in self.buylist.keys():
                                        if high_d > high_5 * 1.02:
                                            지지 = high_5 * 1.015
                                        else:
                                            지지 = open_5
                                    #익절
                                    if code in self.buylist.keys():
                                        if code in self.분할매도.keys():
                                            if self.분할매도[code] == 0 and self.손절[code] == 0:
                                                if 가격 >= float(self.tick_1min_dic[code][-1][2]) * 1.03:
                                                    self.sellQ.put({key: ['SELL1차', code, 가격, 체결시간]})
                                                    self.selllist[code].append([code, 가격, 체결시간, '익절1차'])
                                                    self.분할매도[code] = 1
                                                    self.손절[code] = 1
                                                    print(f"전략2 SELL 3%익절!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                    tmnow = datetime.datetime.now()
                                                    print(str(tmnow.minute)  + ':' + str(tmnow.second))
                                            elif  self.분할매도[code] == 1:
                                                if 가격 < 지지 and 지지 < self.tick_1min_dic[code][-1][2]:
                                                    self.sellQ.put({key: ['SELL2차', code, 가격, 체결시간]})
                                                    self.selllist[code].append([code, 가격, 체결시간, '익절1차'])
                                                    self.분할매도[code] = 2
                                                    self.손절[code] = 2
                                                    print(f"전략2 SELL 1%익절!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                    tmnow = datetime.datetime.now()
                                                    print(str(tmnow.minute)  + ':' + str(tmnow.second))                                                    
                                    #손절
                                        mnow = datetime.datetime.now()
                                        m_hour = tmnow.hour
                                        m_min = tmnow.minute
                                        if not (self.손절[code] == 2 and self.분할매도[code] == 2):
                                            if 가격 < low_5 and low_5 < self.tick_1min_dic[code][-1][2]:
                                                if not code in self.selllist.keys():
                                                    self.selllist[code] = []
                                                self.sellQ.put({key: ['손절', code, 가격, 체결시간]})
                                                self.selllist[code].append([code, 가격, 체결시간, '손절'])
                                                self.손절[code] = 2
                                                self.분할매수[code] = 2
                                                self.분할매도[code] = 2
                                                print(f"전략2 SELL 손절!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                print(f"시가이탈: {open_5}")
                                                tmnow = datetime.datetime.now()
                                                print(str(tmnow.minute)  + ':' + str(tmnow.second))                                            
                                            elif self.손절[code] == False and int(m_hour) == 14 and int(m_min) == 20:
                                                #시간 손절
                                                pass
############################################################################################################################################                                            
                        #1분봉
                        self.tick_1min_dic[code][-1][1] = 가격
                        self.tick_1min_dic[code][-1][2] = 거래량
                        if 고가 > self.tick_1min_dic[code][-1][4]:
                            self.tick_1min_dic[code][-1][4] = 고가
                        if 저가 < self.tick_1min_dic[code][-1][5]:
                            self.tick_1min_dic[code][-1][5] = 저가
                        self.tick_1min_dic[code][-1][6] = 전체누적거래량
                        self.tick_1min_dic[code][-1][7] = 전체누적거래대금
                        # if self.tick_1min_dic[code][-1][7] < self.tick_1min_dic[code][-1][5]:
                        #     self.tick_1min_dic[code][-1][7] = self.tick_1min_dic[code][-1][5]
                        # if self.tick_1min_dic[code][-1][8] > self.tick_1min_dic[code][-1][6]:
                        #     self.tick_1min_dic[code][-1][8] = self.tick_1min_dic[code][-1][6]
                        self.tick_1min_dic[code][-1][8] = 체결강도

                else:
                    if code in self.tick_5min_dic.keys():
                        for key in self.stocklist.keys():
                            if code in self.stocklist[key]:
                                high_d = self.tick_1min_dic[code][-1][7]
                                low_d = self.tick_1min_dic[code][-1][8]
                                line_236 = ((high_d - low_d)) * 0.764 + low_d
                                line_382 = ((high_d - low_d)) * 0.618 + low_d
                                line_50 = ((high_d - low_d)) * 0.5 + low_d
                                line_618 = ((high_d - low_d)) * 0.382 + low_d
                                high_5 = self.tick_5min_dic[code][-1][4]
                                low_5 = self.tick_5min_dic[code][-1][5]
                                open_5 = self.tick_5min_dic[code][-1][6]
                                if len(self.tick_1min_dic[code]) >=4:
                                    temp5체결 = 0
                                    for i in range(len(self.tick_1min_dic[code]), len(self.tick_1min_dic[code]) - 4, -1):
                                        temp5체결 += float(self.tick_1min_dic[code][i-1][9])
                                    temp5체결 += 체결강도
                                    if temp5체결 != 0:
                                        체결강도5 = temp5체결 / 5
#################################매수조건######################################################################
                                if  not 가격 < open_5:
                                    #종가>중앙1차 and 중앙1차>시가
                                    if 가격 > high_5 and high_5 >= self.tick_1min_dic[code][-1][2]:
                                        # if float(self.tick_1min_dic[code][-1][9]) > 100 and 체결강도5 > 100:
                                        if not code in self.buylist.keys():
                                                self.buyQ.put({key: ['BUY1차', code, 가격, 체결시간]})
                                                self.buylist[code] = []
                                                self.selllist[code] = []
                                                self.buylist[code].append([code, 가격, 체결시간, '매수1차'])
                                                self.분할매수[code] = 0
                                                self.분할매도[code] = 0
                                                self.손절[code] = 0
                                                print(f"전략2 BUY!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                print(f"체결강도: {self.tick_1min_dic[code][-1][9]}, 5분체결강도: {체결강도5}")
                                                tmnow = datetime.datetime.now()
                                                print(str(tmnow.minute) + ':' + str(tmnow.second))
####################               ###########################################################################################
####################               #############매도조건######################################################################
                                if code in self.buylist.keys():
                                    if high_d > high_5 * 1.02:
                                        지지 = high_5 * 1.015
                                    else:
                                        지지 = open_5
                                    #익절
                                    if code in self.buylist.keys():
                                        if code in self.분할매도.keys():
                                            if self.분할매도[code] == 0 and self.손절[code] == 0:
                                                if 가격 >= float(self.tick_1min_dic[code][-1][2]) * 1.03:
                                                    self.sellQ.put({key: ['SELL1차', code, 가격, 체결시간]})
                                                    self.selllist[code].append([code, 가격, 체결시간, '익절1차'])
                                                    self.분할매도[code] = 1
                                                    self.손절[code] = 1
                                                    print(f"전략2 SELL 3%익절!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                    tmnow = datetime.datetime.now()
                                                    print(str(tmnow.minute)  + ':' + str(tmnow.second))
                                            elif  self.분할매도[code] == 1:
                                                if 가격 < 지지 and 지지 < self.tick_1min_dic[code][-1][2]:
                                                    self.sellQ.put({key: ['SELL2차', code, 가격, 체결시간]})
                                                    self.selllist[code].append([code, 가격, 체결시간, '익절1차'])
                                                    self.분할매도[code] = 2
                                                    self.손절[code] = 2
                                                    print(f"전략2 SELL 1%익절!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                    tmnow = datetime.datetime.now()
                                                    print(str(tmnow.minute)  + ':' + str(tmnow.second))                                                    
                                    #손절
                                        mnow = datetime.datetime.now()
                                        m_hour = tmnow.hour
                                        m_min = tmnow.minute
                                        if not (self.손절[code] == 2 and self.분할매도[code] == 2):
                                            if 가격 < low_5 and low_5 < self.tick_1min_dic[code][-1][2]:
                                                if not code in self.selllist.keys():
                                                    self.selllist[code] = []
                                                self.sellQ.put({key: ['손절', code, 가격, 체결시간]})
                                                self.selllist[code].append([code, 가격, 체결시간, '손절'])
                                                self.손절[code] = 2
                                                self.분할매수[code] = 2
                                                self.분할매도[code] = 2
                                                print(f"전략2 SELL 손절!! 종목코드: {code}, 가격: {가격}, 시간: {tick_1min[1]}")
                                                print(f"시가이탈: {open_5}")
                                                tmnow = datetime.datetime.now()
                                                print(str(tmnow.minute)  + ':' + str(tmnow.second))                                            
                                            elif self.손절[code] == False and int(m_hour) == 14 and int(m_min) == 20:
                                                #시간 손절
                                                pass
################################################################################################################
                    # if self.tick_1min_dic[code][-1][7] < self.tick_1min_dic[code][-1][5]:
                    #     high_d = 고가
                    # else:
                    #     high_d = self.tick_1min_dic[code][-1][7]
                    # if self.tick_1min_dic[code][-1][8] > self.tick_1min_dic[code][-1][6]:
                    #     low_d = 저가
                    # else:
                    #     low_d = self.tick_1min_dic[code][-1][8]

                    # line_236 = ((high_d - low_d)) * 0.764 + low_d
                    # line_382 = ((high_d - low_d)) * 0.618 + low_d
                    # line_50 = ((high_d - low_d)) * 0.5 + low_d
                    # line_618 = ((high_d - low_d)) * 0.382 + low_d                    
                    self.tick_1min_dic[code].append([체결시간, 가격, 거래량, 시가, 고가, 저가, 전체누적거래량, 전체누적거래대금, 체결강도, 체결강도5])
                    # self.tick_5min_dic[code].append([체결시간, 가격, 분5_거래량, 분5_고가, 분5_저가, 분5_시가, vwap, 분5_누적거래량, 분5_누적거래대금])
################################################################################################################
            #파일저장
            # tmnow = datetime.datetime.now()
            # temp_hour = tmnow.hour
            # temp_min = tmnow.minute
            # if int(temp_hour) == 15 and int(temp_min) >= 35:
            #     FileName_buy = f"buylist.csv"
            #     FileName_sell = f"selllist.csv"
            #     DirName = 'C:\\Datas\\Data_Kiwoom'
            #     DirFileName_buy = f"{DirName}\\{FileName_buy}"
            #     DirFileName_sell = f"{DirName}\\{FileName_sell}"
            #     if os.path.isfile(DirFileName_buy):
            #         DataString_buy = ""
            #     else:
            #         DataString_buy = f"종목코드, 가격, 시간, 유형\n"
            #     if os.path.isfile(DirFileName_sell):
            #         DataString_sell = ""
            #     else:
            #         DataString_sell = f"종목코드, 가격, 시간, 유형\n"

            #     for key in self.buylist.keys():
            #         for i in range(len(self.buylist[key])):
            #             DataString_buy = f"{DataString_buy}{self.buylist[key][i][0]}, {self.buylist[key][i][1]}, {self.buylist[key][i][2]}, {self.buylist[key][i][3]}\n"
            #     for key in self.selllist.keys():
            #         for i in range(len(self.selllist[key])):
            #             DataString_sell = f"{DataString_sell}{self.selllist[key][i][0]}, {self.selllist[key][i][1]}, {self.selllist[key][i][2]}, {self.selllist[key][i][3]}\n"
            #     if not os.path.isdir(DirName):
            #         os.mkdir(DirName)
            #     dirlist = DirName.split('\\')
            #     for i in range(2, len(dirlist) + 1):
            #         currpath = '\\'.join(dirlist[:i])
            #         if not os.path.isdir(currpath):
            #             os.mkdir(currpath)
            #     try:
            #         with open(DirFileName_buy, "a") as f:
            #             f.write(DataString_buy)
            #         print(f"File writting complete : {FileName_buy}")
            #         with open(DirFileName_sell, "a") as f:
            #             f.write(DataString_sell)
            #         print(f"File writting complete : {FileName_sell}")
            #         break                    
            #     except Exception as e:
            #         print(f"File writting error : {e}")


