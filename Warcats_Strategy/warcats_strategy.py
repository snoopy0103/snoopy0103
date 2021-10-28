import multiprocessing
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
from threading import Thread
from multiprocessing import Process, Queue, Manager
from Trading_Bot.Alexander_Elder import Three_dimesion
#############################################################################
#############################################################################
_path = 'C:\PythonProjects\WarCatsServer_v0.1\SERVER_Connector'
os.chdir(_path)
#############################################################################
#############################################################################

from SERVER_Connector.Server_connector import Server_Connector
# from ZMQ_Execution.zeromq_Execution import ZMQ_Execution

class Warcats_Strategy(object):
    
    def __init__(self, BuyQ, SellQ, StockQ, EwmQ, tick_1mindata):

        # self.buyQ = buyQ
        # self.sellQ = sellQ

        self._svr = Server_Connector(BuyQ, SellQ, StockQ, EwmQ, tick_1mindata)
        
        self._svr.start()
        
        self._svr.t1.join()
        self._svr.t2.join()
        self._svr.t3.join()
        self._svr.t4.join()
        self._svr.t5.join()
        # self.trading_bot_proc.join()

        # Modules
        # self._execution = ZMQ_Execution(self._zmq)
        
    ##########################################################################
    
    def _run_(self):
        
        """
        Enter strategy logic here
        """
         
    ##########################################################################

if __name__ == '__main__':
    manager = Manager()
    BuyQ, SellQ, StockQ, EwmQ = \
        Queue(), Queue(), Queue(), Queue()
    tick_1mindata = manager.dict()

    wc = Process(target=Warcats_Strategy, args=(BuyQ, SellQ, StockQ, EwmQ, tick_1mindata))
    trading_bot_proc = Process(target=Three_dimesion, args=(tick_1mindata, BuyQ, SellQ, StockQ, EwmQ), daemon=True)

    wc.start()
    trading_bot_proc.start()
    wc.join()
    trading_bot_proc.join()




    