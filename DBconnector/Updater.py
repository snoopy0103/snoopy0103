import os
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
import DBconnector.DBManager
from datetime import datetime, timedelta, time
from multiprocessing import Queue

class Update_Data:
    def __init__(self, queue_Tick, queue_1min, queue_ATR, queue_ewm_5, queue_ewm_10, queue_ewm_30, BuyQ):
        self.queue_Tick = queue_Tick
        self.queue_1min = queue_1min
        self.queue_ATR = queue_ATR
        self.queue_ewm_5 = queue_ewm_5
        self.queue_ewm_10 = queue_ewm_10
        self.queue_ewm_30 = queue_ewm_30
        self.buyQ = BuyQ

        self.con = DBconnector.DBManager.dbcon()
        self.save_data()

    def save_data(self):
        while True:
            try:
                nowtime = datetime.now()
                if nowtime.time() >= time(15, 35):
                    # today = datetime.today()
                    if not self.queue_Tick.empty():
                        data_tick = self.queue_Tick.get()
                        sql = f"INSERT INTO kiwoom.tick_test \
                            (code, 총시간, 체결시간, 현재가, 체결방향, 전일대비, 등락율, 최우선매도호가, 최우선매수호가, 거래량, 거래방향,누적거래량, \
                            누적거래대금, 시가, 고가, 저가, 전일대비기호, 전일거래량대비, 거래대금증감, 전일거래량대비율, \
                            거래회전율, 거래비용, 체결강도, 시가총액, 장구분, KO접근도, 상한가발생시간, 하한가발생시간, 체결날짜) \
                            VALUES \
                            ('{data_tick[0]}', {data_tick[1]}, '{data_tick[2]}', {data_tick[3]}, '{data_tick[4]}', {data_tick[5]}, {data_tick[6]}, {data_tick[7]}, {data_tick[8]}, \
                             {data_tick[9]}, '{data_tick[10]}', {data_tick[11]}, {data_tick[12]}, {data_tick[13]}, {data_tick[14]}, {data_tick[15]}, {data_tick[16]}, {data_tick[17]}, \
                             {data_tick[18]}, {data_tick[19]}, {data_tick[20]}, {data_tick[21]}, {data_tick[22]}, {data_tick[23]}, {data_tick[24]}, {data_tick[25]}, {data_tick[26]}, \
                             {data_tick[27]}, '{data_tick[28]}') \
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
                    if not self.queue_1min.empty():
                        data_1min = self.queue_1min.get()
                        sql_1min = f"INSERT INTO kiwoom.tick_1min_test \
                            (code, 체결시간, 현재가, 거래량, 시가, 고가, 저가, 체결날짜) \
                            VALUES \
                            ('{data_1min[0]}', '{data_1min[1]}', {data_1min[2]}, {data_1min[3]}, {data_1min[4]}, \
                              {data_1min[5]}, {data_1min[6]}, '{data_1min[7]}') \
                            ON CONFLICT(CODE, 체결시간, 체결날짜) \
                            DO UPDATE SET (code, 체결시간, 현재가, 거래량, 시가, 고가, 저가, 체결날짜) \
                            = (excluded.code, excluded.체결시간, excluded.현재가, excluded.거래량, excluded.시가, excluded.고가, excluded.저가, excluded.체결날짜)"
                        self.con.execute(sql_1min)
                        self.con.commit()
                    if not self.queue_ATR.empty():
                        data_ATR = self.queue_ATR.get()
                        sql_ATR = f"INSERT INTO kiwoom.indicator_atr \
                                (code, 체결시간, tr, atr, center_line, 체결날짜) \
                                VALUES \
                                ('{data_ATR[0]}', '{data_ATR[1]}', {data_ATR[2]}, {data_ATR[3]}, {data_ATR[4]}, '{data_ATR[5]}') \
                                ON CONFLICT(CODE, 체결시간, 체결날짜) \
                                DO UPDATE SET (code, 체결시간, tr, atr, center_line, 체결날짜) \
                                = (excluded.code, excluded.체결시간, excluded.tr, excluded.atr, excluded.center_line, excluded.체결날짜)"
                        self.con.execute(sql_ATR)
                        self.con.commit()
                    if not self.queue_ewm_5.empty():
                        data_EWM5 = self.queue_ewm_5.get()
                        sql_EWM5 = f"INSERT INTO kiwoom.indicator_5ewm \
                                (code, 체결시간, ewm_5, 체결날짜) \
                                VALUES \
                                ('{data_EWM5[0]}', '{data_EWM5[1]}', {data_EWM5[2]}, '{data_EWM5[3]}') \
                                ON CONFLICT(CODE, 체결시간, 체결날짜) \
                                DO UPDATE SET (code, 체결시간, ewm_5, 체결날짜) \
                                = (excluded.code, excluded.체결시간, excluded.ewm_5, excluded.체결날짜)"
                        self.con.execute(sql_EWM5)
                        self.con.commit()
                    if not self.queue_ewm_10.empty():
                        data_EWM10 = self.queue_ewm_10.get()
                        sql_EWM10 = f"INSERT INTO kiwoom.indicator_10ewm \
                                (code, 체결시간, ewm_10, 체결날짜) \
                                VALUES \
                                ('{data_EWM10[0]}', '{data_EWM10[1]}', {data_EWM10[2]}, '{data_EWM10[3]}') \
                                ON CONFLICT(CODE, 체결시간, 체결날짜) \
                                DO UPDATE SET (code, 체결시간, ewm_10, 체결날짜) \
                                = (excluded.code, excluded.체결시간, excluded.ewm_10, excluded.체결날짜)"
                        self.con.execute(sql_EWM10)
                        self.con.commit()
                    if not self.queue_ewm_30.empty():
                        data_EWM30 = self.queue_ewm_30.get()
                        sql_EWM30 = f"INSERT INTO kiwoom.indicator_30ewm \
                                (code, 체결시간, ewm_30, 체결날짜) \
                                VALUES \
                                ('{data_EWM30[0]}', '{data_EWM30[1]}', {data_EWM30[2]}, '{data_EWM30[3]}') \
                                ON CONFLICT(CODE, 체결시간, 체결날짜) \
                                DO UPDATE SET (code, 체결시간, ewm_30, 체결날짜) \
                                = (excluded.code, excluded.체결시간, excluded.ewm_30, excluded.체결날짜)"
                        self.con.execute(sql_EWM30)
                        self.con.commit()
                    if not self.buyQ.empty():
                        data_buy = self.buyQ.get()
                        sql_buy = f"INSERT INTO kiwoom.buy_test \
                                (code, 체결시간, 가격) \
                                VALUES \
                                ('{data_buy[0]}', '{data_buy[1]}'', {data_buy[2]})"
                        self.con.execute(sql_buy)
                        self.con.commit()

            except Exception as e :
                print(e)

