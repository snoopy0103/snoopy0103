import os
import sys
from threading import Thread
import datetime

class Median30():
    def __init__(self, queue_30min, BuyQ1, SellQ1, tick_1minQ1, Stock1Q, queue_30minDB, queue_30fromDB):
        self.stocklist = {}
        self.tick_30min_dic = {}
        self.buylist = {}
        self.selllist = {}
        self.tick_1min_dic = {}
        self.mv20min = {}
        self.분할매수 = {}
        self.분할매도 = {}
        self.손절 = {}
        self.queue_30min = queue_30min
        self.tick_1minQ = tick_1minQ1
        self.buyQ = BuyQ1
        self.sellQ = SellQ1        
        self.stockQ = Stock1Q
        self.queue_30minDB = queue_30minDB
        self.queue_30fromDB = queue_30fromDB
        # self.queue_20min = queue_20min
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

            # if not self.queue_20min.empty():
            #     temp_min20 = self.queue_20min.get()
            #     code = temp_min20[0]
            #     min20 = temp_min20[1]
            #     if not code in self.mv20min.keys():
            #         self.mv20min[code] = []
            #         self.mv20min[code].append([min20])
            #     else:
            #         self.mv20min[code].append([min20])

            if not self.queue_30min.empty():
                tick_30min = self.queue_30min.get()
                code = tick_30min[0]
                tempt = tick_30min[1]
                temp_h = tempt[:2]
                temp_m = tempt[2:4]
                if int(temp_h) == 9 and int(temp_m) < 30:
                    if not code in self.tick_30min_dic.keys():
                        self.tick_30min_dic[code] = []
                        self.tick_30min_dic[code].append(tick_30min)
                        self.queue_30minDB.put(tick_30min)
                # if not code in self.tick_30min_dic.keys():
                #         self.tick_30min_dic[code] = []
                #         self.tick_30min_dic[code].append(tick_30min)
            #장중 켰을때 DB에서 불러옴
            if not self.queue_30fromDB.empty():
                tick_30minDB = self.queue_30fromDB.get()
                code = tick_30minDB[0]
                tempt = tick_30minDB[1]
                temp_h = tempt[:2]
                temp_m = tempt[2:4]
                if temp_h == '09' and int(temp_m) < 30:
                    if not code in self.tick_30min_dic.keys():
                        self.tick_30min_dic[code] = []
                        self.tick_30min_dic[code].append(tick_30minDB)

            if not self.tick_1minQ.empty():
                tick_1min = self.tick_1minQ.get() 
                code = tick_1min[0]
                mintime = tick_1min[1]
                price = tick_1min[2]
                volume = tick_1min[3]
                openp = tick_1min[4]
                high = tick_1min[5]
                low =  tick_1min[6]
                if not code in self.tick_1min_dic.keys():
                    self.tick_1min_dic[code] = []
                    high_d = high
                    low_d = low
                    self.tick_1min_dic[code].append([code, mintime, price, volume, openp, high, low, high_d, low_d])
                temptime = self.tick_1min_dic[code][-1][1]
                if temptime == mintime:
                    # if code in self.tick_30min_dic.keys():
                    #     for key in self.stocklist.keys():
                    #         if code in self.stocklist[key]:
                    #             high_d = self.tick_1min_dic[code][-1][7]
                    #             low_d = self.tick_1min_dic[code][-1][8]
                    #             high_30 = self.tick_30min_dic[code][-1][4]
                    #             low_30 = self.tick_30min_dic[code][-1][5]
                    #             중앙1차 = (high_30 + low_30) / 2
                    #             중앙2차 = (중앙1차 + low_30) / 2
                    #             청산 = (high_30 + 중앙1차) / 2
                    self.tick_1min_dic[code][-1][2] = price
                    self.tick_1min_dic[code][-1][3] = volume
                    if high > self.tick_1min_dic[code][-1][5]:
                        self.tick_1min_dic[code][-1][5] = high
                    if low < self.tick_1min_dic[code][-1][6]:
                        self.tick_1min_dic[code][-1][6] = low
                    if self.tick_1min_dic[code][-1][7] < self.tick_1min_dic[code][-1][5]:
                        self.tick_1min_dic[code][-1][7] = self.tick_1min_dic[code][-1][5]
                    if self.tick_1min_dic[code][-1][8] > self.tick_1min_dic[code][-1][6]:
                        self.tick_1min_dic[code][-1][8] = self.tick_1min_dic[code][-1][6]                    
                else:
                    if code in self.tick_30min_dic.keys():
                        for key in self.stocklist.keys():
                            if code in self.stocklist[key]:
                                high_d = self.tick_1min_dic[code][-1][7]
                                low_d = self.tick_1min_dic[code][-1][8]
                                high_30 = self.tick_30min_dic[code][-1][4]
                                low_30 = self.tick_30min_dic[code][-1][5]
                                중앙1차 = (high_30 + low_30) / 2
                                중앙2차 = (중앙1차 + low_30) / 2
                                청산 = (high_30 + 중앙1차) / 2
