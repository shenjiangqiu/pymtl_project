from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst


class Watcher_data(Component):
    """def construct(s, data_size, return_size, return_buffer, send_buffer):
        construct the watcher_data
        input: getifc
        output: sendifc
        memory: Memifc:req:sendifc resp:recvifc
        Args:
            s (self): self
            data_size (int): the data size
            return_size (int): the returned data size from memory
            return_buffer (int): the returned data buffer size
            send_buffer (int): the send buffer size
    """
    def construct(s, data_size, return_size, return_buffer, send_buffer, meta_data_buffer):
        """construct the watcher_data
        input: getifc
        output sendifc
        Args:
            s (self): self
            data_size (int): the data size
            return_size (int): the returned data size from memory
            return_buffer (int): the returned data buffer size
            send_buffer (int): the send buffer size
            meta_data_buffer (int): the meta buffer size
        """
        # types
        # ifcs
        s.get = GetIfcRTL(data_size)
        s.send = SendIfcRTL(return_size)  # send to watcher unit
        s.meta_mem_send = SendIfcRTL(mk_bits(32))
        s.meta_mem_recv = RecvIfcRTL(mk_bits(64))  # one cache line size
        s.data_mem_send = SendIfcRTL(mk_bits(32))
        s.data_mem_recv = RecvIfcRTL(mk_bits(return_size))

        # buffers
        # get the watcher size and start addr
        s.send_queue = PipeQueueRTL(data_size, send_buffer)
        s.meta_data_queue = PipeQueueRTL(64, meta_data_buffer)
        s.return_queue = PipeQueueRTL(return_size, return_buffer)

        # connects
        s.get.ret //= s.send_queue.enq.msg

        s.meta_mem_recv //= s.meta_data_queue.enq
        s.meta_mem_send.msg //= s.send_queue.deq.ret

        s.data_mem_recv //= s.return_queue.enq

        s.send.msg //= s.return_queue.deq.ret

        # logics
        @update
        def comb():
            s.data_mem_send.msg @= s.meta_data_queue.deq.ret[32:64]
            s.get.en@=s.get.rdy & s.send_queue.enq.rdy
            s.send_queue.enq.en@=s.get.rdy & s.send_queue.enq.rdy

            s.meta_mem_send.en@=s.meta_mem_send.rdy & s.send_queue.deq.rdy
            s.send_queue.deq.en@=s.meta_mem_send.rdy & s.send_queue.deq.rdy

            s.data_mem_send.en@=s.data_mem_send.rdy & s.meta_data_queue.deq.rdy
            s.meta_data_queue.deq.en@=s.data_mem_send.rdy & s.meta_data_queue.deq.rdy

            s.send.en@=s.send.rdy & s.return_queue.deq.rdy
            s.return_queue.deq.en @=s.send.rdy & s.return_queue.deq.rdy
