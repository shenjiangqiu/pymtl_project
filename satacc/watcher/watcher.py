from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL, BypassQueueRTL
from pymtl3.stdlib.queues.enrdy_queues import BypassQueue1RTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst
from . import watcher_data, watcher_process
from ..utils.mem_oparator import Sized_memory_sender
import os
# memory read request type: type:4 op:8 addr:64 len:4 data:96 =176
# memory resp type: type:4 op:8 test:2 len:4 data:96= 114
# watcher send: type:4 op:8 addr:64 len:4 data:64 =144
# watcher recv: type:4 op:8 test:2 len:4 data:64= 82
# value send: type:4 op:8 addr:64 len:2 data:8 =86
# value recv:  type:4 op:8 test:2 len:2 data:8= 24


class Watcher(Component):
    def construct(s, index):
        # ifcs
        s.from_trail_recv = RecvIfcRTL(Bits32)

        # send trail addr to get size and addr
        s.lit_to_size_addr_mem_send = SendIfcRTL(mk_bits(176))
        s.lit_to_size_addr_mem_recv = RecvIfcRTL(
            mk_bits(114))  # recv size and addr
        s.watcher_send_mem_send = SendIfcRTL(Bits144)
        s.watcher_recv = RecvIfcRTL(Bits82)
        s.value_send = SendIfcRTL(Bits86)
        s.value_recv = RecvIfcRTL(Bits24)
        s.cr_send = SendIfcRTL(Bits32)

        s.total_num_mem = 8
        s.lit_recv_buffer = PipeQueueRTL(mk_bits(32), 4)
        s.size_addr_buffer = PipeQueueRTL(mk_bits(12*8), 8)
        s.watcher_buffer = PipeQueueRTL(mk_bits(64), 8)  # lit +cr
        s.value_buffer = PipeQueueRTL(mk_bits(40), 8)  # value 8 +cr
        s.cr_send_buffer = PipeQueueRTL(mk_bits(32), 4)

        s.temp_cr_q = BypassQueueRTL(Bits32, 1)
        s.temp_value_q = BypassQueueRTL(Bits8, 1)
        # def construct(s, size_type, addr_type, item_size, mem_request_dest):
        s.watcher_fetch_unit = Sized_memory_sender(
            Bits32, Bits64, 64, index*s.total_num_mem+1)

        s.lit_recv_buffer.enq //= s.from_trail_recv
        s.watcher_send_mem_send //= s.watcher_fetch_unit.mem_out

        @update
        def comb():
            # send litral:
            s.temp_value_q.deq.en@=s.temp_value_q.deq.rdy & s.temp_cr_q.deq.rdy & s.value_buffer.enq.rdy
            s.temp_cr_q.deq.en@=s.temp_value_q.deq.rdy & s.temp_cr_q.deq.rdy & s.value_buffer.enq.rdy
            s.temp_cr_q.enq.msg@=s.watcher_buffer.deq.ret[32:64]
            s.temp_value_q.enq.en@=s.value_recv.en
            s.value_recv.rdy@=s.temp_value_q.enq.rdy
            s.temp_value_q.enq.msg@=s.value_recv.msg[24-8:24]

            s.watcher_buffer.enq.en@=s.watcher_recv.en
            s.watcher_recv.rdy@=s.watcher_buffer.enq.rdy
            s.watcher_buffer.enq.msg@=s.watcher_recv.msg[82-64:82]

            s.size_addr_buffer.enq.en@=s.lit_to_size_addr_mem_recv.en
            s.lit_to_size_addr_mem_recv.rdy @=s.size_addr_buffer.enq.rdy
            s.size_addr_buffer.enq.msg@=s.lit_to_size_addr_mem_recv.msg[114-96:114]

            s.size_addr_buffer.deq.en@=s.watcher_fetch_unit.size_recv.rdy & s.watcher_fetch_unit.addr_recv.rdy

            s.value_buffer.enq.msg@=concat(s.temp_value_q.deq.ret,
                                           s.temp_cr_q.deq.ret)
            s.value_buffer.enq.en@= s.temp_value_q.deq.rdy & s.temp_cr_q.deq.rdy & s.value_buffer.enq.rdy

            s.lit_to_size_addr_mem_send.en@=s.lit_to_size_addr_mem_send.rdy & s.lit_recv_buffer.deq.rdy
            s.lit_recv_buffer.deq.en@=s.lit_to_size_addr_mem_send.rdy & s.lit_recv_buffer.deq.rdy

            # TODO: set the message
            s.lit_to_size_addr_mem_send.msg@=concat(
                Bits12(0), Bits32(0), s.lit_recv_buffer.deq.ret, Bits100(0))

            s.watcher_fetch_unit.size_recv.en @=s.watcher_fetch_unit.size_recv.rdy & s.size_addr_buffer.deq.rdy
            s.watcher_fetch_unit.addr_recv.en @=s.watcher_fetch_unit.addr_recv.rdy & s.size_addr_buffer.deq.rdy
            s.watcher_fetch_unit.size_recv.msg@=s.size_addr_buffer.deq.ret[18:50]
            s.watcher_fetch_unit.addr_recv.msg@=s.size_addr_buffer.deq.ret[96-64:96]

            # send value request
            s.value_send.en@=s.watcher_buffer.deq.rdy & s.value_send.rdy & s.temp_cr_q.enq.rdy & s.temp_value_q.enq.rdy
            s.watcher_buffer.deq.en@=s.watcher_buffer.deq.rdy & s.value_send.rdy & s.temp_cr_q.enq.rdy & s.temp_value_q.enq.rdy
            s.temp_cr_q.enq.en@= s.watcher_buffer.deq.rdy & s.value_send.rdy & s.temp_cr_q.enq.rdy & s.temp_value_q.enq.rdy

            s.value_send.msg @= concat(Bits12(0), Bits32(0),
                                       s.watcher_buffer.deq.ret[0:32], Bits10(0))

            s.temp_value_q.enq.en@= s.value_recv.en
            s.value_recv.rdy@=s.temp_value_q.enq.rdy
            s.temp_value_q.enq.msg@=s.value_recv.msg[16:24]

            s.value_buffer.deq.en@=((s.value_buffer.deq.ret[0:8] != 0) & s.value_buffer.deq.rdy &
                                    s.cr_send_buffer.enq.rdy) | (s.value_buffer.deq.ret[0:8] == 0)
            s.cr_send_buffer.enq.en@= (
                s.value_buffer.deq.ret[0:8] != 0) & s.value_buffer.deq.rdy & s.cr_send_buffer.enq.rdy

            s.cr_send.en@=s.cr_send.rdy & s.cr_send_buffer.deq.rdy
            s.cr_send_buffer.deq.en@=s.cr_send.rdy & s.cr_send_buffer.deq.rdy
            s.cr_send_buffer.enq.msg@=s.value_buffer.deq.ret[8:40]

            s.cr_send.en@=s.cr_send.rdy & s.cr_send_buffer.deq.rdy
            s.cr_send_buffer.deq.en@=s.cr_send.rdy & s.cr_send_buffer.deq.rdy
            s.cr_send.msg @=s.cr_send_buffer.deq.ret


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
        pass
