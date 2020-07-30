from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst


class Clause_process(Component):
    """the Clause_process class
    input: the clause literals
    output: the generated new literals

    mem_out: the addr of the value of the literal
    mem_in: the value of the literal
    Args:
        Component ([type]): [description]
    """
    def construct(s):
        # ifcs
        s.recv = RecvIfcRTL(mk_bits(32))
        s.send_to_trail = SendIfcRTL(mk_bits(32))

        s.mem_req = SendIfcRTL(mk_bits(32))
        s.mem_resp = RecvIfcRTL(mk_bits(32))

        # buffers
        s.literal_buffer = PipeQueueRTL(mk_bits(32), 8)
        s.literal_value_buffer = PipeQueueRTL(mk_bits(32), 8)
        s.generated_buffer = PipeQueueRTL(mk_bits(32), 8)

        # connects
        s.recv //= s.literal_buffer.enq
        s.mem_resp //= s.literal_value_buffer.enq
        s.send_to_trail.msg //= s.generated_buffer.deq.ret
        s.literal_buffer.deq.ret //= s.mem_req.msg
        # fsm to process the literals
        @update
        def comb():
            s.literal_buffer.deq.en@=s.literal_buffer.deq.rdy & s.mem_req.rdy
            s.mem_req.en@=s.literal_buffer.deq.rdy & s.mem_req.rdy

            # TO-DO need to process the logic of the literal value
            s.literal_value_buffer.deq.en@=s.literal_value_buffer.deq.rdy

            s.generated_buffer.enq.en@=0
            s.generated_buffer.enq.msg@=0
            s.generated_buffer.deq.en@=s.generated_buffer.deq.rdy & s.send_to_trail.rdy
            s.send_to_trail.en@=s.generated_buffer.deq.rdy & s.send_to_trail.rdy
