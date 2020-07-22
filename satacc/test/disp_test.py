from ..utils import oneToNDisp
from pymtl3 import *


def test_disp():
    disp = oneToNDisp.OneToNDisp(8, 8, 2, 8)
    disp.apply(DefaultPassGroup())

    disp.reset@=1
    disp.sim_tick()
    disp.reset@=0
    disp.recv.msg@=1
    disp.recv.en@=1
    disp.sim_tick()
    disp.recv.msg@=2
    disp.recv.en@=1
    disp.sim_tick()
    disp.recv.msg@=3
    disp.recv.en@=1
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
    disp.sim_tick()
    disp.gives[2].en@=1
    disp.sim_tick()
    disp.gives[2].en@=1

    disp.sim_tick()
    disp.gives[2].en@=0

    disp.sim_tick()
    disp.sim_tick()
