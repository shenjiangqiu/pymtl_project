from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst
from . import watcher_data, watcher_process
from ..utils.mem_oparator import Sized_memory_sender


class Watcher(components):
    def construct(s, index):
        s.total_num_mem = 8
        s.size_addr_buffer = PipeQueueRTL(mk_bits(12))
        s.watcher_buffer = PipeQueueRTL(mk_bits(8))
        s.value_buffer=PipeQueueRTL(mk_bits(7))
        s.cr_send_buffer = PipeQueueRTL(mk_bits(4))
        # def construct(s, size_type, addr_type, item_size, mem_request_dest):
        s.watcher_fetch_unit = Sized_memory_sender(
            Bits4, Bits8, 64, index*s.total_num_mem+1)

        @update
        def comb():
            #TODO: finished the comb logic
        


class Watcher_old(Component):
    """the watcher class bind the data and proc
        input: get_from_trail: Getifc
        output: Send_to_clause: Sendifc


    Args:
        Component (self): self
    """
    def construct(s):
        # ifcs
        s.get_from_trail = GetIfcRTL(mk_bits(32))
        s.send_to_clause = SendIfcRTL(mk_bits(32))
        s.meta_mem_send = SendIfcRTL(mk_bits(32))
        s.meta_mem_recv = RecvIfcRTL(mk_bits(64))  # one cache line size
        s.data_mem_send = SendIfcRTL(mk_bits(32))

        # one bool bit and the clause reference
        s.data_mem_recv = RecvIfcRTL(mk_bits(33))

        # components
        s.watcher_data = watcher_data.Watcher_data(32, 33, 8, 8, 2)
        s.watcher_process = watcher_process.Watcher_process(33, 32)
        # connects
        s.get_from_trail //= s.watcher_data.get
        s.send_to_clause //= s.watcher_process.send

        s.watcher_data.send //= s.watcher_process.recv
        s.meta_mem_send //= s.watcher_data.meta_mem_send
        s.meta_mem_recv //= s.watcher_data.meta_mem_recv
        s.data_mem_send //= s.watcher_data.data_mem_send
        s.data_mem_recv //= s.watcher_data.data_mem_recv
