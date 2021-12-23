import os
import sys
from threading import Thread
import datetime

class CrossUp60():
    def __init__(self, queue_60min, BuyQ, SellQ, tick_1minQ, Stock2Q):
        self.stocklist = {}
        self.tick_60min_dic = {}
        self.buylist = {}
        self.selllist = {}
        self.tick_1min_dic = {}
        self.queue_60min = queue_60min
        self.tick_1minQ = tick_1minQ
        self.buyQ = BuyQ
        self.sellQ = SellQ        
        self.stockQ = Stock2Q
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

            if not self.queue_60min.empty():
                tick_60min = self.queue_60min.get()
                code = tick_60min[0]
                tempt = tick_60min[1]
                tempt = tempt[:2]
                # if tempt == '09':
                #     if not code in self.tick_60min_dic.keys():
                #         self.tick_60min_dic[code] = []
                #         self.tick_60min_dic[code].append(tick_60min)
                if not code in self.tick_60min_dic.keys():
                        self.tick_60min_dic[code] = []
                        self.tick_60min_dic[code].append(tick_60min)


            if not self.tick_1minQ.empty():
                tick_1min = self.tick_1minQ.get() 
                code = tick_1min[0]
                mintime = tick_1min[1]
                price = tick_1min[2]
                volume = tick_1min[3]
                openp = tick_1min[4]
                high, low = tick_1min[5], tick_1min[6]  # Starting values
                if not code in self.tick_1min_dic.keys():
                    self.tick_1min_dic[code] = []
                    self.tick_1min_dic[code].append(tick_1min)
                temptime = self.tick_1min_dic[code][-1][1]
                if temptime == mintime:
                    if code in self.tick_60min_dic.keys():
                        for key in self.stocklist.keys():
                            if code in self.stocklist[key]:
                                high_60 = self.tick_60min_dic[code][-1][4]                    
                                #매수조건######################################################################
                                if price > high_60 and high_60 > self.tick_1min_dic[code][-1][2]:
                                    if not code in self.buylist.keys():
                                            self.buyQ.put({key: ['BUY', code, price, mintime]})
                                            self.buylist[code] = [code, price, mintime]
                                            print(f"BUY!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                                            print(f"60분고점: {high_60}")
                                ###############################################################################
                                #매도조건######################################################################
                                #익절
                                if code in self.buylist.keys():
                                    if not code in self.selllist.keys():
                                        if price > self.buylist[code][1] * 1.025:
                                            self.sellQ.put({key: ['SELL', code, price, mintime]})
                                            self.selllist[code] = [code, 'SELL', price, mintime]
                                            print(f"SELL!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                                            print(f"60분고점: {high_60}")                                    
                                #손절
                                if code in self.buylist.keys():
                                    if not code in self.selllist.keys():
                                        if price < self.buylist[code][1] * 0.98 and \
                                            self.tick_1min_dic[code][-1][2] > self.buylist[code][1] * 0.98:
                                            self.sellQ.put({key: ['SELL', code, price, mintime]})
                                            self.selllist[code] = [code, 'SELL', price, mintime]
                                            print(f"SELL!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                                            print(f"60분고점: {high_60}")
                                ###############################################################################
                    self.tick_1min_dic[code][-1][2] = price
                    self.tick_1min_dic[code][-1][3] = volume
                    if high > self.tick_1min_dic[code][-1][5]:
                        self.tick_1min_dic[code][-1][5] = high
                    if low < self.tick_1min_dic[code][-1][6]:
                        self.tick_1min_dic[code][-1][6] = low
                else:
                    if code in self.tick_60min_dic.keys():
                        for key in self.stocklist.keys():
                            if code in self.stocklist[key]:
                                high_60 = self.tick_60min_dic[code][-1][4]                      
                                #매수조건######################################################################
                                if price > high_60 and high_60 > self.tick_1min_dic[code][-1][2]:
                                    if not code in self.buylist.keys():
                                            self.buyQ.put({key: ['BUY', code, price, mintime]})
                                            self.buylist[code] = [code, price, mintime]
                                            print(f"BUY!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                                            print(f"60분고점: {high_60}")
                                ###############################################################################
                                #매도조건######################################################################
                                #익절
                                if code in self.buylist.keys():
                                    if not code in self.selllist.keys():
                                        if price > self.buylist[code][1] * 1.025:
                                            self.sellQ.put({key: ['SELL', code, price, mintime]})
                                            self.selllist[code] = [code, 'SELL', price, mintime]
                                            print(f"SELL!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                                            print(f"60분고점: {high_60}")                         
                                #손절
                                if code in self.buylist.keys():
                                    if not code in self.selllist.keys():
                                        if price < self.buylist[code][1] * 0.98 and \
                                            self.tick_1min_dic[code][-1][2] > self.buylist[code][1] * 0.98:
                                            self.sellQ.put({key: ['SELL', code, price, mintime]})
                                            self.selllist[code] = [code, 'SELL', price, mintime]

                                            print(f"SELL!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                                            print(f"60분고점: {high_60}")
                                ###############################################################################
                    self.tick_1min_dic[code].append([code, mintime, price, volume, openp, high, low])

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
                    DataString_buy = f"종목코드, 가격, 시간\n"
                if os.path.isfile(DirFileName_sell):
                    DataString_sell = ""
                else:
                    DataString_sell = f"종목코드, 가격, 시간\n"

                for key in self.buylist.keys():
                    DataString_buy = f"{DataString_buy}{self.buylist[key][0]}, {self.buylist[key][1]}, {self.buylist[key][2]}\n"
                for key in self.selllist.keys():
                    DataString_sell = f"{DataString_sell}{self.selllist[key][0]}, {self.selllist[key][1]}, {self.selllist[key][2]}\n"                
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


