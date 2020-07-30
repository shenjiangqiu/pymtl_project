from ..utils import memAccessDisp

from pymtl3 import *
def test_main():
    component = memAccessDisp.MemAccessDisp()
    component.apply(DefaultPassGroup())
    component.sim_tick()
    component.sim_tick()