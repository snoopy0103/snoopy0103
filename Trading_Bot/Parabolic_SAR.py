
'''
추세: Keltner Channel
진입 시그널: Keltner Channel
변동성: Keltner Channel / ATR (Keltner Channel 공식에 ATR 포함됨!)
손절: Volaility Stop
'''
import os
import sys
from threading import Thread

class Parabolic():
    def __init__(self, tick_1minQ, BuyQ, SellQ):#af -> 0.01 최적화 (0.001 ~ 0.02 /0.001단위)
        self.tick_1min_dic = {}
        self.paraSAR = {}
        self.vstop = {}
        self.keltner = {}
        self.buylist = {}
        self.af = 0.01
        self.amax = 0.2
        self.mult = 11 #기본 2
        self.kc = 0.5 #3, 기본 1
        self.tick_1minQ = tick_1minQ
        self.buyQ = BuyQ
        self.sellQ = SellQ
        self.start()

    def start(self):
        while True:
            
            if not self.tick_1minQ.empty():
                tick_1min = self.tick_1minQ.get() 
                code = tick_1min[0]
                mintime = tick_1min[1]
                price = tick_1min[2]
                volume = tick_1min[3]
                high, low = tick_1min[4], tick_1min[5]  # Starting values
                tr = tick_1min[6]
                atr_5 = tick_1min[7]
                atr_20 = tick_1min[8]
                ewm_10 = tick_1min[9]
                xpt1, af1 = high, self.af                
                if not code in self.tick_1min_dic.keys():
                    self.tick_1min_dic[code] = []
                    self.tick_1min_dic[code].append(tick_1min)
                temptime = self.tick_1min_dic[code][-1][1]
                if temptime == mintime:
                    self.tick_1min_dic[code][-1][2] = price
                    self.tick_1min_dic[code][-1][3] = volume
                    if high > self.tick_1min_dic[code][-1][4]:
                        self.tick_1min_dic[code][-1][4] = high
                    if low < self.tick_1min_dic[code][-1][5]:
                        self.tick_1min_dic[code][-1][5] = low
                    self.tick_1min_dic[code][-1][6] = tr
                    self.tick_1min_dic[code][-1][7] = atr_5
                    self.tick_1min_dic[code][-1][8] = atr_20
                    self.tick_1min_dic[code][-1][9] = ewm_10
                else:
                    self.tick_1min_dic[code].append([code, mintime, price, volume, high, low, tr, atr_5, atr_20, ewm_10])

                #SAR
                if not code in self.paraSAR.keys():
                    sar = low
                    self.paraSAR[code]=[]
                    self.paraSAR[code].append([mintime, high, low, sar + self.af*(xpt1-sar), xpt1, af1])
                else:
                    # temptime = self.paraSAR[code][-1][0]
                    sar0 = self.paraSAR[code][-1][3]
                    xpt = self.paraSAR[code][-1][4]
                    af0 = self.paraSAR[code][-1][5]
                    if high > self.paraSAR[code][-1][1]:
                        af0 = af0 + self.af
                        xpt = high
                    high = max(self.paraSAR[code][-1][1], high)
                    low = min(self.paraSAR[code][-1][2], low)
                    sar = sar0 + af0 * (xpt - sar0)
                    if temptime == mintime:
                        self.paraSAR[code][-1][1] = high
                        self.paraSAR[code][-1][2] = low
                        self.paraSAR[code][-1][3] = sar
                    else:
                        self.paraSAR[code].append([mintime, high, low, sar, xpt, af0])

                #VSTOP
                if not code in self.vstop.keys():
                    #상승추세일때
                    max1 = price
                    #하락추세일때
                    min1 = price
                    vstop = max1 - self.mult * atr_20
                    self.vstop[code] = []
                    is_uptrend = True
                    self.vstop[code].append([mintime, vstop, is_uptrend])
                else:
                    temptime = self.vstop[code][-1][0]
                    if temptime == mintime:
                        #첫 1개 쌓였을 경우 그전봉이 없으므로...
                        if len(self.vstop[code]) < 2:
                            max1 = max(self.vstop[code][-1][1], price)
                            min1 = min(self.vstop[code][-1][1], price)
                            
                            is_uptrend_prev = self.vstop[code][-1][2]
                            vstop_prev = self.vstop[code][-1][1]
        
                            is_uptrend = price - self.vstop[code][-1][1] >= 0
                            is_trend_changed = is_uptrend != is_uptrend_prev
        
                            if is_uptrend_prev:
                                stop = max1 - self.mult * atr_20
                                vstop1 = max(vstop_prev, stop)
                            else:
                                stop = min1 + self.mult * atr_20
                                vstop1 = min(vstop_prev, stop)
        
                            if is_trend_changed:
                                max_ = price
                                min_ = price
                                if is_uptrend:
                                    vstop = max_ - self.mult * atr_20
                                    self.vstop[code][-1][1] = vstop
                                    self.vstop[code][-1][2] = is_uptrend
                                else:
                                    vstop = min_ + self.mult * atr_20
                                    self.vstop[code][-1][1] = vstop
                                    self.vstop[code][-1][2] = is_uptrend                                    
                            else:
                                max_ = max1
                                min_ = min1
                                vstop = vstop1
                                self.vstop[code][-1][1] = vstop
                                self.vstop[code][-1][2] = is_uptrend                                
                        else:
                            max1 = max(self.vstop[code][-2][1], price)
                            min1 = min(self.vstop[code][-2][1], price)
                            
                            is_uptrend_prev = self.vstop[code][-2][2]
                            vstop_prev = self.vstop[code][-2][1]
        
                            is_uptrend = price - self.vstop[code][-2][1] >= 0
                            is_trend_changed = is_uptrend != is_uptrend_prev
        
                            if is_uptrend_prev:
                                stop = max1 - self.mult * atr_20
                                vstop1 = max(vstop_prev, stop)
                            else:
                                stop = min1 + self.mult * atr_20
                                vstop1 = min(vstop_prev, stop)
        
                            if is_trend_changed:
                                max_ = price
                                min_ = price
                                if is_uptrend:
                                    vstop = max_ - self.mult * atr_20
                                    self.vstop[code][-1][1] = vstop
                                    self.vstop[code][-1][2] = is_uptrend
                                else:
                                    vstop = min_ + self.mult * atr_20
                                    self.vstop[code][-1][1] = vstop
                                    self.vstop[code][-1][2] = is_uptrend                                    
                            else:
                                max_ = max1
                                min_ = min1
                                vstop = vstop1
                                self.vstop[code][-1][1] = vstop
                                self.vstop[code][-1][2] = is_uptrend                                
                    else:
                            max1 = max(self.vstop[code][-1][1], price)
                            min1 = min(self.vstop[code][-1][1], price)
                            
                            is_uptrend_prev = self.vstop[code][-1][2]
                            vstop_prev = self.vstop[code][-1][1]
        
                            is_uptrend = price - self.vstop[code][-1][1] >= 0
                            is_trend_changed = is_uptrend != is_uptrend_prev
        
                            if is_uptrend_prev:
                                stop = max1 - self.mult * atr_20
                                vstop1 = max(vstop_prev, stop)
                            else:
                                stop = min1 + self.mult * atr_20
                                vstop1 = min(vstop_prev, stop)
        
                            if is_trend_changed:
                                max_ = price
                                min_ = price
                                if is_uptrend:
                                    vstop = max_ - self.mult * atr_20
                                    self.vstop[code].append([mintime, vstop, is_uptrend])
                                else:
                                    vstop = min_ + self.mult * atr_20
                                    self.vstop[code].append([mintime, vstop, is_uptrend])
                            else:
                                max_ = max1
                                min_ = min1
                                vstop = vstop1
                                self.vstop[code].append([mintime, vstop, is_uptrend])

                #Keltner 
                highband = ewm_10 + atr_20 * self.kc
                lowband = ewm_10 - atr_20 * self.kc
                if not code in self.keltner.keys():
                    self.keltner[code] = []
                    self.keltner[code].append([mintime, highband, lowband])
                else:
                    if temptime == mintime:
                        self.keltner[code][-1][1] = highband
                        self.keltner[code][-1][2] = lowband
                    else:
                        self.keltner[code].append([mintime, highband, lowband])

                #Buy
                # if len(self.keltner[code]) > 1 and len(self.tick_1min_dic[code]) > 1:
                #     if price > self.keltner[code][-1][1] and \
                #         self.keltner[code][-1][1] > self.keltner[code][-2][1] and \
                #         self.tick_1min_dic[code][-2][2] < self.keltner[code][-1][1] and \
                #         atr_5 > atr_20 and price > ewm_10 and atr_20 > 0 and is_uptrend:

                #         self.buyQ.put([code, price, mintime])

                #         if not code in self.buylist.keys():
                #             self.buylist[code] = [code, price, mintime]
                #             print(f"BUY!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                #             print(f"켈트너현재: {self.keltner[code][-1][1]}, \
                #                 켈트너과거: {self.keltner[code][-2][1]}, \
                #                 1분과거: {self.tick_1min_dic[code][-2][2]}, \
                #                 5ATR: {atr_5}, \
                #                 20ATR: {atr_20}, \
                #                 10EWM: {ewm_10}")
                if len(self.keltner[code]) > 1 and len(self.tick_1min_dic[code]) > 2:
                    threecandlehigh = self.tick_1min_dic[code][-3][3] > self.tick_1min_dic[code][-2][3] and \
                        self.tick_1min_dic[code][-1][3] > self.tick_1min_dic[code][-2][3]
                    threecandlelow = self.tick_1min_dic[code][-3][4] > self.tick_1min_dic[code][-2][4] and \
                        self.tick_1min_dic[code][-1][4] > self.tick_1min_dic[code][-2][4]
                    threecandleclose = price > self.tick_1min_dic[code][-2][3]
                    threecandlearea = self.tick_1min_dic[code][-2][4] < self.keltner[code][-1][1]
                    #필터링
                    up = price > ewm_10
                    down = price < ewm_10
                    ascending = self.tick_1min_dic[code][-1][9] > self.tick_1min_dic[code][-2][9]
                    goingup = up and ascending
                    #캔들패턴
                    threecandle = threecandlehigh and threecandlelow and threecandleclose and goingup and \
                        threecandlearea
                    real_ = threecandle and price > self.paraSAR[code][-1][3]
                    if(real_):
                        if not code in self.buylist.keys():
                            self.buyQ.put([code, price, mintime])
                            self.buylist[code] = [code, price, mintime]
                            print(f"BUY!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                            print(f"파라볼릭: {self.paraSAR[code][-1][3]}")
                    if code in self.buylist.keys():
                        if price < self.paraSAR[code][-1][3]:
                            print(f"SELL!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                            print(f"파라볼릭: {self.paraSAR[code][-1][3]}")
                            del self.buylist[code]


                # if code in self.vstop.keys():
                #     if code in self.buylist.keys():
                #         if self.vstop[code] != []:
                #             if price > self.vstop[code][-1][1] and is_uptrend == False:
                #                 self.sellQ.put(code)
                #                 print(f"SELL!! 종목코드: {code}, 가격: {price}, 시간: {mintime}")
                #                 print(f"VSTOP: {self.vstop[code][-1][1]}")

                    
                    












                    







    #     for i in range(1, len(s)):
    #         sig1, xpt1, af1 = sig0, xpt0, af0 
    #         lmin = min(low[i - 1], low[i])
    #         lmax = max(high[i - 1], high[i])
    #         if sig1:
    #             sig0 = low[i] > sar[-1]
    #             xpt0 = max(lmax, xpt1)
    #         else:
    #             sig0 = high[i] >= sar[-1]
    #             xpt0 = min(lmin, xpt1)
    #         if sig0 == sig1:
    #             '''
    #             SAR = SAR_ + AF * (EP - SAR_)
    #             AF (Acceleration Factor) = 0.02, EP가 갱신될 때마다 0.02만큼 증가해 최대 0.2까지 증가
    #             EP (Extreme Point) = 상승 추세에서 가장 높은 값, 하락 추세에서는 가장 낮은 값
    #             SAR값이 가격과 만나면 추세가 변경되며
    #             SAR값은 이전 추세의 EP값으로 초기화, AF는 0.02로 초기화
    #             '''
    #             sari = sar[-1] + (xpt1 - sar[-1])*af1
    #             af0 = min(amax, af1 + af)
    #             if sig0:
    #                 af0 = af0 if xpt0 > xpt1 else af1
    #                 sari = min(sari, lmin)
    #             else:
    #                 af0 = af0 if xpt0 < xpt1 else af1
    #                 sari = max(sari, lmax)
    #         else:
    #             af0 = af
    #             sari = xpt0 
    #             sar.append(sari)
    #             return sar
    
    # def flip_signal(Data, what, buy, sell):
    #     for i in range(len(Data)):
    #         try:
    #             if Data[i, what] < Data[i, 3] and Data[i - 1, what] > Data[i - 1, 3]:
    #                 Data[i, buy] = 1
    #             elif Data[i, what] > Data[i, 3] and Data[i - 1, what] < Data[i - 1, 3]:
    #                 Data[i, sell] = -1
    #             else:
    #                 continue
    #         except IndexError:
    #             pass
    # def three_dots_signal(Data, buy, sell):
    #     for i in range(len(Data)):
    #         try:
    #             #매수
    #             if Data[i, 4] < Data[i, 3] and Data[i - 1, 4] < Data[i - 1, 3] and \
    #                 Data[i - 2, 4] < Data[i - 2, 3] and Data[i - 3, 4] > Data[i - 3, 3]:
    #                 Data[i, buy] = 1
    #             #매도
    #             elif Data[i, 4] > Data[i, 3] and Data[i - 1, 4] > Data[i - 1, 3] and \
    #                 Data[i - 2, 4] > Data[i - 2, 3] and Data[i - 3, 4] < Data[i - 3, 3]:
    #                 Data[i, sell] = -1
    #             else:
    #                 continue
    #         except IndexError:
    #             pass