#################################매수조건######################################################################
                                #30분고점을 한번이라도 돌파 and 30분저점을 한번이라도 돌파 했으면 사지 않음
                                if  high_30 >= high_d and low_30 <= low_d:
                                    #종가>중앙1차 and 중앙1차>시가
                                    if self.tick_1min_dic[code][-1][2] > 중앙1차 and 중앙1차 > self.tick_1min_dic[code][-1][4]:
                                        if not code in self.buylist.keys():
                                                self.buyQ.put({key: ['BUY1차', code, price, mintime]})
                                                self.buylist[code] = []
                                                self.selllist[code] = []
                                                self.buylist[code].append([code, price, mintime, '매수1차'])
                                                self.분할매수[code] = 0
                                                self.분할매도[code] = 0
                                                self.손절[code] = 0
                                                print(f"전략1 BUY 1차!! 종목코드: {code}, 가격: {price}, 시간: {tick_1min[1]}")
                                                print(f"중앙1차: {중앙1차}")
                                                tmnow = datetime.datetime.now()
                                                print(str(tmnow.minute) + ':' + str(tmnow.second))
                                    #종가>중앙2차 and 중앙2차>시가
                                    elif self.tick_1min_dic[code][-1][2] > 중앙2차 and 중앙2차 > self.tick_1min_dic[code][-1][4]:
                                        if code in self.분할매수.keys():
                                            if self.분할매수[code] == 0 and self.손절 == 0 and self.분할매도[code] == 0:
                                                self.buyQ.put({key: ['BUY2차', code, price, mintime]})
                                                self.buylist[code].append([code, price, mintime, '매수2차'])
                                                self.분할매수[code] = 1
                                                print(f"전략1 BUY 2차!! 종목코드: {code}, 가격: {price}, 시간: {tick_1min[1]}")
                                                print(f"중앙2차: {중앙2차}")
                                                tmnow = datetime.datetime.now()
                                                print(str(tmnow.minute)  + ':' + str(tmnow.second))
###############################################################################################################
#################################매도조건######################################################################
                                #익절
                                if code in self.buylist.keys():
                                    if code in self.분할매도.keys():
                                        if self.분할매도[code] == 0 and self.손절[code] == 0:
                                            #종가>30분고점 and 30분고점>시가
                                            if self.tick_1min_dic[code][-1][2] > high_30 and high_30 > self.tick_1min_dic[code][-1][4]:
                                                self.sellQ.put({key: ['SELL1차', code, price, mintime]})
                                                self.selllist[code].append([code, price, mintime, '익절1차'])
                                                self.분할매도[code] = 1
                                                print(f"전략1 SELL 1차!! 종목코드: {code}, 가격: {price}, 시간: {tick_1min[1]}")
                                                print(f"30분고점: {high_30}")
                                                tmnow = datetime.datetime.now()
                                                print(str(tmnow.minute)  + ':' + str(tmnow.second))                                                
                                        elif self.분할매도[code] == 1 and self.손절[code] == 0:
                                            #1차 익절후 청산라인에 오면 청산하자
                                            #종가<청산 and 청산<시가
                                            if price < 청산 and 청산 < self.tick_1min_dic[code][-1][4]:
                                                self.sellQ.put({key: ['SELL2차', code, price, mintime]})
                                                self.selllist[code].append([code, price, mintime, '익절2차'])
                                                self.분할매도[code] = 2
                                                self.손절[code] = 1
                                                print(f"전략1 SELL 2차 청산!! 종목코드: {code}, 가격: {price}, 시간: {tick_1min[1]}")
                                                print(f"청산: {청산}")
                                                tmnow = datetime.datetime.now()
                                                print(str(tmnow.minute)  + ':' + str(tmnow.second))                                                
                                            #20분봉을 하회할때 매도 하자
                                            if code in self.mv20min.keys():
                                                #청산을 하지 않았다면~
                                                if self.분할매도[code] == 1 and self.손절[code] == 0:
                                                    #시가>20분이평 and 20분이평 > 종가
                                                    if self.tick_1min_dic[code][-1][4] > self.mv20min[code][-1][0] and self.mv20min[code][-1][0] > self.tick_1min_dic[code][-1][2]:
                                                        self.sellQ.put({key: ['SELL2차', code, price, mintime]})
                                                        self.selllist[code].append([code, price, mintime, '익절2차'])
                                                        self.분할매도[code] = 2
                                                        self.손절[code] = 1
                                                        print(f"전략1 SELL 2차!! 종목코드: {code}, 가격: {price}, 시간: {tick_1min[1]}")
                                                        print(f"20분이평: {self.mv20min[code][-1][0]}")   
                                                        tmnow = datetime.datetime.now()
                                                        print(str(tmnow.minute)  + ':' + str(tmnow.second))                                                                                                         
                                #손절
                                if code in self.buylist.keys():
                                    mnow = datetime.datetime.now()
                                    m_hour = tmnow.hour
                                    m_min = tmnow.minute
                                    if self.손절[code] == 0 and self.분할매도[code] != 2:
                                        #종가<30분저점 and 30분저점<시가
                                        if self.tick_1min_dic[code][-1][2] < low_30 and low_30 < self.tick_1min_dic[code][-1][4]:
                                            if not code in self.selllist.keys():
                                                self.selllist[code] = []
                                            self.sellQ.put({key: ['손절', code, price, mintime]})
                                            self.selllist[code].append([code, price, mintime, '손절'])
                                            self.손절[code] = 1
                                            self.분할매수[code] = 1
                                            self.분할매도[code] = 2
                                            print(f"전략1 SELL 손절!! 종목코드: {code}, 가격: {price}, 시간: {tick_1min[1]}")
                                            print(f"30분저점: {low_30}")
                                            tmnow = datetime.datetime.now()
                                            print(str(tmnow.minute)  + ':' + str(tmnow.second))                                            
                                        elif self.손절[code] == False and int(m_hour) == 14 and int(m_min) == 20:
                                            #시간 손절
                                            pass
