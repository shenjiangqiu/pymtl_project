
from pymtl3 import *
from ..clause.clause import Clause


def test_base():
    # def construct(self, size_type, addr_type, item_size, mem_request_dest):
    #
    m = Clause(0)
    m.apply(DefaultPassGroup())
    m.sim_tick()
