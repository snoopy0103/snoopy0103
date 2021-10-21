import multiprocessing
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
from threading import Thread
from multiprocessing import Process, Queue, Manager

#############################################################################
#############################################################################
_path = 'C:\PythonProjects\WarCatsServer_v0.1\SERVER_Connector'
os.chdir(_path)
#############################################################################
#############################################################################

from SERVER_Connector.Server_connector import Server_Connector
# from ZMQ_Execution.zeromq_Execution import ZMQ_Execution

class Warcats_Strategy(object):
    
    def __init__(self, buyQ, sellQ, 관심종목):

        self.buyQ = buyQ
        self.sellQ = sellQ

        self._svr = Server_Connector(buyQ, sellQ, 관심종목)
        self._svr.start()
        self._svr.t1.join()
        self._svr.t2.join()
        self._svr.t3.join()
        self._svr.t4.join()
        self._svr.t5.join()

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
    buyQ, sellQ = Queue(), Queue()
    관심종목 = manager.dict()

    wc = Process(target=Warcats_Strategy, args=(buyQ, sellQ, 관심종목))

    wc.start()
    wc.join()




    