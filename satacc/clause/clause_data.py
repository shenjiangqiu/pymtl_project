from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst


class Clause_data(Component):
    """Clause data fetch class
    input: recv: the clause reference\n
    output: send: the literals\n
    mem_send: send the reference ,get the literals of the clause
    mem_recv: recive the literals

    Args:
        clause_data_bits (int): number bits of the reference data
    """
    def construct(s, clause_data_bits):
        """construct the clause data

        Args:
            s (self): self
            clause_data_bits (int): number bits of the reference data
        """
        s.recv = RecvIfcRTL(mk_bits(clause_data_bits))
        s.send = SendIfcRTL(mk_bits(32))  # one literal in the clause,

        s.mem_send = SendIfcRTL(mk_bits(32))
        s.mem_recv = RecvIfcRTL(mk_bits(32))

        # buffers

        s.clause_cr_buffer = PipeQueueRTL(mk_bits(clause_data_bits), 8)
        s.literal_buffer = PipeQueueRTL(mk_bits(32), 64)

        # connects
        s.recv //= s.clause_cr_buffer.enq
        s.mem_recv //= s.literal_buffer.enq
        s.clause_cr_buffer.deq.ret //= s.mem_send.msg
        s.literal_buffer.deq.ret //= s.send.msg

        @update
        def comb():
            s.mem_send.en@=s.mem_send.rdy & s.clause_cr_buffer.deq.rdy
            s.clause_cr_buffer.deq.en@=s.mem_send.rdy & s.clause_cr_buffer.deq.rdy
            
            s.send.en@=s.send.rdy & s.literal_buffer.deq.rdy
            s.literal_buffer.deq.en@=s.send.rdy & s.literal_buffer.deq.rdy
            
