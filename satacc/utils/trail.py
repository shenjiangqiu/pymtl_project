from pymtl3 import *
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL


class Trail(Component):
    '''
    the trail queue,
    have a recv ifs as input
    and a send ifs as output
    Args:
            s (self): [description]
            data_bits (int): the data size
            trail_size (int): the trail size
    '''
    def construct(s, data_bits, trail_size):
        """def construct(s, data_bits, trail_size):

        Args:
            s (self): [description]
            data_bits (int): the data size
            trail_size (int): the trail size
        """
        # ifcs
        s.recv = RecvIfcRTL(mk_bits(data_bits))
        s.send = SendIfcRTL(mk_bits(data_bits))
        # buffers
        s.trail = PipeQueueRTL(mk_bits(data_bits), trail_size)
        # wires
        # connects
        s.recv //= s.trail.enq
        s.send.msg //= s.trail.deq.ret
        # logic

        @update
        def comb():
            s.send.en@=s.send.rdy & s.trail.deq.rdy
            s.trail.deq.en @= s.send.rdy & s.trail.deq.rdy
            

    def line_trace(s):
        return "{},{},{}".format(s.recv, s.trail.line_trace(), s.send)
