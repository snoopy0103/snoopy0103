import os
import sys
from threading import Thread


class Three_dimesion():
    def __init__(self, tick_1mindata, BuyQ, SellQ, StockQ, ewmQ):
        self.ewmQ = ewmQ
        self.tick_1mindata = tick_1mindata
        self.BuyQ = BuyQ
        self.SellQ = SellQ
        self.StockQ = StockQ
        self.ewm_5 = {}
        self.ewm_10 = {}
        self.ewm_30 = {}
        self.macd = {}
        self.signal = {}
        self.macd_hist = {}
        self.nmin_high = {}
        self.nmin_low = {}
        self.fast_k = {}
        self.slow_d = {}
        self.list_buy = []
        self.list_sell = []

        t = Thread(target=self.start, daemon=True)
        t.start()
        t.join()
        # self.start()

    def start(self):
        while True:
            if self.ewmQ.qsize() > 1000:
                mintime = self.tick_1mindata['041830'].체결시간[-1]

                tempQ = self.ewmQ.get()
                self.Code = tempQ[0][0]
                self.Price = self.tick_1mindata[self.Code].현재가[-1]
                self.temptime = tempQ[0][1]
                self.tempdate = tempQ[0][3]
                self.ewm_5Q = tempQ[0][2]
                self.ewm_10Q = tempQ[1][2]
                self.ewm_30Q = tempQ[2][2]            

                #ewm5
                if not self.Code in self.ewm_5.keys():
                    self.ewm_5[self.Code] = []
                    self.ewm_5[self.Code].append([self.Code, self.temptime, self.ewm_5Q, self.tempdate])
                else:
                    self.ewm_5[self.Code].append([self.Code, self.temptime, self.ewm_5Q, self.tempdate])
                #ewm10
                if not self.Code in self.ewm_10.keys():
                    self.ewm_10[self.Code] = []
                    self.ewm_10[self.Code].append([self.Code, self.temptime, self.ewm_10Q, self.tempdate])
                else:
                    self.ewm_10[self.Code].append([self.Code, self.temptime, self.ewm_10Q, self.tempdate])
                #ewm30
                if not self.Code in self.ewm_30.keys():
                    self.ewm_30[self.Code] = []
                    self.ewm_30[self.Code].append([self.Code, self.temptime, self.ewm_30Q, self.tempdate])
                else:
                    self.ewm_30[self.Code].append([self.Code, self.temptime, self.ewm_30Q, self.tempdate])

                #macd
                macd = self.ewm_10[self.Code][-1][2] - self.ewm_30[self.Code][-1][2]
                if not self.Code in self.macd.keys():
                    self.macd[self.Code] = []
                    self.macd[self.Code].append([self.Code, self.temptime, macd, self.tempdate])
                else:
                    self.macd[self.Code].append([self.Code, self.temptime, macd, self.tempdate])

                #signal
                self.signal[self.Code] = []
                if len(self.macd[self.Code]) > 5:
                    # temptime = self.macd[self.Code][-1][1]
                    tempSignal = 0
                    for i in range(len(self.macd[self.Code]), len(self.macd[self.Code])-5, -1):
                        tempSignal += self.macd[self.Code][i-1][2] / 5
                    if not self.Code in self.signal.keys():
                        self.signal[self.Code] = []
                        self.signal[self.Code].append([self.Code, mintime, tempSignal, self.macd[self.Code][-1][3]])
                    if self.temptime == mintime:
                        if self.signal[self.Code] == []:
                            self.signal[self.Code].append([self.Code, mintime, tempSignal, self.macd[self.Code][-1][3]])
                        self.signal[self.Code][-1][2] = tempSignal
                    else:
                        self.signal[self.Code].append([self.Code, mintime, tempSignal, self.macd[self.Code][-1][3]])

                #macd_hist
                if len(self.signal[self.Code]) > 0:
                    temp_macdhist = self.macd[self.Code][-1][2] - self.signal[self.Code][-1][2]
                    if not self.Code in self.macd_hist.keys():
                        self.macd_hist[self.Code] = []
                        self.macd_hist[self.Code].append([self.Code, mintime, temp_macdhist, self.macd[self.Code][-1][3]])
                    else:
                        self.macd_hist[self.Code].append([self.Code, mintime, temp_macdhist, self.macd[self.Code][-1][3]])

                #nmin_high
                if len(self.tick_1mindata[self.Code].체결시간) > 14:
                    temp_high = 0
                    temp_low = 999999999
                    for i in range(len(self.tick_1mindata[self.Code].체결시간), len(self.tick_1mindata[self.Code].체결시간)-14, -1):
                        temp_high = max(self.tick_1mindata[self.Code].고가[i-1], temp_high)
                        temp_low = min(self.tick_1mindata[self.Code].고가[i-1], temp_low)
                    if not self.Code in self.nmin_high.keys():
                        self.nmin_high[self.Code] = []
                        self.nmin_high[self.Code].append([self.Code, mintime, temp_high, self.macd[self.Code][-1][3]])
                    if not self.Code in self.nmin_low.keys():
                        self.nmin_low[self.Code] = []
                        self.nmin_low[self.Code].append([self.Code, mintime, temp_low, self.macd[self.Code][-1][3]])
                    if self.temptime == mintime:
                        if self.nmin_high[self.Code] == []:
                            self.nmin_high[self.Code].append([self.Code, mintime, temp_high, self.macd[self.Code][-1][3]])
                        if self.nmin_low[self.Code] == []:
                            self.nmin_low[self.Code].append([self.Code, mintime, temp_low, self.macd[self.Code][-1][3]])
                        self.nmin_high[self.Code][-1][2] = temp_high
                        self.nmin_low[self.Code][-1][2] = temp_low
                    else:
                        self.nmin_high[self.Code].append([self.Code, mintime, temp_high, self.macd[self.Code][-1][3]])
                        self.nmin_low[self.Code].append([self.Code, mintime, temp_low, self.macd[self.Code][-1][3]])

                #fast_k
                if (self.nmin_high[self.Code][-1][2] - self.nmin_low[self.Code][-1][2]) == 0:
                    temp_fastk = 0
                else:
                    temp_fastk = (self.Price - self.nmin_low[self.Code][-1][2]) / (self.nmin_high[self.Code][-1][2] - self.nmin_low[self.Code][-1][2]) * 100
                if not self.Code in self.fast_k.keys():
                    self.fast_k[self.Code] = []
                    self.fast_k[self.Code].append([self.Code, mintime, temp_fastk, self.macd[self.Code][-1][3]])
                if self.temptime == mintime:
                    if self.fast_k[self.Code] == []:
                        self.fast_k[self.Code].append([self.Code, mintime, temp_fastk, self.macd[self.Code][-1][3]])
                    self.fast_k[self.Code][-1][2] = temp_fastk
                else:
                    self.fast_k[self.Code].append([self.Code, mintime, temp_fastk, self.macd[self.Code][-1][3]])

                #slow_d
                temp_slowd = 0
                if len(self.fast_k[self.Code]) > 3:
                    for i in range(len(self.fast_k[self.Code]), len(self.fast_k[self.code])-3, -1):
                        temp_slowd += self.fast_k[self.Code][i-1][2] / 3
                    if not self.Code in self.slow_d.keys():
                        self.slow_d[self.Code] = []
                        self.slow_d[self.Code].append([self.Code, mintime, temp_slowd, self.macd[self.Code][-1][3]])
                    if self.temptime == mintime:
                        if self.slow_d[self.Code] == []:
                            self.slow_d[self.Code].append([self.Code, mintime, temp_slowd, self.macd[self.Code][-1][3]])
                        self.slow_d[self.Code][-1][2] = temp_slowd
                    else:
                        self.slow_d[self.Code].append([self.Code, mintime, temp_slowd, self.macd[self.Code][-1][3]])

                #Buy & Sell
                if len(self.ewm_30[self.Code]) > 1 and len(self.slow_d[self.Code]) > 1:
                    if self.ewm_30[self.Code][-2][2] < self.ewm_30[self.Code][-1][2] and \
                        self.ewm_5[self.Code][-1][2] > self.Price and \
                        self.slow_d[self.Code][-2][2] >= 30 and self.slow_d[self.Code][-1][2] < 30:
                        self.BuyQ.put([self.Code, self.Price])






