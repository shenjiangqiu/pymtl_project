# pymtl_project
## overview
this is a pymtl3 project to simulate a SAT solver accelerator for python3.6 (their are some problem when using python3.8)
## install
pip install pymtl3
pip install .
## usage
```python
from pymtl3 import *
from satacc.acc import Acc
my_acc=Acc()
my_acc.apply(DefaultPassGroup())
my_acc.sim_tick()
```
