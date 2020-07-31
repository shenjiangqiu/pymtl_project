from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst

from .watcher.watcher import Watcher
from .clause.clause import Clause
from .utils import trail, nToOneDisp, oneToNDisp


class Acc(Component):
    def construct(s):
        # ifcs
        req = Bits153
        resp = Bits81
        s.clause_size_mem_sends = [SendIfcRTL(mk_bits(110)) for _ in range(8)]
        s.clause_size_mem_recvs = [RecvIfcRTL(mk_bits(48)) for _ in range(8)]
        s.clause_fetcher_mem_outs = [SendIfcRTL(req) for _ in range(8)]
        s.clause_fetcher_mem_ins = [RecvIfcRTL(resp) for _ in range(8)]
        s.clause_value_mem_sends = [SendIfcRTL(mk_bits(79)) for _ in range(8)]
        s.clause_value_mem_recvs = [RecvIfcRTL(mk_bits(17)) for _ in range(8)]
        s.clause_confs = [OutPort() for _ in range(8)]

        s.watcher_lit_to_size_addr_mem_sends = [
            SendIfcRTL(mk_bits(176)) for _ in range(8)]
        s.watcher_lit_to_size_addr_mem_recvs = [
            RecvIfcRTL(mk_bits(114)) for _ in range(8)]
        s.watcher_watcher_send_mem_sends = [
            SendIfcRTL(Bits144) for _ in range(8)]
        s.watcher_watcher_recvs = [RecvIfcRTL(Bits82) for _ in range(8)]
        s.watcher_value_sends = [SendIfcRTL(Bits86) for _ in range(8)]
        s.watcher_value_recvs = [RecvIfcRTL(Bits24) for _ in range(8)]

        s.trail_input_ifc = RecvIfcRTL(mk_bits(32))

        # components
        s.n_to_trail = nToOneDisp.NToOneDispWithBuffer(32, 9, 16, 16)
        s.trail_to_watchers = oneToNDisp.OneToNDispWithBuffer(32, 8, 2, 16)
        s.trail = trail.Trail(32, 1024)

        s.watchers = [Watcher(i) for i in range(8)]
        s.clauses = [Clause(i) for i in range(8)]

        # connects
        for i in range(8):
            s.clause_size_mem_sends[i] //= s.clauses[i].size_mem_send
            s.clause_size_mem_recvs[i] //= s.clauses[i].size_mem_recv
            s.clause_fetcher_mem_outs[i] //= s.clauses[i].fetcher_mem_out
            s.clause_fetcher_mem_ins[i] //= s.clauses[i].fetcher_mem_in
            s.clause_value_mem_sends[i] //= s.clauses[i].value_mem_send
            s.clause_value_mem_recvs[i] //= s.clauses[i].value_mem_recv
            s.clause_confs[i] //= s.clauses[i].conf

            s.watcher_lit_to_size_addr_mem_sends[i] //= s.watchers[i].lit_to_size_addr_mem_send
            s.watcher_lit_to_size_addr_mem_recvs[i] //= s.watchers[i].lit_to_size_addr_mem_recv
            s.watcher_watcher_send_mem_sends[i] //= s.watchers[i].watcher_send_mem_send
            s.watcher_watcher_recvs[i] //= s.watchers[i].watcher_recv
            s.watcher_value_sends[i] //= s.watchers[i].value_send
            s.watcher_value_recvs[i] //= s.watchers[i].value_recv

            s.watchers[i].cr_send //= s.clauses[i].cr_recv
            s.trail_to_watchers.sends[i] //= s.watchers[i].from_trail_recv
            s.n_to_trail.recvs[i] //= s.clauses[i].to_trail
            
        s.n_to_trail.recvs[-1] //= s.trail_input_ifc
        
        s.trail_to_watchers.recv //= s.trail.send
        #s.trail.recv.msg //= s.n_to_trail.give.ret
        s.trail.recv //= s.n_to_trail.send
