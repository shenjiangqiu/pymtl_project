from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL, GiveIfcRTL, GetIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.queues import PipeQueueRTL
from pymtl3.stdlib.mem import mk_mem_msg, MemMasterIfcRTL, MemMsgType
from pymtl3.stdlib.basic_rtl import Reg, RegEn, RegEnRst


class Sized_memory_sender(Component):
    def construct(s, size_type, addr_type, item_size, mem_request_dest):
        # types
        s.size_type = size_type
        s.addr_type = addr_type
        s.item_size = item_size
        req = Bits144
        # ifcs

        s.size_recv = RecvIfcRTL(size_type)
        s.addr_recv = RecvIfcRTL(addr_type)

        s.mem_out = SendIfcRTL(req)

        # buffers
        s.size_reg = RegEnRst(size_type)
        s.addr_reg = RegEnRst(addr_type)

        # logic
        s.size_en_mux = Mux(Bits1, 2)
        s.size_data_mux = Mux(size_type, 2)
        s.addr_en_mux = Mux(Bits1, 2)
        s.addr_data_mux = Mux(addr_type, 2)
        # connections

        # controled by mux

        s.size_reg.en //= s.size_en_mux.out
        s.size_reg.in_ //= s.size_data_mux.out
        s.addr_reg.en //= s.addr_en_mux.out
        s.addr_reg.in_ //= s.addr_data_mux.out
        # controled by outter signal
        s.addr_en_mux.in_[0] //= s.addr_recv.en
        s.addr_data_mux.in_[0] //= s.addr_recv.msg
        s.size_en_mux.in_[0] //= s.size_recv.en
        s.size_data_mux.in_[0] //= s.size_recv.msg

        @update
        def comb():
            s.size_recv.rdy @= s.size_reg.out != 0
            s.addr_recv.rdy @= s.size_reg.out != 0

            # if the size is zero, listen to outsize sigal, else listen to my self
            s.size_en_mux.sel @= 0 if s.size_reg.out == 0 else 1
            s.size_data_mux.sel @=0 if s.size_reg.out == 0 else 1
            # build the request.
            message = req()

            s.mem_out.msg @= message
            s.size_data_mux.in_[1] @= s.size_data_mux.out - 1
            # addr will change every round
            s.addr_data_mux.in_[
                1]@=s.addr_reg.out + item_size  # addr offset

            if s.mem_out.rdy & (s.size_reg.out != 0):
                # send the request and deduce the size
                s.size_en_mux.in_[1] @= 1
                s.mem_out.en @=1
                s.addr_en_mux.in_[1]@=1

            else:
                s.size_en_mux.in_[1]@=0
                s.addr_en_mux.in_[1]@=0
                s.mem_out.en@=0


# in this class, this component will wait for all request to comeback and then accept new request
class Sized_memory_sender_in_order(Component):
    def construct(s, size_type, addr_type, item_size, mem_request_dest, recv_queue_size):
        # types

        s.size_recv = RecvIfcRTL(size_type)
        s.addr_recv = RecvIfcRTL(addr_type)
        s.data_out = SendIfcRTL(mk_bits(item_size))
        s.mem_out = SendIfcRTL(b153)
        s.mem_in = RecvIfcRTL(b81)
        # buffers
        s.size_reg = RegEnRst(size_type)
        s.addr_reg = RegEnRst(addr_type)
        s.remaining_recv_reg = Reg(size_type)
        s.need_to_push_zero = Reg(b1)
        s.recv_queue = PipeQueueRTL(mk_bits(item_size), recv_queue_size)
        # logic
        s.size_en_mux = Mux(b1, 2)
        s.size_data_mux = Mux(size_type, 2)
        s.addr_en_mux = Mux(b1, 2)
        s.addr_data_mux = Mux(addr_type, 2)
        s.remaining_mux = Mux(size_type, 2)
        # connections

        # controled by mux
        s.remaining_recv_reg.in_ //= s.remaining_mux.out
        s.size_reg.en //= s.size_en_mux.out
        s.size_reg.in_ //= s.size_data_mux.out
        s.addr_reg.en //= s.addr_en_mux.out
        s.addr_reg.in_ //= s.addr_data_mux.out

        s.recv_queue.deq.ret //= s.data_out.msg
        # controled by outter signal

        s.addr_en_mux.in_[0] //= s.addr_recv.en
        s.addr_data_mux.in_[0] //= s.addr_recv.msg
        s.size_en_mux.in_[0] //= s.size_recv.en
        s.size_data_mux.in_[0] //= s.size_recv.msg
        s.remaining_mux.in_[0] //= s.size_recv.msg
        s.recv_queue.enq.rdy //= s.mem_in.rdy
        s.recv_queue.enq.en //= s.mem_in.en

        #s.recv_queue.enq.msg //= s.mem_in.msg[17:81]

        @update
        def comb():
            if s.need_to_push_zero.out == 0:
                s.recv_queue.enq.msg @= s.mem_in.msg[17:49]
            else:
                s.recv_queue.enq.msg @= 0
            if s.need_to_push_zero.out & s.recv_queue.enq.rdy:  # current need, and push it
                s.need_to_push_zero.in_ @=0
            elif s.remaining_recv_reg.out != 0:  # not need yet
                s.need_to_push_zero.in_ @=0
            else:  # it's zero, push zero is needed
                s.need_to_push_zero.in_@=1
            s.recv_queue.deq.en @= s.recv_queue.deq.rdy & s.data_out.rdy
            s.data_out.en @= s.recv_queue.deq.rdy & s.data_out.rdy

            s.size_recv.rdy @=(s.size_reg.out != 
                0) & (s.remaining_recv_reg.out == 0) & (s.need_to_push_zero.out == 0)
            s.addr_recv.rdy @= (s.size_reg.out != 
                0) & (s.remaining_recv_reg.out == 0) & (s.need_to_push_zero.out == 0)

            # if the size is zero, listen to outsize sigal, else listen to my self
            s.size_en_mux.sel @= 0 if s.size_reg.out == 0 else 1
            s.size_data_mux.sel @=0 if s.size_reg.out == 0 else 1
            s.remaining_mux.sel @=0 if s.size_reg.out == 0 else 1
            # build the request.

            s.mem_out.msg @= concat(Bits4(0),
                                    Bits8(mem_request_dest), s.addr_reg.out, Bits77(0))
            s.size_data_mux.in_[1] @= s.size_data_mux.out - 1
            # addr will change every round
            s.addr_data_mux.in_[
                1]@=s.addr_reg.out + item_size  # addr offset

            s.size_en_mux.in_[
                1] @= s.mem_out.rdy & (s.size_reg.out != 0)
            s.mem_out.en @=s.mem_out.rdy & (s.size_reg.out != 0)
            s.addr_en_mux.in_[1]@=s.mem_out.rdy & (s.size_reg.out != 0)
            s.remaining_mux.in_[1]@=s.remaining_mux.out-1 if s.mem_out.rdy & (
                s.size_reg.out != 0) else s.remaining_mux.out
