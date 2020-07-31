from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL, BypassQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst
from pymtl3.stdlib.queues.enrdy_queues import BypassQueue1RTL

from .clause_data import Clause_data
from .clause_process import Clause_process
from ..utils.mem_oparator import Sized_memory_sender_in_order
from .clause_controller import Clause_fsm

# watcher send: type:4 op:8 addr:64 len:2 data:32 =110
# watcher recv: type:4 op:8 test:2 len:2 data:32= 48
# value send: type:4 op:8 addr:64 len:1 data:2 =79

# value recv: type:4 op:8 test:2 len:1 data:2= 17


class Clause(Component):
    def construct(s, index):
        # ifcs
        s.cr_recv = RecvIfcRTL(mk_bits(32))
        s.size_mem_send = SendIfcRTL(mk_bits(110))
        s.size_mem_recv = RecvIfcRTL(mk_bits(48))

        req = Bits153
        resp = Bits81
        # ifcs

        s.fetcher_mem_out = SendIfcRTL(req)
        s.fetcher_mem_in = RecvIfcRTL(resp)

        s.value_mem_send = SendIfcRTL(mk_bits(79))
        s.value_mem_recv = RecvIfcRTL(mk_bits(17))
        s.conf = OutPort()

        s.to_trail = SendIfcRTL(mk_bits(32))

        # buffers
        s.cr_q = BypassQueueRTL(Bits32, 4)
        s.size_addr_q = PipeQueueRTL(Bits96, 8)
        #   def construct(s, size_type, addr_type, item_size, mem_request_dest, recv_queue_size):
        s.clause_fetcher = Sized_memory_sender_in_order(
            Bits32, Bits64, 32, 1, 8)
        s.clause_lit_queue = PipeQueueRTL(Bits32, 8)
        s.clause_lit_with_value = PipeQueueRTL(Bits34, 8)
        s.clause_process_fsm = Clause_fsm()

        s.temp_cr_size = BypassQueueRTL(Bits32, 1)
        s.temp_cr_addr = BypassQueueRTL(Bits64, 1)

        s.cr_recv //= s.cr_q.enq
        s.clause_lit_queue.enq //= s.clause_fetcher.data_out
        s.to_trail //= s.clause_process_fsm.generated_send
        s.conf //= s.clause_process_fsm.conflict

        s.temp_lit = BypassQueueRTL(Bits32, 1)
        s.temp_value = BypassQueueRTL(Bits2, 1)
        s.fetcher_mem_in //= s.clause_fetcher.mem_in
        s.fetcher_mem_out //= s.clause_fetcher.mem_out

        @update
        def comb():
            s.value_mem_recv.rdy@=s.temp_value.enq.rdy
            s.size_mem_send.en@=s.size_mem_send.rdy & s.temp_cr_size.enq.rdy & s.temp_cr_addr.enq.rdy & s.cr_q.deq.rdy
            s.cr_q.deq.en@=s.size_mem_send.rdy & s.temp_cr_size.enq.rdy & s.temp_cr_addr.enq.rdy & s.cr_q.deq.rdy
            s.temp_cr_size.enq.en@=s.temp_cr_addr.enq.rdy & s.size_mem_recv.en
            s.size_mem_recv.rdy@=s.temp_cr_size.enq.rdy
            s.temp_cr_addr.enq.en@=s.size_mem_send.rdy & s.temp_cr_size.enq.rdy & s.temp_cr_addr.enq.rdy & s.cr_q.deq.rdy
            msg = Bits110()

            s.size_mem_send.msg@=msg
            s.temp_cr_size.enq.msg@=s.size_mem_recv.msg[48-32:48]
            # TODO: the real addr can be calculated immediately
            s.temp_cr_addr.enq.msg@=concat(Bits32(0), s.cr_q.deq.ret)

            s.size_addr_q.enq.en@=s.size_addr_q.enq.rdy & s.temp_cr_size.deq.rdy & s.temp_cr_addr.deq.rdy
            s.temp_cr_size.deq.en@= s.size_addr_q.enq.rdy & s.temp_cr_size.deq.rdy & s.temp_cr_addr.deq.rdy
            s.temp_cr_addr.deq.en@= s.size_addr_q.enq.rdy & s.temp_cr_size.deq.rdy & s.temp_cr_addr.deq.rdy
            s.size_addr_q.enq.msg@=concat(s.temp_cr_size.deq.ret,
                                          s.temp_cr_addr.deq.ret)
            s.clause_fetcher.size_recv.en@=s.clause_fetcher.size_recv.rdy & s.size_addr_q.deq.rdy
            s.clause_fetcher.addr_recv.en@=s.clause_fetcher.addr_recv.rdy & s.size_addr_q.deq.rdy
            s.size_addr_q.deq.en@=s.clause_fetcher.size_recv.rdy & s.clause_fetcher.addr_recv.rdy & s.size_addr_q.deq.rdy
            s.clause_fetcher.size_recv.msg@=s.size_addr_q.deq.ret[0:32]
            s.clause_fetcher.addr_recv.msg@=s.size_addr_q.deq.ret[32:96]
            #
            s.value_mem_send.en@=s.value_mem_send.rdy & s.temp_value.enq.rdy & s.temp_lit.enq.rdy & s.clause_lit_queue.deq.rdy
            s.clause_lit_queue.deq.en@=s.value_mem_send.rdy & s.temp_value.enq.rdy & s.temp_lit.enq.rdy & s.clause_lit_queue.deq.rdy
            s.temp_value.enq.en@=s.temp_lit.enq.rdy & s.size_mem_recv.en
            s.size_mem_recv.rdy@=s.temp_value.enq.rdy
            s.temp_lit.enq.en@=s.value_mem_send.rdy & s.temp_value.enq.rdy & s.temp_lit.enq.rdy & s.clause_lit_queue.deq.rdy
            msg = Bits79()

            s.value_mem_send.msg@=msg

            s.temp_value.enq.msg@=s.value_mem_recv.msg[17-2:17]
            # TODO: the real addr can be calculated immediately
            s.temp_lit.enq.msg@= s.clause_lit_queue.deq.ret

            s.clause_lit_with_value.enq.en@=s.clause_lit_with_value.enq.rdy & s.temp_value.deq.rdy & s.temp_lit.deq.rdy
            s.temp_value.deq.en@= s.clause_lit_with_value.enq.rdy & s.temp_value.deq.rdy & s.temp_lit.deq.rdy
            s.temp_lit.deq.en@= s.clause_lit_with_value.enq.rdy & s.temp_value.deq.rdy & s.temp_lit.deq.rdy

            s.clause_lit_with_value.enq.msg@=concat(
                s.temp_lit.deq.ret, s.temp_value.deq.ret)

            s.clause_lit_with_value.deq.en@=s.clause_lit_with_value.deq.rdy & s.clause_process_fsm.value_recv.rdy
            s.clause_process_fsm.value_recv.en@=s.clause_lit_with_value.deq.rdy & s.clause_process_fsm.value_recv.rdy

            pass
        pass
    pass


class Clause_old(Component):
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
