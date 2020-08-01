from satacc.acc import Acc
from satacc.watcher.watcher import Watcher
from satacc.clause.clause import Clause
from pymtl3 import *
import os
from pymtl3.passes.backends.yosys import YosysTranslationPass
done = False
try:
    
    macc = Clause(1)
    macc.set_metadata( YosysTranslationPass.enable, True)
    macc.elaborate()
    macc.apply(YosysTranslationPass())
    done = True
finally:
    if done:
        print("finished generate verilog")
        path = os.getcwd() + \
            f"/{macc.get_metadata(YosysTranslationPass.translated_filename)}"
        print("\nTranslation finished successfully!")
        print(f"You can find the generated SystemVerilog file at {path}.")
