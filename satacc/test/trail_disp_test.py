from ..utils import trail, oneToNDisp
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL


class Trail_Disp(Component):
    '''
    the trail and dispatcher test class
    '''
    def construct(s, data_bits, trail_size, num_outs, input_buffer_size, out_put_buffer_size):
        # ifcs
        s.recv = RecvIfcRTL(mk_bits(data_bits))
        s.gives = [GiveIfcRTL(mk_bits(data_bits)) for _ in range(num_outs)]

        # buffers
        s.trail = trail.Trail(data_bits, trail_size)
        s.disp = oneToNDisp.OneToNDisp(data_bits, num_outs,
                                       input_buffer_size, out_put_buffer_size)

        # wires
        # connects
        s.trail.send //= s.disp.recv
        # logic
        s.recv //= s.trail.recv
        for i in range(num_outs):
            s.gives[i] //= s.disp.gives[i]

    def line_trace(s):
        return "{},{},{}".format(s.recv, s.disp.line_trace(), [give for give in s.gives])


def test_disp():
    disp = Trail_Disp(8, 8, 8, 2, 8)
    disp.apply(DefaultPassGroup())
    disp.reset@=1
    disp.sim_tick()
    disp.reset@=0
    disp.sim_tick()
    disp.recv.msg@=1
    disp.recv.en@=1
    disp.sim_tick()
    disp.recv.msg@=2
    disp.recv.en@=1
    disp.sim_tick()
    disp.recv.msg@=3
    disp.recv.en@=1
    disp.sim_tick()
    disp.recv.msg@=4
    disp.recv.en@=1
    disp.sim_tick()
    disp.sim_tick()
    for i in range(10):
        disp.sim_tick()
    disp.recv.en@=0
    for i in range(8):
        disp.gives[i].en@=1
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
