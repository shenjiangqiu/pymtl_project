from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL, BypassQueueRTL
from pymtl3.stdlib.queues.enrdy_queues import BypassQueue1RTL


class NToOneDispNoBuffer(Component):
    '''
    the NToOneDispNoBuffer class
    input: N recv ifc
    output: 1 give ifc

    Args:
            data_type : the data type 
            num_in (int): The N inputs
            

    '''
    def construct(self, data_type, num_in):
        '''
        def construct(s, data_type, num_in):
        Args:
            data_type-: the data type 
            num_in (int): The N inputs
            
        '''
        # types
        choose_type = mk_bits(max(1, clog2(num_in)))

        # ifcs
        self.recvs = [RecvIfcRTL(data_type) for _ in range(num_in)]
        self.send = SendIfcRTL(data_type)

        # buffers
        self.input_buffer = [BypassQueue1RTL(
            data_type) for _ in range(num_in)]
        self.out_buffer = BypassQueue1RTL(data_type)

        self.current_chose = Wire(mk_bits(max(1, clog2(num_in))))
        # wires
        self.choose = Mux(mk_bits(1), num_in)
        self.msg_choose = Mux(data_type, num_in)
        # connections

        for i in range(num_in):
            self.recvs[i] //= self.input_buffer[i].enq
            self.input_buffer[i].deq.ret //= self.msg_choose.in_[i]
            self.input_buffer[i].deq.rdy //= self.choose.in_[i]

        self.msg_choose.out //= self.out_buffer.enq.msg

        self.choose.sel //= self.current_chose
        self.msg_choose.sel //= self.current_chose
        # logic

        @update
        def comb():
            self.send.en @=self.send.rdy & self.out_buffer.deq.rdy
            self.out_buffer.deq.en@=self.send.rdy & self.out_buffer.deq.rdy

            self.out_buffer.enq.en @= self.out_buffer.enq.rdy & self.choose.out
            for i in range(num_in):
                self.input_buffer[i].deq.en @= 1 if self.out_buffer.enq.rdy & self.input_buffer[i].deq.rdy & (
                    choose_type(i) == self.current_chose) else 0

        @update_ff
        def seq():

            self.current_chose <<= (
                self.current_chose + 1) % (num_in-1) if ~(self.reset) else 0

    def line_trace(self):
        return "{},{},{}".format([input_buffer.line_trace() for input_buffer in self.input_buffer], self.current_chose, self.out_buffer.line_trace)


class NToOneDispWithBuffer(Component):
    '''
    the NToOneDisp class
    input: N recv ifc
    output: 1 give ifc

    Args:
            data_bits (int): the data size 
            num_in (int): The N inputs
            input_buffer_size (int): buffer size to store the input
            out_put_buffer_size (int): buffer size to store the output

    '''
    def construct(self, data_type, num_in, input_buffer_size, out_put_buffer_size):
        '''
        def construct(s, data_bits, num_in, input_buffer_size, out_put_buffer_size):
        Args:
            data_bits (int): the data size 
            num_in (int): The N inputs
            input_buffer_size (int): buffer size to store the input
            out_put_buffer_size (int): buffer size to store the output

        '''
        # types
        choose_type = mk_bits(max(1, clog2(num_in)))

        # ifcs
        self.recvs = [RecvIfcRTL(data_type) for _ in range(num_in)]
        self.send = SendIfcRTL(data_type)

        # buffers
        self.input_buffer = [PipeQueueRTL(
            data_type, input_buffer_size) for _ in range(num_in)]
        self.out_buffer = PipeQueueRTL(data_type, out_put_buffer_size)

        self.current_chose = Wire(mk_bits(max(1, clog2(num_in))))
        # wires
        self.choose = Mux(mk_bits(1), num_in)
        self.msg_choose = Mux(data_type, num_in)
        # connections

        for i in range(num_in):
            self.recvs[i] //= self.input_buffer[i].enq
            self.input_buffer[i].deq.ret //= self.msg_choose.in_[i]
            self.input_buffer[i].deq.rdy //= self.choose.in_[i]

        self.msg_choose.out //= self.out_buffer.enq.msg

        self.choose.sel //= self.current_chose
        self.msg_choose.sel //= self.current_chose
        # logic

        @update
        def comb():
            self.send.en @=self.send.rdy & self.out_buffer.deq.rdy
            self.out_buffer.deq.en@=self.send.rdy & self.out_buffer.deq.rdy

            self.out_buffer.enq.en @= self.out_buffer.enq.rdy & self.choose.out
            for i in range(num_in):
                self.input_buffer[i].deq.en @= 1 if self.out_buffer.enq.rdy & self.input_buffer[i].deq.rdy & (
                    choose_type(i) == self.current_chose) else 0

        @update_ff
        def seq():

            self.current_chose <<= (
                self.current_chose + 1) % (num_in-1) if ~(self.reset) else 0

    def line_trace(self):
        return "{},{},{}".format([input_buffer.line_trace() for input_buffer in self.input_buffer], self.current_chose, self.out_buffer.line_trace)
