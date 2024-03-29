import os

#############################################################################
#############################################################################
_path = 'C:\PythonProjects\WarCatsServer_v0.1\SERVER_Connector'
os.chdir(_path)
#############################################################################
#############################################################################

from Warcats_Strategy.warcats_strategy import Warcats_Strategy

from pandas import Timedelta, to_datetime
from threading import Thread, Lock
from time import sleep
import random

class ex_traders(Warcats_Strategy):
    
    def __init__(self, _name="EX_TRADERS"):
        super().__init__(_name)
        
        self._svr
        # This strategy's variables
        self._traders = []
        self._market_open = True
        self.strategies = []
        
        # lock for acquire/release of ZeroMQ connector
        self._lock = Lock()
        
    ##########################################################################
    
    def _run_(self):
        
        """
        Logic:
        """
        
        # Launch traders!
        for _symbol in self._symbols:
            
            _t = Thread(name="{}_Trader".format(_symbol[0]),
                        target=self._trader_, args=(_symbol,self._max_trades))
            
            _t.daemon = True
            _t.start()
            
            print('[{}_Trader] Alright, here we go.. Gerrrronimooooooooooo!  ..... xD'.format(_symbol[0]))
            
            self._traders.append(_t)
        
        print('\n\n+--------------+\n+ LIVE UPDATES +\n+--------------+\n')
        
        # _verbose can print too much information.. so let's start a thread
        # that prints an update for instructions flowing through ZeroMQ
        self._updater_ = Thread(name='Live_Updater',
                               target=self._updater_,
                               args=(self._delay,))
        
        self._updater_.daemon = True
        self._updater_.start()
        
    ##########################################################################
    
    def _updater_(self, _delay=0.1):
        
        while self._market_open:
            
            try:
                # Acquire lock
                self._lock.acquire()
                
                print('\r{}'.format(str(self._zmq._get_response_())), end='', flush=True)
                
            finally:
                # Release lock
                self._lock.release()
        
            sleep(self._delay)
            
    ##########################################################################
    
    def _trader_(self, _symbol, _max_trades):
        
        # Note: Just for this example, only the Order Type is dynamic.
        _default_order = self._zmq._generate_default_order_dict()
        _default_order['_symbol'] = _symbol[0]
        _default_order['_lots'] = _symbol[1]
        _default_order['_SL'] = _default_order['_TP'] = 100
        _default_order['_comment'] = '{}_Trader'.format(_symbol[0])
        
        """
        Default Order:
        --
        {'_action': 'OPEN',
         '_type': 0,
         '_symbol': EURUSD,
         '_price':0.0,
         '_SL': 100,                     # 10 pips
         '_TP': 100,                     # 10 pips
         '_comment': 'EURUSD_Trader',
         '_lots': 0.01,
         '_magic': 123456}
        """
        
        while self._market_open:
            
            try:
                
                # Acquire lock
                self._lock.acquire()
            
                #############################
                # SECTION - GET OPEN TRADES #
                #############################
                
                _ot = self._reporting._get_open_trades_('{}_Trader'.format(_symbol[0]),
                                                        self._delay,
                                                        10)
                
                # Reset cycle if nothing received
                if self._zmq._valid_response_(_ot) == False:
                    continue
                
                ###############################
                # SECTION - CLOSE OPEN TRADES #
                ###############################
                
                for i in _ot.index:
                    
                    if abs((Timedelta((to_datetime('now') + Timedelta(self._broker_gmt,'h')) - to_datetime(_ot.at[i,'_open_time'])).total_seconds())) > self._close_t_delta:
                        
                        _ret = self._execution._execute_({'_action': 'CLOSE',
                                                          '_ticket': i,
                                                          '_comment': '{}_Trader'.format(_symbol[0])},
                                                          self._verbose,
                                                          self._delay,
                                                          10)
                       
                        # Reset cycle if nothing received
                        if self._zmq._valid_response_(_ret) == False:
                            break
                        
                        # Sleep between commands to MetaTrader
                        sleep(self._delay)
                
                ##############################
                # SECTION - OPEN MORE TRADES #
                ##############################
                
                if _ot.shape[0] < _max_trades:
                    
                    # Randomly generate 1 (OP_BUY) or 0 (OP_SELL)
                    # using random.getrandbits()
                    _default_order['_type'] = random.getrandbits(1)
                    
                    # Send instruction to MetaTrader
                    _ret = self._execution._execute_(_default_order,
                                                     self._verbose,
                                                     self._delay,
                                                     10)
                  
                    # Reset cycle if nothing received
                    if self._zmq._valid_response_(_ret) == False:
                        continue
                
            finally:
                self._lock.release()
            sleep(self._delay)
            
    ##########################################################################
    
    def _stop_(self):
        pass
        
    ##########################################################################

if __name__ == '__main__':
    zmqs = ex_traders()
    zmqs._run_()