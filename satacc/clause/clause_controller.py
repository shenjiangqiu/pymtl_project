from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst
from ..utils.give_to_send import Give_to_send


class Clause_fsm(Component):
    def construct(s):
        # ifcs
        s.value_recv = RecvIfcRTL(Bits34)  # lit:32,value 2
        s.generated_send = SendIfcRTL(mk_bits(32))
        s.conflict = OutPort()
        # regs

        s.status = RegEnRst(Bits2)
        s.unit_lit = RegEnRst(Bits32)

        s.generated_queue = PipeQueueRTL(Bits32)

        # logic
        s.generate_adpter = Give_to_send(Bits32)
        s.generate_adpter.give_en //= s.generated_queue.deq.en
        s.generate_adpter.give_rdy //= s.generated_queue.deq.rdy
        s.generate_adpter.give_ret //= s.generated_queue.deq.ret
        s.generate_adpter.send //= s.generated_send

        @update
        def comb():
            s.generated_queue.enq.msg @= s.unit_lit.out
            # the control logic
            if (s.generated_queue.enq.rdy == 0) | (s.value_recv.en == 0):
                s.status.en@=0
                s.unit_lit.en@=0
            else:
                s.status.en@=1
                s.unit_lit.en@=1

            s.value_recv.rdy@= s.generated_queue.enq.rdy
            s.conflict@=(s.value_recv.msg[0:32] == 0) & (s.status.out == 0) & (
                s.generated_queue.enq.rdy == 1) & (s.value_recv.en == 1)

            # the status change logic
            # s.unit_lit.in_@=s.unit_lit.out

            s.generated_queue.enq.en @= (s.generated_queue.enq.rdy == 1) & (
                s.value_recv.en == 1) & (s.status.out == 1) & (s.value_recv.msg[0:32] == 0)
            # the end of a string , no need to read the value

            if s.value_recv.msg[0:32] != 0:
                if s.status.out == 0:  # start all flase
                    if s.value_recv.msg[32:34] == 0:  # undefined
                        s.status.in_@=1
                        s.unit_lit.in_@=s.value_recv.msg[0:32]
                    elif s.value_recv.msg[32:34] == 1:  # true
                        s.status.in_@=3
                    elif s.value_recv.msg[32:34] == 2:  # false
                        s.status.in_@=0
                elif s.status.out == 1:  # have one undefined and no true
                    if s.value_recv.msg[32:34] == 0:  # undefined
                        s.status.in_@=2
                    elif s.value_recv.msg[32:34] == 1:  # true
                        s.status.in_@=3
                    elif s.value_recv.msg[32:34] == 2:  # false
                        s.status.in_@=1
                elif s.status.out == 2:  # have two or more undefined and no true
                    if s.value_recv.msg[32:34] == 0:  # undefined
                        s.status.in_@=2
                    elif s.value_recv.msg[32:34] == 1:  # true
                        s.status.in_@=3
                    elif s.value_recv.msg[32:34] == 2:  # false
                        s.status.in_@=2
                elif s.status.out == 3:  # have one true
                    if s.value_recv.msg[32:34] == 0:  # undefined
                        s.status.in_@=3
                    elif s.value_recv.msg[32:34] == 1:  # true
                        s.status.in_@=3
                    elif s.value_recv.msg[32:34] == 2:  # false
                        s.status.in_@=3
            else:
                s.status.in_@=0
                s.unit_lit.in_@=s.unit_lit.out
        pass
