# pymtl_project
## overview
this is a pymtl3 project to simulate a SAT solver accelerator
## install
pip install .
## usage
```python
from satacc.acc import Acc
my_acc=Acc()
my_acc.apply(DefaultPassGroup())
my_acc.sim_tick()
```
