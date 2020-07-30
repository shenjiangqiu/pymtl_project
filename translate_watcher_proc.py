from satacc.acc import Acc
from satacc.watcher.watcher import Watcher
from satacc.watcher.watcher_data import Watcher_data
from satacc.watcher.watcher_process import Watcher_process
from pymtl3 import *
import os
from pymtl3.passes.backends.yosys import YosysTranslationPass
done = False
try:
    
    macc = Watcher_process(33, 32)
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
