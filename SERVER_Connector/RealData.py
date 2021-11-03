class RealData:
    def __init__(self, code: str):#, name: str, market: str):
        # 종목코드, 종목명, 시장타입 설정
        self.code   = code
        # self.name   = name
        # if market == '': # ETN은 공백이 넘어옴
        #     self.market = 'ETN'
        # else:
        #     self.market = market
        
        # self.tick_count = 0
        
        # '주식체결' 데이터 저장용
        self.총시간           = []
        self.체결시간         = []
        self.현재가           = []
        self.체결방향         = []
        self.전일대비         = []
        self.등락율           = []
        self.최우선매도호가   = []
        self.최우선매수호가   = []
        self.거래량           = []
        self.거래방향         = []
        self.누적거래량       = []
        self.누적거래대금     = []
        self.시가             = []
        self.고가             = []
        self.저가             = []
        self.전일대비기호     = []
        self.전일거래량대비   = []
        self.거래대금증감     = []
        self.전일거래량대비율 = []
        self.거래회전율       = []
        self.거래비용         = []
        self.체결강도         = []
        self.시가총액         = []
        self.장구분           = []
        self.KO접근도         = []
        self.상한가발생시간   = []
        self.하한가발생시간   = []
        self.체결날짜        = []

    def append(self, 총시간: str, 체결시간: str, 현재가: str, 체결방향: str, 전일대비: str, 등락율: str, 최우선매도호가: str, 최우선매수호가: str, 거래량: str, 거래방향: str, 누적거래량: str, 누적거래대금: str, 시가: str, 고가: str, 저가: str, 전일대비기호: str, 전일거래량대비: str, 거래대금증감: str, 전일거래량대비율: str, 거래회전율: str, 거래비용: str, 체결강도: str, 시가총액: str, 장구분: str, KO접근도: str, 상한가발생시간: str, 하한가발생시간: str, 체결날짜: str) -> None:
        '''
        실시간 데이터를 추가하는 함수
        '''
        self.총시간.append(총시간)
        self.체결시간.append(체결시간)
        self.현재가.append(현재가)
        self.체결방향.append(체결방향)
        self.전일대비.append(전일대비)
        self.등락율.append(등락율)
        self.최우선매도호가.append(최우선매도호가)
        self.최우선매수호가.append(최우선매수호가)
        self.거래량.append(거래량)
        self.거래방향.append(거래방향)
        self.누적거래량.append(누적거래량)
        self.누적거래대금.append(누적거래대금)
        self.시가.append(시가)
        self.고가.append(고가)
        self.저가.append(저가)
        self.전일대비기호.append(전일대비기호)
        self.전일거래량대비.append(전일거래량대비)
        self.거래대금증감.append(거래대금증감)
        self.전일거래량대비율.append(전일거래량대비율)
        self.거래회전율.append(거래회전율)
        self.거래비용.append(거래비용)
        self.체결강도.append(체결강도)
        self.시가총액.append(시가총액)
        self.장구분.append(장구분)
        self.KO접근도.append(KO접근도)
        self.상한가발생시간.append(상한가발생시간)
        self.하한가발생시간.append(하한가발생시간)
        self.체결날짜.append(체결날짜)

        RowCount = len(self.체결시간)
        # if RowCount >= RealData.DATA_FULL_SIZE:
        #     self.save_data(True)