from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL


class Watcher_data(Component):
    """def construct(s, data_size, return_size, return_buffer, send_buffer):
        construct the watcher_data
        input: getifc
        output: sendifc
        memory: Memifc
        Args:
            s (self): self
            data_size (int): the data size
            return_size (int): the returned data size from memory
            return_buffer (int): the returned data buffer size
            send_buffer (int): the send buffer size
    """
    def construct(s, data_size, return_size, return_buffer, send_buffer):
        """construct the watcher_data
        input: getifc
        output sendifc
        Args:
            s (self): self
            data_size (int): the data size
            return_size (int): the returned data size from memory
            return_buffer (int): the returned data buffer size
            send_buffer (int): the send buffer size
        """
        #types
        req_class, resp_class = mk_mem_msg(8, 32, 32)

        # ifcs
        s.get = GetIfcRTL(data_size)
        s.send = SendIfcRTL(data_size)
        s.dmem = MemMasterIfcRTL(req_class, resp_class)

        # buffers
        s.send_queue = PipeQueueRTL(data_size, send_buffer)
        s.return_queue = PipeQueueRTL(return_size, return_buffer)

        #connects
        s.dmem //=s.send_queu


  
    pass
    pass
