from pymtl3 import *

from .. import acc


def test_acc():
    macc = acc.Acc()
    macc.apply(DefaultPassGroup())
    macc.reset@=1
    macc.sim_tick()
    macc.reset@=0
    macc.sim_tick()
