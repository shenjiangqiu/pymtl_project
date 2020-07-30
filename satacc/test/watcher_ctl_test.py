from ..watcher.watcher_controller import Sized_memory_sender, Sized_memory_sender_in_order
from pymtl3 import *


def test_base():
    # def construct(self, size_type, addr_type, item_size, mem_request_dest):
    #
    m = Sized_memory_sender(mk_bits(32), Bits64, 32, 1)
    m.apply(DefaultPassGroup())
    m.sim_tick()


def test_inorder():

    # def construct(self, size_type, addr_type, item_size, mem_request_dest, recv_queue_size):
    m = Sized_memory_sender_in_order(mk_bits(32), Bits64, 64, 1, 8)
    
    m.apply(DefaultPassGroup())
    
    m.sim_tick()
