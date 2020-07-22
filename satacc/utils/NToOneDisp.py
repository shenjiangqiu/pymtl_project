from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL


class NToOneDisp(Component):
    '''
    the NToOneDisp class
    input: N recv ifc
    output: 1 give ifc
    '''
    def construct(s, data_bits, num_in, input_buffer_size, out_put_buffer_size):
        '''
        def construct(s, data_bits, num_in, input_buffer_size, out_put_buffer_size):
        Args:
            data_bits (int): the data size 
            num_in (int): The N inputs
            input_buffer_size (int): buffer size to store the input
            out_put_buffer_size (int): buffer size to store the output

        '''
        # types
        choose_type = mk_bits(max(1, clog2(num_outs)))

        # ifcs
        s.recvs = [RecvIfcRTL(mk_bits(data_bits)) for _ in range(num_in)]
        s.give = GiveIfcRTL(mk_bits(data_bits))

        # buffers
        s.input_buffer = [PipeQueueRTL(
            mk_bits(data_bits), input_buffer_size) for _ in range(num_outs)]
        s.out_buffer = PipeQueueRTL(mk_bits(data_bits), out_put_buffer_size)

        s.current_chose = Wire(max(1, clog2(num_outs)))
        # wirs
        s.choose = Mux(1, num_outs)

        # connections
        s.give //= s.out_buffer.deq
        for i in range(num_outs):
            s.recvs[i] //= s.input_buffer[i].enq
            s.input_buffer[i].deq.ret //= s.out_buffer.enq.msg
            s.input_buffer[i].deq.rdy //= s.choose.in_[i]

        s.choose.sel //= s.current_chose

        # logic

        @update
        def comb():
            s.output_buffer.enq.en @= s.output_buffer.enq.rdy and s.choose.out
            for i in range(num_outs):
                s.input_buffer[i].deq.en @= 1 if s.output_buffer.enq.rdy and s.input_buffer[i].deq.rdy and choose_type(
                    i) == s.current_chose else 0
            pass

        @update_ff
        def seq():

            s.current_chose <<= (
                s.current_chose + 1) % (num_outs-1) if not s.reset else 0
            pass

    def line_trace(s):
        return "{},{},{}".format([input_buffer.line_trace() for input_buffer in s.input_buffer], s.current_chose, s.out_buffer.line_trace)
