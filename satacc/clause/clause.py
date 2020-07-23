from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst

from .clause_data import Clause_data
from .clause_process import Clause_process


class Clause(Component):
    """the clause,input the clause reference\n
    output: the generated literals

    Args:
        Component (s): self
    """
    def construct(s):
        # ifcs
        s.recv = RecvIfcRTL(mk_bits(32))
        s.send = SendIfcRTL(mk_bits(32))

        s.mem_data_send = SendIfcRTL(mk_bits(32))
        s.mem_data_recv = RecvIfcRTL(mk_bits(32))

        s.mem_proc_send = SendIfcRTL(mk_bits(32))
        s.mem_proc_recv = RecvIfcRTL(mk_bits(32))

        # components

        s.clause_data = Clause_data(32)
        s.clause_process = Clause_process()

        # connects

        s.clause_data.send //= s.clause_process.recv
        s.recv //= s.clause_data.recv
        s.send //= s.clause_process.send_to_trail

        s.mem_data_recv //= s.clause_data.mem_recv
        s.mem_data_send //= s.clause_data.mem_send
        s.mem_proc_recv //= s.clause_process.mem_resp
        s.mem_proc_send //= s.clause_process.mem_req
