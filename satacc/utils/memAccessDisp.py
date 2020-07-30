from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL, MemMinionIfcRTL

from .nToOneDisp import NToOneDispNoBuffer
from .oneToNDisp import OneToNDispNoBuffer, MemOneToNDispNoBuffer


class MemAccessDispNoBuffer(Component):
    def construct(self, num_in, req_data_type, resp_data_type):
        # type

        # ifcs
        self.c_in_ifcs = [RecvIfcRTL(req_data_type) for _ in range(num_in)]
        self.c_out_ifcs = [SendIfcRTL(resp_data_type) for _ in range(num_in)]
        self.mem_in_ifc = RecvIfcRTL(resp_data_type)
        self.mem_out_ifc = SendIfcRTL(req_data_type)
        # buffers "no buffer"
        self.send_to_mem_disp = NToOneDispNoBuffer(req_data_type, num_in)
        self.return_to_acc_disp = MemOneToNDispNoBuffer(resp_data_type, num_in)

        # connect
        for i in range(num_in):
            self.c_in_ifcs[i] //= self.send_to_mem_disp.recvs[i]
            self.c_out_ifcs[i] //= self.return_to_acc_disp.sends[i]

        self.mem_in_ifc //= self.return_to_acc_disp.recv
        self.mem_out_ifc //= self.send_to_mem_disp.send

        pass
