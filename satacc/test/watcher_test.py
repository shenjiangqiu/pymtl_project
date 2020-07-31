
from pymtl3 import *
from ..watcher.watcher import Watcher


def test_base():
    # def construct(self, size_type, addr_type, item_size, mem_request_dest):
    #
    m = Watcher(0)
    m.apply(DefaultPassGroup())
    m.sim_tick()
