
class RealData_1min():
    def __init__(self, code: str):#, name: str, market: str):
        # 종목코드, 종목명, 시장타입 설정
        self.code   = code
        # self.name   = name
        # if market == '': # ETN은 공백이 넘어옴
        #     self.market = 'ETN'
        # else:
        #     self.market = market
        
        self.tick_count = 0
        
        # '주식체결' 데이터 저장용
        self.체결시간         = []
        self.현재가           = []
        self.거래량           = []
        self.시가             = []
        self.고가             = []
        self.저가             = []
        self.체결날짜        = []

    def append(self, 체결시간: str, 현재가: str, 거래량: str, 시가: str, 고가: str, 저가: str, 체결날짜: str) -> None:
        '''
        실시간 데이터를 추가하는 함수
        '''
        self.체결시간+=[체결시간]
        self.현재가+=[현재가]
        self.거래량+=[거래량]
        self.시가+=[시가]
        self.고가+=[고가]
        self.저가+=[저가]
        self.체결날짜+=[체결날짜]
        # self.체결시간.append(체결시간)
        # self.현재가.append(현재가)
        # self.거래량.append(거래량)
        # self.시가.append(시가)
        # self.고가.append(고가)
        # self.저가.append(저가)
        # self.체결날짜.append(체결날짜)

        # RowCount = len(self.체결시간)
        # if RowCount >= RealData.DATA_FULL_SIZE:
        #     self.save_data(True)

    def last(self):
        
        체결시간 = self.체결시간[-1]
        현재가 = self.현재가[-1]
        거래량 = self.거래량[-1]
        시가 = self.시가[-1]
        고가 = self.고가[-1]
        저가 = self.저가[-1]
        체결날짜 =self.체결날짜[-1]
        temp_list = [체결시간, 현재가, 거래량, 시가, 고가, 저가, 체결날짜]
        return temp_list
        