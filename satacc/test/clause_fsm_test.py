from pymtl3 import *
from ..clause.clause_controller import Clause_fsm
def test_clause_fsm():

    # def construct(self, size_type, addr_type, item_size, mem_request_dest, recv_queue_size):
    m = Clause_fsm()
    
    m.apply(DefaultPassGroup())
    
    m.sim_tick()
