import os
from datetime import datetime

class test1:
    def __init__(self):
        self.valuse = '0930457'

    def start(self):
        today = datetime.today().strftime("%Y-%m-%d")
        print(today, '11111')


if __name__ == "__main__":
    cc = test1()
    cc.start()