################################################################################################################
                    if self.tick_1min_dic[code][-1][7] < self.tick_1min_dic[code][-1][5]:
                        high_d = high
                    else:
                        high_d = self.tick_1min_dic[code][-1][7]
                    if self.tick_1min_dic[code][-1][8] > self.tick_1min_dic[code][-1][6]:
                        low_d = low
                    else:
                        low_d = self.tick_1min_dic[code][-1][8]
                    self.tick_1min_dic[code].append([code, mintime, price, volume, openp, high, low, high_d, low_d])

################################################################################################################
            #파일저장
            tmnow = datetime.datetime.now()
            temp_hour = tmnow.hour
            temp_min = tmnow.minute
            if int(temp_hour) == 15 and int(temp_min) >= 35:
                FileName_buy = f"buylist.csv"
                FileName_sell = f"selllist.csv"
                DirName = 'C:\\Datas\\Data_Kiwoom'
                DirFileName_buy = f"{DirName}\\{FileName_buy}"
                DirFileName_sell = f"{DirName}\\{FileName_sell}"
                if os.path.isfile(DirFileName_buy):
                    DataString_buy = ""
                else:
                    DataString_buy = f"종목코드, 가격, 시간, 유형\n"
                if os.path.isfile(DirFileName_sell):
                    DataString_sell = ""
                else:
                    DataString_sell = f"종목코드, 가격, 시간, 유형\n"

                for key in self.buylist.keys():
                    for i in range(len(self.buylist[key])):
                        DataString_buy = f"{DataString_buy}{self.buylist[key][i][0]}, {self.buylist[key][i][1]}, {self.buylist[key][i][2]}, {self.buylist[key][i][3]}\n"
                for key in self.selllist.keys():
                    for i in range(len(self.selllist[key])):
                        DataString_sell = f"{DataString_sell}{self.selllist[key][i][0]}, {self.selllist[key][i][1]}, {self.selllist[key][i][2]}, {self.selllist[key][i][3]}\n"
                if not os.path.isdir(DirName):
                    os.mkdir(DirName)
                dirlist = DirName.split('\\')
                for i in range(2, len(dirlist) + 1):
                    currpath = '\\'.join(dirlist[:i])
                    if not os.path.isdir(currpath):
                        os.mkdir(currpath)
                try:
                    with open(DirFileName_buy, "a") as f:
                        f.write(DataString_buy)
                    print(f"File writting complete : {FileName_buy}")
                    with open(DirFileName_sell, "a") as f:
                        f.write(DataString_sell)
                    print(f"File writting complete : {FileName_sell}")
                    break                    
                except Exception as e:
                    print(f"File writting error : {e}")


