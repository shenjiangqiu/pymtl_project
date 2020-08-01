from ..utils.mem_oparator import Sized_memory_sender_in_order

from pymtl3 import *


def test_main():
    component = Sized_memory_sender_in_order(
        Bits32, Bits64, 32, 1, 8)
    component.apply(DefaultPassGroup())
    component.sim_tick()
    component.sim_tick()
