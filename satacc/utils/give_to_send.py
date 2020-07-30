from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL, MemMsgType
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst


class Give_to_send(Component):
    def construct(s, data_type):
        s.give_en = OutPort()
        s.give_rdy = InPort()
        s.give_ret = InPort(data_type)
        s.send = SendIfcRTL(data_type)

        @update
        def comb():
            s.send.en@=s.send.rdy & s.give_rdy
            s.give_en@=s.send.rdy & s.give_rdy
            s.send.msg@=s.give_ret
