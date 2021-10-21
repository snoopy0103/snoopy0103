import multiprocessing
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath((os.path.dirname(__file__)))))
from threading import Thread
from multiprocessing import Process, Queue, Manager
from SERVER_Connector.Server_connector import Server_Connector


class ATR():
    def __init__(self, min1Q):
        self.min1Q = min1Q




    def make_TR(self):
        pass

    def make_ATR(self):
        pass

    def update_ATR(self):
        pass


