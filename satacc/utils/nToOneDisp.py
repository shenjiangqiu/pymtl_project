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
    def construct(s, data_type, num_in):
        '''
        def construct(s, data_type, num_in):
        Args:
            data_type-: the data type 
            num_in (int): The N inputs

        '''
        # types
        choose_type = mk_bits(max(1, clog2(num_in)))

        # ifcs
        s.recvs = [RecvIfcRTL(data_type) for _ in range(num_in)]
        s.send = SendIfcRTL(data_type)

        # buffers
        s.input_buffer = [BypassQueue1RTL(
            data_type) for _ in range(num_in)]
        s.out_buffer = BypassQueue1RTL(data_type)

        s.current_chose = Wire(mk_bits(max(1, clog2(num_in))))
        # wires
        s.choose = Mux(mk_bits(1), num_in)
        s.msg_choose = Mux(data_type, num_in)
        # connections

        for i in range(num_in):
            s.recvs[i] //= s.input_buffer[i].enq
            s.input_buffer[i].deq.ret //= s.msg_choose.in_[i]
            s.input_buffer[i].deq.rdy //= s.choose.in_[i]

        s.msg_choose.out //= s.out_buffer.enq.msg

        s.choose.sel //= s.current_chose
        s.msg_choose.sel //= s.current_chose
        # logic

        @update
        def comb():
            s.send.en @=s.send.rdy & s.out_buffer.deq.rdy
            s.out_buffer.deq.en@=s.send.rdy & s.out_buffer.deq.rdy

            s.out_buffer.enq.en @= s.out_buffer.enq.rdy & s.choose.out
            for i in range(num_in):
                s.input_buffer[i].deq.en @= 1 if s.out_buffer.enq.rdy & s.input_buffer[i].deq.rdy & (
                    choose_type(i) == s.current_chose) else 0

        @update_ff
        def seq():

            s.current_chose <<= (
                s.current_chose + 1) % (num_in-1) if ~(s.reset) else 0

    def line_trace(s):
        return "{},{},{}".format([input_buffer.line_trace() for input_buffer in s.input_buffer], s.current_chose, s.out_buffer.line_trace)


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
    def construct(s, data_type, num_in, input_buffer_size, out_put_buffer_size):
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
        s.recvs = [RecvIfcRTL(data_type) for _ in range(num_in)]
        s.send = SendIfcRTL(data_type)

        # buffers
        s.input_buffer = [PipeQueueRTL(
            data_type, input_buffer_size) for _ in range(num_in)]
        s.out_buffer = PipeQueueRTL(data_type, out_put_buffer_size)

        s.current_chose = Wire(mk_bits(max(1, clog2(num_in))))
        # wires
        s.choose = Mux(mk_bits(1), num_in)
        s.msg_choose = Mux(data_type, num_in)
        # connections

        for i in range(num_in):
            s.recvs[i] //= s.input_buffer[i].enq
            s.input_buffer[i].deq.ret //= s.msg_choose.in_[i]
            s.input_buffer[i].deq.rdy //= s.choose.in_[i]

        s.msg_choose.out //= s.out_buffer.enq.msg

        s.choose.sel //= s.current_chose
        s.msg_choose.sel //= s.current_chose
        # logic

        @update
        def comb():
            s.send.en @=s.send.rdy & s.out_buffer.deq.rdy
            s.out_buffer.deq.en@=s.send.rdy & s.out_buffer.deq.rdy
            s.send.msg@=s.out_buffer.deq.ret
            s.out_buffer.enq.en @= s.out_buffer.enq.rdy & s.choose.out
            for i in range(num_in):
                s.input_buffer[i].deq.en @= 1 if s.out_buffer.enq.rdy & s.input_buffer[i].deq.rdy & (
                    choose_type(i) == s.current_chose) else 0

        @update_ff
        def seq():

            s.current_chose <<= (
                s.current_chose + 1) % (num_in-1) if ~(s.reset) else 0

    def line_trace(s):
        return "{},{},{}".format([input_buffer.line_trace() for input_buffer in s.input_buffer], s.current_chose, s.out_buffer.line_trace)
