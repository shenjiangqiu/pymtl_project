from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL, BypassQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst


class Watcher_process(Component):
    """the Watcher Process class
    input: the wather:recvifc
    output: the clause cr to be send:sendifc

    Args:
        data_bits (int): the data bits of the watcher:1 bit bool, 32bit clause reference
        clause_bits (int): the generated clause bits
    """
    def construct(s, data_bits, clause_bits):
        """[summary]

        Args:
            s ([type]): [description]
            data_bits (int): the data bits of the watcher:1 bit bool, 32bit clause reference
            clause_bits (int): the generated clause bits
        """
        # ifcs

        s.recv = RecvIfcRTL(mk_bits(data_bits))
        s.send = SendIfcRTL(mk_bits(clause_bits))

        s.watcher_buffer = PipeQueueRTL(mk_bits(data_bits), 8)
        s.clause_send_buffer = PipeQueueRTL(mk_bits(clause_bits), 8)

        s.send.msg //= s.clause_send_buffer.deq.ret
        s.recv //= s.watcher_buffer.enq

        @update
        def comb():
            s.clause_send_buffer.enq.msg @= s.watcher_buffer.deq.ret[1:]
            s.watcher_buffer.deq.en @=s.watcher_buffer.deq.rdy and (
                s.clause_send_buffer.enq.rdy or s.watcher_buffer.deq.ret[0] == 1)  # if clause buffer rdy or no need to enqueue
            s.clause_send_buffer.enq.en @=s.clause_send_buffer.enq.rdy and s.watcher_buffer.deq.rdy and (
                s.watcher_buffer.deq.ret[0] == 0)  # only if deq.rdy and not bypass(==0)
            s.send.en @=s.send.rdy and s.clause_send_buffer.deq.rdy
            s.clause_send_buffer.deq.en @= s.send.rdy and s.clause_send_buffer.deq.rdy
            pass

        pass
