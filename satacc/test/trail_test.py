from ..utils import trail
from pymtl3 import *


def test_disp():
    t = trail.Trail(8, 8)
    t.apply(DefaultPassGroup())

    t.reset@=1
    t.sim_tick()
    t.reset@=0

    t.recv.en@=1
    t.recv.msg@=1
    t.sim_tick()
    t.recv.en@=1
    t.recv.msg@=2
    t.sim_tick()
    t.recv.en@=1
    t.recv.msg@=3
    t.sim_tick()
    t.recv.en@=0
    t.sim_tick()
    t.sim_tick()
    t.send.rdy@=1
    t.sim_tick()
    t.sim_tick()
