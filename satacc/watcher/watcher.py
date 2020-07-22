from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst
from . import watcher_data, watcher_process


class Watcher(Component):

    def construct(s):
        # ifcs
        s.get_from_trail = GetIfcRTL(mk_bits(32))
        s.send_to_clause = SendIfcRTL(mk_bits(32))
        # components
        s.watcher_data = watcher_data.Watcher_data(32, 33, 8, 8)
        s.watcher_process = watcher_process.Watcher_process(33, 32)
        # connects
        s.get_from_trail //= s.watcher_data.get
        s.send_to_clause //= s.watcher_process.send

        s.watcher_data.send //= s.watcher_process.recv
        s.meta_mem_send //= s.watcher_data.meta_mem_send
        s.meta_mem_recv //= s.watcher_data.meta_mem_recv
        s.data_mem_send //= s.watcher_data.data_mem_send
        s.data_mem_recv //= s.watcher_data.data_mem_recv

    pass
