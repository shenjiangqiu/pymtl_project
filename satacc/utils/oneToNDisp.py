from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.queues.enrdy_queues import BypassQueue1RTL


class MemOneToNDispNoBuffer(Component):
    '''
    the OneToNDispNoBuffer class
    input:1 recv ifc
    output: N give ifc

    Args:
            data_bits (int): the data size 
            num_outs (int): The N out_puts

    '''
    def construct(s, data_type, num_outs):
        '''
        def construct(s, data_bits, num_outs):
        Args:
            data_bits (int): the data size 
            num_outs (int): The N out_puts


        '''
        # types
        choose_type = mk_bits(max(1, clog2(num_outs)))

        # ifcs
        s.recv = RecvIfcRTL(data_type)
        s.sends = [SendIfcRTL(data_type) for _ in range(num_outs)]

        # buffers
        s.input_buffer = BypassQueue1RTL(data_type)
        s.out_buffer = [BypassQueue1RTL(data_type)
                        for _ in range(num_outs)]

        s.current_chose = Wire(choose_type)
        # wirs
        s.choose = Mux(mk_bits(1), num_outs)

        # connections
        s.recv //= s.input_buffer.enq
        for i in range(num_outs):
            #s.gives[i] //= s.out_buffer[i].deq
            s.out_buffer[i].enq.msg //= s.input_buffer.deq.ret
            s.out_buffer[i].enq.rdy //= s.choose.in_[i]

        s.choose.sel //= s.current_chose

        # logic

        @update
        def comb():

            s.input_buffer.deq.en @= s.input_buffer.deq.rdy & s.choose.out
            for i in range(num_outs):
                s.sends[i].en @= s.sends[i].rdy & s.out_buffer[i].deq.rdy
                s.out_buffer[i].deq.en @= s.out_buffer[i].rdy & s.sends[i].rdy

                s.out_buffer[i].enq.en @= 1 if s.input_buffer.deq.rdy & s.out_buffer[i].enq.rdy & (choose_type(
                    i) == s.current_chose) else 0

        @update_ff
        def seq():
            s.current_chose <<= s.input_buffer.deq.ret[4:12]

    def line_trace(s):
        return "{},{},{}".format(s.input_buffer.line_trace(), s.current_chose, [out.line_trace() for out in s.out_buffer])


class OneToNDispNoBuffer(Component):
    '''
    the OneToNDispNoBuffer class
    input:1 recv ifc
    output: N give ifc

    Args:
            data_bits (int): the data size 
            num_outs (int): The N out_puts

    '''
    def construct(s, data_type, num_outs):
        '''
        def construct(s, data_bits, num_outs):
        Args:
            data_bits (int): the data size 
            num_outs (int): The N out_puts


        '''
        # types
        choose_type = mk_bits(max(1, clog2(num_outs)))

        # ifcs
        s.recv = RecvIfcRTL(data_type)
        s.sends = [SendIfcRTL(data_type) for _ in range(num_outs)]

        # buffers
        s.input_buffer = BypassQueue1RTL(data_type)
        s.out_buffer = [BypassQueue1RTL(data_type)
                        for _ in range(num_outs)]

        s.current_chose = Wire(choose_type)
        # wirs
        s.choose = Mux(mk_bits(1), num_outs)

        # connections
        s.recv //= s.input_buffer.enq
        for i in range(num_outs):
            #s.gives[i] //= s.out_buffer[i].deq
            s.out_buffer[i].enq.msg //= s.input_buffer.deq.ret
            s.out_buffer[i].enq.rdy //= s.choose.in_[i]

        s.choose.sel //= s.current_chose

        # logic

        @update
        def comb():

            s.input_buffer.deq.en @= s.input_buffer.deq.rdy & s.choose.out
            for i in range(num_outs):
                s.sends[i].en @= s.sends[i].rdy & s.out_buffer[i].deq.rdy
                s.out_buffer[i].deq.en @= s.out_buffer[i].rdy & s.sends[i].rdy

                s.out_buffer[i].enq.en @= 1 if s.input_buffer.deq.rdy & s.out_buffer[i].enq.rdy & (choose_type(
                    i) == s.current_chose) else 0

        @update_ff
        def seq():

            s.current_chose <<= (
                s.current_chose + 1) % (num_outs-1) if ~(s.reset) else 0

    def line_trace(s):
        return "{},{},{}".format(s.input_buffer.line_trace(), s.current_chose, [out.line_trace() for out in s.out_buffer])


class OneToNDispWithBuffer(Component):
    '''
    the OneToNDisp class
    input:1 recv ifc
    output: N give ifc

    Args:
            data_type: the data type 
            num_outs (int): The N out_puts
            input_buffer_size (int): buffer size to store the input
            out_put_buffer_size (int): buffer size to store the output
    '''
    def construct(s, data_type, num_outs, input_buffer_size, out_put_buffer_size):
        '''
        def construct(s, data_bits, num_outs, input_buffer_size, out_put_buffer_size):
        Args:
            data_type: the data type 
            num_outs (int): The N out_puts
            input_buffer_size (int): buffer size to store the input
            out_put_buffer_size (int): buffer size to store the output

        '''
        # types
        choose_type = mk_bits(max(1, clog2(num_outs)))

        # ifcs
        s.recv = RecvIfcRTL(data_type)
        s.sends = [SendIfcRTL(data_type) for _ in range(num_outs)]

        # buffers
        s.input_buffer = PipeQueueRTL(data_type, input_buffer_size)
        s.out_buffer = [PipeQueueRTL(data_type, out_put_buffer_size)
                        for _ in range(num_outs)]

        s.current_chose = Wire(choose_type)
        # wirs
        s.choose = Mux(mk_bits(1), num_outs)

        # connections
        s.recv //= s.input_buffer.enq
        for i in range(num_outs):
            #s.gives[i] //= s.out_buffer[i].deq
            s.out_buffer[i].enq.msg //= s.input_buffer.deq.ret
            s.out_buffer[i].enq.rdy //= s.choose.in_[i]

        s.choose.sel //= s.current_chose

        # logic

        @update
        def comb():

            s.input_buffer.deq.en @= s.input_buffer.deq.rdy & s.choose.out
            for i in range(num_outs):
                s.sends[i].en @= s.sends[i].rdy & s.out_buffer[i].deq.rdy
                s.out_buffer[i].deq.en @= s.out_buffer[i].rdy & s.sends[i].rdy

                s.out_buffer[i].enq.en @= 1 if s.input_buffer.deq.rdy & s.out_buffer[i].enq.rdy & (choose_type(
                    i) == s.current_chose) else 0

        @update_ff
        def seq():

            s.current_chose <<= (
                s.current_chose + 1) % (num_outs-1) if ~(s.reset) else 0

    def line_trace(s):
        return "{},{},{}".format(s.input_buffer.line_trace(), s.current_chose, [out.line_trace() for out in s.out_buffer])
