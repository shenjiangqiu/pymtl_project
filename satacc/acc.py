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
        s.trail_input_ifc = RecvIfcRTL(mk_bits(32))

        s.watcher_meta_mem_send = [SendIfcRTL(
            mk_bits(32)) for _ in range(8)]  # send watcher addr
        s.watcher_meta_mem_recv = [RecvIfcRTL(
            mk_bits(64)) for _ in range(8)]  # get watcher metadata
        s.watcher_data_mem_send = [SendIfcRTL(
            mk_bits(32)) for _ in range(8)]  # send watcher data addr
        # get watcher wachers(include one bit bool and a clause ref)
        s.watcher_data_mem_recv = [RecvIfcRTL(mk_bits(33)) for _ in range(8)]

        s.clause_mem_data_send = [SendIfcRTL(
            mk_bits(32)) for _ in range(8)]  # send clause ref
        s.clause_mem_data_recv = [RecvIfcRTL(
            mk_bits(32)) for _ in range(8)]  # recive literals
        s.clause_mem_proc_send = [SendIfcRTL(
            mk_bits(32)) for _ in range(8)]  # send literal value addr
        s.clause_mem_proc_recv = [RecvIfcRTL(
            mk_bits(32)) for _ in range(8)]  # get values

        # components
        s.n_to_trail = nToOneDisp.NToOneDisp(32, 9, 16, 16)
        s.trail_to_watchers = oneToNDisp.OneToNDisp(32, 8, 2, 16)
        s.trail = trail.Trail(32, 1024)
        s.watchers = [Watcher() for _ in range(8)]
        s.clauses = [Clause() for _ in range(8)]

        # connects
        for i in range(8):
            s.watchers[i].send_to_clause //= s.clauses[i].recv
            s.watchers[i].get_from_trail //= s.trail_to_watchers.gives[i]
            s.clauses[i].send //= s.n_to_trail.recvs[i]

            s.watchers[i].data_mem_recv //= s.watcher_data_mem_recv[i]
            s.watchers[i].data_mem_send //= s.watcher_data_mem_send[i]
            s.watchers[i].meta_mem_recv //= s.watcher_meta_mem_recv[i]
            s.watchers[i].meta_mem_send //= s.watcher_meta_mem_send[i]

            s.clauses[i].mem_data_recv //= s.clause_mem_data_recv[i]
            s.clauses[i].mem_data_send //= s.clause_mem_data_send[i]
            s.clauses[i].mem_proc_recv //= s.clause_mem_proc_recv[i]
            s.clauses[i].mem_proc_send //= s.clause_mem_proc_send[i]

        s.n_to_trail.recvs[-1] //= s.trail_input_ifc
        s.trail_to_watchers.recv //= s.trail.send
        s.trail.recv.msg //= s.n_to_trail.give.ret
        @update
        def comb():
            s.trail.recv.en @=s.trail.recv.rdy & s.n_to_trail.give.rdy
            s.n_to_trail.give.en @=s.trail.recv.rdy & s.n_to_trail.give.rdy
