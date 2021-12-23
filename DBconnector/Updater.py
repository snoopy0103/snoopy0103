import os
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
import DBconnector.DBManager
from datetime import datetime, timedelta, time
from time import sleep
from multiprocessing import Queue

class Update_Data:
    def __init__(self, queue_Tick, queue_1min, queue_ATR, queue_ewm_5DB, queue_ewm_20, queue_ewm_30, BuyQ, queue_30minDB, queue_5minDB, queue_bollinger):
        self.queue_Tick = queue_Tick
        self.queue_1min = queue_1min
        self.queue_ATR = queue_ATR
        self.queue_ewm_5DB = queue_ewm_5DB
        self.queue_ewm_20 = queue_ewm_20
        self.queue_ewm_30 = queue_ewm_30
        self.buyQ = BuyQ
        self.queue_5minDB = queue_5minDB
        self.queue_30minDB = queue_30minDB
        self.queue_bollinger = queue_bollinger
        self.con = DBconnector.DBManager.dbcon()
        self.save_data()

    def save_data(self):
        while True:
            try:
                nowtime = datetime.now()
                if nowtime.time() >= time(19, 35):
                #     # today = datetime.today()
                #     if not self.queue_Tick.empty():
                #         data_tick = self.queue_Tick.get()
                #         sql = f"INSERT INTO kiwoom.tick_test \
                #             (code, 총시간, 체결시간, 현재가, 체결방향, 전일대비, 등락율, 최우선매도호가, 최우선매수호가, 거래량, 거래방향,누적거래량, \
                #             누적거래대금, 시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, \
                #             거래회전율, 거래비용, 체결강도, 시가총액, 장구분, KO접근도, 상한가발생시간, 하한가발생시간, 체결날짜) \
                #             VALUES \
                #             ('{data_tick[0]}', {data_tick[1]}, '{data_tick[2]}', {data_tick[3]}, '{data_tick[4]}', {data_tick[5]}, {data_tick[6]}, {data_tick[7]}, {data_tick[8]}, \
                #              {data_tick[9]}, '{data_tick[10]}', {data_tick[11]}, {data_tick[12]}, {data_tick[13]}, {data_tick[14]}, {data_tick[15]}, {data_tick[16]}, {data_tick[17]}, \
                #              {data_tick[18]}, {data_tick[19]}, {data_tick[20]}, {data_tick[21]}, {data_tick[22]}, {data_tick[23]}, {data_tick[24]}, {data_tick[25]}, {data_tick[26]}, \
                #              {data_tick[27]}, '{data_tick[28]}') \
                #             ON CONFLICT(code, 총시간, 누적거래량) \
                #             DO UPDATE SET (code, 총시간, 체결시간, 현재가, 체결방향, 전일대비, 등락율, 최우선매도호가, 최우선매수호가, 거래량, 거래방향, \
                #             누적거래량, 누적거래대금, 시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, \
                #             거래회전율, 거래비용, 체결강도, 시가총액, 장구분, KO접근도, 상한가발생시간, 하한가발생시간, 체결날짜) = \
                #             (excluded.code ,excluded.총시간, excluded.체결시간 ,excluded.현재가, excluded.체결방향, excluded.전일대비 ,excluded.등락율 ,excluded.최우선매도호가 \
                #             ,excluded.최우선매수호가 ,excluded.거래량, excluded.거래방향, excluded.누적거래량 ,excluded.누적거래대금 ,excluded.시가 ,excluded.고가 \
                #             ,excluded.저가 ,excluded.전일대비기호 ,excluded.전일거래량대비 ,excluded.거래대금증감 ,excluded.전일거래량대비율 \
                #             ,excluded.거래회전율 ,excluded.거래비용 ,excluded.체결강도 ,excluded.시가총액 ,excluded.장구분 ,excluded.KO접근도 \
                #             ,excluded.상한가발생시간 ,excluded.하한가발생시간, excluded.체결날짜)"
                #         self.con.execute(sql)
                #         self.con.commit()
                #     if not self.queue_1min.empty():
                #         data_1min = self.queue_1min.get()
                #         sql_1min = f"INSERT INTO kiwoom.tick_1min_test \
                #             (code, 체결시간, 현재가, 거래량, 시가, 고가, 저가, 체결날짜) \
                #             VALUES \
                #             ('{data_1min[0]}', '{data_1min[1]}', {data_1min[2]}, {data_1min[3]}, {data_1min[4]}, \
                #               {data_1min[5]}, {data_1min[6]}, '{data_1min[7]}') \
                #             ON CONFLICT(CODE, 체결시간, 체결날짜) \
                #             DO UPDATE SET (code, 체결시간, 현재가, 거래량, 시가, 고가, 저가, 체결날짜) \
                #             = (excluded.code, excluded.체결시간, excluded.현재가, excluded.거래량, excluded.시가, excluded.고가, excluded.저가, excluded.체결날짜)"
                #         self.con.execute(sql_1min)
                #         self.con.commit()
                #     if not self.queue_ATR.empty():
                #         data_ATR = self.queue_ATR.get()
                #         sql_ATR = f"INSERT INTO kiwoom.indicator_atr_test \
                #                 (code, 체결시간, tr, atr_5, atr_20, center_line, 체결날짜) \
                #                 VALUES \
                #                 ('{data_ATR[0]}', '{data_ATR[1]}', {data_ATR[2]}, {data_ATR[3]}, {data_ATR[4]}, {data_ATR[5]}, '{data_ATR[6]}') \
                #                 ON CONFLICT(CODE, 체결시간, 체결날짜) \
                #                 DO UPDATE SET (code, 체결시간, tr, atr_5, atr_20, center_line, 체결날짜) \
                #                 = (excluded.code, excluded.체결시간, excluded.tr, excluded.atr_5, excluded.atr_20, excluded.center_line, excluded.체결날짜)"
                #         self.con.execute(sql_ATR)
                #         self.con.commit()
                    # if not self.queue_ewm_5DB.empty():
                    #     data_EWM5 = self.queue_ewm_5DB.get()
                    #     sql_EWM5 = f"INSERT INTO kiwoom.indicator_5ewm_test \
                    #             (code, 체결시간, ewm_5, 체결날짜) \
                    #             VALUES \
                    #             ('{data_EWM5[0]}', '{data_EWM5[1]}', {data_EWM5[2]}, '{data_EWM5[3]}') \
                    #             ON CONFLICT(CODE, 체결시간, 체결날짜) \
                    #             DO UPDATE SET (code, 체결시간, ewm_5, 체결날짜) \
                    #             = (excluded.code, excluded.체결시간, excluded.ewm_5, excluded.체결날짜)"
                    #     self.con.execute(sql_EWM5)
                    #     self.con.commit()
                    # if not self.queue_ewm_20.empty():
                    #     data_EWM20 = self.queue_ewm_20.get()
                    #     sql_EWM20 = f"INSERT INTO kiwoom.indicator_20ewm_test \
                    #             (code, 체결시간, ewm_20, 체결날짜) \
                    #             VALUES \
                    #             ('{data_EWM20[0]}', '{data_EWM20[1]}', {data_EWM20[2]}, '{data_EWM20[3]}') \
                    #             ON CONFLICT(CODE, 체결시간, 체결날짜) \
                    #             DO UPDATE SET (code, 체결시간, ewm_20, 체결날짜) \
                    #             = (excluded.code, excluded.체결시간, excluded.ewm_20, excluded.체결날짜)"
                    #     self.con.execute(sql_EWM20)
                    #     self.con.commit()
                #     if not self.queue_ewm_30.empty():
                #         data_EWM30 = self.queue_ewm_30.get()
                #         sql_EWM30 = f"INSERT INTO kiwoom.indicator_30ewm_test \
                #                 (code, 체결시간, ewm_30, 체결날짜) \
                #                 VALUES \
                #                 ('{data_EWM30[0]}', '{data_EWM30[1]}', {data_EWM30[2]}, '{data_EWM30[3]}') \
                #                 ON CONFLICT(CODE, 체결시간, 체결날짜) \
                #                 DO UPDATE SET (code, 체결시간, ewm_30, 체결날짜) \
                #                 = (excluded.code, excluded.체결시간, excluded.ewm_30, excluded.체결날짜)"
                #         self.con.execute(sql_EWM30)
                #         self.con.commit()


                    # if not self.buyQ.empty():
                    #     data_buy = self.buyQ.get()
                    #     sql_buy = f"INSERT INTO kiwoom.buy_test \
                    #             (code, 체결시간, 가격) \
                    #             VALUES \
                    #             ('{data_buy[0]}', '{data_buy[1]}'', {data_buy[2]})"
                    #     self.con.execute(sql_buy)
                    #     self.con.commit()

                    if not self.queue_5minDB.empty():
                        data_5min = self.queue_5minDB.get()
                        sql_5min = f"INSERT INTO kiwoom.tick_5min \
                                    (code, 체결시간, 현재가, 거래량, 고가, 저가, 시가, 체결날짜, vwap, 누적거래량, 누적거래대금) \
                                    values \
                                    ('{data_5min[0]}', '{data_5min[1]}', {data_5min[2]}, {data_5min[3]}, {data_5min[4]}, {data_5min[5]}, {data_5min[6]}, '{data_5min[7]}', {data_5min[8]}, {data_5min[9]}, {data_5min[10]}) \
                                    on conflict(code, 체결시간, 체결날짜) \
                                    do update set (code, 체결시간, 현재가, 거래량, 고가, 저가, 시가, 체결날짜, vwap, 누적거래량, 누적거래대금) \
                                    = (excluded.code, excluded.체결시간, excluded.현재가, excluded.거래량, excluded.고가, excluded.저가, excluded.시가, excluded.체결날짜, excluded.vwap, excluded.누적거래량, excluded.누적거래대금)"
                        self.con.execute(sql_5min)
                        self.con.commit()
                    if not self.queue_bollinger.empty():
                        data_bollinger = self.queue_bollinger.get()
                        sql_bollinger = f"insert into kiwoom.indicator_bollinger \
                            (code, 체결시간, std, highvalue, lowvalue, 체결날짜, 중심선) \
                            values \
                                 ('{data_bollinger[0]}', '{data_bollinger[1]}', {data_bollinger[2]}, {data_bollinger[3]}, {data_bollinger[4]}, '{data_bollinger[5]}', {data_bollinger[6]}) \
                                 ON CONFLICT(CODE, 체결시간, 체결날짜) \
                                 DO UPDATE SET (code, 체결시간, std, highvalue, lowvalue, 체결날짜) \
                                 = (excluded.code, excluded.체결시간, excluded.std, excluded.highvalue, excluded.lowvalue, excluded.체결날짜, excluded.중심선)"
                        self.con.execute(sql_bollinger)
                        self.con.commit()

                    # if not self.queue_30minDB.empty():
                    #     data_30min = self.queue_30minDB.get()
                    #     sql_30min = f"INSERT INTO kiwoom.tick_30min \
                    #                 (code, 체결시간, 현재가, 거래량, 고가, 저가, 체결날짜) \
                    #                 values \
                    #                 ('{data_30min[0]}', '{data_30min[1]}', {data_30min[2]}, {data_30min[3]}, {data_30min[4]}, {data_30min[5]}, '{data_30min[6]}') \
                    #                 on conflict(code, 체결시간, 체결날짜) \
                    #                 do update set (code, 체결시간, 현재가, 거래량, 고가, 저가, 체결날짜) \
                    #                 = (excluded.code, excluded.체결시간, excluded.현재가, excluded.거래량, excluded.고가, excluded.저가, excluded.체결날짜)"
                    #     self.con.execute(sql_30min)
                    #     self.con.commit()


            except Exception as e :
                print(e)

            
            # sleep(0.01)